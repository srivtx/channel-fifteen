// Copies the plates from ../figures into public/ so the site serves them.
import { cpSync, mkdirSync } from "node:fs";
mkdirSync("public/figures", { recursive: true });
cpSync("../figures", "public/figures", { recursive: true });
console.log("synced figures");
