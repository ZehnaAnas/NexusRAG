import { useEffect, useRef, useState } from "react";
import { Send, Sparkles, Plus, Loader2 } from "lucide-react";
import Orb from "./Orb.jsx";
import MessageBubble from "./MessageBubble.jsx";
import TypingIndicator from "./TypingIndicator.jsx";
import StatusBadge from "./StatusBadge.jsx";

export default function ChatPanel({
  activeFile,
  messages,
  onAsk,
  asking,
  onUploadFile,
  uploading,
}) {
  const [input, setInput] = useState("");
  const scrollRef = useRef(null);
  const fileInputRef = useRef(null);
  const isReady = activeFile?.status === "completed";

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, asking]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || !isReady || asking) return;
    onAsk(trimmed);
    setInput("");
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) onUploadFile(file);
    e.target.value = "";
  };

  if (!activeFile) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-4 p-8 text-center">
        <Orb state="idle" size={80} />
        <h2 className="font-display text-xl font-semibold text-ink">
          Upload a document to get started
        </h2>
        <p className="max-w-sm text-base text-ink-soft">
          Use the + button next to the message box below to add a PDF, DOCX,
          or TXT file. Once it's ready, ask it anything.
        </p>
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          className="flex items-center gap-2 rounded-full bg-primary px-5 py-2.5 text-base font-medium text-white transition-transform hover:bg-primary-dark active:scale-95 disabled:opacity-50"
        >
          {uploading ? (
            <Loader2 size={18} className="animate-spin" />
          ) : (
            <Plus size={18} />
          )}
          Upload a document
        </button>
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          disabled={uploading}
          onChange={handleFileChange}
        />
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <header className="flex items-center justify-between border-b border-border bg-surface/70 px-6 py-4 backdrop-blur-sm">
        <div>
          <h2 className="font-display text-lg font-semibold text-ink">
            {activeFile.name}
          </h2>
          <p className="text-sm text-ink-soft">Ask anything about this file</p>
        </div>
        <StatusBadge status={activeFile.status} />
      </header>

      <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto p-6">
        {!isReady && (
          <div className="flex items-center gap-2 rounded-2xl border border-amber/30 bg-amber-light px-4 py-3 text-base text-ink">
            <Sparkles size={18} />
            Still reading through this document — you can ask questions once
            it says "Ready".
          </div>
        )}
        {messages.length === 0 && isReady && (
          <p className="rounded-2xl border border-dashed border-border p-4 text-center text-base text-ink-soft">
            No questions yet — try asking what this document is about.
          </p>
        )}
        {messages.map((m, i) => (
          <MessageBubble key={i} role={m.role} content={m.content} />
        ))}
        {asking && <TypingIndicator />}
      </div>

      <form
        onSubmit={handleSubmit}
        className="flex items-center gap-3 border-t border-border bg-surface/70 p-4 backdrop-blur-sm"
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          disabled={uploading}
          onChange={handleFileChange}
        />
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          title="Upload a document"
          className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full border border-border bg-white text-ink-soft transition-colors hover:border-primary hover:text-primary disabled:opacity-50"
        >
          {uploading ? (
            <Loader2 size={18} className="animate-spin" />
          ) : (
            <Plus size={20} />
          )}
        </button>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={!isReady || asking}
          placeholder={
            isReady ? "Ask about this document…" : "Waiting for processing…"
          }
          className="flex-1 rounded-full border border-border bg-white px-4 py-3 text-base text-ink placeholder:text-ink-soft/70 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 disabled:opacity-60"
        />
        <button
          type="submit"
          disabled={!isReady || asking || !input.trim()}
          className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-primary text-white transition-transform hover:bg-primary-dark active:scale-95 disabled:opacity-40 disabled:hover:bg-primary"
        >
          <Send size={18} />
        </button>
      </form>
    </div>
  );
}