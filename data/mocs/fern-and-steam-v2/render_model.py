#!/usr/bin/env python3
"""Render actual recursive LDraw meshes with Mitsuba, without proxy geometry.

Example:
  /private/tmp/fern-steam-py/bin/python render_model.py --samples 128
  ... render_model.py --input other.ldr --output /tmp/check.png --width 640 --samples 16

Requires numpy, Pillow and Mitsuba. Geometry defaults to Studio's installed
LDraw library; --library may select another complete LDraw installation.
"""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re
import time

import numpy as np

HERE = Path(__file__).resolve().parent


class Library:
    def __init__(self, root: Path, extra: Path | None = None):
        self.root = root
        self.roots = [root / 'parts', root / 'p', root / 'UnOfficial/parts',
                      root / 'UnOfficial/p']
        if extra is not None:
            self.roots.extend([extra / 'parts', extra / 'p'])
        self.used = set()

    @lru_cache(None)
    def resolve(self, name: str) -> Path:
        name = name.replace('\\', '/').lower()
        for folder in self.roots:
            path = folder / name
            if path.is_file():
                self.used.add(path)
                return path
        raise FileNotFoundError(f'LDraw geometry missing: {name}')

    @lru_cache(None)
    def part(self, name: str):
        return self.parse(self.resolve(name).read_text(errors='replace'))

    def parse(self, text: str, step_limit=None):
        groups = defaultdict(list)
        clockwise = False
        invert = False
        step = 1
        for line in text.splitlines():
            t = line.split()
            if not t:
                continue
            if t[0] == '0':
                if len(t) > 1 and t[1] == 'STEP':
                    step += 1
                    if step_limit is not None and step > step_limit:
                        break
                if 'BFC' in t:
                    if 'INVERTNEXT' in t:
                        invert = True
                    if 'CCW' in t:
                        clockwise = False
                    elif 'CW' in t:
                        clockwise = True
                continue
            if t[0] == '1':
                color = int(t[1], 0) if t[1].lower().startswith('0x') else int(t[1])
                offset = np.array(t[2:5], dtype=float)
                matrix = np.array(t[5:14], dtype=float).reshape(3, 3)
                reflected = np.linalg.det(matrix) < 0
                for child_color, tris in self.part(' '.join(t[14:])).items():
                    transformed = tris @ matrix.T + offset
                    if reflected != invert:
                        transformed = transformed[:, [0, 2, 1], :]
                    groups[color if child_color == 16 else child_color].append(transformed)
                invert = False
            elif t[0] in ('3', '4'):
                count = int(t[0])
                color = int(t[1], 0) if t[1].lower().startswith('0x') else int(t[1])
                vertices = np.array(t[2:2 + count * 3], dtype=float).reshape(count, 3)
                tris = vertices[[[0, 1, 2]]] if count == 3 else vertices[[[0, 1, 2], [0, 2, 3]]]
                if clockwise:
                    tris = tris[:, [0, 2, 1], :]
                groups[color].append(tris)
                invert = False
        return {c: np.concatenate(v) for c, v in groups.items() if v}


def read_colors(path):
    colors = {}
    for line in path.read_text(errors='replace').splitlines():
        m = re.search(r'!COLOUR (\S+)\s+CODE\s+(\d+)\s+VALUE\s+#([0-9A-Fa-f]{6})', line)
        if m:
            name, code, value = m.groups()
            alpha = re.search(r'ALPHA\s+(\d+)', line)
            rgb = np.array([int(value[i:i+2], 16) / 255 for i in (0, 2, 4)])
            colors[int(code)] = {'name': name, 'rgb': rgb, 'alpha': int(alpha[1]) if alpha else 255}
    # Studio bundles a 2013 LDConfig alongside a newer color table. Read newly
    # introduced codes (such as Coral 353) from that table without replacing
    # colors present in LDConfig or silently choosing a neighboring color.
    studio_table = path.parent.parent / 'data/StudioColorDefinition.txt'
    if studio_table.is_file():
        with studio_table.open() as f:
            for row in csv.DictReader(f, delimiter='\t'):
                try:
                    code = int(row['LDraw Color Code'])
                    value = row['RGB value'].lstrip('#')
                    rgb = np.array([int(value[i:i+2], 16) / 255 for i in (0, 2, 4)])
                    colors.setdefault(code, {'name': row['LDraw Color Name'], 'rgb': rgb,
                                             'alpha': round(float(row['Alpha']) * 255)})
                except (ValueError, KeyError):
                    continue
    return colors


def write_ply(path, tris):
    # Keep polygon normals hard: no shading across real LEGO edges. Weld exact
    # positions to reduce file size; Mitsuba face_normals preserves faceting.
    vertices, indices = np.unique(tris.astype('<f4').reshape(-1, 3), axis=0, return_inverse=True)
    indices = indices.reshape(-1, 3).astype('<i4')
    faces = np.empty(len(indices), dtype=[('count', 'u1'), ('indices', '<i4', (3,))])
    faces['count'] = 3
    faces['indices'] = indices
    header = (f'ply\nformat binary_little_endian 1.0\nelement vertex {len(vertices)}\n'
              f'property float x\nproperty float y\nproperty float z\n'
              f'element face {len(indices)}\nproperty list uchar int vertex_indices\nend_header\n')
    with path.open('wb') as f:
        f.write(header.encode())
        vertices.tofile(f)
        faces.tofile(f)


def material(color):
    rgb = color['rgb']
    # LDConfig values are display sRGB; convert for linear-light reflectance.
    linear = np.where(rgb <= .04045, rgb / 12.92, ((rgb + .055) / 1.055) ** 2.4)
    if color['alpha'] < 255:
        # Solid dielectric respects the actual inner and outer glazing surfaces.
        # LDConfig's transparent clear is tinted pale cyan for CAD visibility;
        # clear ABS in a photographic render should be almost colorless.
        tint = np.ones(3) * .985 if 'Clear' in color['name'] else .65 + .34 * rgb
        return {'type': 'dielectric', 'int_ior': 1.49, 'ext_ior': 1.0,
                'specular_transmittance': {'type': 'rgb', 'value': tint.tolist()}}
    return {'type': 'roughplastic', 'distribution': 'ggx', 'alpha': .13,
            'int_ior': 1.49, 'diffuse_reflectance': {'type': 'rgb', 'value': linear.tolist()}}


def render(args):
    import mitsuba as mi
    mi.set_variant('scalar_rgb')
    from PIL import Image
    start = time.time()
    library = Library(args.library, args.extra_library)
    groups = library.parse(args.input.read_text(), args.step)
    if not groups:
        raise ValueError('No triangles found in input model')
    colors = read_colors(args.library / 'LDConfig.ldr')
    mesh_key = args.input.read_bytes() + f'\nstep={args.step}'.encode()
    folder = args.mesh_dir / hashlib.sha256(mesh_key).hexdigest()[:12]
    folder.mkdir(parents=True, exist_ok=True)
    lo, hi = np.full(3, np.inf), np.full(3, -np.inf)
    meshes = {}
    count = 0
    for code, triangles in groups.items():
        triangles = triangles * np.array([.05, -.05, .05])
        triangles = triangles[:, [0, 2, 1], :]  # handedness change: Y down to Y up
        lo = np.minimum(lo, triangles.min(axis=(0, 1)))
        hi = np.maximum(hi, triangles.max(axis=(0, 1)))
        count += len(triangles)
        filename = folder / f'color-{code}.ply'
        write_ply(filename, triangles)
        if code >= 0x2000000:
            value = code & 0xffffff
            color = {'name': 'Direct', 'alpha': 255,
                     'rgb': np.array([(value >> shift & 255) / 255 for shift in (16, 8, 0)])}
        elif code in colors:
            color = colors[code]
        else:
            raise ValueError(f'Unknown LDraw color {code}; no substitute rendered')
        meshes[f'part_color_{code}'] = {'type': 'ply', 'filename': str(filename),
                                      'face_normals': True, 'bsdf': material(color)}
    print(f'Geometry: {count:,} triangles; {len(meshes)} colors; {len(library.used)} LDraw files', flush=True)
    center = (lo + hi) / 2
    extent = hi - lo
    # Camera is in front (+Z), elevated 30 degrees, with a restrained side angle.
    direction = np.array([.70, .73, 1.0])
    if args.rear:
        direction[0] *= -1
        direction[2] *= -1
    direction /= np.linalg.norm(direction)
    origin = center + direction * max(extent) * 4
    right = np.cross(direction, [0, 1, 0]); right /= np.linalg.norm(right)
    up = np.cross(right, direction)
    corners = np.array([[x, y, z] for x in (lo[0], hi[0])
                        for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]) - center
    aspect = args.width / args.height
    half_w = np.ptp(corners @ right) / 2 * 1.13
    half_h = np.ptp(corners @ up) / 2 * 1.13
    half_w = max(half_w, half_h * aspect)
    half_h = half_w / aspect
    T = mi.ScalarTransform4f
    scene_dict = {
        'type': 'scene',
        'integrator': {'type': 'path', 'max_depth': 24, 'rr_depth': 8, 'hide_emitters': True},
        'sensor': {'type': 'orthographic',
                   'to_world': T().look_at(origin=origin.tolist(), target=center.tolist(), up=[0, 1, 0])
                               @ T().scale([half_w, half_w, 1]),
                   'sampler': {'type': 'independent', 'sample_count': args.samples},
                   'film': {'type': 'hdrfilm', 'width': args.width, 'height': args.height,
                            'rfilter': {'type': 'tent'}, 'pixel_format': 'rgb'}},
        'environment': {'type': 'constant', 'radiance': {'type': 'rgb', 'value': [.48, .465, .43]}},
        'floor': {'type': 'rectangle',
                  'to_world': T().translate([center[0], lo[1] - .015, center[2]])
                              @ T().rotate([1, 0, 0], -90) @ T().scale(250),
                  'bsdf': {'type': 'diffuse', 'reflectance': {'type': 'rgb', 'value': [.80, .775, .73]}}},
        **meshes,
    }
    def area_light(key, position, power, size):
        scene_dict[key] = {'type': 'rectangle',
                           'to_world': T().look_at(origin=position, target=center.tolist(), up=[0, 1, 0])
                                       @ T().scale(size),
                           'emitter': {'type': 'area', 'radiance': {'type': 'rgb', 'value': power}}}
    area_light('key', (center + [-22, 40, 32]).tolist(), [5.5, 5.25, 4.85], [17, 17, 1])
    area_light('fill', (center + [27, 24, 8]).tolist(), [2.0, 2.05, 2.2], [13, 18, 1])
    area_light('rim', (center + [0, 33, -25]).tolist(), [3.2, 3.15, 3.0], [12, 10, 1])
    scene = mi.load_dict(scene_dict)
    print(f'Rendering {args.width}×{args.height}, {args.samples} spp…', flush=True)
    radiance = np.array(mi.render(scene, seed=args.seed)) * args.exposure
    # Gentle shoulder, preserving white ABS highlights without a harsh clip.
    radiance = np.maximum(0, radiance)
    mapped = radiance / (1 + .20 * radiance)
    srgb = np.where(mapped <= .0031308, mapped * 12.92, 1.055 * mapped ** (1 / 2.4) - .055)
    pixels = np.uint8(np.clip(srgb, 0, 1) * 255 + .5)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(pixels).save(args.output)
    metadata = {'input': str(args.input), 'input_sha256': hashlib.sha256(args.input.read_bytes()).hexdigest(),
                'triangles': count, 'colors': len(meshes), 'library_files': len(library.used),
                'width': args.width, 'height': args.height, 'samples': args.samples,
                'seed': args.seed, 'rear': args.rear, 'exposure': args.exposure,
                'library_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in sorted(library.used)},
                'bounds_studs': [lo.tolist(), hi.tolist()], 'step': args.step,
                'seconds': round(time.time() - start, 1)}
    args.output.with_suffix('.render.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(f'Saved {args.output} ({metadata["seconds"]}s)', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=HERE / 'fern-and-steam-v2.ldr')
    parser.add_argument('--output', type=Path, default=HERE / 'preview.png')
    parser.add_argument('--library', type=Path, default=Path('/Applications/Studio 2.0/ldraw'))
    parser.add_argument('--mesh-dir', type=Path, default=Path('/private/tmp/fern-steam-v2-mesh'))
    parser.add_argument('--extra-library', type=Path,
                        default=HERE / 'ldraw')
    parser.add_argument('--width', type=int, default=1440)
    parser.add_argument('--height', type=int, default=1200)
    parser.add_argument('--samples', type=int, default=128)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--exposure', type=float, default=1.12)
    parser.add_argument('--rear', action='store_true')
    parser.add_argument('--step', type=int)
    render(parser.parse_args())


if __name__ == '__main__':
    main()
