# Asset Remediation Report

- Scope: source figures 17.1-17.4 and 18.1-18.3 owned by parts `065`-`072`.
- Source authority: `parts/part-065.pdf`, `part-066.pdf`, `part-067.pdf`, and `part-069.pdf`.
- Method: extracted embedded PDF image objects with `pdfimages`; PPM objects were converted to JPEG without redrawing or adding labels.
- Result: 7 of 7 requested figure assets restored; no unresolved external asset limitation remains for this scope.

| Figure | Source | Asset | Evidence |
| --- | --- | --- | --- |
| 17.1 | `part-065.pdf`, PDF page 5 | `../assets/part-065-figure-17-1-000.jpg` | Embedded JPEG, 881 x 385 px |
| 17.2 | `part-065.pdf`, PDF page 6 | `../assets/part-065-figure-17-2-000.jpg` | Embedded JPEG, 863 x 755 px |
| 17.3 | `part-065.pdf`, PDF page 6 | `../assets/part-065-figure-17-3-000.jpg` | Embedded image, 978 x 424 px |
| 17.4 | `part-066.pdf`, PDF page 6 | `../assets/part-066-figure-17-4-000.jpg` | Embedded JPEG, 1070 x 364 px |
| 18.1 | `part-067.pdf`, PDF page 6 | `../assets/part-067-figure-18-1-000.jpg` | Embedded image, 559 x 844 px |
| 18.2 | `part-067.pdf`, PDF page 7 | `../assets/part-067-figure-18-2-000.jpg` | Embedded image, 1652 x 871 px |
| 18.3 | `part-069.pdf`, PDF page 7 | `../assets/part-069-figure-18-3-000.jpg` | Embedded image, 1519 x 413 px |

## Markdown References

- `vi/parts/part-065.md`: Figures 17.1-17.3, each reference immediately precedes its existing caption.
- `vi/parts/part-066.md`: Figure 17.4, reference immediately precedes its existing caption.
- `vi/parts/part-067.md`: Figures 18.1-18.2, each reference immediately precedes its existing caption.
- `vi/parts/part-069.md`: Figure 18.3, reference immediately precedes its existing caption.

## Verification

- All seven asset files exist under `vi/assets/`.
- Each asset opens as a non-empty JPEG and retains the source diagram's visible labels and relationships.
- Existing prose, captions, code, output, and ownership boundaries were preserved.
- Markdown links were checked against the seven created paths.
