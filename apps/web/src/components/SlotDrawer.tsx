import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MapPin, Clock, Thermometer, Users, Sparkles } from "lucide-react";

/**
 * SlotDrawer — minimalist, auto-hiding glassmorphism drawer.
 * Floats at the bottom of the voice orb screen.
 * Shows extracted clinical biomarkers as small glowing pills.
 * Auto-collapses when empty; expands smoothly when data arrives.
 */

interface SlotDrawerProps {
  slots: Record<string, any>;
  visible: boolean;
}

interface SlotPill {
  key: string;
  label: string;
  value: string | null;
  icon: React.ReactNode;
  isAlert?: boolean;
}

export const SlotDrawer: React.FC<SlotDrawerProps> = ({ slots, visible }) => {
  const pills: SlotPill[] = [
    {
      key: "body_site",
      label: "SITE",
      value: slots.body_site ? String(slots.body_site).toUpperCase() : null,
      icon: <MapPin className="w-3 h-3" />,
    },
    {
      key: "duration_days",
      label: "DURATION",
      value: slots.duration_days != null ? `${slots.duration_days}D` : null,
      icon: <Clock className="w-3 h-3" />,
    },
    {
      key: "has_itching",
      label: "ITCH",
      value: slots.has_itching === true ? "YES" : slots.has_itching === false ? "NO" : null,
      icon: <Sparkles className="w-3 h-3" />,
    },
    {
      key: "has_fever",
      label: "FEVER",
      value: slots.has_fever === true ? "YES" : slots.has_fever === false ? "NO" : null,
      icon: <Thermometer className="w-3 h-3" />,
      isAlert: slots.has_fever === true,
    },
    {
      key: "household_contacts_affected",
      label: "CONTACTS",
      value: slots.household_contacts_affected === true
        ? "AFFECTED"
        : slots.household_contacts_affected === false
        ? "CLEAR"
        : null,
      icon: <Users className="w-3 h-3" />,
      isAlert: slots.household_contacts_affected === true,
    },
  ];

  const filledPills = pills.filter((p) => p.value !== null);
  const show = visible && filledPills.length > 0;

  return (
    <AnimatePresence>
      {show && (
        <motion.div
          initial={{ opacity: 0, y: 20, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 20, scale: 0.95 }}
          transition={{ type: "spring", stiffness: 260, damping: 24 }}
          className="glass-panel rounded-2xl px-4 py-3 flex flex-wrap items-center justify-center gap-2 max-w-md mx-auto"
        >
          {filledPills.map((pill) => (
            <motion.span
              key={pill.key}
              layout
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full font-mono text-[10px] font-bold tracking-wider border transition-all ${
                pill.isAlert
                  ? "bg-neon/15 text-neon-light border-neon/40 shadow-neon-glow animate-pulse"
                  : "bg-electric/10 text-electric-light border-electric/30"
              }`}
            >
              {pill.icon}
              <span>{pill.label}: {pill.value}</span>
            </motion.span>
          ))}
        </motion.div>
      )}
    </AnimatePresence>
  );
};

