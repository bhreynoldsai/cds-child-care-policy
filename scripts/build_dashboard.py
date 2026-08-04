#!/usr/bin/env python3
"""
Build the interactive dashboard.

Injects dashboard/data.json into dashboard/template.html and writes a single
self-contained file to dashboard/index.html and dist/.

Edit dashboard/data.json to change content; edit dashboard/template.html to
change layout or styling. No build dependencies, no network calls.

data.json shape
---------------
states[]   one object per state; `id`, `name`, `centers`, `dir`, `pay`,
           `payclass`, `headline`, plus the profile fields rendered in the
           detail panel and a `watch` list of strings.
           dir      -> expanding | contracting | flat | split   (card edge colour)
           payclass -> good | warn | bad                        (tag colour)
           ratecurrent -> bool; whether the rate benchmark is current. Set
                       explicitly per the staleness table in src/02-comparison.md
                       rather than inferred from the `ratevintage` prose.
calendar[] [date, state, item, urgency]  urgency -> crit | now | soon | later
opens[]    [tier, item, where, route]    tier -> "Tier 1" | "Tier 2" | "Tier 3"
ratios[]   [state, infant, 1yr, 2yr, 3yr, 4yr, 5yr, school-age, group-size note]

Usage:  python scripts/build_dashboard.py
"""
import json
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DASH = os.path.join(ROOT, "dashboard")
DIST = os.path.join(ROOT, "dist")
OUT_NAME = "CDS-Child-Care-Policy-Dashboard.html"


def main():
    data = json.load(open(os.path.join(DASH, "data.json")))
    template = open(os.path.join(DASH, "template.html")).read()

    if "__DATA__" not in template:
        raise SystemExit("template.html has no __DATA__ placeholder")

    total = sum(s["centers"] for s in data["states"])
    print("%d states, %d centers, %d calendar items, %d open items"
          % (len(data["states"]), total, len(data["calendar"]), len(data["opens"])))

    html = template.replace("__DATA__", json.dumps(data, ensure_ascii=False))

    open(os.path.join(DASH, "index.html"), "w").write(html)
    os.makedirs(DIST, exist_ok=True)
    shutil.copy(os.path.join(DASH, "index.html"), os.path.join(DIST, OUT_NAME))
    print("wrote dashboard/index.html and dist/%s" % OUT_NAME)


if __name__ == "__main__":
    main()
