# Asset Remediation Report: Parts 057-064

- Scope: `vi/parts/part-057.md` through `vi/parts/part-064.md` only.
- Source checked: `parts/part-057.pdf` through `parts/part-064.pdf`.
- Instructions checked: `instructions/05-markdown-preservation.md`, `instructions/07-table-diagram-query-plan.md`, `instructions/09-qa-validation.md`, `instructions/04-boundary-context.md`, `prompts/qa-review-agent.md`, and `prompts/boundary-review-agent.md`.

## Page Mapping and Assets

| Source | Printed page | Asset | Markdown reference |
| --- | ---: | --- | --- |
| `part-057.pdf`, QR artwork | 533 | `vi/assets/part-057-qr-discord.png` | `vi/parts/part-057.md`, after the Discord URL |
| `part-061.pdf`, QR artwork | 572 | `vi/assets/part-061-qr-discord.png` | `vi/parts/part-061.md`, after the Discord URL |
| `part-063.pdf`, Figure 16.1 | 590 | `vi/assets/part-063-figure-16-1.jpg` | `vi/parts/part-063.md`, before the Figure 16.1 caption |
| `part-063.pdf`, Figure 16.2 | 591 | `vi/assets/part-063-figure-16-2.jpg` | `vi/parts/part-063.md`, before the Figure 16.2 caption |
| `part-063.pdf`, Figure 16.3 | 592 | `vi/assets/part-063-figure-16-3.jpg` | `vi/parts/part-063.md`, before the Figure 16.3 caption |
| `part-064.pdf`, QR artwork | 605 | `vi/assets/part-064-qr-discord.png` | `vi/parts/part-064.md`, after the Discord URL |

The three Figure 16 screenshots were extracted from the embedded raster image objects in `part-063.pdf` with `pdfimages`; their order maps to PDF pages 3-5 and printed pages 590-592. They were converted to JPEG without redrawing or inferring image content.

The QR graphics were not listed as standalone `pdfimages` objects. Each was confirmed in a 300-DPI render of the source PDF page and cropped from that render, preserving the actual source artwork. The crop for `part-061` was verified to contain only the QR code and its white quiet area.

## Verification

- All six referenced files exist under `vi/assets/`.
- Figure references occur immediately before their existing captions.
- QR references occur after the existing Discord URL because the source has no caption for the QR artwork.
- Existing prose, captions, URLs, code/output, and part ownership were preserved.
- No asset was inferred or redrawn.
- `pdfimages -list` found no standalone QR image object in parts 057, 061, or 064; the rendered-page crop method above is therefore recorded as the extraction limitation.
