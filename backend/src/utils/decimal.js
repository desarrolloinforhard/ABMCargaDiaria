function decimalToCents(value) {
  const text = String(value ?? "0").trim();
  const sign = text.startsWith("-") ? -1 : 1;
  const normalized = text.replace("-", "");
  const [integerPart, decimalPart = ""] = normalized.split(".");
  const centsText = `${integerPart || "0"}${decimalPart.padEnd(2, "0").slice(0, 2)}`;
  const cents = Number.parseInt(centsText, 10);
  return Number.isNaN(cents) ? 0 : sign * cents;
}

function centsToDecimal(cents) {
  const sign = cents < 0 ? "-" : "";
  const absolute = Math.abs(cents);
  const integerPart = Math.floor(absolute / 100);
  const decimalPart = String(absolute % 100).padStart(2, "0");
  return `${sign}${integerPart}.${decimalPart}`;
}

module.exports = {
  decimalToCents,
  centsToDecimal,
};
