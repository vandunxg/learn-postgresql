# 00 - Core Rules

## Mục tiêu

Dịch toàn bộ nội dung sách Learn PostgreSQL từ PDF tiếng Anh sang Markdown tiếng Việt với độ trung thành cao về meaning và cấu trúc kỹ thuật.

## Source of truth

PDF gốc là authority tuyệt đối. Không dịch dựa trên trí nhớ, tài liệu PostgreSQL khác, blog, documentation mới hơn hoặc kiến thức hiện tại nếu source không nói như vậy.

Nếu sách sử dụng PostgreSQL version cũ, giữ đúng version/context lịch sử. Không tự modernize command, syntax, configuration hoặc recommendation.

## Không được làm

- Không tóm tắt.
- Không bỏ paragraph, note, warning, example, exercise, table, caption hoặc list.
- Không thêm giải thích riêng.
- Không tự sửa technical claim của tác giả.
- Không tự cập nhật syntax/API/configuration mới hơn.
- Không biến sách thành tutorial riêng của translator.
- Không suy đoán text bị mất chỉ từ context part trước/sau.

## Phải làm

- Đọc toàn bộ source part trước khi dịch.
- Dùng context part trước/sau tại boundary.
- Dịch toàn bộ prose thuộc ownership của current part.
- Bảo toàn code/SQL/commands/output/identifiers.
- Duy trì terminology nhất quán.
- Kiểm tra semantic equivalence trước khi đánh dấu hoàn thành.

## Thứ tự ưu tiên khi có xung đột

1. Source fidelity.
2. Technical correctness.
3. Không mất content.
4. Boundary/context continuity.
5. Terminology consistency.
6. Markdown structure.
7. Natural Vietnamese style.

Không hy sinh meaning chỉ để câu nghe mượt hơn.
