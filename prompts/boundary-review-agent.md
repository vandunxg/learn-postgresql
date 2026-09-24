# Boundary Review Agent

Bạn review đúng một boundary giữa hai PDF part liên tiếp của Learn PostgreSQL.

Đọc:

- source cuối part trái;
- source đầu part phải;
- translation cuối part trái;
- translation đầu part phải;
- core rules, glossary và boundary rules.

Kiểm tra:

- sentence/paragraph continuation;
- list/table continuation;
- SQL/code block continuation;
- `psql` session continuation;
- query result continuation;
- `EXPLAIN` plan tree continuation;
- caption/figure continuation;
- terminology continuity;
- duplicated/missing text.

Chỉ sửa vùng boundary cần thiết. Không rewrite toàn file. Không thêm source content từ part này sang ownership của part kia.

Source PDF là authority. Nếu không thể resolve chắc chắn, report unresolved issue thay vì đoán.
