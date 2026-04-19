"use client";

import type { ReactNode } from "react";
import { motion } from "framer-motion";

interface Props {
  /** When true, clouds slide in and hold. When false, clouds retreat. */
  loading: boolean;
  /** Optional content (spinner, label) shown in the middle while loading. */
  children?: ReactNode;
}

const SLIDE_DURATION = 0.75;
const EASE_IN_TO_CENTER: [number, number, number, number] = [0.22, 1, 0.36, 1];
const EASE_OUT_FROM_CENTER: [number, number, number, number] = [
  0.64, 0, 0.78, 0,
];

/**
 * Loading veil that reuses the cloud transition visuals. The clouds slide in
 * when `loading` flips true, hold indefinitely while loading is active, then
 * retreat back off-screen when it flips false.
 */
export function CloudLoadingOverlay({ loading, children }: Props) {
  const enter = { duration: SLIDE_DURATION, ease: EASE_IN_TO_CENTER };
  const exit = { duration: SLIDE_DURATION, ease: EASE_OUT_FROM_CENTER };
  const transition = loading ? enter : exit;

  return (
    <div
      className="pointer-events-none fixed inset-0 z-50 overflow-hidden"
      aria-hidden={!loading}
    >
      <motion.img
        src="/assets/cloudspixelright.png"
        alt=""
        aria-hidden
        draggable={false}
        initial={{ x: "-144%", scale: 1.44 }}
        animate={{ x: loading ? "0%" : "-144%", scale: 1.44 }}
        transition={transition}
        className="absolute inset-y-0 left-0 h-full w-auto max-w-[60%] select-none object-contain"
        style={{ imageRendering: "pixelated" }}
      />
      <motion.img
        src="/assets/cloudspixelleft.png"
        alt=""
        aria-hidden
        draggable={false}
        initial={{ x: "144%", scale: 1.44 }}
        animate={{ x: loading ? "0%" : "144%", scale: 1.44 }}
        transition={transition}
        className="absolute inset-y-0 right-0 h-full w-auto max-w-[60%] select-none object-contain"
        style={{ imageRendering: "pixelated" }}
      />
      {children && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: loading ? 1 : 0 }}
          transition={{ duration: 0.25, delay: loading ? SLIDE_DURATION * 0.6 : 0 }}
          className="absolute inset-0 flex items-center justify-center"
        >
          {children}
        </motion.div>
      )}
    </div>
  );
}
