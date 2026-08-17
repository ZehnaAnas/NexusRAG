import { CheckCircle2, Loader2, AlertTriangle, Circle } from "lucide-react";

const CONFIG = {
  processing: {
    label: "Processing",
    icon: Loader2,
    className: "bg-amber-light text-amber",
    spin: true,
  },
  completed: {
    label: "Ready",
    icon: CheckCircle2,
    className: "bg-mint-light text-mint",
    spin: false,
  },
  failed: {
    label: "Failed",
    icon: AlertTriangle,
    className: "bg-rose-light text-rose",
    spin: false,
  },
  unknown: {
    label: "Unknown",
    icon: Circle,
    className: "bg-border text-ink-soft",
    spin: false,
  },
};

export default function StatusBadge({ status }) {
  // backend can return "Failed: <reason>" — normalize to "failed"
  const key = status?.toLowerCase().startsWith("failed")
    ? "failed"
    : CONFIG[status]
    ? status
    : "unknown";
  const { label, icon: Icon, className, spin } = CONFIG[key];

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium font-mono ${className}`}
    >
      <Icon size={12} className={spin ? "animate-spin" : ""} />
      {label}
    </span>
  );
}
