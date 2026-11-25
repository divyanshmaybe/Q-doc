import { motion, useReducedMotion } from "framer-motion";
import { TeamPortrait } from "./TeamPortrait";

const chapters = [
  { id: "waiting-room", name: "The starting point", title: "A checkup shouldn’t cost a whole day.", text: "Long journeys. Crowded waiting rooms. Another day away from work. Q-Doc began with a frustration our team knew firsthand: even the first step in getting care can feel out of reach.", detail: "Our focus: the patients and care teams navigating crowded government hospital OPDs.", presenter: 0 },
  {
    id: "kiosk-idea",
    name: "The idea",
    title: "Walk up. Speak your language. Get connected to care.",
    text: "We’re developing a voice-first health kiosk for hospitals and public spaces. You can explain what brought you in using a language you’re comfortable speaking, without having to read or fill out a form.",
    detail: "The kiosk is designed to support basic health checks and pass a clear summary to the clinician who will guide your care.",
    presenter: 1,
  },
  {
    id: "saving-time",
    name: "Why time matters",
    title: "Less time in queues. More time for care.",
    text: "Healthcare should be one of India’s most efficient services. Patients shouldn’t lose hours in queues for basic checks or routine follow-ups, and doctors need time for cases that require their attention. Q-Doc is being developed to screen patients at the first point of contact, identify possible conditions, and flag who may need further care. A supervising clinician reviews the assessment and makes the final diagnosis.",
    detail: "India’s 2018 National Health Profile reported one government allopathic doctor per 11,082 people nationwide. China offers a practical example of how technology can help: some rural clinics have used AI to support primary care doctors with assessment and diagnosis.",
    sources: [
      { label: "India’s National Health Profile, 2018", url: "https://cbhidghs.mohfw.gov.in/sites/default/files/NHP/National-health-2018-chapter5.pdf" },
      { label: "China’s primary care AI initiatives", url: "https://www.nhc.gov.cn/xcs/c100122/202406/5cd18dd4255e472882246fee67f8e27d.shtml" },
    ],
    presenter: 0,
  },
  { id: "first-prototype", name: "The first build", title: "Start small. Learn from something real.", text: "Our first build explores one part of that journey: a conversation about a skin concern, supported by photographs and a structured case brief. It lets us test the interaction before building the full kiosk.", detail: "Available now: Hindi and English intake, photo capture, and a clinician review workflow. Clinical validation is still ahead.", presenter: 2 },
  { id: "hospital-pilot", name: "The road ahead", title: "From a browser to the hospital floor.", text: "The next chapters are software refinement, kiosk and sensor integration, a complete kiosk prototype, and conversations with hospitals about pilots. Our proposed starting point is Varanasi and nearby districts in eastern Uttar Pradesh.", detail: "We’re looking to learn with clinicians, hospital teams, hardware collaborators, and pilot partners.", presenter: 0 },
];

export function VentureStory() {
  const reduceMotion = useReducedMotion();

  return (
    <div className="story-route">
      <nav aria-label="Story chapters" className="story-route-nav">
        {chapters.map(({ id, name }) => <a key={id} href={`#${id}`}>{name}</a>)}
      </nav>
      <div className="story-scenes">
        {chapters.map(({ id, name, title, text, detail, sources, presenter }, index) => (
          <motion.article
            key={id}
            id={id}
            className={`story-scene story-card ${index % 2 ? "story-card-right" : "story-card-left"}`}
            aria-labelledby={`${id}-title`}
            initial={reduceMotion ? false : { opacity: 0, x: index % 2 ? 52 : -52, scale: 0.94 }}
            whileInView={{ opacity: 1, x: 0, scale: 1 }}
            viewport={{ once: true, amount: 0.25 }}
            transition={reduceMotion ? { duration: 0 } : { type: "spring", stiffness: 205, damping: 21, opacity: { duration: 0.24 } }}
          >
            <div className="story-presenter" aria-hidden="true">
              <TeamPortrait index={presenter} />
            </div>
            <div className="story-card-copy">
              <span className="world-label">{name}</span>
              <h3 id={`${id}-title`}>{title}</h3>
              <p>{text}</p>
              <p className="story-detail">{detail}</p>
              {sources && (
                <ul className="story-sources" aria-label="Sources">
                  {sources.map(({ label, url }) => <li key={url}><a href={url}>{label}</a></li>)}
                </ul>
              )}
            </div>
          </motion.article>
        ))}
      </div>
    </div>
  );
}
