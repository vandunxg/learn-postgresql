# 10 - Progress và Atomicity

## Status lifecycle

Khuyến nghị:

```text
pending
translating
translated
boundary-reviewed
semantic-reviewed
qa-passed
merged
```

Chỉ ghi status phản ánh công việc thực tế.

## Atomic write ownership

- Translation worker: chỉ ghi `vi/parts/part-N.md` và metadata/report riêng của N.
- Boundary reviewer: chỉ ghi pair được giao, không chạy overlap pair đồng thời.
- Semantic reviewer: một writer/file tại một thời điểm.
- QA agent: ưu tiên report; nếu sửa trực tiếp phải có ownership rõ và không trùng reviewer khác.
- Merge agent: chỉ chạy sau khi upstream phase kết thúc.

## Retry

Worker fail chỉ retry part fail. Không rerun toàn bộ corpus nếu không cần.

Nếu extraction không chắc chắn, đánh dấu issue thay vì hallucinate.

## Glossary

Trong parallel phase, glossary là read-only. Terminology change toàn cục chỉ thực hiện ở consistency pass có kiểm soát.
