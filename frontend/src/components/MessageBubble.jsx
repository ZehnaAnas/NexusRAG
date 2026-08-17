import Orb from "./Orb.jsx";

export default function MessageBubble({ role, content }) {
  const isUser = role === "user";

  return (
    <div
      className={`flex items-end gap-2 animate-riseIn ${
        isUser ? "flex-row-reverse" : "flex-row"
      }`}
    >
      {!isUser && <Orb state="idle" size={30} />}
      <div
        className={`max-w-[70%] px-4 py-3 text-sm leading-relaxed shadow-sm
          ${
            isUser
              ? "bg-primary text-white rounded-3xl rounded-br-lg"
              : "bg-white text-ink rounded-3xl rounded-bl-lg border border-border"
          }`}
      >
        {content}
      </div>
    </div>
  );
}
