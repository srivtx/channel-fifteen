import { getCollection, type CollectionEntry } from "astro:content";

export type Chapter = CollectionEntry<"chapters">;

export async function chapters() {
  const all = await getCollection("chapters");
  return all.sort((a, b) => a.id.localeCompare(b.id));
}

/** "03 · Radio" from the chapter's first heading. */
export function title(c: Chapter) {
  const h = (c.body ?? "").split("\n").find((l) => l.startsWith("# ")) ?? c.id;
  return h.replace(/^#\s*/, "");
}

export function number(c: Chapter) {
  return c.id.slice(0, 2);
}

export function name(c: Chapter) {
  return title(c).replace(/^\d\d\s*·\s*/, "");
}

/** The chapter's first plate, used as its card image. */
export function firstPlate(c: Chapter) {
  return (c.body ?? "").match(/\.\.\/figures\/([\w-]+\.svg)/)?.[1];
}

/** The "In the story" line, or the first paragraph. */
export function blurb(c: Chapter) {
  const lines = (c.body ?? "").split("\n");
  const story = lines.find((l) => l.startsWith("> **In the story:**"));
  const text = story ?? lines.find((l) => l && !l.startsWith("#") && !l.startsWith("!") && !l.startsWith(">")) ?? "";
  const plain = text.replace(/^> \*\*In the story:\*\*\s*/, "").replace(/[*`]/g, "").slice(0, 210);
  return plain.charAt(0).toUpperCase() + plain.slice(1);
}
