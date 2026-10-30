// The search index, written once at build time: every chapter cut into its
// sections, plus every plate with its caption.
import type { APIRoute } from "astro";
import { render } from "astro:content";
import { chapters, number, name } from "../scripts/chapters";

// Markdown down to the words a reader would type.
function plain(md: string) {
  return md
    .replace(/^```.*$/gm, "")
    .replace(/!\[[^\]]*\]\([^)]*\)/g, "")
    .replace(/\[([^\]]+)\]\([^)]*\)/g, "$1")
    .replace(/<[^>]+>/g, "")
    .replace(/^\s*\|?[-:| ]+\|?\s*$/gm, "")
    .replace(/[|*_`>#]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

export const GET: APIRoute = async () => {
  const sections: { c: string; n: string; t: string; h: string; id: string; x: string }[] = [];
  const plates: { c: string; n: string; t: string; p: string; f: string }[] = [];
  for (const entry of await chapters()) {
    const { headings } = await render(entry);
    const h2 = headings.filter((h) => h.depth === 2);
    const body = (entry.body ?? "").replace(/^# .*$/m, "");
    // Text before the first "## " is the chapter's opening; each "## " after starts a section.
    const parts = body.split(/^## .*$/m);
    parts.forEach((part, i) => {
      sections.push({
        c: entry.id,
        n: number(entry),
        t: name(entry),
        h: i === 0 ? "" : h2[i - 1]?.text ?? "",
        id: i === 0 ? "" : h2[i - 1]?.slug ?? "",
        x: plain(part),
      });
    });
    for (const m of body.matchAll(/!\[([^\]]*)\]\(\.\.\/figures\/(([\w]+)-[\w-]+\.svg)\)/g)) {
      plates.push({ c: entry.id, n: number(entry), t: name(entry), p: m[1], f: m[2] });
    }
  }
  return new Response(JSON.stringify({ sections, plates }), { headers: { "Content-Type": "application/json" } });
};
