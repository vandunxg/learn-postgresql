# Merge and Package Agent

Bạn chỉ chạy sau khi translation, boundary review, semantic review và blocking QA hoàn tất.

1. Discover tất cả translated parts.
2. Verify part count và missing part.
3. Sort natural numeric order.
4. Merge thành `vi/learn-postgresql-vi.md`.
5. Không chèn part markers không tồn tại trong source.
6. Chạy structural sanity checks: code fences, headings, tables, query plans, boundary transitions.
7. Verify final file không rỗng.
8. Tạo `vi/learn-postgresql-vi.zip` chứa translation, glossary, progress, reports và assets cần thiết.
9. Test ZIP integrity.
10. Chỉ báo hoàn thành khi verification thực sự pass.
