import { motion, useReducedMotion } from "framer-motion";
import { TeamPortrait } from "./TeamPortrait";

const chapters = [
  { id: "waiting-room", name: "The starting point", title: "A checkup shouldn’t cost a whole day.", text: "Long journeys. Crowded waiting rooms. Another day away from work. Q-Doc began with a frustration our team knew firsthand: even the first step in getting care can feel out of reach.", detail: "Our focus: the patients and care teams navigating crowded government hospital OPDs.", presenter: 0 },
  { id: "kiosk-idea", name: "The idea", title: "Walk up. Speak freely. Find the next step.", text: "We’re developing a voice-first health kiosk that people can approach in a hospital and use in their own language. The ambition is to bring together their story, basic health checks, and a useful handoff to a clinician.", detail: "Regional-language conversations, vitals sensors, and connected health records are part of the broader kiosk vision.", presenter: 1 },
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
        {chapters.map(({ id, name, title, text, detail, presenter }, index) => (
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
            </div>
          </motion.article>
        ))}
      </div>
    </div>
  );
}
