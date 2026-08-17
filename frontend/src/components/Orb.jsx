// The Orb is NexusRAG's little companion. Its color and motion reflect
// what the app is actually doing, so it's read as status, not decoration.
//   idle      -> gentle float, calm violet/peach gradient
//   uploading -> amber gradient, faster pulse
//   thinking  -> spinning gradient ring, quick pulse
//   error     -> rose gradient, still

const STATE_STYLES = {
  idle: {
    gradient: ["#7C5CFC", "#FF8FA3"],
    className: "animate-float",
  },
  uploading: {
    gradient: ["#F5A524", "#FF8FA3"],
    className: "animate-pulseSoft",
  },
  thinking: {
    gradient: ["#7C5CFC", "#2DD4BF"],
    className: "animate-pulseSoft",
  },
  error: {
    gradient: ["#FB5B7B", "#F5A524"],
    className: "",
  },
};

export default function Orb({ state = "idle", size = 56 }) {
  const { gradient, className } = STATE_STYLES[state] || STATE_STYLES.idle;
  const gradId = `orb-grad-${gradient.join("").replace(/#/g, "")}`;

  return (
    <div
      className={`relative shrink-0 ${className}`}
      style={{ width: size, height: size }}
      aria-hidden="true"
    >
      <svg viewBox="0 0 100 100" width={size} height={size}>
        <defs>
          <linearGradient id={gradId} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={gradient[0]} />
            <stop offset="100%" stopColor={gradient[1]} />
          </linearGradient>
        </defs>
        <path
          d="M50 8C68 8 90 22 92 45C94 66 76 90 52 92C28 94 8 76 8 52C8 28 30 8 50 8Z"
          fill={`url(#${gradId})`}
        />
        <circle cx="38" cy="46" r="5" fill="white" opacity="0.9" />
        <circle cx="62" cy="46" r="5" fill="white" opacity="0.9" />
        <path
          d="M38 62c5 5 19 5 24 0"
          stroke="white"
          strokeWidth="4"
          strokeLinecap="round"
          fill="none"
          opacity="0.9"
        />
      </svg>
    </div>
  );
}
