# Asset Remediation Report: Parts 033-040

- Scope: asset remediation for `vi/parts/part-033.md` through `vi/parts/part-040.md` only.
- Source inspection: `parts/part-034.pdf` and `parts/part-039.pdf` were checked with `pdfimages -list`; neither PDF contains extractable raster images.
- Source pages: the Discord QR appears on PDF page 8 (printed page 305) of `part-034.pdf` and PDF page 10 (printed page 357) of `part-039.pdf`.
- Method: rendered each source page at 300 DPI with `pdftocairo`, then cropped the complete QR artwork from the faithful page render without recreating it. QR decoding was used only afterward to verify the extracted content.
- Assets:
  - `vi/assets/part-034-qr-discord.png`
  - `vi/assets/part-039-qr-discord.png`
- Markdown references: `part-034.md` references only its corresponding asset; `part-039.md` references only its corresponding asset. No other part was changed for asset references.
- Preservation: the visible URL `https://discord.gg/jYWCjF6Tku` and source invitation text remain in both Markdown parts.
- Limitation: the source QR is vector artwork represented by page drawing commands, not an independently extractable image object. The stored PNGs are faithful crops of the rendered source pages, not invented QR content. No other source diagram in parts 033-040 required an asset reference.
- Verification: both PNGs are non-empty, complete QR renders, and both relative Markdown links resolve to the corresponding files.
