import { defineConfig } from "astro/config";

// Served from GitHub Pages at /<repo>; change BASE if the repository is named differently.
const BASE = "/channel-fifteen";

// The chapters are written to read well on GitHub (../figures/x.svg, 04-name.md);
// rewrite those links for the website.
function rewriteLinks() {
  const walk = (node) => {
    if (node.type === "image" && node.url.startsWith("../figures/")) {
      node.url = `${BASE}/figures/${node.url.slice("../figures/".length)}`;
    }
    if (node.type === "link") {
      const m = node.url.match(/^(\d\d-[\w-]+)\.md(#.*)?$/);
      if (m) node.url = `${BASE}/chapters/${m[1]}/${m[2] ?? ""}`;
    }
    (node.children ?? []).forEach(walk);
  };
  return (tree) => walk(tree);
}

export default defineConfig({
  site: "https://srivtx.github.io",
  base: BASE,
  trailingSlash: "ignore",
  markdown: {
    remarkPlugins: [rewriteLinks],
    shikiConfig: { themes: { light: "github-light", dark: "github-dark" } },
  },
});
