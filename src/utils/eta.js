export function calculateETA(pieces) {
  if (!pieces || pieces <= 0) return "N/A";
  
  let ratePerHour;
  if (pieces < 300) {
    ratePerHour = 250;
  } else if (pieces <= 1000) {
    ratePerHour = 200;
  } else {
    ratePerHour = 150;
  }
  
  const minutes = (pieces / ratePerHour) * 60;
  const roundedMins = Math.round(minutes / 5) * 5;
  
  // Ensure at least 5 mins
  return `${Math.max(5, roundedMins)} mins`;
}
