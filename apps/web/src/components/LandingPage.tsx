import React from "react";
import { Sparkles, ArrowRight, ShieldCheck, Activity, Users, Stethoscope } from "lucide-react";

interface LandingPageProps {
  onLaunchDemo: () => void;
  onOpenClinician: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({
  onLaunchDemo,
  onOpenClinician,
}) => {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-[#eaeaea] font-sans antialiased selection:bg-[#f72585] selection:text-white">
      {/* ── BRAND ROW / HEADER ── */}
      <header className="border-b border-[#1f1f1f] py-4 bg-[#0a0a0a]/90 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-[1080px] mx-auto px-6 flex items-center justify-between">
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>
            <svg
              className="w-8 h-8 shrink-0"
              viewBox="0 0 34 34"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
            >
              <circle cx="17" cy="17" r="15.5" stroke="#4361ee" strokeWidth="2" />
              <rect x="15.25" y="8.5" width="3.5" height="17" rx="1.75" fill="#f72585" />
              <rect x="8.5" y="15.25" width="17" height="3.5" rx="1.75" fill="#f72585" />
            </svg>
            <span className="font-head font-bold text-xl text-[#eaeaea] tracking-tight">Q-Doc</span>
          </div>

          <div className="flex items-center gap-3 sm:gap-4">
            <button
              onClick={onOpenClinician}
              className="px-3.5 py-1.5 rounded-md font-mono text-xs font-semibold text-[#888888] hover:text-[#eaeaea] border border-[#1f1f1f] hover:border-[#333333] transition"
            >
              Clinician Portal
            </button>
            <button
              onClick={onLaunchDemo}
              className="px-4 py-1.5 rounded-md font-semibold text-xs text-white bg-[#f72585] hover:bg-[#d4186e] transition shadow-[0_2px_14px_rgba(247,37,133,0.32)] flex items-center gap-1.5"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Launch AI Demo</span>
            </button>
          </div>
        </div>
      </header>

      {/* ── HERO ── */}
      <section className="py-16 md:py-20 border-b border-[#1f1f1f]" aria-labelledby="hero-heading">
        <div className="max-w-[1080px] mx-auto px-6">
          <div className="grid grid-cols-1 lg:grid-cols-[1fr_400px] items-center gap-12">
            <div className="space-y-6">
              <h1 id="hero-heading" className="font-head font-bold text-3xl sm:text-4xl lg:text-5xl text-[#eaeaea] leading-[1.14] tracking-tight">
                Screening <em className="not-italic text-[#f72585]">without queue.</em>
              </h1>

              <div className="text-[#888888] text-base leading-relaxed space-y-3.5 max-w-[540px]">
                <p>
                  Outside major government hospitals across the country, lines start forming at 4:00&nbsp;AM
                  just to secure an OPD appointment when the doors finally open at 8:00&nbsp;AM. In a nation
                  where the doctor-to-patient ratio is stretched to its absolute limit, healthcare is often
                  defined by endless, exhausting queues. People travel long distances and lose a full day of
                  wages just for a basic checkup or a routine prescription.
                </p>

                <p>
                  It doesn’t have to be this way. Many common conditions can be screened reliably
                  before a patient ever reaches a doctor. A well-designed first filter that listens,
                  checks symptoms, inspects lesion imagery, and routes intelligently can safely handle
                  routine OPD load without replacing clinical judgment.
                </p>

                <p>
                  Q-Doc is built to be that filter. By screening patients at the door, it lifts a massive
                  burden off our doctors so they can focus on critical cases while sparing patients with
                  non-serious conditions from wasting hours in a waiting room.
                </p>

                <p>
                  Powered by advanced multimodal voice &amp; vision models across regional languages,
                  patients don’t need to be tech-savvy as they just speak in their mother tongue and take a photo.
                </p>
              </div>

              {/* ACTION CTA ROW */}
              <div className="flex flex-wrap items-center gap-4 pt-2">
                <button
                  onClick={onLaunchDemo}
                  className="px-6 py-3 rounded-md font-semibold text-sm text-white bg-[#f72585] hover:bg-[#d4186e] transition shadow-[0_2px_14px_rgba(247,37,133,0.32)] flex items-center gap-2"
                >
                  <span>Launch AI Kiosk Demo</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
                <a
                  href="#how"
                  className="px-5 py-3 rounded-md font-semibold text-sm text-[#eaeaea] border border-[#1f1f1f] hover:border-[#333333] hover:bg-[#111111] transition"
                >
                  See how it works
                </a>
              </div>

              {/* STATS ROW */}
              <div className="flex flex-wrap gap-8 pt-4">
                <div className="border-l-3 border-[#4361ee] pl-3.5">
                  <div className="font-head font-bold text-xl text-[#eaeaea] leading-tight mb-1">
                    1&thinsp;:&thinsp;11,082
                  </div>
                  <div className="text-xs text-[#888888] leading-snug">
                    rural India’s doctor-to-patient ratio<br />(vs WHO norm of 1&thinsp;:&thinsp;1,000)
                  </div>
                </div>

                <div className="border-l-3 border-[#4361ee] pl-3.5">
                  <div className="font-head font-bold text-xl text-[#eaeaea] leading-tight mb-1">
                    22
                  </div>
                  <div className="text-xs text-[#888888] leading-snug">
                    regional languages we’re building toward
                  </div>
                </div>

                <div className="border-l-3 border-[#f72585] pl-3.5">
                  <div className="font-head font-bold text-xl text-[#eaeaea] leading-tight mb-1">
                    100%
                  </div>
                  <div className="text-xs text-[#888888] leading-snug">
                    red-flag malignancy safety recall
                  </div>
                </div>
              </div>
            </div>

            {/* ABSTRACT ECG / KIOSK DIAGRAM */}
            <div className="w-full max-w-[380px] mx-auto lg:max-w-none flex justify-center" aria-hidden="true">
              <svg viewBox="0 0 420 400" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-auto">
                <circle cx="210" cy="200" r="162" stroke="#4361ee" strokeWidth="1.5" opacity="0.38" />
                <circle cx="210" cy="200" r="100" stroke="#4361ee" strokeWidth="1" strokeDasharray="3 9" opacity="0.22" />
                <circle cx="76" cy="128" r="4" fill="#4361ee" opacity="0.52" />
                <circle cx="338" cy="92" r="3" fill="#f72585" opacity="0.62" />
                <circle cx="362" cy="274" r="4.5" fill="#4361ee" opacity="0.38" />
                <circle cx="60" cy="284" r="3" fill="#f72585" opacity="0.52" />
                <circle cx="210" cy="32" r="3.5" fill="#4361ee" opacity="0.46" />
                <circle cx="150" cy="362" r="3" fill="#f72585" opacity="0.42" />
                <circle cx="288" cy="358" r="3.5" fill="#4361ee" opacity="0.38" />
                <circle cx="374" cy="188" r="3" fill="#f72585" opacity="0.46" />
                <circle cx="46" cy="205" r="3" fill="#4361ee" opacity="0.42" />
                <circle cx="122" cy="46" r="3" fill="#f72585" opacity="0.38" />
                <circle cx="302" cy="44" r="3" fill="#4361ee" opacity="0.38" />
                <circle cx="148" cy="278" r="2.5" fill="#4361ee" opacity="0.32" />
                <circle cx="278" cy="130" r="2.5" fill="#f72585" opacity="0.32" />
                <line x1="136" y1="124" x2="144" y2="124" stroke="#4361ee" strokeWidth="1.5" opacity="0.48" />
                <line x1="140" y1="120" x2="140" y2="128" stroke="#4361ee" strokeWidth="1.5" opacity="0.48" />
                <line x1="276" y1="266" x2="284" y2="266" stroke="#4361ee" strokeWidth="1.5" opacity="0.48" />
                <line x1="280" y1="262" x2="280" y2="270" stroke="#4361ee" strokeWidth="1.5" opacity="0.48" />
                <line x1="268" y1="122" x2="276" y2="122" stroke="#f72585" strokeWidth="1.5" opacity="0.38" />
                <line x1="272" y1="118" x2="272" y2="126" stroke="#f72585" strokeWidth="1.5" opacity="0.38" />
                <path
                  d="M 36 200 L 112 200 L 128 216 L 148 148 L 168 258 L 184 190 L 200 200 L 384 200"
                  stroke="#f72585"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <circle cx="384" cy="200" r="9" stroke="#f72585" strokeWidth="1" opacity="0.32" />
                <circle cx="384" cy="200" r="4.5" fill="#f72585" opacity="0.88" />
              </svg>
            </div>
          </div>
        </div>
      </section>

      {/* ── LIVE DEMO BANNER ── */}
      <section className="py-8 bg-[#0f0f0f] border-b border-[#1f1f1f]">
        <div className="max-w-[1080px] mx-auto px-6">
          <div className="border border-[#1f1f1f] rounded-lg p-5 bg-[#111111] flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3.5">
              <div className="w-10 h-10 rounded-full bg-[#f72585]/15 flex items-center justify-center shrink-0">
                <Activity className="w-5 h-5 text-[#f72585]" />
              </div>
              <div>
                <h3 className="font-head font-bold text-sm text-[#eaeaea]">
                  Interactive AI Screening Kiosk Live Simulation
                </h3>
                <p className="text-xs text-[#888888]">
                  Speak in Hindi or English, take an early lesion photo, and observe dynamic clinical differential inquiry.
                </p>
              </div>
            </div>
            <button
              onClick={onLaunchDemo}
              className="w-full md:w-auto px-5 py-2 rounded-md font-semibold text-xs text-white bg-[#4361ee] hover:bg-[#3a50d9] transition shadow-[0_2px_14px_rgba(67,97,238,0.32)] shrink-0 flex items-center justify-center gap-1.5"
            >
              <span>Try Live Kiosk Demo</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </section>

      {/* ── PROBLEM ── */}
      <section className="py-20 border-b border-[#1f1f1f]" aria-labelledby="problem-heading">
        <div className="max-w-[1080px] mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-2 border border-[#1f1f1f] rounded-lg overflow-hidden">
            <div className="p-8 md:p-10 bg-[#111111] md:border-r border-b md:border-b-0 border-[#1f1f1f]">
              <p className="text-xs font-semibold text-[#888888] mb-3 uppercase tracking-wider">The core problem</p>
              <h2 id="problem-heading" className="font-head font-bold text-lg text-[#eaeaea] mb-3 leading-snug">
                Chronic shortage, overloaded hospitals,<br />long queues for routine care.
              </h2>
              <p className="text-sm text-[#888888] leading-relaxed">
                India’s doctor shortage is severe enough that even a basic checkup can mean hours
                of waiting, and that is not only a rural issue. <strong className="text-[#eaeaea] font-semibold">Urban government
                hospitals are equally understaffed relative to demand.</strong> Routine and urgent cases
                funnel through the same overwhelmed system, discouraging people from seeking help until
                a symptom becomes too serious to ignore.
              </p>
            </div>

            <div className="p-8 md:p-10 bg-[#111111]">
              <p className="text-xs font-semibold text-[#888888] mb-3 uppercase tracking-wider">The impact</p>
              <h2 className="font-head font-bold text-lg text-[#eaeaea] mb-3 leading-snug">
                Patients lose wages. Doctors lose time.<br />Minor conditions worsen.
              </h2>
              <p className="text-sm text-[#888888] leading-relaxed">
                For anyone on a daily wage, a hospital visit is <strong className="text-[#eaeaea] font-semibold">a financial trade-off, not just
                a health decision.</strong> A day spent in a queue is a day without income. When the
                outcome is “you’re fine, come back in three months,” the deterrent
                registers clearly. Meanwhile, doctors triaging routine cases have less attention left for
                patients with genuinely urgent or complex needs.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── ROOT CAUSE STRIP ── */}
      <div className="bg-[#0f0f0f] border-b border-[#1f1f1f] py-12" role="region" aria-label="Root cause">
        <div className="max-w-[1080px] mx-auto px-6">
          <div className="max-w-[720px] space-y-5">
            <p className="text-base text-[#888888] leading-relaxed">
              There’s no accessible first-level filter for routine, predictable conditions.
              <strong className="text-[#eaeaea] font-semibold"> Minor and urgent cases funnel through the same overloaded system</strong> regardless of location.
              A patient with a manageable, common condition waits alongside someone in genuine distress, and neither receives the attention they deserve.
            </p>
            <p className="text-sm text-[#888888] italic border-l-2 border-[#1f1f1f] pl-4">
              “We’ve stood in that queue too, and that is why we are building this.”<br />
              <strong className="not-italic text-[#eaeaea]">Divyansh Soni</strong>, Founder · Q-Doc, founded 2026
            </p>
          </div>
        </div>
      </div>

      {/* ── WHO THIS IS FOR ── */}
      <section className="py-20 border-b border-[#1f1f1f]" aria-labelledby="who-heading">
        <div className="max-w-[1080px] mx-auto px-6">
          <h2 id="who-heading" className="font-head font-bold text-2xl text-[#eaeaea] mb-8">
            Who this is for
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 border border-[#1f1f1f] rounded-lg overflow-hidden">
            <div className="p-8 md:p-9 bg-[#111111] md:border-r border-b md:border-b-0 border-[#1f1f1f]">
              <span className="inline-block text-[11px] font-semibold tracking-wider px-2 py-0.5 rounded bg-[#f72585]/15 text-[#f72585] mb-3">
                PRIMARY
              </span>
              <h3 className="font-head font-bold text-base text-[#eaeaea] mb-2.5">
                First-Point Triage Patients
              </h3>
              <p className="text-sm text-[#888888] leading-relaxed mb-5">
                For individuals arriving at overwhelmed medical facilities, Q-Doc acts as an
                intelligent front door that categorizes and channels care instantly. Instead of a
                one-size-fits-all line, the system sorts patients based on actual medical need.
              </p>

              <ul className="space-y-3.5 list-none">
                <li className="flex items-start gap-2.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#4361ee] mt-1.5 shrink-0" />
                  <div>
                    <span className="text-xs font-semibold text-[#eaeaea] block">Immediate Resolution</span>
                    <span className="text-xs text-[#888888]">Straightforward conditions are assessed and given care protocols right at the terminal.</span>
                  </div>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#f72585] mt-1.5 shrink-0" />
                  <div>
                    <span className="text-xs font-semibold text-[#eaeaea] block">Targeted Routing</span>
                    <span className="text-xs text-[#888888]">Patients requiring in-person examination are directed to the right clinical department.</span>
                  </div>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#e05c5c] mt-1.5 shrink-0" />
                  <div>
                    <span className="text-xs font-semibold text-[#eaeaea] block">Urgent Escalation</span>
                    <span className="text-xs text-[#888888]">Critical red flags are flagged and fast-tracked for emergency attention immediately.</span>
                  </div>
                </li>
              </ul>
            </div>

            <div className="p-8 md:p-9 bg-[#111111]">
              <span className="inline-block text-[11px] font-semibold tracking-wider px-2 py-0.5 rounded bg-[#4361ee]/15 text-[#4361ee] mb-3">
                SECONDARY
              </span>
              <h3 className="font-head font-bold text-base text-[#eaeaea] mb-2.5">
                General Public Seeking On-Demand Care
              </h3>
              <p className="text-sm text-[#888888] leading-relaxed">
                Anyone needing a reliable health screening without the friction of scheduling and
                commuting. Wherever a Q-Doc kiosk is stationed, citizens can step up and receive
                immediate, frictionless medical guidance on their own terms.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS ── */}
      <section id="how" className="py-20 border-b border-[#1f1f1f]" aria-labelledby="how-heading">
        <div className="max-w-[1080px] mx-auto px-6">
          <div className="max-w-[620px]">
            <h2 id="how-heading" className="font-head font-bold text-2xl text-[#eaeaea] mb-10">
              How it works
            </h2>

            <div className="space-y-8">
              <div className="grid grid-cols-[48px_1fr] gap-5 items-start">
                <div className="w-11 h-11 rounded-full border border-[#1f1f1f] bg-[#0a0a0a] flex items-center justify-center font-head font-bold text-sm text-[#f72585] shrink-0">
                  1
                </div>
                <div>
                  <h3 className="font-head font-bold text-base text-[#eaeaea] mb-1.5">
                    Walk up and speak
                  </h3>
                  <p className="text-sm text-[#888888] leading-relaxed">
                    No app, no form, no appointment. The patient describes how they’re feeling,
                    out loud, in their own language such as Hindi, English, or whichever regional tongue
                    they think in. The kiosk listens and understands acoustic nuance.
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-[48px_1fr] gap-5 items-start">
                <div className="w-11 h-11 rounded-full border border-[#1f1f1f] bg-[#0a0a0a] flex items-center justify-center font-head font-bold text-sm text-[#f72585] shrink-0">
                  2
                </div>
                <div>
                  <h3 className="font-head font-bold text-base text-[#eaeaea] mb-1.5">
                    Early photo scan &amp; dynamic inquiry
                  </h3>
                  <p className="text-sm text-[#888888] leading-relaxed">
                    The patient takes a lesion photo early. Multimodal vision inspects the morphological
                    patterns directly, derives candidate differential hypotheses, and asks targeted,
                    condition-specific questions without arbitrary caps until clinical clarity is reached.
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-[48px_1fr] gap-5 items-start">
                <div className="w-11 h-11 rounded-full border border-[#1f1f1f] bg-[#0a0a0a] flex items-center justify-center font-head font-bold text-sm text-[#f72585] shrink-0">
                  3
                </div>
                <div>
                  <h3 className="font-head font-bold text-base text-[#eaeaea] mb-1.5">
                    A clear answer, not just a number
                  </h3>
                  <p className="text-sm text-[#888888] leading-relaxed">
                    Non-urgent conditions receive clear provisional diagnoses, evidence-based OTC care,
                    and daily hygiene instructions. Anything ambiguous or critical is formatted into a
                    structured 1-page Clinician Brief with doctor sign-off gating.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── WHERE WE FIT IN ── */}
      <section className="py-20 border-b border-[#1f1f1f]" aria-labelledby="diff-heading">
        <div className="max-w-[1080px] mx-auto px-6">
          <h2 id="diff-heading" className="font-head font-bold text-2xl text-[#eaeaea] mb-8">
            Where we fit in
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 border border-[#1f1f1f] rounded-lg overflow-hidden">
            <div className="p-8 md:p-9 bg-[#111111] md:border-r border-b md:border-b-0 border-[#1f1f1f]">
              <p className="text-xs font-semibold text-[#888888] mb-3 uppercase tracking-wider">What already exists</p>
              <h3 className="font-head font-bold text-base text-[#888888] mb-2.5">
                Tools that help doctors decide
              </h3>
              <p className="text-sm text-[#888888] leading-relaxed">
                Government systems like Smart Doctor CDSS and eSanjeevani are built for the
                provider’s side of care, offering decision support for clinicians and
                teleconsultation for registered patients. Several kiosk makers already screen
                well, but mostly through touchscreens and structured forms, in a handful of
                languages, assuming a patient who can read, type, and navigate a menu.
              </p>
            </div>

            <div className="p-8 md:p-9 bg-[#111111]">
              <p className="text-xs font-semibold text-[#4361ee] mb-3 uppercase tracking-wider">What we’re building</p>
              <h3 className="font-head font-bold text-base text-[#4361ee] mb-2.5">
                A kiosk that listens, sees, and speaks back
              </h3>
              <p className="text-sm text-[#eaeaea] leading-relaxed">
                Voice-native, in the patient’s own regional language, combined with
                multimodal lesion vision to reach the last-mile public locations
                existing government infrastructure hasn’t fully covered yet. The interface
                is a conversation, not a form. Patients describe symptoms in their own words;
                the system understands the way people actually talk about feeling unwell.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── ABOUT / CONTACT ── */}
      <section id="about" className="py-20 border-b border-[#1f1f1f]" aria-labelledby="about-heading">
        <div className="max-w-[1080px] mx-auto px-6">
          <h2 id="about-heading" className="font-head font-bold text-2xl text-[#eaeaea] mb-8">
            About &amp; Contact
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 border border-[#1f1f1f] rounded-lg overflow-hidden">
            <div className="p-8 md:p-9 bg-[#111111] md:border-r border-b md:border-b-0 border-[#1f1f1f]">
              <p className="text-xs font-semibold text-[#888888] mb-3 uppercase tracking-wider">Who we are</p>
              <h3 className="font-head font-bold text-base text-[#eaeaea] mb-2.5">
                Built by someone who’s been in that queue
              </h3>
              <p className="text-sm text-[#888888] leading-relaxed mb-3">
                Q-Doc is an early-stage health-tech startup building <strong className="text-[#eaeaea] font-semibold">AI-powered screening
                kiosks for government hospitals and public spaces across India</strong>. Patients
                describe symptoms in their own language, basic vitals and lesions are inspected, and anyone who needs a doctor is routed to one.
              </p>
              <p className="text-sm text-[#888888] leading-relaxed mb-3">
                Our goal is to cut OPD queues and free doctors for critical cases.
              </p>
              <p className="text-sm text-[#888888] leading-relaxed mb-5">
                I’m a 3rd-year <strong className="text-[#eaeaea] font-semibold">Mathematics and Computing student at IIT&nbsp;BHU</strong>.
              </p>

              <div className="flex flex-col gap-2.5">
                <div className="inline-flex items-center gap-3 p-3 border border-[#1f1f1f] rounded-md bg-[#0a0a0a]">
                  <div className="w-9 h-9 rounded-full bg-gradient-to-br from-[#4361ee] to-[#f72585] flex items-center justify-center font-head font-bold text-xs text-white shrink-0">
                    DS
                  </div>
                  <div className="flex flex-col">
                    <span className="text-xs font-semibold text-[#eaeaea]">Divyansh Soni</span>
                    <span className="text-[11px] text-[#888888]">Founder · Q-Doc · Founded 2026</span>
                  </div>
                </div>

                <div className="inline-flex items-center gap-3 p-3 border border-[#1f1f1f] rounded-md bg-[#0a0a0a]">
                  <div className="w-9 h-9 rounded-full bg-gradient-to-br from-[#4361ee] to-[#3a0ca3] flex items-center justify-center font-head font-bold text-[10px] text-white shrink-0 tracking-tight">
                    IIT
                  </div>
                  <div className="flex flex-col">
                    <span className="text-xs font-semibold text-[#eaeaea]">IIT BHU Incubation Centre</span>
                    <span className="text-[11px] text-[#888888]">Supported by</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="p-8 md:p-9 bg-[#111111]">
              <p className="text-xs font-semibold text-[#888888] mb-3 uppercase tracking-wider">Get in touch</p>
              <h3 className="font-head font-bold text-base text-[#eaeaea] mb-2.5">
                We’d love to hear from you
              </h3>
              <p className="text-sm text-[#888888] leading-relaxed mb-3">
                Whether you run a government hospital, manage public health infrastructure, or
                are a researcher interested in last-mile healthcare access, please reach out.
              </p>
              <p className="text-sm text-[#888888] leading-relaxed mb-5">
                We are actively looking for pilot partners across India.
              </p>
              <a
                href="https://mail.google.com/mail/?view=cm&to=founder@q-doc.live"
                className="inline-flex items-center gap-2 text-sm text-[#f72585] hover:underline font-medium"
                target="_blank"
                rel="noopener noreferrer"
              >
                <span>founder@q-doc.live</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* ── FOOTER ── */}
      <footer className="py-12 bg-[#0a0a0a]">
        <div className="max-w-[1080px] mx-auto px-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <p className="text-xs text-[#888888] leading-relaxed">
            Early-stage, built by a team that has stood in that queue too. Founded 2026.<br />
            Supported by <strong className="text-[#eaeaea]">IIT BHU Incubation Centre</strong>.
          </p>
          <a
            href="https://mail.google.com/mail/?view=cm&to=founder@q-doc.live"
            className="text-xs text-[#f72585] hover:underline font-medium"
            target="_blank"
            rel="noopener noreferrer"
          >
            founder@q-doc.live
          </a>
        </div>
      </footer>
    </div>
  );
};

