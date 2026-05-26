#!/usr/bin/env python3
"""
fix-nerd-fonts.py
Scales down Nerd Font glyphs that are too large and constrains all
advance widths to the font's base cell size.
Usage: python3 fix-nerd-fonts.py <input_dir> <output_dir> [scale]
"""
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
import os, glob, sys

input_dir = sys.argv[1]
output_dir = sys.argv[2]
scale = float(sys.argv[3]) if len(sys.argv) > 3 else 0.75

os.makedirs(output_dir, exist_ok=True)

for path in sorted(glob.glob(f'{input_dir}/**/*.ttf', recursive=True)):
    rel = os.path.relpath(path, input_dir)
    out_path = os.path.join(output_dir, rel)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    font = TTFont(path)
    cmap = font.getBestCmap()
    glyf_table = font['glyf']
    hmtx = font['hmtx'].metrics

    widths = set(v[0] for v in hmtx.values() if v[0] > 0)
    cell = min(widths)
    offset_x = (cell - cell * scale) / 2
    offset_y = offset_x - 50

    nerd_font_glyphs = {name for cp, name in cmap.items() if cp >= 0xE000}

    for gname in nerd_font_glyphs:
        try:
            glyph = glyf_table[gname]
            if glyph.numberOfContours == 0:
                continue
            rec = RecordingPen()
            glyph.draw(rec, glyf_table)
            pen = TTGlyphPen(None)
            rec.replay(TransformPen(pen, (scale, 0, 0, scale, offset_x, offset_y)))
            glyf_table[gname] = pen.glyph()
            w, lsb = hmtx[gname]
            hmtx[gname] = (cell, int(lsb * scale + offset_x))
        except Exception:
            pass

    for gname, (w, lsb) in hmtx.items():
        if w > cell:
            hmtx[gname] = (cell, lsb)

    font['OS/2'].xAvgCharWidth = cell
    font.save(out_path)
    print(f"  ✓ {rel}")
