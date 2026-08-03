#!/usr/bin/env python3
"""
Build the Child Development Schools landscape assessment.

Concatenates src/*.md in filename order, then emits four files into dist/:

  CDS-Child-Care-Policy-Landscape-2026.docx                    (Word, TOC field)
  CDS-Child-Care-Policy-Landscape-2026.pdf                     (WeasyPrint, real TOC)
  CDS-Child-Care-Policy-Landscape-2026-Executive-Summary.docx
  CDS-Child-Care-Policy-Landscape-2026-Executive-Summary.pdf

src/00-exec-summary.md is the standalone executive summary and is NOT part of
the full report body. src/01-*.md through src/06-*.md are the report, in order.

Requires: pandoc, weasyprint (pip install weasyprint).

Usage:  python scripts/build.py [--docx-only | --pdf-only]
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
DIST = os.path.join(ROOT, "dist")
ASSETS = os.path.join(ROOT, "assets")
BUILD = os.path.join(ROOT, ".build")
REF = os.path.join(ASSETS, "reference.docx")
CSS = os.path.join(ASSETS, "print.css")

TITLE = "Child Care Policy, Regulation and Funding"
SUBTITLE = "A Multi-State Landscape Assessment for Child Development Schools, Inc."
STRAPLINE = "Federal Environment and Eleven-State Operating Footprint"
FIRM = "True North Strategies"
DATE = "August 3, 2026"
STEM = "CDS-Child-Care-Policy-Landscape-2026"

# Raw OOXML page break, injected before each top-level Part / Appendix heading.
PAGEBREAK = '\n```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```\n\n'

# The first nine lines of 01-front-federal.md are the printed title block.
# Both output paths replace it with their own cover, so strip it here.
TITLE_BLOCK_LINES = 9


def sh(*cmd):
    subprocess.run(list(cmd), check=True)


def read_body():
    """Concatenate the report chapters with guaranteed blank-line separators.

    The blank line matters: without it a trailing paragraph followed by a
    leading '---' is parsed as a setext H2 and pollutes the table of contents.
    """
    parts = sorted(f for f in os.listdir(SRC)
                   if f.endswith(".md") and not f.startswith("00-"))
    text = "\n\n".join(open(os.path.join(SRC, p)).read().strip() for p in parts)
    return "\n".join(text.split("\n")[TITLE_BLOCK_LINES:]).lstrip("\n")


def read_exec():
    text = open(os.path.join(SRC, "00-exec-summary.md")).read()
    return "\n".join(text.split("\n")[8:]).lstrip("\n")


def yaml_block(subtitle, author):
    return (
        "---\n"
        'title: "%s"\n'
        'subtitle: "%s"\n'
        'author: "%s"\n'
        'date: "%s"\n'
        "---\n\n" % (TITLE, subtitle, author, DATE)
    )


def cover(subtitle, strapline):
    return """
<div class="cover">
  <div class="rule"></div>
  <h1>Child Care Policy,<br/>Regulation and Funding</h1>
  <div class="sub">%s</div>
  <div class="sub2">%s</div>
  <div class="meta">
    <div class="hr"></div>
    <div class="firm">%s</div>
    <div class="date">%s</div>
  </div>
</div>
""" % (subtitle, strapline, FIRM, DATE)


def html_from(md_path, out_path, cover_html, toc=False, extra_head=""):
    """pandoc -> standalone HTML -> strip pandoc's own title header -> add cover."""
    tmp = os.path.join(BUILD, os.path.basename(out_path) + ".pandoc.html")
    cmd = ["pandoc", md_path, "-o", tmp, "--standalone", "--metadata", "title=x"]
    if toc:
        cmd += ["--toc", "--toc-depth=2"]
    sh(*cmd)

    h = open(tmp).read()
    inner = re.search(r"<body>(.*)</body>", h, re.S).group(1)
    inner = re.sub(r"<header[^>]*>.*?</header>", "", inner, flags=re.S)
    inner = re.sub(r'<h1 class="title">.*?</h1>', "", inner, flags=re.S)

    open(out_path, "w").write(
        '<!DOCTYPE html><html><head><meta charset="utf-8"><title>%s</title>'
        '<link rel="stylesheet" href="%s">%s</head><body>%s%s</body></html>'
        % (TITLE, os.path.relpath(CSS, os.path.dirname(out_path)),
           extra_head, cover_html, inner)
    )


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else ""
    os.makedirs(BUILD, exist_ok=True)
    os.makedirs(DIST, exist_ok=True)

    if not os.path.exists(REF):
        print("reference.docx missing — generating it")
        sh(sys.executable, os.path.join(ROOT, "scripts", "make_reference_docx.py"))

    body = read_body()
    ex = read_exec()

    # ---- Word ----
    if only != "--pdf-only":
        docx_body = re.sub(r"\n(# (?:Part |Appendix))",
                           lambda m: "\n" + PAGEBREAK + m.group(1), body)
        p = os.path.join(BUILD, "full.docx.md")
        open(p, "w").write(
            yaml_block(SUBTITLE, "%s  ·  Prepared by %s" % (STRAPLINE, FIRM))
            + PAGEBREAK + docx_body)
        sh("pandoc", p, "-o", os.path.join(DIST, STEM + ".docx"),
           "--reference-doc=" + REF, "--toc", "--toc-depth=2", "--standalone")

        p = os.path.join(BUILD, "exec.docx.md")
        open(p, "w").write(
            yaml_block("Executive Summary", "%s  ·  Prepared by %s" % (SUBTITLE, FIRM)) + ex)
        sh("pandoc", p, "-o", os.path.join(DIST, STEM + "-Executive-Summary.docx"),
           "--reference-doc=" + REF, "--standalone")
        print("built Word")

    # ---- PDF ----
    if only != "--docx-only":
        from weasyprint import HTML  # imported late so --docx-only works without it

        p = os.path.join(BUILD, "full.md")
        open(p, "w").write(body)
        hp = os.path.join(BUILD, "full.html")
        html_from(p, hp,
                  cover("A Multi-State Landscape Assessment for<br/>"
                        "Child Development Schools, Inc.", STRAPLINE),
                  toc=True)
        HTML(hp).write_pdf(os.path.join(DIST, STEM + ".pdf"))

        p = os.path.join(BUILD, "exec.md")
        open(p, "w").write(ex)
        hp = os.path.join(BUILD, "exec.html")
        # The exec summary is short: suppress the page break before every H1.
        html_from(p, hp, cover("Executive Summary", SUBTITLE),
                  extra_head="<style>h1{break-before:auto !important;}</style>")
        HTML(hp).write_pdf(os.path.join(DIST, STEM + "-Executive-Summary.pdf"))
        print("built PDF")

    for f in sorted(os.listdir(DIST)):
        print("  dist/%s  %s" % (f, os.path.getsize(os.path.join(DIST, f))))


if __name__ == "__main__":
    main()
