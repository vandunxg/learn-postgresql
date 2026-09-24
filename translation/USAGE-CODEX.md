# Usage với Codex / coding agent

## 1. Đặt bộ instruction vào project

Ví dụ:

```text
learn-postgresql/
  document.pdf hoặc parts/*.pdf
  translation-instructions/
  vi/
```

Copy toàn bộ pack này vào `translation-instructions/` hoặc root project.

## 2. Split

Với sách khoảng 750 trang, target 8-10 trang/part. 10 trang/part cho khoảng 75 part là default hợp lý.

Nếu PDF đã được split thì không cần split lại chỉ vì boundary cắt giữa section; workflow neighbor-context + boundary review được thiết kế để xử lý cut cứng.

## 3. Prompt khởi chạy

Yêu cầu agent đọc `prompts/orchestrator-agent.md` và toàn bộ `instructions/`, sau đó thực thi.

## 4. Parallelism

- tối đa 30 translation worker;
- mỗi part một writer;
- glossary read-only;
- boundary review Wave A rồi Wave B;
- semantic/QA reviewer không ghi cùng file đồng thời.

## 5. Context rule quan trọng

Worker part N đọc current full part + previous tail + next head. Neighbor không được copy vào output.

## 6. PostgreSQL rule quan trọng

Không sửa SQL/code/output/query plan. Translation prose phải source-grounded và không modernize theo PostgreSQL version mới hơn.
