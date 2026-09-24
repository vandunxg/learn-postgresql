# 11 - Merge và Package

## Preconditions

Chỉ merge khi:

- mọi part translated;
- boundary review hoàn thành;
- semantic review theo scope yêu cầu hoàn thành;
- blocking QA issue đã resolve;
- không có concurrent writer.

## Merge order

Natural numeric order tuyệt đối:

```text
part-001.md
part-002.md
...
```

Không dựa vào filesystem order.

## Final book

Khuyến nghị:

```text
vi/learn-postgresql-vi.md
```

Không chèn separator kỹ thuật kiểu `PART 001` nếu source không có.

## Final sequential pass

Sau merge, đọc theo thứ tự toàn sách để phát hiện:

- boundary artifact còn sót;
- duplicate/missing transition;
- terminology drift;
- heading/list/table continuation lỗi;
- broken code fence;
- query plan bị tách/hỏng;
- metadata/report lọt vào book.

## ZIP

Deliverable khuyến nghị:

```text
vi/learn-postgresql-vi.zip
```

ZIP nên chứa:

- `parts/`;
- final merged Markdown;
- `GLOSSARY.md`;
- `PROGRESS.md`;
- reports cần thiết;
- assets nếu đã extract.

Không đưa cache/temp/renders vào ZIP trừ khi user yêu cầu.

Trước khi hoàn thành phải verify ZIP integrity và file count.
