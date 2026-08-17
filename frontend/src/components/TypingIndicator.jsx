import Orb from "./Orb.jsx";

export default function TypingIndicator() {
  return (
    <div className="flex items-end gap-2 animate-riseIn">
      <Orb state="thinking" size={30} />
      <div className="flex items-center gap-1 rounded-3xl rounded-bl-lg border border-border bg-white px-4 py-3 shadow-sm">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="h-1.5 w-1.5 rounded-full bg-primary/60 animate-dotBounce"
            style={{ animationDelay: `${i * 0.15}s` }}
          />
        ))}
      </div>
    </div>
  );
}
