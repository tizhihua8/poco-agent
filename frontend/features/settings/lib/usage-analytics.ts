export function getCurrentYearMonth(): string {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
}

export function shiftYearMonth(value: string, delta: number): string {
  const [year, month] = value.split("-").map(Number);
  const next = new Date(year, month - 1 + delta, 1);
  return `${next.getFullYear()}-${String(next.getMonth() + 1).padStart(2, "0")}`;
}

export function getBrowserTimeZone(): string {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
  } catch {
    return "UTC";
  }
}

export function formatMonthLabel(month: string, locale: string): string {
  const date = new Date(`${month}-01T00:00:00`);
  return new Intl.DateTimeFormat(locale, {
    year: "numeric",
    month: "long",
  }).format(date);
}

export function formatDayLabel(day: string, locale: string): string {
  const date = new Date(`${day}T00:00:00`);
  return new Intl.DateTimeFormat(locale, {
    month: "short",
    day: "numeric",
    weekday: "short",
  }).format(date);
}

export function formatCompactNumber(
  value: number,
  locale: string,
  fractionDigits = 2,
): string {
  const absoluteValue = Math.abs(value);

  if (absoluteValue < 1_000) {
    return formatNumber(value, locale);
  }

  const suffixes = ["", "K", "M", "B", "T"];
  let compactValue = absoluteValue;
  let suffixIndex = 0;

  while (compactValue >= 1_000 && suffixIndex < suffixes.length - 1) {
    compactValue /= 1_000;
    suffixIndex += 1;
  }

  if (
    Number(compactValue.toFixed(fractionDigits)) >= 1_000 &&
    suffixIndex < suffixes.length - 1
  ) {
    compactValue /= 1_000;
    suffixIndex += 1;
  }

  const sign = value < 0 ? "-" : "";
  return `${sign}${compactValue.toFixed(fractionDigits)}${suffixes[suffixIndex]}`;
}

export interface CompactNumberScale {
  divisor: number;
  suffix: string;
}

export function getCompactNumberScale(value: number): CompactNumberScale {
  const absoluteValue = Math.abs(value);

  if (absoluteValue >= 1_000_000_000_000) {
    return { divisor: 1_000_000_000_000, suffix: "T" };
  }

  if (absoluteValue >= 1_000_000_000) {
    return { divisor: 1_000_000_000, suffix: "B" };
  }

  if (absoluteValue >= 1_000_000) {
    return { divisor: 1_000_000, suffix: "M" };
  }

  if (absoluteValue >= 1_000) {
    return { divisor: 1_000, suffix: "K" };
  }

  return { divisor: 1, suffix: "" };
}

export function formatNumberWithScale(
  value: number,
  locale: string,
  scale: CompactNumberScale,
  fractionDigits = 1,
): string {
  if (value === 0) {
    return "0";
  }

  if (scale.divisor === 1) {
    return formatNumber(value, locale);
  }

  return `${new Intl.NumberFormat(locale, {
    minimumFractionDigits: fractionDigits,
    maximumFractionDigits: fractionDigits,
  }).format(value / scale.divisor)}${scale.suffix}`;
}

export function formatNumber(value: number, locale: string): string {
  return new Intl.NumberFormat(locale).format(value);
}
