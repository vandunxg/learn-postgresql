# 05 - Markdown Preservation

Output là Markdown sạch, có thể merge theo thứ tự part.

## Giữ structure

Reconstruct hợp lý:

- heading hierarchy;
- paragraph boundaries;
- ordered/unordered list;
- blockquote;
- fenced code block;
- inline code;
- table;
- emphasis;
- link;
- image reference nếu asset thực sự tồn tại;
- caption;
- note/warning callout theo format thống nhất.

## Heading

Dịch heading prose nhưng không tự thêm heading để "làm đẹp". Không thay đổi hierarchy nếu source không có căn cứ.

## Inline code

Text trong backtick dùng cho identifier, SQL fragment, config key, command hoặc literal phải được giữ nguyên nội dung kỹ thuật.

## Code fence

Language tag phải phản ánh source nếu xác định được, ví dụ:

```text
sql
bash
text
json
```

Không tự đổi code sang format khác.

## Link

Giữ URL target. Có thể dịch link label nếu label là prose.

## Footnote/reference

Giữ numbering/meaning. Không biến reference thành prose mới hoặc bỏ reference vì extraction khó.

## Page header/footer

Không đưa running header/footer, page number hoặc watermark của PDF vào nội dung sách nếu chúng không phải content.
