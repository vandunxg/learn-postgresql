part: part-009
source: parts/part-009.pdf
source_pages: 1-10 (printed pages 48-57; Chapter 3 begins on printed page 51)
status: translated

boundary:
  begins:
    state: starts with a complete paragraph on printed page 48
    begins_inside_paragraph: false
    begins_inside_sql: false
    begins_inside_code_block: false
    context_previous: pages 9-10 of part-008.pdf, read-only
  ends:
    state: ends immediately after the DROP ROLE error output on printed page 57
    ends_inside_paragraph: false
    ends_inside_sql: false
    ends_inside_code_block: false
    section_continues_in_next_part: true
    context_next: pages 1-2 of part-010.pdf, read-only

ownership:
  translated_content_only: part-009
  neighbor_content_copied: false
  running_headers_footers_removed: true

extraction:
  primary: pdftotext -layout
  fallback_checked: pdftotext -raw
  confidence: clear; layout and raw extraction agree on prose, code, and output
