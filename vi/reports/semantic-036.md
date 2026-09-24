# Semantic Review Report

- Scope: `parts/part-036.pdf` (printed pages 318-327) compared with `vi/parts/part-036.md`, including the `part-035` and `part-037` boundary context
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| - | - | Không phát hiện lỗi semantic hoặc technical terminology cần sửa | Bản dịch giữ đúng quan hệ role/group membership, điều kiện `INHERIT`/`NOINHERIT`, dynamic inheritance, explicit `SET ROLE`, cách decode ACL, quyền của `PUBLIC`, và hành vi của các ví dụ ACL | Không chỉnh sửa | pass |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 0
- Unresolved: 0

## Verification

- Đã đối chiếu trực tiếp toàn bộ prose, heading, bullet list, bảng ACL, ví dụ và phần mở đầu `Default ACLs` theo paragraph/context với source PDF đầy đủ.
- Đã kiểm tra các quan hệ kỹ thuật về role, user, group, privilege/permission, `WITH INHERIT`, `INHERIT`, `NOINHERIT`, membership direction, dynamic inheritance và explicit `SET ROLE`.
- Đã kiểm tra cách diễn giải `grantee`, `grantor`, owner, ACL flag, `PUBLIC` catch-all, `INSERT`/`UPDATE`/`SELECT`/`DELETE`, và sự khác biệt giữa ACL cụ thể với ACL áp dụng cho mọi role.
- SQL, command, `psql` prompt, identifier, ACL string, result set, error message và output formatting không bị chỉnh sửa.
- Đã giữ nguyên inconsistency có sẵn trong source về dòng ACL owner thay vì tự sửa technical claim của tác giả.
- Boundary `part-035` -> `part-036` và `part-036` -> `part-037` được kiểm tra; phần output `\\dp perm_test` tiếp nối đúng ownership và không có nội dung neighbor bị copy vào part này.
- Không chỉnh sửa `vi/parts/part-036.md`; report này là artifact duy nhất được ghi bởi semantic review.
