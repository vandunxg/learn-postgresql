```text
forumdb=> select pk,title,category from delete_posts ;
 pk | title | category
----+-------+----------
(0 rows)
```

2. Bây giờ giả sử chúng ta muốn xóa một số record khỏi table `posts`, đồng thời muốn tất cả record đã xóa khỏi table `t_posts` được chèn vào table `delete_posts`. Để đạt được mục tiêu này, chúng ta phải sử dụng CTE như sau:

```text
forumdb=> with del_posts as (
     delete from t_posts
    where category in (select pk from categories where title
='Database Discussions')
    returning *)
    insert into delete_posts select * from del_posts;
    INSERT 0 2
```

Query ở đây xóa tất cả record khỏi table `t_posts` có category là `'Database'`, rồi trong cùng transaction chèn tất cả record đã xóa vào table `delete_posts`, như chúng ta có thể thấy ở đây:

```text
forumdb=> select pk,title,category from t_posts ;
 pk |                title                 | category
----+------------------------------+----------
  3 | A view of      Data types in C++ |              3
(1 row)


forumdb=> select pk,title,category from delete_posts ;
 pk |           title           | category
----+---------------------+----------
  1 | Indexing PostgreSQL |                1
  2 | Indexing Mysql            |          1
(2 rows)
```

3. Bây giờ hãy thử một ví dụ khác bằng cách quay lại scenario ban đầu:

```text
forumdb=> drop table if exists t_posts;
DROP TABLE
```

```text
forumdb=> create temp table t_posts as select * from posts;
SELECT 3
```

4. Như đã làm trước đó, hãy tạo một table mới tên là `inserted_post` với cùng data structure như table `posts`:

```text
forumdb=> create table inserted_posts as select * from posts limit
0;
SELECT 0
```

5. Bây giờ giả sử chúng ta muốn thực hiện một SQL query di chuyển, trong cùng transaction, tất cả record hiện có trong table `t_posts` sang table `inserted_posts`. Query sẽ như sau:

```text
forumdb=> with ins_posts as ( insert into inserted_posts select *
from t_posts returning pk) delete from t_posts where pk in (select
pk from ins_posts);
DELETE 3
```

Như chúng ta có thể thấy từ các result, query đã đạt được mục tiêu:

```text
forumdb=> select pk,title,category from t_posts ;
 pk | title | category
----+-------+----------
(0 rows)


forumdb=> select pk,title,category from inserted_posts ;
 pk |                title                | category
----+------------------------------+----------
     1 | Indexing PostgreSQL              |          1
     2 | Indexing Mysql                   |          1
     3 | A view of   Data types in C++ |             3
(3 rows)
```

## Query đệ quy

Trong PostgreSQL, có thể tạo các query đệ quy. Query đệ quy được dùng trong graph database và trong nhiều trường hợp sử dụng phổ biến, chẳng hạn như query các table biểu diễn menu của website.

Recursive CTE giúp tạo query đệ quy trong PostgreSQL.

## Recursive CTEs

Một recursive CTE là một construct đặc biệt cho phép một auxiliary statement tham chiếu đến chính nó và vì vậy join chính nó vào các result đã được tính trước đó. Điều này đặc biệt hữu ích khi chúng ta cần join một table với số lần không biết trước, thường là để “explode” một flat tree structure. Giải pháp truyền thống sẽ cần một dạng iteration nào đó, có lẽ thông qua một cursor lặp qua toàn bộ resultset, mỗi lần một tuple. Tuy nhiên, với recursive CTE, chúng ta có thể sử dụng một approach sạch và đơn giản hơn nhiều. Một recursive CTE được tạo bởi một auxiliary statement xây dựng dựa trên các thành phần sau:

- Một non-recursive statement, hoạt động như một bootstrap statement và được thực thi khi auxiliary term được đánh giá lần đầu.
- Một recursive statement, có thể tham chiếu đến bootstrap statement hoặc chính nó.

Hai phần này được nối với nhau bằng một predicate `UNION`. Ví dụ, hãy chèn một record mới vào table `tag` rồi xem bên trong:

```text
forumdb=>    insert into tags (tag,parent) values ('PostgreSQL',1);
INSERT 0 1

forumdb=>    select * from tags order by pk;
 pk |          tag         | parent
----+-------------------+--------
  1 | Database             |
  2 | Operating Systems |
  3 | PostgreSQL           |        1
(3 rows)
```

Bây giờ chúng ta muốn “explode” flat tree structure và lần theo quan hệ giữa parent và child bằng field `parent` của table `tags`. Vì vậy, chúng ta muốn result có dạng như sau:

```text
level   |            tag
-------+------------------------
     1 | Database
     1 | Operating Systems
     2 | Database -> PostgreSQL
```

Để đạt được mục tiêu này, chúng ta phải thực hiện như sau:

```sql
forumdb=> WITH RECURSIVE tags_tree AS (
 -- non recursive statement
SELECT tag, pk, 1 AS level
FROM tags WHERE parent IS NULL
UNION
-- recursive statement
SELECT tt.tag|| ' -> ' || ct.tag, ct.pk
, tt.level + 1
FROM tags ct
JOIN tags_tree tt ON tt.pk = ct.parent
)
SELECT level,tag FROM tags_tree
order by level;
 level |                tag
-------+------------------------
       1 | Database
       1 | Operating Systems
       2 | Database -> PostgreSQL
(3 rows)
```

> Khi sử dụng CTE, điều quan trọng là phải tránh các vòng lặp vô hạn. Điều này có thể xảy ra nếu đệ quy không kết thúc đúng cách.

Như vậy, chúng ta đã học cách sử dụng CTE để thao tác với các table.

## Tóm tắt

Hy vọng chapter này mang đến nhiều ý tưởng thú vị cho developer và DBA. Trong chapter này, chúng ta đã nói về các query phức tạp; sau đó xem statement `SELECT` và cách sử dụng các clause `LIKE`, `ILIKE`, `DISTINCT`, `OFFSET`, `LIMIT`, `IN` và `NOT IN`. Tiếp theo, chúng ta bắt đầu nói về aggregate thông qua các clause `GROUP BY` và `HAVING`, đồng thời giới thiệu một số aggregate function như `SUM()`, `COUNT()`, `AVG()`, `MIN()` và `MAX()`.

Sau đó, chúng ta đã nói sâu về subquery và join. Một nhóm chủ đề rất thú vị khác được đề cập trong chapter này là các query `UNION`, `EXCEPT` và `INTERSECT`. Cuối cùng, bằng cách xem xét các option nâng cao của các instruction `INSERT`, `DELETE`, `UPDATE` và `MERGE`, cũng như đề cập đến CTE, chúng ta đã thấy được sức mạnh của ngôn ngữ SQL do PostgreSQL cung cấp.

Xét về khái niệm aggregate, trong chapter tiếp theo chúng ta sẽ thấy một cách mới để tạo aggregate bằng window function. Thông qua window function, chúng ta sẽ thấy rằng có thể tạo tất cả aggregate và aggregate function được mô tả trong chapter này, nhưng cũng có tùy chọn tạo các aggregate function mới.

## Kiểm tra kiến thức

- Nếu chạy query này và dữ liệu trên table có tên `mytable` không thay đổi, chúng ta có luôn nhận được cùng một result không?

  ```sql
  select * from mytable
  ```

  Không, vì thứ tự của dữ liệu có thể khác nhau.

  Xem section *Khám phá statement SELECT* để biết thêm chi tiết.

- Có thể chỉ nhận được 3 record làm result của một query không?

  Có, có thể dùng clause `LIMIT`.

  Xem section *Sử dụng limit và offset* để biết thêm chi tiết.

- Nếu có 2 table: table A có 3 record với một field `id` là primary key, và table B có 2 record với một field `id` là primary key, chúng ta phải dùng loại join nào để match tất cả record có cùng ID trên table A và table B?

  Chúng ta phải sử dụng query inner join:

  ```sql
  select tableA.id from tableA inner join tableB using(id)
  ```

  Xem section *Sử dụng INNER JOIN* để biết thêm chi tiết.

- Nếu có 2 table: table A có 3 record với một field `id` là primary key, và table B có 2 record với một field `id` là primary key, sử dụng clause `NOT EXISTS`, làm thế nào viết một query hiển thị tất cả record có trong table A nhưng không có trong table B?

  ```sql
  select * from tableA where not exists (select 1 from tableB where
  tableA.id=tableB.id)
  ```

  Xem section *Subquery và điều kiện EXISTS/NOT EXISTS* để biết thêm chi tiết.

- PostgreSQL 11 và PostgreSQL 16 có cùng cách sử dụng CTE không?

  Không. PostgreSQL 11 luôn materialize dữ liệu. PostgreSQL 16, nếu không được chỉ định, chỉ materialize dữ liệu khi CTE được gọi từ hai lần trở lên bên trong query.

  Xem section *Subquery và điều kiện EXISTS/NOT EXISTS* và *Khám phá CTE* để biết thêm chi tiết.

## Tài liệu tham khảo

- Tài liệu chính thức về subquery expression: https://www.postgresql.org/docs/current/functions-subquery.html
- Tài liệu chính thức về join: https://www.postgresql.org/docs/current/tutorial-join.html
- Tài liệu chính thức về CTE: https://www.postgresql.org/docs/current/queries-with.html
- Tài liệu chính thức về `MERGE`: https://www.postgresql.org/docs/current/sql-merge.html
- `MERGE` ANSI 2003 SQL: https://www.w3resource.com/sql/sql-syntax.php

## Tìm hiểu thêm trên Discord

Để tham gia cộng đồng Discord dành cho cuốn sách này, nơi bạn có thể chia sẻ feedback, đặt câu hỏi cho tác giả và tìm hiểu về các bản phát hành mới, hãy dùng QR code bên dưới:

https://discord.gg/jYWCjF6Tku

# 6. Window Functions

Trong chapter trước, chúng ta đã nói về aggregate. Trong chapter này, chúng ta sẽ thảo luận sâu hơn về một cách khác để tạo aggregate: window function. Tài liệu chính thức (https://www.postgresql.org/docs/current/tutorial-window.html) mô tả window function như sau:

> Window function thực hiện một phép tính trên một tập các row của table có liên quan với row hiện tại theo một cách nào đó. Điều này tương tự loại phép tính có thể thực hiện bằng aggregate function. Tuy nhiên, window function không khiến các row được nhóm lại thành một output row duy nhất như các lời gọi aggregate không phải window function. Thay vào đó, các row vẫn giữ identity riêng của chúng. Ở hậu trường, window function có thể truy cập không chỉ row hiện tại của query result.

Trong chapter này, chúng ta sẽ nói về window function, chúng là gì và có thể sử dụng chúng như thế nào để cải thiện performance của query.

Các chủ đề sau sẽ được đề cập trong chapter này:

- Sử dụng các statement window function cơ bản
- Sử dụng các statement window function nâng cao

## Technical requirements

Trước khi bắt đầu, hãy nhớ khởi động Docker container có tên `chapter_06` như dưới đây:

```bash
$ bash run-pg-docker.sh chapter_06
```

## Sử dụng các statement window function cơ bản

Như đã thấy trong chapter trước, các aggregate function hoạt động theo cách sau:

![Hình 6.1: Aggregation bằng GROUP BY tiêu chuẩn](../assets/part-019-figure-6-1-000.jpg)

*Hình 6.1: Aggregation bằng GROUP BY tiêu chuẩn*

Dữ liệu trước tiên được sort rồi aggregate; sau đó dữ liệu được flatten thông qua aggregation. Đây là điều xảy ra khi chúng ta thực thi statement sau, sau khi kết nối tới database `forumdb` bằng user `forum`:

```text
forumdb=> select category,count(*) from posts group by category order by
category;
 category | count
----------+-------
        1 |     2
        3 |     1
(2 rows)
```

Ngoài ra, chúng ta có thể chọn sử dụng window function bằng cách thực thi statement sau:

```text
forumdb=> select category, count(*) over (partition by category) from
posts order by category;
 category | count
----------+-------
        1 |       2
        1 |       2
        3 |       1
(3 rows)
```

Window function tạo aggregate mà không flatten dữ liệu thành một row duy nhất. Tuy nhiên, chúng replicate aggregate cho tất cả row mà các group function tham chiếu đến. Behavior của PostgreSQL được mô tả trong diagram sau:

![Hình 6.2: Aggregation bằng window function](../assets/part-019-figure-6-2-000.jpg)

*Hình 6.2: Aggregation bằng window function*

Đó là lý do keyword `distinct` phải được thêm vào query trước đó nếu chúng ta muốn nhận được cùng result như khi dùng query `GROUP BY` kinh điển.

## Sử dụng function PARTITION BY và clause WINDOW

Bây giờ hãy chạy một số query cơ bản sử dụng window function. Giả sử chúng ta muốn sử dụng hai clause `over`. Ví dụ, nếu trên một column chúng ta muốn đếm các row liên quan đến category, còn trên một column khác muốn đếm tổng số column, thì chúng ta phải chạy statement sau:

```text
forumdb=> select category, count(*) over (partition by category),count(*)
over () from posts order by category;
 category | count | count
----------+-------+-------
        1 |       2 |       3
```
