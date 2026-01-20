// src/utils/format.js

/**
 * Formatteer bedrag als € 1.234,56
 */
export function formatCurrency(value) {
  if (value === null || value === undefined || value === "") return "";

  const number = Number(value);
  if (isNaN(number)) return "";

  return new Intl.NumberFormat("nl-NL", {
    style: "currency",
    currency: "EUR",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(number);
}

/**
 * Aantal netjes weergeven (geen decimalen)
 */
export function formatQty(value) {
  if (value === null || value === undefined || value === "") return "";
  return Number(value);
}
