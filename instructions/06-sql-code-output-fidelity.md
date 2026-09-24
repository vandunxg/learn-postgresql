# 06 - SQL, Code, Commands và Output Fidelity

## Nguyên tắc

Executable/source blocks là immutable content.

Không sửa:

- SQL query;
- DDL/DML;
- PL/pgSQL;
- shell command;
- `psql` meta-command;
- configuration snippet;
- JSON/XML/YAML sample;
- terminal output;
- query result;
- log line;
- error message;
- `EXPLAIN` / `EXPLAIN ANALYZE` output.

## Không làm

- Không translate SQL keyword/identifier.
- Không rename table/column/alias.
- Không format lại query chỉ vì style preference.
- Không sửa syntax dù nghi source có typo.
- Không đổi `SERIAL` thành identity, hay syntax cũ thành syntax mới.
- Không thay command bằng command hiện đại hơn.
- Không thay sample value có technical meaning.
- Không dịch error/output do PostgreSQL trả về.

## Comments trong code

Mặc định giữ nguyên comment nằm trong executable/source block để code copy-paste và diff được bảo toàn. Dịch explanation ở prose/caption bên ngoài block.

## `psql` session

Giữ prompt và output, ví dụ:

```text
postgres=#
mydb=>
```

Không xóa prompt chỉ vì nghĩ là decoration.

## EXPLAIN plan

Giữ tuyệt đối:

- node name;
- indentation;
- arrow/tree layout;
- cost/rows/width;
- actual time/loops;
- filter/index condition;
- planning/execution time;
- buffers và metadata khác.

Prose giải thích plan được dịch; plan output không dịch.
