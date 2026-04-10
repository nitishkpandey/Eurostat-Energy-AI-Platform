export const numberFmt = new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 });
export const compactFmt = new Intl.NumberFormat("en-US", {
  notation: "compact",
  maximumFractionDigits: 1,
});

export const formatAxis = (value) => numberFmt.format(Number.isFinite(Number(value)) ? Number(value) : 0);

export const formatDateTime = (date) =>
  date.toLocaleString("en-US", {
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });

export const isoNow = () => new Date().toISOString();
