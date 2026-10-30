import { defineCollection } from "astro:content";
import { glob } from "astro/loaders";

// The chapters live at the repository root so they also read as plain Markdown on GitHub.
const chapters = defineCollection({
  loader: glob({ pattern: "*.md", base: "../chapters" }),
});

export const collections = { chapters };
