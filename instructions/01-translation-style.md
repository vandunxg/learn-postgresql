# 01 - Translation Style

## Văn phong

Bản dịch phải đọc giống tài liệu PostgreSQL/SQL do backend hoặc database engineer Việt viết: trực tiếp, kỹ thuật, tự nhiên, không Việt hóa từng từ.

## English-first theo ngữ cảnh

Giữ English khi term là technical/domain concept và English tự nhiên hoặc chính xác hơn trong ngữ cảnh.

Ví dụ thường giữ English:

`database`, `database cluster`, `server`, `instance`, `session`, `connection`, `schema`, `table`, `row`, `column`, `tuple`, `query`, `statement`, `clause`, `expression`, `predicate`, `transaction`, `commit`, `rollback`, `savepoint`, `isolation level`, `lock`, `deadlock`, `snapshot`, `MVCC`, `WAL`, `checkpoint`, `replication`, `primary`, `standby`, `failover`, `tablespace`, `extension`, `role`, `privilege`, `sequence`, `index`, `query planner`, `execution plan`, `cache`, `partition`, `trigger`, `function`, `procedure`, `view`, `materialized view`.

Technical verbs có thể giữ English khi cách đó tự nhiên hơn:

`scan`, `join`, `aggregate`, `filter`, `sort`, `hash`, `cast`, `commit`, `rollback`, `vacuum`, `analyze`, `replicate`, `promote`, `materialize`, `serialize`, `deserialize`.

Danh sách này là baseline, không phải whitelist.

## Quyết định theo meaning, không theo token

- `table` khi là relation/table trong database thường giữ `table`.
- `table of contents` phải dịch theo nghĩa thông thường.
- `role` khi là PostgreSQL role nên giữ `role`.
- `role of the planner` có thể dịch theo nghĩa thông thường nếu không phải object/domain concept.
- `statement` trong SQL context có thể giữ `statement`; trong prose thông thường có thể dịch theo nghĩa câu.

## Không lạm dụng English

Phần grammar, liên từ và diễn giải thông thường phải là tiếng Việt tự nhiên. Không tạo câu nửa Anh nửa Việt vô lý.

Tốt:

> Query planner chọn execution plan dựa trên statistics hiện có của table.

Không tốt:

> Query planner will chọn execution plan based trên statistics của table.

## Recommendation strength

Giữ đúng mức độ của source: `must`, `should`, `may`, `might`, `can`, `generally`, `usually`, `often`, `rarely`, `never`, `always`, `recommend`, `avoid`.

Không biến `may` thành `sẽ`, `should` thành `phải`, hoặc bỏ các qualifier như `usually`/`generally`.
