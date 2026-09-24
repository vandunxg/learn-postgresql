# Learn PostgreSQL - Bộ instruction dịch PDF sang tiếng Việt

Bộ instruction này dùng cho workflow dịch một sách **Learn PostgreSQL** dài khoảng **750 trang** từ PDF sang Markdown tiếng Việt bằng nhiều AI agent chạy song song.

Mục tiêu chính:

- dịch đầy đủ, không tóm tắt và không tự thêm kiến thức;
- giữ đúng semantic PostgreSQL/SQL;
- dùng English-first cho technical terms;
- giữ nguyên SQL, command, terminal output, identifiers và query plan;
- không mất context khi PDF bị chia cứng giữa câu, paragraph, table, code block hoặc execution plan;
- cho phép nhiều worker chạy song song nhưng không có concurrent write conflict;
- có phase boundary reconciliation, semantic review, QA và merge cuối;
- tạo một Markdown hoàn chỉnh và ZIP deliverable.

## Cấu trúc

```text
instructions/
  00-core-rules.md
  01-translation-style.md
  02-postgresql-glossary.md
  03-pdf-part-workflow.md
  04-boundary-context.md
  05-markdown-preservation.md
  06-sql-code-output-fidelity.md
  07-table-diagram-query-plan.md
  08-semantic-review.md
  09-qa-validation.md
  10-progress-atomicity.md
  11-merge-package.md
prompts/
  orchestrator-agent.md
  worker-agent.md
  boundary-review-agent.md
  semantic-review-agent.md
  qa-review-agent.md
  merge-package-agent.md
schemas/
  PROGRESS.template.md
  PART-METADATA.template.md
  BOUNDARY-REPORT.template.md
  REVIEW-REPORT.template.md
  QA.template.md
USAGE-CODEX.md
VERSION.md
```

## Quy mô đề xuất cho 750 trang

Default tốt: **8-10 trang/PDF part**. Nếu dùng 10 trang/part thì khoảng **75 part**. Với tối đa 30 worker, translation có thể chạy theo queue song song; boundary review chạy sau theo hai wave chẵn/lẻ để tránh hai reviewer ghi cùng file.

Mỗi worker dịch part `N` phải được đọc context lân cận:

- tối đa 2 trang cuối của part `N-1`;
- toàn bộ part `N`;
- tối đa 2 trang đầu của part `N+1`.

Neighbor chỉ là context. Worker chỉ được ghi nội dung thuộc part mình sở hữu.

## Output khuyến nghị

```text
vi/
  parts/
    part-001.md
    part-002.md
    ...
  assets/
  reports/
  learn-postgresql-vi.md
  GLOSSARY.md
  PROGRESS.md
  learn-postgresql-vi.zip
```
