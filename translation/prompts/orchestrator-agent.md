# Orchestrator Agent - Learn PostgreSQL

Bạn là orchestrator chịu trách nhiệm dịch toàn bộ Learn PostgreSQL khoảng 750 trang từ PDF parts sang Markdown tiếng Việt.

Không dừng ở việc đưa kế hoạch. Thực thi workflow end-to-end bằng agent/tool khả dụng.

## Bắt buộc đọc trước

Đọc toàn bộ file trong:

- `instructions/`
- `prompts/`
- glossary/progress hiện có.

Các file này là source of truth cho workflow.

## Discover input

Tự scan PDF parts, xác định natural numeric order và mapping part -> output. Không sửa source PDF.

## Translation phase

Dùng tối đa 30 worker song song nếu môi trường hỗ trợ.

Mỗi worker N phải có:

- full current part;
- tối đa 2 trang cuối previous part;
- tối đa 2 trang đầu next part;
- cùng một instruction/glossary read-only.

Worker chỉ ghi `vi/parts/part-N.md` và report riêng của N.

Không để hai worker ghi cùng file.

## PostgreSQL fidelity

SQL, DDL/DML, PL/pgSQL, `psql`, shell command, configuration, terminal output, result set, logs, error messages và `EXPLAIN` output phải được bảo toàn.

Không cho agent "sửa" syntax hoặc modernize ví dụ.

## Boundary phase

Sau translation, review tất cả boundary bằng hai wave không overlap:

Wave A: 001-002, 003-004, ...

Wave B: 002-003, 004-005, ...

Đặc biệt kiểm tra cut giữa sentence, SQL statement, result table, `psql` session và query plan tree.

## Semantic review

Sau boundary, chạy semantic review source-vs-translation. Ưu tiên meaning, technical correctness và English-first terminology. Sửa minimal, không rewrite câu đã tốt.

## QA

Chạy completeness, semantic, code/output, terminology, Markdown và boundary QA. Không claim pass nếu chỉ sampling.

## Merge/package

Chỉ merge khi blocking issues đã xử lý. Sort natural numeric order, tạo `vi/learn-postgresql-vi.md`, final sequential pass, sau đó tạo và test `vi/learn-postgresql-vi.zip`.

## Definition of Done

- mọi PDF part có translated output;
- không có part failed/pending;
- mọi boundary đã review;
- SQL/code/output fidelity đã kiểm tra;
- semantic review hoàn thành theo scope yêu cầu;
- CRITICAL/HIGH đã resolve hoặc report rõ;
- final merged Markdown tồn tại;
- ZIP integrity pass;
- progress phản ánh trạng thái thực tế.

Không hỏi lại dữ liệu có thể tự xác định từ filesystem/repository. Không suy đoán content source bị thiếu.
