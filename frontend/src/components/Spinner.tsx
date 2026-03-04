/** Generic loading spinner. */
export default function Spinner({ size = 24 }: { size?: number }) {
  return (
    <div
      className="animate-spin rounded-full border-2 border-primary/30 border-t-primary"
      style={{ width: size, height: size }}
      role="status"
      aria-label="Loading"
    />
  );
}
