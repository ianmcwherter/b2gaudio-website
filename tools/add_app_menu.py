#!/usr/bin/env python3
"""Inject the shared app menu (_appmenu.html) into every page's nav bar.

Idempotent: an existing block is replaced rather than duplicated, so this is the way to roll
out a change to the menu across the whole site — edit _appmenu.html, run this, commit.
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
START, END = "<!-- app-menu:start -->", "<!-- app-menu:end -->"

snippet = (ROOT / "_appmenu.html").read_text()
block = f"{START}\n{snippet}\n{END}"

# The menu belongs at the END of .nav-inner, so it sits at the right-hand edge of the bar.
NAV_INNER_CLOSE = re.compile(r'(<div class="nav-inner">.*?)(\n\s*</div>)', re.S)

changed, skipped = [], []
for path in sorted(ROOT.glob("*.html")):
    if path.name.startswith("_"):
        continue
    html = path.read_text()

    if START in html:                                   # replace an older copy
        html = re.sub(re.escape(START) + ".*?" + re.escape(END), block, html, flags=re.S)
    else:
        m = NAV_INNER_CLOSE.search(html)
        if not m:
            skipped.append(path.name)
            continue
        html = html[:m.end(1)] + "\n" + block + html[m.end(1):]

    if html != path.read_text():
        path.write_text(html)
        changed.append(path.name)

print(f"menu written into {len(changed)} page(s)")
for name in changed:
    print("  ", name)
if skipped:
    print(f"no <div class=\"nav-inner\"> found, left alone: {', '.join(skipped)}")
