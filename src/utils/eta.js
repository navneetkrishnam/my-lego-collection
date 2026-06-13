export function calculateRawMinutes(pieces) {
  if (!pieces || pieces <= 0) return 0;

  let ratePerHour;
  if (pieces < 500) {
    ratePerHour = 300;
  } else if (pieces <= 2000) {
    ratePerHour = 250;
  } else {
    ratePerHour = 200;
  }

  const minutes = (pieces / ratePerHour) * 60;
  const roundedMins = Math.round(minutes / 5) * 5;

  return Math.max(5, roundedMins);
}

export function calculateETA(pieces) {
  const mins = calculateRawMinutes(pieces);
  if (mins === 0) return "N/A";
  return `${mins} mins`;
}
