export function ConsultationProgress({ stage, hasPhoto, hasResult }: { stage?: string; hasPhoto: boolean; hasResult: boolean }) {
  const steps = ["Your symptoms", "Photo", "Confirm details", "Screening"];
  const active = hasResult ? 3 : stage === "summary" || stage === "assessment" ? 2 : stage === "photo" ? 1 : 0;
  return <nav aria-label="Consultation progress" className="mb-4">
    <ol className="grid grid-cols-4 gap-2 text-[10px]">
      {steps.map((label, index) => <li key={label} aria-current={index === active ? "step" : undefined}
        className={index === active ? "text-electric-light font-semibold" : "text-white/50"}>
        <span className={`block h-1 mb-2 rounded-full ${index <= active || (index === 1 && hasPhoto) ? "bg-electric" : "bg-white/10"}`} />
        {label}
      </li>)}
    </ol>
    <p className="mt-2 text-xs text-white/50">You can correct an earlier answer at any time.</p>
  </nav>;
}
