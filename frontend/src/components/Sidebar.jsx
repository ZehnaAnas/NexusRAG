import { FileText } from "lucide-react";
import Orb from "./Orb.jsx";
import StatusBadge from "./StatusBadge.jsx";

export default function Sidebar({ files, activeFile, onSelectFile, uploading }) {
  return (
    <aside className="flex h-full w-80 shrink-0 flex-col gap-5 border-r border-border bg-surface/70 p-5 backdrop-blur-sm">
      <div className="flex items-center gap-3">
        <Orb state={uploading ? "uploading" : "idle"} size={48} />
        <div>
          <h1 className="font-display text-2xl font-semibold leading-tight text-ink">
            NexusRAG
          </h1>
          <p className="text-sm text-ink-soft">talk to your documents</p>
        </div>
      </div>

      <div className="flex flex-1 flex-col gap-2 overflow-hidden">
        <p className="px-1 text-sm font-semibold uppercase tracking-wide text-ink-soft">
          Chat history
        </p>
        <div className="flex flex-1 flex-col gap-2 overflow-y-auto pr-1">
          {files.length === 0 && (
            <p className="rounded-2xl border border-dashed border-border p-4 text-center text-sm text-ink-soft">
              No documents yet. Use the + button by the message box to
              upload one and start a chat.
            </p>
          )}
          {files.map((f) => (
            <button
              key={f.name}
              onClick={() => onSelectFile(f.name)}
              className={`flex items-center gap-3 rounded-2xl border p-3.5 text-left transition-all
                ${
                  activeFile === f.name
                    ? "border-primary bg-primary-light shadow-sm"
                    : "border-border bg-white hover:border-primary/40"
                }`}
            >
              <div className="rounded-xl bg-peach-light p-2 text-peach-dark">
                <FileText size={18} />
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-base font-medium text-ink font-mono">
                  {f.name}
                </p>
                <div className="mt-1">
                  <StatusBadge status={f.status} />
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
}