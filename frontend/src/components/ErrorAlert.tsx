/** Error alert box. */
export default function ErrorAlert({ message }: { message: string }) {
  return (
    <div className="card border-red-500/40 bg-red-500/10 text-red-400 text-sm p-4">
      ⚠️ {message}
    </div>
  );
}
