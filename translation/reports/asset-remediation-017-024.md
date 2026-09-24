# Asset Remediation Report: Parts 017-024

- Scope: Figures 5.5-5.6 and 6.1-6.7 reported missing by `vi/reports/qa-017-024.md`.
- Ownership: Only `vi/parts/part-017.md`, `vi/parts/part-019.md`, and `vi/parts/part-021.md` were changed. Parts 018, 020, 022, 023, and 024 were not changed because they do not own one of the reported figures.
- Source authority: `parts/part-017.pdf`, `parts/part-019.pdf`, and `parts/part-021.pdf`.

## Extracted Assets

| Figure | Source page | Embedded object | Output asset |
| --- | --- | --- | --- |
| 5.5 | part 017, local p. 1; printed p. 128 | JPEG, 707x404 | `vi/assets/part-017-figure-5-5-000.jpg` |
| 5.6 | part 017, local p. 4; printed p. 131 | JPEG, 1156x783 | `vi/assets/part-017-figure-5-6-000.jpg` |
| 6.1 | part 019, local p. 9; printed p. 156 | JPEG, 1359x914 | `vi/assets/part-019-figure-6-1-000.jpg` |
| 6.2 | part 019, local p. 10; printed p. 157 | JPEG, 1356x884 | `vi/assets/part-019-figure-6-2-000.jpg` |
| 6.3 | part 021, local p. 2; printed p. 169 | Raw raster, 1112x733 | `vi/assets/part-021-figure-6-3-000.png` |
| 6.4 | part 021, local p. 3; printed p. 170 | Raw raster, 1329x890 | `vi/assets/part-021-figure-6-4-000.png` |
| 6.5 | part 021, local p. 4; printed p. 171 | Raw raster, 1246x827 | `vi/assets/part-021-figure-6-5-000.png` |
| 6.6 | part 021, local p. 4; printed p. 171 | Raw raster, 1253x842 | `vi/assets/part-021-figure-6-6-000.png` |
| 6.7 | part 021, local p. 5; printed p. 172 | Raw raster, 1019x681 | `vi/assets/part-021-figure-6-7-000.png` |

## Method

1. Used `pdfimages -list` to confirm the source PDFs contain embedded image objects and identify their page-local order and dimensions.
2. Used `pdfimages -j` to extract the JPEG objects directly. The raw raster objects from part 021 were converted to PNG without resizing or content changes.
3. Rendered the corresponding source pages with `pdftoppm` and visually checked each extracted object against its source figure and caption. No diagram was redrawn or inferred.
4. Added one Markdown image reference immediately before each existing caption in its owning part. Existing translated prose and captions were preserved.

## Verification

- All nine output assets are non-empty and have the dimensions recorded above.
- All nine references resolve from `vi/parts/` via `../assets/`.
- The references occur immediately before Figures 5.5-5.6 and 6.1-6.7 captions.
- No Markdown part outside the owned 017-024 scope was modified.
