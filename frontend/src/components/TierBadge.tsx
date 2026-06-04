interface Props {
  tier: number | null;
  points: number;
}

function tone(tier: number | null, points: number) {
  if (tier === null) return "bg-ink-700 text-ink-200";
  if (points > 0 && tier <= 2) return "bg-good/15 text-good border border-good/30";
  if (points > 0) return "bg-warn/15 text-warn border border-warn/30";
  if (points === 0) return "bg-ink-700 text-ink-200 border border-ink-500/30";
  return "bg-bad/15 text-bad border border-bad/30";
}

export function TierBadge({ tier, points }: Props) {
  return (
    <span
      className={[
        "inline-flex items-center rounded-full px-2.5 py-1 text-[11px] font-semibold tracking-wide",
        tone(tier, points),
      ].join(" ")}
    >
      {tier === null ? "N/A" : `Tier ${tier}`}
    </span>
  );
}
