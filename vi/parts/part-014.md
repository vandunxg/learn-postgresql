Lệnh này tạo một table có tên `temp_data` với cùng data structure và data như table `categories`:

```text
forumdb=> select * from temp_categories ;
 pk |              title            |              description
----+-----------------------+----------------------------
     1 | Database                   | Database related discussions
     2 | Unix                       | Unix and Linux discussions
     3 | Programming Languages | All about programming languages
     4 | C Language                 | Languages
     5 | Python Language            | Languages
     6 | A new discussion           | NULL
(6 rows)
```

## Cập nhật dữ liệu

Bây giờ hãy thử update một số data:

1. Nếu muốn thay đổi giá trị Unix thành Linux, bạn cần chạy statement sau:

   ```text
   forumdb=> update temp_categories set title='Linux' where pk = 2;
   UPDATE 1
   ```

   Statement này sẽ sửa giá trị Unix thành Linux trong field `title` cho mọi row của table `temp_categories` có `pk=2`, như sau:

   ```text
   forumdb=> select * from temp_categories where pk=2;
    pk | title |             description
   ----+-------+----------------------------
     2 | Linux | Unix and Linux discussions
   (1 row)
   ```

2. Nếu muốn thay đổi giá trị `title` của tất cả các dòng có giá trị `description` là Languages, bạn cần chạy statement sau:

   ```text
   forumdb=> update temp_categories set title = 'no title' where
   description = 'Languages';
   UPDATE 2
   ```

`UPDATE 2` có nghĩa là chỉ hai row đã được sửa đổi, như minh họa sau:

```text
forumdb=> select * from temp_categories order by description;
 pk |           title            |             description
----+----------------------------+----------------------------
  3 | Programming Languages | All about programming languages
  1 | Database                   | Database related discussions
  4 | no title                   | Languages
  5 | no title                   | Languages
  2 | Linux                      | Unix and Linux discussions
  6 | A new discussion           | NULL
(6 rows)
```

Bạn phải cẩn thận khi sử dụng command `UPDATE`. Nếu làm việc ở chế độ auto-commit, bạn không còn cơ hội quay lại sau khi update hoàn tất. Auto-commit là mặc định trong `psql`.

## Xóa dữ liệu

Trong phần này, chúng ta sẽ xem cách xóa data khỏi một table. Command cần dùng để xóa data là `delete`. Hãy bắt đầu:

1. Nếu muốn xóa tất cả record trong table `temp_categories` có `pk=5`, chúng ta phải thực hiện command sau:

   ```text
   forumdb=> delete from temp_categories where pk=5;
   DELETE 1
   ```

   Statement trên xóa tất cả record có `pk=5`. `DELETE 1` có nghĩa là một record đã bị xóa. Như bạn có thể thấy ở đây, row có giá trị `pk=5` không còn hiện diện trong `temp_categories`:

   ```text
   forumdb=>   select * from temp_categories where pk=5;
    pk | title | description
   ----+-------+-------------
   (0 rows)
   ```

2. Bây giờ, nếu muốn xóa tất cả row có giá trị `description` bằng `NULL`, chúng ta phải thực thi statement này:

   ```text
   forumdb=> delete from temp_categories where description is null;
   DELETE 1
   ```

Statement trên sử dụng command `DELETE` kết hợp với operator `IS NULL`.

3. Nếu muốn xóa tất cả record khỏi một table, bạn phải thực thi lệnh sau:

   ```text
   forumdb=> delete from temp_categories ;
   DELETE 4
   ```

> Hãy hết sức cẩn thận khi sử dụng command này - tất cả record hiện có trong table sẽ bị xóa!

Bây giờ table `temp_categories` trống, như minh họa sau:

```text
forumdb=> select * from temp_categories;
 pk | title | description
----+-------+-------------
(0 rows)
```

4. Nếu muốn nạp lại toàn bộ data từ table `categories` vào table `temp_categories`, chúng ta phải thực thi statement này:

   ```text
   forumdb=> insert into temp_categories select * from categories;
   INSERT 0 6
   ```

   Statement trên lấy tất cả value từ table `categories` và đưa chúng vào table `temp_categories`, như bạn có thể thấy ở đây:

   ```text
   forumdb=> select * from temp_categories order by description;
    pk |            title            |              description
   ----+----------------------------+----------------------------
     3 | Programming Languages | All about programming languages
     1 | Database                    | Database related discussions
     4 | C Language                  | Languages
     5 | Python Language             | Languages
     2 | Unix                        | Unix and Linux discussions
     6 | A new discussion            | NULL
   (6 rows)
   ```

5. Một cách khác để xóa data là sử dụng command `TRUNCATE`. Khi muốn xóa toàn bộ data khỏi một table mà không cung cấp điều kiện `where`, chúng ta có thể sử dụng command `TRUNCATE`:

   ```text
   forumdb=> truncate table temp_categories ;
   TRUNCATE TABLE
   ```

Command `TRUNCATE` xóa toàn bộ data trong một table. Như bạn có thể thấy, table `temp_categories` hiện đã trống:

```text
forumdb=> select * from temp_categories;
 pk | title | description
 ----+-------+-------------
(0 rows)
```

Dưới đây là một số thông tin quan trọng về command `TRUNCATE`:

- `TRUNCATE` xóa tất cả record trong một table, tương tự command `DELETE`.
- Trong command `TRUNCATE`, không thể sử dụng các điều kiện where.
- Command `TRUNCATE` xóa record nhanh hơn nhiều so với command `DELETE`.

## Tóm tắt

Chapter này đã giới thiệu cho bạn các statement SQL/PostgreSQL cơ bản và một số command SQL cơ bản. Bạn đã học cách tạo và xóa database, cách tạo và xóa table, các loại table hiện có, những statement cơ bản dùng để insert, modify và delete data, cùng với những query cơ bản đầu tiên trong số nhiều query mà bạn có thể dùng để query database.

Trong chapter tiếp theo, bạn sẽ học cách viết các query phức tạp hơn, liên quan đến nhiều table theo những cách khác nhau.

## Kiểm tra kiến thức

- Trên PostgreSQL 15 và PostgreSQL, có thể thực hiện DDL với tư cách một user thông thường không?

  Không, không thể. Xem phần PostgreSQL và public schema để biết thêm chi tiết.

- Command `psql` nào dùng để liệt kê tất cả database cùng với kích thước của chúng?

  ```text
  postgres=# \l+
  ```

  Xem phần Xác nhận kích thước database để biết thêm chi tiết.

- Nếu table được định nghĩa như sau:

  ```sql
  create table mytable (id integer,city_name varchar(60));
  ```

  Câu hỏi là, query sau có hiển thị tất cả record mà field `city_name` là null không?

  ```sql
  select * from mytable where city_name = '';
  ```

  Không. Query đúng là:

  ```sql
  select * from mytable where city_name is null;
  ```

  Xem phần Giá trị `NULL` để biết thêm chi tiết.

- Có thể tạo một database mới, lấy một database hiện có làm điểm bắt đầu không?

  Có. Chúng ta có thể sử dụng option `TEMPLATE`.

  Xem phần Tạo database mới từ một template đã sửa đổi để biết thêm chi tiết.

- Query sau có phải là cách tốt nhất để xóa tất cả record trong table có tên `mytable` không?

  ```sql
  delete from mytable;
  ```

  Không. Cách tốt nhất để xóa toàn bộ record trong một table là sử dụng statement `TRUNCATE`.

  Xem phần Xóa dữ liệu để biết thêm chi tiết.

## Tài liệu tham khảo

- Tài liệu chính thức về `CREATE DATABASE`: https://www.PostgreSQL.org/docs/current/sql-createdatabase.html
- Tài liệu chính thức về `CREATE TABLE`: https://www.PostgreSQL.org/docs/current/sql-createtable.html
- Tài liệu chính thức về `SELECT`: https://www.PostgreSQL.org/docs/current/sql-select.html
- Tài liệu chính thức về `INSERT`: https://www.PostgreSQL.org/docs/current/sql-insert.html
- Tài liệu chính thức về `DELETE`: https://www.PostgreSQL.org/docs/current/sql-delete.html
- Tài liệu chính thức về `UPDATE`: https://www.PostgreSQL.org/docs/current/sql-update.html
- Tài liệu chính thức về `TRUNCATE`: https://www.PostgreSQL.org/docs/current/sql-truncate.html

## Tìm hiểu thêm trên Discord

Để tham gia cộng đồng Discord dành cho cuốn sách này - nơi bạn có thể chia sẻ feedback, đặt câu hỏi cho tác giả và tìm hiểu về các bản phát hành mới - hãy quét QR code bên dưới:

https://discord.gg/jYWCjF6Tku

# 5. Advanced Statements

Trong chapter trước, chúng ta đã bắt đầu những bước đầu tiên với PostgreSQL. Trong chapter này, chúng ta sẽ phân tích ngôn ngữ SQL sâu hơn và viết các query phức tạp hơn. Chúng ta sẽ lại đề cập đến `SELECT`/`INSERT`/`UPDATE`, nhưng lần này sẽ sử dụng các option nâng cao xoay quanh chúng. Sau đó, chúng ta sẽ đi sâu vào join, common table expressions (CTEs) và merge.

Các chủ đề chúng ta sẽ thảo luận gồm:

- Khám phá statement `SELECT`
- Sử dụng `UPSERT` và `MERGE`
- Khám phá CTE

## Yêu cầu kỹ thuật

Trước khi bắt đầu, hãy nhớ khởi động Docker container có tên `chapter_05`, như minh họa dưới đây:

```text
$ bash run-pg-docker.sh chapter_05
postgres@learn_postgresql:~$ psql -U forum forumdb
```

## Khám phá statement `SELECT`

Như đã thấy trong chapter trước, chúng ta có thể sử dụng statement `SELECT` để filter dataset bằng điều kiện so sánh bằng. Tương tự, chúng ta có thể filter record bằng các điều kiện `>` hoặc `<`, như trong ví dụ sau:

```text
forumdb=> select * from categories where pk > 2;
    pk |         title            |                 description
----+-----------------------+---------------------------------
     3 | Programming Languages | All about programming languages
   (1 row)
```

Query trên trả về tất cả record có `pk > 2`.

Một điều kiện khác có thể dùng với statement `SELECT` là điều kiện like. Hãy xem ví dụ tiếp theo.

## Sử dụng clause like

Giả sử chúng ta muốn tìm tất cả record có giá trị field `title` bắt đầu bằng string Prog.

Để làm vậy, chúng ta phải sử dụng điều kiện like:

```text
forumdb=> \x
Expanded display is on.
forumdb=> select * from categories where title like 'Prog%';
-[ RECORD 1 ]--------------------------------
pk           | 3
title        | Programming Languages
description | All about programming languages
```

Như minh họa, query trên trả về tất cả record có `title` bắt đầu bằng string Prog. Tương tự, nếu muốn tìm tất cả record có title kết thúc bằng từ Languages, chúng ta sẽ viết như sau:

```text
forumdb=> select * from categories where title like '%Languages';
-[ RECORD 1 ]--------------------------------
pk           | 3
title        | Programming Languages
description | All about programming languages
```

Hai kiểu tìm kiếm này cũng có thể kết hợp. Ví dụ, nếu muốn tìm tất cả record chứa chuỗi con `discuss`, chúng ta sẽ viết như sau:

```text
forumdb=> \x
Expanded display is off
forumdb=> select * from categories where description like '%discuss%';
 pk |   title   |           description
----+----------+------------------------------
1 | Database | Database related discussions
2 | Unix       | Unix and Linux discussions
(2 rows)
```

Query ở đây sẽ trả về tất cả record mà `description` chứa string discuss.

Bây giờ hãy thử chạy query sau và xem điều gì xảy ra:

```text
forumdb=> select * from categories where title like 'prog%';
(0 rows)
```

Như có thể thấy, tìm kiếm không trả về kết quả nào. Điều này xảy ra vì tìm kiếm like phân biệt chữ hoa chữ thường.

Bây giờ hãy giới thiệu function `upper` (text). Function upper, khi nhận một input string, trả về chính string đó với tất cả ký tự được viết hoa, như sau:

```text
forumdb=> select upper('prog');
 upper
-------
 PROG
(1 row)
```

> Trong PostgreSQL, có thể gọi function mà không cần viết `FROM`. PostgreSQL không cần dummy table để thực thi câu lệnh `SELECT`. Nếu dùng Oracle DB, query tương tự phải được viết như sau: `select upper('prog') from DUAL;`.

Quay lại ví dụ trước, nếu muốn thực hiện tìm kiếm like không phân biệt chữ hoa chữ thường, chúng ta phải viết statement này:

```text
forumdb=> select * from categories where upper(description) like
'%DISCUSS%';
 pk |  title   |            description
----+----------+------------------------------
   1 | Database | Database related discussions
   2 | Unix       | Unix and Linux discussions
(2 rows)
```

Đến đây, chúng ta đã trình bày mọi cách sử dụng operator `like`.
