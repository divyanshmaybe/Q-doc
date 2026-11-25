import { QDocWordmark } from "./QDocWordmark";
import React from "react";
import { Plus, Volume2, Flag, Monitor, HeartPulse, Map, Users, Play, ChevronDown } from "lucide-react";
import "./LandingPage.css";
import { VentureStory } from "./VentureStory";
import { TeamPortrait } from "./TeamPortrait";

interface LandingPageProps { onLaunchDemo: () => void; onOpenClinician: () => void; }
function DemoButton({ onClick, children, className = "" }: {
  onClick: () => void;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <button type="button" className={`world-button demo-entry ${className}`} onClick={onClick}>
      <Play size={14} fill="currentColor" aria-hidden="true" />
      {children}
    </button>
  );
}

function CareWorld() {
  return <svg className="care-world" viewBox="0 0 900 620" role="img" aria-labelledby="world-title">
    <title id="world-title">An illustrated block-built community, connected by a path to a Q-Doc kiosk and hospital</title>
    <defs>
      <pattern id="grass" width="46" height="26" patternUnits="userSpaceOnUse"><rect width="46" height="26" fill="#414e8a"/><path d="M5 6h8m20 13h6" stroke="#5869a8" strokeWidth="3"/></pattern>
      <g id="tree"><path d="M-5 0v-49h12V0" fill="#76543e"/><path d="m-32-47 0-35 30-16 32 16v35L0-30Z" fill="#43539b"/><path d="m-32-82 30-16 32 16L0-65Z" fill="#8294ed"/><path d="M0-65v35l30-17v-35Z" fill="#303f78"/></g>
      <g id="person"><ellipse cy="5" rx="14" ry="6" fill="#263a3426"/><path d="M-6-2v-14h5v14m4 0v-14h5v14" stroke="#293c43" strokeWidth="5"/><path d="M-10-17v-23h20v23" fill="currentColor"/><path d="M-7-42h14v17H-7Z" fill="#e6b486"/><path d="M-8-42h16v6H-8Z" fill="#373c36"/></g>
    </defs>
    <g className="world-cloud" fill="#343e6c"><path d="M98 91h27V73h47v13h35v22H98Z"/><path d="M653 52h30V33h52v16h31v19H653Z"/></g>
    <path d="m72 353 366-199 389 207-366 212Z" fill="#263e36" opacity=".13" transform="translate(0 28)"/>
    <path d="m72 319 366-199 389 207-366 212Z" fill="url(#grass)"/>
    <path d="M72 319v48l389 215v-48Z" fill="#323851"/><path d="m461 534 366-207v48L461 582Z" fill="#222638"/>
    <path d="M72 319v13l389 215v-13Zm389 215v13l366-207v-13Z" fill="#5668b0"/>
    <path d="m169 369 249-137 40 22-250 137Z" fill="#9ba4cb"/><path d="m331 281 42-23 298 162-43 25Z" fill="#9ba4cb"/><path d="m435 486 165-92 39 21-165 93Z" fill="#9ba4cb"/>
    <path d="m184 369 230-128m-54 32 277 153m-181 68 159-88" fill="none" stroke="#c9d1f2" strokeWidth="3" strokeDasharray="10 12"/>
    <g transform="translate(592 255)">
      <path d="m-83-33 101-56 102 56-101 58Z" fill="#dce2ff"/><path d="M-83-33v91L19 116V25Z" fill="#b9c4ed"/><path d="m19 25 101-58v91L19 116Z" fill="#7b8ab9"/>
      <path d="m-92-40 111-61 111 61-111 63Z" fill="#f72585"/><path d="M-92-40v12L19 35V23Zm111 63v12l111-63v-12Z" fill="#a71c60"/>
      <path d="M-60-7v39l28 16V9Zm43 25v39L9 72V33Z" fill="#527b7b"/><path d="m40 38 27-15v71L40 109Z" fill="#3e625d"/><path d="m81 14 22-13v33L81 47Z" fill="#527b7b"/>
      <path d="m-6-64 14-8 14 8v-17l14 8v17l14 8-14 8-14-8v17l-14-8v-17Z" fill="#fff8df"/>
    </g>
    <g transform="translate(260 248)"><path d="m-56-12 65-36 63 35L7 24Z" fill="#efbd70"/><path d="M-56-12v59L7 83V24Z" fill="#f3e3b5"/><path d="m7 24 65-37v59L7 83Z" fill="#c4b181"/><path d="m-65-14 36-61 46 1 64 57L7 22Z" fill="#49757d"/><path d="m-65-14 36-61L7-40v62Z" fill="#6c9695"/><path d="M-40 13v21l18 10V23Z" fill="#799e9b"/><path d="m23 33 22-12v41L23 74Z" fill="#64523d"/></g>
    <g transform="translate(463 385)"><path d="m-58 0 57-32L59 0 1 34Z" fill="#b4c4a0"/><path d="M-58 0v10L1 44V34Zm59 34v10L59 10V0Z" fill="#7e9774"/>
      <path d="M-28-105 7-124 38-106 3-86Z" fill="#faf7da"/><path d="M-28-105v105L3 18V-86Z" fill="#eeeacc"/><path d="m3-86 35-20V-2L3 18Z" fill="#a5b9a3"/>
      <path d="M-21-92v49L-3-33v-49Z" fill="#274d49"/><path d="m-17-69 3 2 3-7 4 17" fill="none" stroke="#ff72b1" strokeWidth="2"/><path d="M-19-24v6l15 8v-6Z" fill="#537b65"/><path d="M11-77v38l17-10v-38Z" fill="#729c83"/>
    </g>
    {[[151,310],[367,190],[706,342],[743,317],[345,457],[265,410],[547,489],[767,365]].map(([x,y])=><use key={`${x}-${y}`} href="#tree" x={x} y={y}/>)}
    <use href="#person" x="393" y="367" color="#e9a84e"/><use href="#person" x="510" y="420" color="#e77958"/><use href="#person" x="589" y="349" color="#f3edcf"/><use href="#person" x="224" y="343" color="#60869e"/>
    <g fill="#ff72b1"><path d="M305 349h6v6h-6Zm321 119h6v6h-6Zm-297 2h6v6h-6ZM181 297h6v6h-6Z"/></g>
    <g fill="#727cff"><path d="M119 350h12v5h-12Zm378 172h14v5h-14Zm221-134h12v5h-12Z"/></g>
  </svg>;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onLaunchDemo, onOpenClinician }) => {
  return <div className="qdoc-landing" id="top">
    <a className="landing-skip" href="#landing-main">Skip to content</a>
    <header className="venture-nav"><a className="venture-brand" href="#top"><QDocWordmark /><span className="brand-location">BUILT IN VARANASI</span></a><nav aria-label="Main navigation"><a href="#story">The story</a><a href="#vision">The vision</a><a href="#team">The people</a></nav><DemoButton onClick={onLaunchDemo}>Enter demo</DemoButton></header>
    <main id="landing-main">
      <section className="venture-hero" aria-labelledby="landing-title">
        <div className="hero-horizon" aria-hidden="true"/>
        <div className="venture-hero-copy"><span className="world-label"><span className="label-block"/> VOICE-FIRST CARE. BUILT FOR INDIA.</span><h1 id="landing-title">Less time in line.<br/><span>More time with your doctor.</span></h1><p>We’re building a better first step into healthcare.<br className="desktop-break"/> A voice-first health kiosk designed for 22 Indian languages.<br className="desktop-break"/> A clearer, faster path to the care you need.</p><div className="world-actions"><a className="world-button" href="#story"><Map size={18}/> Explore our story</a><DemoButton onClick={onLaunchDemo}>Try the prototype</DemoButton></div><span className="hero-footnote">ROOTED IN INDIA. BUILDING ONE STEP AT A TIME.</span></div>
        <div className="world-scene"><span className="world-coordinate">THE WORLD WE’RE WORKING TOWARD</span><CareWorld/><a className="world-pin pin-village" href="#story"><span>⌂</span> The community</a><a className="world-pin pin-hospital" href="#vision"><Plus size={15}/> The care team</a><DemoButton className="pin-kiosk" onClick={onLaunchDemo}>Meet Q-Doc</DemoButton><span className="world-caption">Concept illustration: a Q-Doc kiosk near a public hospital.</span></div>
        <a className="scroll-invite" href="#story"><ChevronDown size={18}/> THERE’S A STORY BEHIND THE BUILD</a>
      </section>
      <div className="venture-ribbon"><span>VOICE FIRST</span><Plus/><span>PEOPLE AT THE CENTRE</span><Plus/><span>CARE CLOSER TO HOME</span><Plus/><span>BUILT TO BE UNDERSTOOD</span></div>
      <section className="venture-section story-section" id="story" aria-labelledby="story-title"><div className="section-heading"><span className="world-label">THE Q-DOC JOURNEY</span><h2 id="story-title">It started in<br/>a <em>waiting room.</em></h2></div>
        <VentureStory />
      </section>
      <section className="vision-section" id="vision" aria-labelledby="vision-title"><div className="venture-section"><div className="vision-header"><div><span className="world-label">THE BIGGER PICTURE</span><h2 id="vision-title">One first step.<br/>More ways to care.</h2></div><p>The vision is a walk-up health kiosk in a public hospital, helping patients explain what’s wrong and helping care teams decide what comes next.</p></div><div className="vision-path"><article><Volume2/><span className="world-label">SPEAK</span><h3>In your own words.</h3><p>Speak in the language you’re most comfortable with. We’re designing Q-Doc for 22 Indian languages so more people can start a health check without having to read or fill out a form.</p></article><article><HeartPulse/><span className="world-label">UNDERSTAND</span><h3>Bring the pieces together.</h3><p>Our roadmap brings symptom history, basic vitals, and connected health records into one place.</p></article><article><Users/><span className="world-label">CONNECT</span><h3>A useful next step.</h3><p>Give the care team a structured starting point, with attention to cases that need further assessment.</p></article></div><p className="vision-note">The kiosk, vitals sensors, and ABDM integration are planned capabilities, still to be built and evaluated.</p></div></section>
      <section className="venture-section demo-section" id="prototype" aria-labelledby="demo-title"><div className="demo-terminal"><div className="terminal-bar"><span>Q-DOC / PROTOTYPE</span><Monitor size={17}/></div><div className="terminal-body"><span className="terminal-cross" aria-hidden="true">✚</span><p className="terminal-greeting">Hello. नमस्ते.</p><p>Let’s start with your story.</p><div className="terminal-wave" aria-hidden="true">{[12,24,16,38,54,30,18,44,64,36,22,46,26,14,30,16].map((h,i)=><i key={i} style={{height:h}}/>)}</div><span className="terminal-language">HINDI + ENGLISH</span></div><DemoButton className="terminal-demo-entry" onClick={onLaunchDemo}>Start a conversation</DemoButton></div><div className="demo-copy"><span className="world-label">TRY IT TODAY / THE FIRST BUILD</span><h2 id="demo-title">Try a skin<br/><em>screening conversation.</em></h2><p>Try our voice-and-photo skin screening prototype. It’s a small, working part of the wider Q-Doc idea: listen to a patient, collect context, and prepare a case for review.</p><p className="demo-boundary">An early prototype, not a clinically validated service. It doesn’t replace a clinician’s examination or treatment advice.</p><div className="world-actions"><DemoButton onClick={onLaunchDemo}>Try the demo</DemoButton><button className="world-link" onClick={onOpenClinician}>Open clinician view</button></div></div></section>
      <section className="team-section venture-section" id="team" aria-labelledby="team-title"><div className="section-heading"><span className="world-label">THE TEAM BEHIND Q-DOC</span><h2 id="team-title">Meet the team<br/>in Varanasi.</h2><p>Three students at IIT BHU building Q-Doc.</p></div><div className="team-list">{[{name:"Divyansh Soni",course:"Mathematics & Computing",initials:"DS"},{name:"Divyansh Srivastava",course:"Civil Engineering",initials:"DS"},{name:"Sanil",course:"Mechanical Engineering",initials:"S"}].map((person,i)=><article key={person.name}><span className="team-portrait"><TeamPortrait index={i} /></span><div><h3>{person.name}</h3><p>{person.course}</p><span>IIT BHU · Varanasi</span></div></article>)}</div></section>
      <section className="join-section"><div><span className="world-label">THE NEXT CHAPTER IS OPEN</span><h2>Help us build<br/>what comes next.</h2><p>Clinician, hospital team, hardware builder, or simply curious?<br/>Help shape a useful first step for patients and care teams.</p><a className="world-button" href="mailto:founder@q-doc.live">Let’s talk</a><a className="join-email" href="mailto:founder@q-doc.live">founder@q-doc.live</a></div><div className="join-flag" aria-hidden="true"><Flag size={115} strokeWidth={1.5}/><span>STILL BUILDING.<br/>ALWAYS LEARNING.</span></div></section>
    </main><footer className="venture-footer"><a className="venture-brand" href="#top"><QDocWordmark /></a><p>A better beginning for healthcare.</p><a href="#top">Back to the surface</a></footer>
  </div>;
};
