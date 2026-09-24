# Requirements: Antora Documentation Page UI từ HTML Template V3

## 1. Mục tiêu

Chuyển giao diện và interaction trong `sample-postgresql-theme-v3.html` thành UI template thực tế cho website tài liệu **Learn PostgreSQL** sử dụng:

- AsciiDoc
- Antora
- Valentus theme làm base
- Content nằm riêng trong `content/`
- UI/template nằm riêng trong `ui/`

`sample-postgresql-theme-v3.html` chỉ là **reference về layout, màu sắc và behavior**.

Không hardcode nội dung Chapter 7, ACID, MVCC, Isolation Level hoặc navigation của file sample vào template production.

Mỗi file `.adoc` phải có thể render thành một documentation page theo cùng layout.

---

## 2. Boundary bắt buộc

Cấu trúc trách nhiệm:

```text
content/
  antora.yml
  modules/
    ROOT/
      pages/
      images/
      examples/
      partials/
      nav.adoc

ui/
  src/
    css/
    js/
    layouts/
    partials/
    helpers/

playbook/
  antora-playbook.yml
```

### `content/`

Chỉ chứa nội dung sách:

- AsciiDoc
- images
- examples
- partials
- navigation

Không chứa CSS/JS/template frontend.

### `ui/`

Chỉ chứa:

- layout
- partial template
- CSS
- JavaScript
- icon
- behavior của reader

Template không được chứa nội dung chapter cụ thể.

---

## 3. Layout chính

Desktop phải có cấu trúc 3 cột giống V3:

```text
┌───────────────────────────────────────────────────────────────┐
│ Logo / Book       Search          Highlight      Dark mode   │
├────────────────┬─────────────────────────────┬────────────────┤
│                │                             │                │
│ Book navigation│ Documentation content       │ On this page   │
│                │                             │                │
│ Part           │ Chapter title               │ Section A      │
│ Chapter        │ prose                       │ Section B      │
│ Section        │ code                        │ Section C      │
│                │ table                       │                │
│                │ figure                      │                │
│                │                             │                │
└────────────────┴─────────────────────────────┴────────────────┘
```

Kích thước tham khảo:

```text
Header: 64px

Left sidebar:
220px - 280px

Article:
fluid
prose width tối ưu khoảng 760px - 850px

Right TOC:
khoảng 220px - 250px
```

Không để article prose trải toàn bộ màn hình lớn.

Code block và table có thể rộng hơn prose khi cần.

---

## 4. Header

Header phải sticky.

Bao gồm:

```text
Book identity
Search
Highlight mode
Dark / Light mode
Mobile navigation
```

Book title phải lấy từ Antora site/component metadata khi có thể, không hardcode `Learn PostgreSQL` vào layout dùng chung.

---

## 5. Left navigation

Sidebar bên trái phải được sinh từ Antora navigation.

Nguồn chính:

```text
nav.adoc
```

Hierarchy:

```text
Part
  Chapter
    Section
```

Yêu cầu:

- chapter hiện tại được active
- section hiện tại được highlight nhẹ
- sidebar sticky
- sidebar có scroll độc lập
- không reload mất vị trí scroll sidebar nếu có thể
- hỗ trợ navigation nhiều chapter
- không hardcode tên chapter
- không phụ thuộc tên file `part-001`, `part-002`

URL cuối cùng phải dựa trên semantic page name.

Ví dụ:

```text
/transactions/mvcc/
/query-planning/
/indexes/btree/
```

thay vì:

```text
/part-035/
```

---

## 6. Main article

Article phải render trực tiếp nội dung AsciiDoc do Antora cung cấp.

Hỗ trợ đầy đủ:

```text
h1-h6
paragraph
strong
emphasis
inline code
code block
table
image
figure
caption
list
blockquote
xref
footnote
admonition
```

Typography ưu tiên đọc lâu:

```text
font-size body: khoảng 17px
line-height: khoảng 1.65 - 1.75
```

Font ưu tiên:

```text
Body/UI:
Source Sans 3

Code:
JetBrains Mono
```

Nếu không bundle font thì phải có system fallback hợp lý.

---

## 7. Page heading

Đầu mỗi documentation page cần hiển thị semantic hierarchy khi có dữ liệu:

```text
Chapter 7

Transactions & MVCC

Intro / lead paragraph
```

Không giả định mọi page đều là chapter.

Page cũng có thể là:

```text
Chapter
Section
Appendix
Introduction
Reference page
```

Template phải generic.

---

## 8. Right-side "On this page"

TOC bên phải phải được sinh tự động từ headings của page.

Không hardcode anchor.

Ví dụ AsciiDoc:

```asciidoc
== ACID

== MVCC

== Isolation Levels
```

phải sinh:

```text
On this page

ACID
MVCC
Isolation Levels
```

Behavior:

- sticky
- click smooth scroll
- section đang đọc tự active
- active item dùng PostgreSQL blue
- sử dụng `IntersectionObserver`
- heading cần có `scroll-margin-top` phù hợp sticky header

Desktop hiển thị.

Tablet/mobile có thể ẩn.

---

## 9. Color system

Sử dụng semantic CSS variables.

Light mode:

```text
background       #F7F7F5
surface          #FCFCFA
secondary        #F0F1EE

text             #242629
muted            #666B70
border           #E1E3DF

PostgreSQL blue  #336791
accent dark      #285476
link             #2F628C

code background  #202428
code text        #E8EDF1
```

Dark mode:

```text
background       #1B1D1E
surface          #222426
secondary        #292C2F

text             #D8D9DA
muted            #A6A8AB
border           #36393C

accent           #6EA6D7
link             #79AEDD

code background  #151719
```

Tránh:

```text
#FFFFFF + #000000
```

làm combination chính cho long-reading mode.

---

## 10. Dark mode

Có nút chuyển:

```text
Light ↔ Dark
```

Theme preference phải lưu bằng:

```text
localStorage
```

Key phải có namespace rõ ràng.

Ví dụ:

```text
learn-postgresql:theme
```

Nếu chưa có preference, có thể ưu tiên:

```text
prefers-color-scheme
```

Không flash sai theme rõ rệt khi reload nếu có thể tránh.

---

## 11. Code block

AsciiDoc source block:

```asciidoc
[source,sql]
----
SELECT *
FROM users;
----
```

phải render thành code block phù hợp giao diện V3.

Yêu cầu:

```text
language label
syntax highlighting
Copy button
horizontal overflow
code font riêng
dark background
```

Copy button:

```text
Copy
→
Copied
```

Sau khoảng 1-2 giây trở lại `Copy`.

Nếu clipboard API thất bại phải fail gracefully.

Không mutate code content.

---

## 12. Tables

AsciiDoc table phải:

- responsive
- không phá layout
- horizontal scroll nếu quá rộng
- header rõ
- border nhẹ
- dark mode tương thích
- phù hợp SQL result table

Không ép table co đến mức text/code không đọc được.

---

## 13. Admonitions

Hỗ trợ tối thiểu:

```text
NOTE
TIP
WARNING
IMPORTANT
CAUTION
```

Visual phải nhẹ, không dùng màu saturation quá mạnh.

Reference:

```text
NOTE      blue
TIP       green
WARNING   amber
IMPORTANT red nhẹ
```

Phải support dark mode.

---

## 14. Previous / Next page

Cuối page phải có navigation:

```text
← Previous
Next →
```

Tên page lấy từ Antora navigation model.

Không hardcode chapter.

Nếu là page đầu hoặc cuối thì chỉ hiển thị direction tồn tại.

---

# 15. Reading progress + Back to top

Giữ behavior của V3.

Một floating button duy nhất ở góc phải dưới.

Button có:

```text
circular progress ring
↑ icon
```

Progress ring thể hiện phần trăm page đã scroll.

Tooltip:

```text
Đã đọc 64% · Về đầu trang
```

Click:

```text
smooth scroll → top
```

ARIA label phải cập nhật tương ứng:

```text
Tiến độ đọc 64 phần trăm, về đầu trang
```

Có thể giữ thin progress line ở trên cùng giống V3.

---

# 16. Highlight mode

Giữ feature quan trọng của V3.

Header có icon Highlight.

Default:

```text
Highlight mode OFF
```

Click:

```text
Highlight mode ON
```

Khi bật mode:

- kéo chuột chọn text
- selection được chuyển thành persistent highlight
- có thể highlight nhiều đoạn liên tiếp
- click highlight hiện tại để xóa
- có trạng thái trực quan cho biết Highlight mode đang bật

Highlight color:

Light:

```text
#FFF1A8
```

Dark:

```text
#6B5A1C
```

Highlight chỉ được áp dụng lên text user-readable.

Không được highlight:

```text
button
input
textarea
select
script
style
```

---

## 17. Persistent highlight

Không copy cách prototype V3 lưu:

```js
readingArea.innerHTML
```

vào production.

Production phải lưu highlight dưới dạng structured data.

Ví dụ concept:

```text
pageKey
text/start/end/context
```

Mỗi page phải có highlight độc lập.

Storage key phải dựa trên URL hoặc Antora page identity.

Ví dụ:

```text
learn-postgresql:highlights:<page-id>
```

Reload page phải restore đúng highlights.

Highlight của:

```text
transactions.adoc
```

không được xuất hiện ở:

```text
indexes.adoc
```

Không persist toàn bộ generated HTML vào localStorage.

---

## 18. Reading position

Nên hỗ trợ lưu reading position riêng theo page.

Concept:

```text
learn-postgresql:reading-position:<page-id>
```

Mục tiêu:

khi quay lại chapter đang đọc, có thể restore gần vị trí trước đó.

Không bắt buộc auto-scroll ngay ở version đầu nếu gây UX khó chịu.

Nhưng architecture không được cản việc thêm feature này.

---

## 19. Highlight vs Antora generated content

Highlight là client-side enhancement.

Nó không được:

- sửa `.adoc`
- sửa Antora source
- thay đổi generated navigation model
- tạo dependency giữa content và UI

AsciiDoc vẫn là source of truth.

---

## 20. Search

Header có search field.

Template phải dành interface cho Antora-compatible search.

Không cần tự viết search engine nếu project chưa chọn implementation.

UI phải cho phép sau này tích hợp:

```text
Lunr
Algolia
Pagefind
Antora search extension
```

Search không được hardcode sample data.

---

## 21. Responsive behavior

Desktop:

```text
Left sidebar + article + right TOC
```

Tablet:

```text
Left sidebar + article
Right TOC có thể ẩn
```

Mobile:

```text
Article full width
Sidebar đóng mặc định
Hamburger mở sidebar drawer
Right TOC ẩn hoặc chuyển vào page navigation
```

Target tối thiểu:

```text
320px
768px
1024px
1440px
```

Không horizontal scroll toàn page.

Chỉ code/table được phép horizontal scroll khi cần.

---

## 22. Accessibility

Tối thiểu:

- semantic HTML
- một `h1` chính cho page
- heading hierarchy đúng
- keyboard navigation
- focus-visible
- ARIA label cho icon-only button
- `aria-pressed` cho Highlight mode
- đủ color contrast
- table có semantic structure
- copy button keyboard accessible
- mobile menu keyboard accessible
- progress/back-to-top button có accessible name

Không dùng `div onclick` nếu có thể dùng `button`.

---

## 23. Performance

Không thêm framework frontend nặng chỉ để implement các interaction này.

Ưu tiên:

```text
HTML generated bởi Antora
CSS
Vanilla JavaScript
```

Không yêu cầu React/Vue.

JavaScript phải progressive enhancement:

nếu JS fail thì người dùng vẫn đọc/navigate docs được.

---

## 24. Antora integration

Template phải sử dụng Antora page model thay vì hardcode.

Dữ liệu cần lấy động gồm tối thiểu:

```text
site title
component title
page title
page content
navigation
breadcrumbs nếu có
page TOC
previous page
next page
canonical/meta information khi có
```

UI phải hoạt động cho tất cả `.adoc` trong:

```text
content/modules/ROOT/pages/
```

Không thiết kế riêng cho một chapter.

---

## 25. Template structure

Không viết toàn bộ page trong một file lớn.

Tách responsibility theo hướng:

```text
ui/src/
  layouts/
    default.hbs

  partials/
    header.hbs
    sidebar.hbs
    toc.hbs
    article.hbs
    pagination.hbs
    reader-tools.hbs

  css/
    tokens.css
    base.css
    layout.css
    article.css
    code.css
    table.css
    admonition.css
    reader.css
    responsive.css

  js/
    theme.js
    sidebar.js
    toc.js
    copy-code.js
    reading-progress.js
    highlight.js
```

Tên thực tế có thể điều chỉnh theo conventions của Valentus/Antora UI đang dùng.

Không tạo abstraction không cần thiết.

---

## 26. Không làm trong phase này

Phase hiện tại chỉ xây docs template.

Không làm:

```text
login
account
cloud highlight sync
database
backend API
comment system
annotation sharing
AI assistant
book editor
WYSIWYG
analytics dashboard
```

Không sửa nội dung AsciiDoc để phục vụ layout.

Không build SPA.

---

## 27. Source reference

Trước khi implement phải đọc:

```text
sample-postgresql-theme-v3.html
```

và dùng nó làm reference cho:

- visual hierarchy
- spacing
- palette
- header
- 3-column layout
- sticky sidebar
- right TOC
- code styling
- tables
- admonitions
- dark mode
- reading progress
- back-to-top
- Highlight mode

Không copy nguyên sample thành production template.

Phải chuyển nó thành reusable Antora UI components.

---

## 28. Acceptance criteria

Implementation được coi là đạt khi:

1. Một `.adoc` bất kỳ render thành docs page đúng template.
2. Navigation bên trái được sinh từ `nav.adoc`.
3. TOC bên phải được sinh từ headings thật của page.
4. Không còn chapter/sample content hardcode trong UI.
5. Light/dark mode hoạt động và persist.
6. Code block có Copy.
7. Table không phá responsive layout.
8. NOTE/TIP/WARNING render đúng.
9. Section hiện tại được active khi scroll.
10. Reading progress hoạt động.
11. Floating progress/back-to-top hoạt động.
12. Highlight mode hoạt động trên nhiều page độc lập.
13. Highlight persist sau reload mà không lưu toàn bộ `innerHTML`.
14. Previous/Next lấy từ Antora navigation.
15. Mobile navigation hoạt động.
16. Build Antora thành công.
17. Console không có JavaScript error.
18. Content và UI vẫn tách biệt hoàn toàn.

---

## 29. Verification bắt buộc

Sau implementation, AI agent phải:

```text
build UI bundle
build Antora site
mở generated site
test desktop
test mobile
test dark mode
test sidebar
test TOC active state
test copy SQL
test progress
test back-to-top
test create/remove highlight
reload và kiểm tra highlight persistence
navigate sang page khác và kiểm tra highlight isolation
kiểm tra browser console
```

Không được kết luận hoàn thành chỉ vì build thành công.

---

## 30. Nguyên tắc cuối

`sample-postgresql-theme-v3.html` là prototype.

Production implementation phải đạt:

```text
prototype behavior
+
Antora dynamic content
+
reusable templates
+
multi-page support
+
persistent per-page reader state
+
responsive
+
accessible
```

Giữ implementation đơn giản nhất có thể.

Ưu tiên:

```text
Antora + Valentus
Handlebars templates
CSS
Vanilla JavaScript
```

Không thay đổi content architecture và không viết frontend framework nếu không thực sự cần thiết.
