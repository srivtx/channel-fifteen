// Site-wide motion and small affordances: things rise in as they scroll into
// view, code blocks get a label and a copy button, headings get a link.

const toastEl = document.querySelector<HTMLElement>(".toast");
let toastTimer = 0;
export function toast(msg: string) {
  if (!toastEl) return;
  toastEl.textContent = msg;
  toastEl.classList.add("on");
  clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => toastEl.classList.remove("on"), 1600);
}

async function copy(text: string) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    return false;
  }
}

// Chapter text: every block rises in once.
for (const el of document.querySelectorAll(".prose > :not(h1)")) el.classList.add("reveal");

// Code blocks: a specimen strip with the language and a copy button.
for (const pre of document.querySelectorAll<HTMLPreElement>(".prose pre")) {
  const box = document.createElement("div");
  box.className = "codebox reveal";
  const head = document.createElement("div");
  head.className = "codehead mono";
  const lang = pre.dataset.language && pre.dataset.language !== "plaintext" ? pre.dataset.language : "text";
  head.innerHTML = `<span><i></i><i></i><i></i>${lang}</span><button type="button">copy</button>`;
  pre.classList.remove("reveal");
  pre.replaceWith(box);
  box.append(head, pre);
  const btn = head.querySelector("button")!;
  btn.addEventListener("click", async () => {
    const ok = await copy(pre.innerText.replace(/\n$/, ""));
    btn.textContent = ok ? "copied ✓" : "press ⌘C";
    btn.classList.toggle("ok", ok);
    setTimeout(() => { btn.textContent = "copy"; btn.classList.remove("ok"); }, 1400);
  });
}

// Headings: a # that copies a link straight to the section.
for (const h of document.querySelectorAll<HTMLElement>(".prose h2[id], .prose h3[id]")) {
  const a = document.createElement("a");
  a.className = "anchor";
  a.href = `#${h.id}`;
  a.textContent = "#";
  a.setAttribute("aria-label", `Link to “${h.textContent}”`);
  a.addEventListener("click", async (e) => {
    e.preventDefault();
    history.replaceState(null, "", a.href);
    h.scrollIntoView({ behavior: "smooth", block: "start" });
    if (await copy(location.href)) toast("LINK TO SECTION COPIED");
  });
  h.append(a);
}

// Rise-in on scroll. Anything already on screen at load just plays in.
const calm = matchMedia("(prefers-reduced-motion: reduce)").matches;
const items = document.querySelectorAll<HTMLElement>(".reveal");
if (calm || !("IntersectionObserver" in window)) {
  items.forEach((el) => el.classList.add("in"));
} else {
  const io = new IntersectionObserver(
    (entries) => {
      for (const e of entries) {
        if (!e.isIntersecting) continue;
        e.target.classList.add("in");
        io.unobserve(e.target);
      }
    },
    { rootMargin: "0px 0px -8% 0px", threshold: 0.08 },
  );
  items.forEach((el) => io.observe(el));
}
