# Child Care Policy, Regulation and Funding

**A Multi-State Landscape Assessment for Child Development Schools, Inc.**
Prepared by True North Strategies · Current as of **August 3, 2026**

Federal framework plus profiles of the eleven states in which Child Development
Schools operates — approximately 267 centers across North Carolina, Georgia,
Arizona, Texas, Florida, Arkansas, Oklahoma, Virginia, Alabama, Tennessee and
Kentucky. Roughly 48,000 words; 104 pages as typeset.

---

## Quick start

```bash
pip install weasyprint          # PDF renderer
# pandoc must also be on PATH (apt install pandoc / brew install pandoc)

make            # builds everything into dist/
make docx       # Word only
make pdf        # PDF only
make dashboard  # rebuild the interactive dashboard from data.json
```

Or without make:

```bash
python scripts/build.py
python scripts/build_dashboard.py
```

---

## Layout

```
src/                    the report, in build order
  00-exec-summary.md      standalone 2-page executive summary (NOT in the full report)
  01-front-federal.md     front matter + Part I, the federal landscape
  02-comparison.md        Part II, cross-state comparison tables
  03-states-a.md          Part III, North Carolina and Georgia
  04-states-b.md          Part III, Arizona, Texas, Florida, Arkansas
  05-states-c.md          Part III, Oklahoma, Virginia, Alabama, Tennessee, Kentucky
  06-themes-calendar.md   Parts IV and V + appendix

assets/
  print.css               paged-media stylesheet driving the PDF (cover, TOC,
                          running heads, page numbers, table and callout styling)
  reference.docx          branded pandoc style reference; generated on first build

dashboard/
  data.json               all dashboard content — edit this
  template.html           layout, CSS and JS; `__DATA__` is the injection point
  index.html              built output (self-contained, no dependencies)

scripts/
  build.py                markdown -> docx + pdf
  build_dashboard.py      data.json + template.html -> index.html
  make_reference_docx.py  generates assets/reference.docx

research/                 raw research memos with inline source URLs (see below)
dist/                     build output — the five client deliverables
```

---

## How the build works

**Word.** `pandoc` with `--reference-doc=assets/reference.docx`, which carries the
navy/gold style definitions. A raw OOXML page break is injected before each
top-level `# Part` and `# Appendix` heading. The table of contents is a Word
field — it populates when the document is opened in Word, and renders empty if
you convert the .docx to PDF with LibreOffice. That is why the PDF is built by a
separate path rather than from the .docx.

**PDF.** `pandoc` to standalone HTML with `--toc`, then WeasyPrint against
`assets/print.css`. The TOC page numbers come from CSS
`target-counter(attr(href), page)`, so they are real and resolve at render time.
The cover is injected as a `.cover` div and pinned to `@page :first`.

**Dashboard.** One self-contained HTML file — inline CSS and JS, no CDN, no
build step beyond the JSON injection. Opens from `file://`.

### Two things that will bite you if you edit `src/`

1. **Keep a blank line between concatenated chapters.** `build.py` joins files
   with `"\n\n"` deliberately. Without it, a trailing paragraph followed by a
   leading `---` parses as a setext H2 and appears as a junk entry in the table
   of contents.
2. **`# Part` and `# Appendix` are load-bearing.** `build.py` matches those
   strings to insert Word page breaks, and `print.css` puts `break-before: page`
   on every `h1`. Renaming the top-level headings changes pagination.

---

## Source material and confidence marks

Every factual assertion is drawn from a primary or authoritative source
retrieved on August 3, 2026 — state administrative codes, legislative bill
records, enacted appropriations acts, agency policy manuals and rate schedules,
the Federal Register, govinfo bill status data, and statutory reports to
legislatures. Nothing time-sensitive comes from model general knowledge.

Facts that could not be verified from an accessible source are marked
**`[unconfirmed]`** in the text rather than estimated. There are roughly 130 such
marks. They are deliberate: in a document supporting operating and advocacy
decisions, a flagged gap beats a confident guess. Appendix A.3 consolidates them
by priority with a retrieval route for each; the project also carries a
standalone open-items tracker.

Twelve of the highest-stakes claims were re-verified on a separate adversarial
pass whose brief was to falsify them. That pass confirmed the CCDF rule's
citation, type, publication date, effective date and RIN; the scope of all four
rescissions; the Head Start rule's status as a proposed rule; FY2026
appropriations; the §45F amendments; the CACFP notice; the center counts; and
every element of Alabama's facility tax credit. It produced one date correction
(Oklahoma HB 4298) and three sourcing caveats, all incorporated. Appendix A.4
records what it found.

### `research/`

Raw research memos, each with inline source URLs and its own confidence-and-gaps
section. These are the working papers behind `src/`, kept for traceability.

`federal.md`, `ga.md`, `az.md`, `ar.md`, `ok.md`, `va.md`, `al.md`, `ky.md`

**Not included:** the North Carolina, Texas, Florida and Tennessee memos were
returned inline during research rather than written to disk, so no raw file
exists for them. Their substance is fully incorporated into `src/03-states-a.md`,
`src/04-states-b.md` and `src/05-states-c.md`, with the same sourcing discipline
and confidence marks.

---

## Deliverables in `dist/`

| File | What it is |
|---|---|
| `CDS-Child-Care-Policy-Landscape-2026.pdf` | The report, 104pp, cover + real TOC with page numbers |
| `CDS-Child-Care-Policy-Landscape-2026.docx` | Same, editable; TOC populates on open in Word |
| `...-Executive-Summary.pdf` | Two pages plus cover |
| `...-Executive-Summary.docx` | Same, editable |
| `CDS-Child-Care-Policy-Dashboard.html` | Interactive; open directly in a browser |

---

## Refreshing the assessment

The material has a short half-life. The items most likely to be stale first:

- **Payment basis** in Georgia, North Carolina and Tennessee — unconfirmed at
  time of writing and covering 159 of the 267 centers.
- **Arkansas** subsidy funding, which expires September 30, 2026.
- **North Carolina's** statewide rate floor, effective October 1, 2026.
- **Every political map**, after the November 3, 2026 elections — nine
  gubernatorial races, seven with term-limited incumbents, and committee
  assignments resetting in states that begin new terms in January 2027.

Part V of the report is a dated monitoring calendar running through the end of
2027; the same items drive the dashboard's Calendar tab from `data.json`.
