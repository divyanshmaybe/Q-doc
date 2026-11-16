import React from "react";
import { ArrowRight, AudioLines, Camera, ClipboardList, Stethoscope, ShieldCheck, MessageCircle, Mail, Plus, Check } from "lucide-react";
import "./LandingPage.css";

interface LandingPageProps {
  onLaunchDemo: () => void;
  onOpenClinician: () => void;
}

const steps = [
  { icon: MessageCircle, title: "Start with your story", text: "Describe the skin concern in Hindi or English, by voice or text. Q-Doc asks about symptoms, timing, previous treatments, and how the problem affects your day." },
  { icon: Camera, title: "Add a photo, if comfortable", text: "A clear photograph adds visual context to your history. You can skip this step and continue toward an in-person examination." },
  { icon: ClipboardList, title: "Review the next step", text: "Confirm the details you shared, then receive a provisional screening assessment or a recommendation for clinical review." },
];

export const LandingPage: React.FC<LandingPageProps> = ({ onLaunchDemo, onOpenClinician }) => (
  <div className="qdoc-landing">
    <a className="landing-skip" href="#landing-main">Skip to content</a>
    <header className="landing-nav">
      <div className="landing-container landing-nav-inner">
        <a href="#" className="landing-brand" aria-label="Q-Doc home"><span className="brand-symbol"><Plus size={23} /></span>Q-Doc<span className="brand-caption">SKIN SCREENING</span></a>
        <nav aria-label="Main navigation"><a href="#how">How it works</a><a href="#clinical">For clinicians</a><a href="#about">About</a></nav>
        <button className="landing-button compact" onClick={onLaunchDemo}>Try the demo <ArrowRight size={15} /></button>
      </div>
    </header>
    <main id="landing-main">
      <section className="landing-hero landing-container" aria-labelledby="landing-title">
        <div className="hero-copy">
          <div className="landing-eyebrow"><span className="pink-dot" /> VOICE-FIRST DERMATOLOGY SCREENING</div>
          <h1 id="landing-title">Better skin care<br />starts with<br /><em>being heard.</em></h1>
          <p className="hero-description">Describe what’s changed. Share what concerns you. Q-Doc brings your symptoms and skin photographs together to help prepare for the next step in care.</p>
          <div className="landing-actions"><button className="landing-button" onClick={onLaunchDemo}>Explore the screening demo <ArrowRight size={17} /></button><a className="landing-text-link" href="#how">See how it works <span>↘</span></a></div>
          <p className="hero-note">An early-stage screening prototype. Clinical examination and treatment decisions remain with a qualified clinician.</p>
        </div>
        <div className="landing-preview" aria-label="Illustrative preview of a Q-Doc conversation">
          <div className="preview-top"><span><span className="pink-dot" /> Q-DOC CONSULTATION</span><span>Example conversation</span></div>
          <div className="preview-orb-scene" aria-hidden="true"><div className="preview-orbit" /><div className="preview-orbit outer" /><div className="preview-orb"><AudioLines size={42} strokeWidth={1.2} /></div><span className="preview-orb-label">SPACE TO TALK. TIME TO LISTEN.</span></div>
          <div className="preview-chat patient"><span>YOU</span><p>“The itching keeps waking me up at night.”</p></div>
          <div className="preview-chat assistant"><span><span className="tiny-cross">+</span> Q-DOC</span><p>“That sounds uncomfortable. When did the itching first begin?”</p></div>
          <div className="preview-input"><AudioLines size={16} /><span>Speak or type in your own words</span><span className="preview-send"><ArrowRight size={15} /></span></div>
        </div>
      </section>
      <div className="landing-capabilities landing-container" aria-label="Current prototype capabilities">
        <span><AudioLines />Hindi &amp; English</span><span><Camera />Symptoms + photographs</span><span><ClipboardList />Structured case summaries</span><span><Stethoscope />Clinician review workflow</span>
      </div>
      <section className="landing-section landing-container" id="how" aria-labelledby="how-title">
        <div className="section-intro"><div><span className="landing-eyebrow">01 / THE EXPERIENCE</span><h2 id="how-title">A conversation with<br /><em>a clear structure.</em></h2></div><p>Good screening begins with context. Q-Doc gathers the details step by step and gives you a chance to correct them before preparing an assessment.</p></div>
        <div className="landing-step-grid">{steps.map(({ icon: Icon, title, text }, index) => <article className="landing-step" key={title}><div className="step-top"><Icon size={23} strokeWidth={1.4} /><span>0{index + 1}</span></div><h3>{title}</h3><p>{text}</p></article>)}</div>
      </section>
      <section className="clinical-section" id="clinical" aria-labelledby="clinical-title"><div className="landing-container clinical-layout">
        <div className="clinical-copy"><span className="landing-eyebrow">02 / FOR THE CARE TEAM</span><h2 id="clinical-title">The patient’s story.<br /><em>Ready for review.</em></h2><p>Q-Doc is being developed to support the intake stage of a dermatology visit. The clinician portal brings the symptom history, image findings, and screening output into one case brief.</p><ul><li><Check />Review the history and reported symptoms.</li><li><Check />Inspect possible conditions and flagged concerns.</li><li><Check />Record approval or add a clinical override.</li></ul><button className="landing-button secondary" onClick={onOpenClinician}>Explore the clinician portal <ArrowRight size={16} /></button></div>
        <div className="brief-preview"><div className="brief-title"><ClipboardList size={20} /><div><strong>One case. A structured overview.</strong><span>Illustrative case brief</span></div></div><div className="brief-row"><span>Patient history</span><strong>Concern · onset · symptoms</strong></div><div className="brief-row"><span>Visual context</span><strong>Photograph &amp; image quality</strong></div><div className="brief-row"><span>Screening assessment</span><strong>Possible conditions &amp; uncertainty</strong></div><div className="brief-row"><span>Clinical review</span><strong>Notes, approval, or override</strong></div><div className="brief-bottom"><ShieldCheck size={17} /><span>Clinical judgment stays with the care team.</span></div></div>
      </div></section>
      <section className="landing-section landing-container scope-layout" aria-labelledby="scope-title"><div><span className="landing-eyebrow">03 / BUILT WITH BOUNDARIES</span><h2 id="scope-title">Clear about its role.<br /><em>Honest about its limits.</em></h2><p className="scope-lead">Q-Doc is a working prototype focused on skin screening. Clinical validation and real-world evaluation are still needed before routine patient use.</p></div><div className="scope-list"><article><span>01</span><div><h3>A provisional assessment</h3><p>Symptoms and photos can support screening. They cannot confirm a diagnosis or replace a physical examination.</p></div></article><article><span>02</span><div><h3>A route to further care</h3><p>Reported warning signs or unclear findings can prompt advice to seek clinical assessment. Q-Doc does not arrange emergency care.</p></div></article><article><span>03</span><div><h3>Treatment requires review</h3><p>The current patient-facing flow recommends clinician review before starting or changing medication.</p></div></article></div></section>
      <section className="landing-container" id="about" aria-labelledby="about-title"><div className="landing-about"><div><span className="landing-eyebrow">THE PROJECT / Q-DOC</span><h2 id="about-title">Building a more useful<br />first step in skin care.</h2><p>Q-Doc’s goal is to make symptom collection easier for patients and more useful for care teams. We’re starting with dermatology, conversational intake, and a reviewable clinical summary.</p><div className="founder-line"><span className="founder-avatar">DS</span><div><strong>Divyansh Soni</strong><span>Founder · Mathematics &amp; Computing, IIT BHU</span></div></div></div><div className="contact-panel"><Mail size={24} /><h3>Help shape what comes next.</h3><p>We welcome conversations with clinicians, researchers, and potential pilot partners about clinical workflows, evaluation, and patient experience.</p><a className="landing-text-link" href="mailto:founder@q-doc.live">founder@q-doc.live <ArrowRight size={16} /></a></div></div></section>
      <section className="landing-container landing-final"><span className="landing-eyebrow">TAKE A LOOK INSIDE</span><h2>See the conversation in action.</h2><p>Explore how Q-Doc collects a skin history and prepares the next step.</p><button className="landing-button" onClick={onLaunchDemo}>Try the screening demo <ArrowRight size={17} /></button></section>
    </main>
    <footer className="landing-container landing-footer"><a className="landing-brand" href="#"><span className="brand-symbol"><Plus size={20} /></span>Q-Doc</a><p>Dermatology screening prototype · Founded 2026</p><a href="mailto:founder@q-doc.live">Get in touch <ArrowRight size={14} /></a></footer>
  </div>
);
