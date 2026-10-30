/** Each chapter's poster ink: background, text on it, and the accent used for shadows and marks. */
const INKS = [
  { bg: "#121110", fg: "#efe8d8", accent: "#ff5a36" },
  { bg: "#d9ddc9", fg: "#1b1a17", accent: "#2c4fa3" },
  { bg: "#e9b44c", fg: "#1b1a17", accent: "#e0462f" },
  { bg: "#2c4fa3", fg: "#efe8d8", accent: "#e9b44c" },
  { bg: "#1e5e3f", fg: "#efe8d8", accent: "#4be08a" },
  { bg: "#e0462f", fg: "#1b1a17", accent: "#121110" },
  { bg: "#cddbd3", fg: "#1b1a17", accent: "#e0462f" },
];

export function ink(i: number) {
  return INKS[i % INKS.length];
}
