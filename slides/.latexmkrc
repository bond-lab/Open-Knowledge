# These slides use fontspec and Noto Color Emoji, which needs the Harfbuzz
# renderer, so they build with lualatex only: pdflatex cannot load fontspec
# and xelatex cannot load the bitmap emoji font.  The .tex files carry the
# same setting for AUCTeX as "%%% TeX-engine: luatex".
$pdf_mode = 4;    # 4 = lualatex
