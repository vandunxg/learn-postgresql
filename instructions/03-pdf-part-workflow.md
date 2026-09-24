# 03 - PDF Part Workflow

## Split strategy cho khoảng 750 trang

Default: **10 trang/part**. Có thể dùng 8 trang nếu section dày code/table/query plan. Không nên tăng quá lớn chỉ để giảm số file vì worker cần xử lý extraction + semantic translation + structure reconstruction.

Với 750 trang:

- 10 trang/part -> khoảng 75 part;
- 8 trang/part -> khoảng 94 part.

Nếu có thể điều chỉnh boundary theo chapter/section mà không làm workflow phức tạp, ưu tiên semantic boundary. Nếu đã split cứng theo page thì dùng boundary-aware workflow, không cần split lại.

## Naming

Khuyến nghị zero-padded:

```text
part-001.pdf
part-002.pdf
...
part-075.pdf
```

Output:

```text
vi/parts/part-001.md
vi/parts/part-002.md
...
```

Sort bằng natural numeric order.

## Context cho worker N

Worker phải đọc:

1. instruction + glossary;
2. tối đa 2 trang cuối của part N-1;
3. toàn bộ part N;
4. tối đa 2 trang đầu của part N+1.

Neighbor là read-only context. Output chỉ chứa source content thuộc current part.

## Ownership

Một part có đúng một translation owner tại một thời điểm.

Worker không được:

- ghi file part khác;
- sửa glossary;
- sửa instruction;
- merge final book;
- copy overlap context vào output.

## Trước khi đánh dấu translated

Worker phải xác nhận:

- đã đọc toàn bộ current part;
- không bỏ prose/table/list/caption;
- code/SQL/output không bị sửa;
- boundary state đã được ghi metadata;
- output tồn tại và không rỗng.
