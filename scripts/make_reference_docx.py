#!/usr/bin/env python3
"""
Generate a branded pandoc reference.docx (True North Strategies navy/gold).

Pandoc ships a default reference.docx; this script extracts it, rewrites the
style definitions, and repacks it. Run once — build.py will call it
automatically if assets/reference.docx is missing.

Usage:  python scripts/make_reference_docx.py [outpath]
Output: assets/reference.docx
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

NAVY = "14284B"
GOLD = "B08D2E"
SLATE = "3E4A5B"
SERIF = "Georgia"
SANS = "Calibri"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "assets", "reference.docx")


def restyle(xml, style_id, color=None, size=None, font=None,
            bold=False, caps=False, spacing=None):
    """Rewrite one <w:style> block in styles.xml. Sizes are half-points."""
    m = re.search(r'(<w:style [^>]*w:styleId="%s".*?</w:style>)' % style_id, xml, re.S)
    if not m:
        print("  ! style not found:", style_id)
        return xml
    orig = blk = m.group(1)

    if "<w:rPr>" not in blk:
        blk = blk.replace("</w:style>", "<w:rPr></w:rPr></w:style>")

    def setprop(b, tag, snippet):
        b = re.sub(r"<w:%s [^/>]*/>" % tag, "", b)
        b = re.sub(r"<w:%s/>" % tag, "", b)
        return b.replace("<w:rPr>", "<w:rPr>" + snippet, 1)

    if color:
        blk = setprop(blk, "color", '<w:color w:val="%s"/>' % color)
    if size:
        blk = setprop(blk, "sz", '<w:sz w:val="%d"/>' % size)
        blk = setprop(blk, "szCs", '<w:szCs w:val="%d"/>' % size)
    if caps:
        blk = blk.replace("<w:rPr>", "<w:rPr><w:caps/>", 1)
    if font:
        blk = setprop(blk, "rFonts",
                      '<w:rFonts w:ascii="%s" w:hAnsi="%s" w:cs="%s"/>' % (font, font, font))
    if bold:
        blk = blk.replace("<w:rPr>", "<w:rPr><w:b/>", 1)
    if spacing:
        before, after = spacing
        if "<w:pPr>" not in blk:
            blk = blk.replace("<w:rPr>", "<w:pPr></w:pPr><w:rPr>", 1)
        blk = re.sub(r"<w:spacing [^/>]*/>", "", blk)
        blk = blk.replace("<w:pPr>",
                          '<w:pPr><w:spacing w:before="%d" w:after="%d"/>' % (before, after), 1)

    return xml.replace(orig, blk)


TABLE_STYLE = (
    '<w:style w:type="table" w:styleId="Table"><w:name w:val="Table"/>'
    '<w:basedOn w:val="TableNormal"/><w:uiPriority w:val="0"/>'
    '<w:pPr><w:spacing w:before="40" w:after="40"/></w:pPr>'
    '<w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>'
    '<w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr>'
    '<w:tblPr><w:tblBorders>'
    '<w:top w:val="single" w:sz="4" w:space="0" w:color="C9D0DA"/>'
    '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="C9D0DA"/>'
    '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="DDE2EA"/>'
    "</w:tblBorders>"
    '<w:tblCellMar><w:top w:w="60" w:type="dxa"/><w:left w:w="90" w:type="dxa"/>'
    '<w:bottom w:w="60" w:type="dxa"/><w:right w:w="90" w:type="dxa"/></w:tblCellMar>'
    "</w:tblPr>"
    '<w:tblStylePr w:type="firstRow">'
    '<w:rPr><w:b/><w:color w:val="FFFFFF"/><w:sz w:val="18"/></w:rPr>'
    '<w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="14284B"/></w:tcPr>'
    "</w:tblStylePr>"
    '<w:tblStylePr w:type="band2Horz">'
    '<w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="F2F5F9"/></w:tcPr>'
    "</w:tblStylePr></w:style>"
)


def main():
    tmp = tempfile.mkdtemp()
    base = os.path.join(tmp, "base.docx")
    # pandoc writes the default reference.docx to the path given by -o
    subprocess.run(
        ["pandoc", "-o", base, "--print-default-data-file", "reference.docx"],
        check=True)

    work = os.path.join(tmp, "unpacked")
    with zipfile.ZipFile(base) as z:
        z.extractall(work)

    sp = os.path.join(work, "word", "styles.xml")
    s = open(sp).read()

    s = restyle(s, "Title",       color=NAVY,  size=52, font=SERIF, bold=True, spacing=(0, 240))
    s = restyle(s, "Subtitle",    color=GOLD,  size=28, font=SANS,  bold=True, caps=True, spacing=(0, 360))
    s = restyle(s, "Author",      color=SLATE, size=22, font=SANS)
    s = restyle(s, "Date",        color=SLATE, size=22, font=SANS)
    s = restyle(s, "Heading1",    color=NAVY,  size=32, font=SERIF, bold=True, spacing=(400, 180))
    s = restyle(s, "Heading2",    color=NAVY,  size=26, font=SERIF, bold=True, spacing=(320, 140))
    s = restyle(s, "Heading3",    color=GOLD,  size=23, font=SANS,  bold=True, spacing=(260, 120))
    s = restyle(s, "Heading4",    color=SLATE, size=21, font=SANS,  bold=True, spacing=(220, 100))
    s = restyle(s, "Heading5",    color=SLATE, size=20, font=SANS,  bold=True, spacing=(200, 90))
    s = restyle(s, "Normal",      size=20, font=SANS)
    s = restyle(s, "BodyText",    size=20, font=SANS, spacing=(0, 140))
    s = restyle(s, "BlockText",   color=NAVY, size=20, font=SANS)
    s = restyle(s, "Compact",     size=20, font=SANS)
    s = restyle(s, "TOCHeading",  color=NAVY, size=30, font=SERIF, bold=True)
    s = restyle(s, "Hyperlink",   color="1F5FA9")

    old_table = re.search(r'<w:style [^>]*w:styleId="Table".*?</w:style>', s, re.S)
    if old_table:
        s = s.replace(old_table.group(0), TABLE_STYLE)

    open(sp, "w").write(s)

    # Ask Word to refresh the TOC field on open.
    setp = os.path.join(work, "word", "settings.xml")
    st = open(setp).read()
    if "updateFields" not in st:
        st = re.sub(r"(<w:settings[^>]*>)", r'\1<w:updateFields w:val="true"/>', st, count=1)
        open(setp, "w").write(st)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    if os.path.exists(OUT):
        os.remove(OUT)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for dirpath, _, files in os.walk(work):
            for fn in files:
                full = os.path.join(dirpath, fn)
                z.write(full, os.path.relpath(full, work))

    shutil.rmtree(tmp, ignore_errors=True)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
