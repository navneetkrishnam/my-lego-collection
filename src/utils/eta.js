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
  
  if (minutes < 60) {
    const roundedMins = Math.round(minutes / 5) * 5;
    if (roundedMins < 15) return "~10 mins";
    if (roundedMins <= 20) return "15 - 20 mins";
    if (roundedMins <= 30) return "20 - 30 mins";
    if (roundedMins <= 45) return "30 - 45 mins";
    return "45 - 60 mins";
  } else {
    const hours = minutes / 60;
    const roundedHours = Math.round(hours * 2) / 2;
    
    if (roundedHours === 1) return "~1 hour";
    if (Number.isInteger(roundedHours)) {
      return `${roundedHours - 0.5} - ${roundedHours} hours`;
    } else {
      return `${Math.floor(roundedHours)} - ${roundedHours} hours`;
    }
  }
}
