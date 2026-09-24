# 04 - Boundary Context Rules

PDF part có thể bị cắt giữa bất kỳ construct nào. Không giả định đầu/cuối part là semantic boundary.

## Các dạng cut phải chủ động phát hiện

- giữa sentence;
- giữa paragraph;
- giữa section/chapter;
- giữa numbered/bullet list;
- giữa table/result set;
- giữa SQL statement;
- giữa `psql` session;
- giữa terminal command/output;
- giữa code block;
- giữa query plan tree;
- giữa figure/caption;
- giữa exercise và lời giải thích.

## Sentence cut

Không tự đóng câu ở cuối part nếu source tiếp tục sang part sau. Không viết lại đầu part sau như một câu độc lập nếu nó là continuation.

## SQL cut

Nếu statement bắt đầu ở part N và kết thúc ở N+1:

- worker N không tự thêm phần còn thiếu;
- worker N+1 không tự thêm phần đầu;
- giữ fragment fidelity;
- metadata đánh dấu `ends_inside_sql`/`begins_inside_sql`;
- boundary reviewer reconcile representation sau.

## Query plan cut

Tree indentation và parent-child relation là semantic. Nếu plan bị cut, không tự reconstruct node bị thiếu. Reviewer phải đọc source hai phía.

## Boundary review hai wave

Để tránh concurrent write:

Wave A:

```text
001 <-> 002
003 <-> 004
005 <-> 006
...
```

Wave B sau khi A hoàn thành:

```text
002 <-> 003
004 <-> 005
006 <-> 007
...
```

Reviewer chỉ sửa vùng boundary cần thiết, không rewrite toàn part.
