"""Draws every plate into figures/. Run from anywhere: python3 tools/build_figures.py"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plate  # noqa: E402

MODULES = ["figs_story", "figs_bits", "figs_link", "figs_protocol", "figs_app"]


def main():
    fns = []
    for name in MODULES:
        try:
            fns += __import__(name).PLATES
        except ModuleNotFoundError:
            pass
    plate.TOTAL_PLATES = len(fns)
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
    os.makedirs(out, exist_ok=True)
    only = set(sys.argv[1:])
    if not only:
        for old in os.listdir(out):
            if old.endswith(".svg"):
                os.remove(os.path.join(out, old))
    for i, fn in enumerate(fns, 1):
        p = fn(i)
        name = f"{i:02d}-{p.slug}.svg"
        if only and p.slug not in only:
            continue
        with open(os.path.join(out, name), "w") as f:
            f.write(p.svg())
        print(name, round(os.path.getsize(os.path.join(out, name)) / 1024), "KB")


if __name__ == "__main__":
    main()
