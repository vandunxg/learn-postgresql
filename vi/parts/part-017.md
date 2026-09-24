4. Nếu muốn có các phép nối left và right giữa các table `new_posts` và `category`, chúng ta phải dùng full outer join và viết như sau:

```text
forumdb=> select c.pk,c.title,p.pk,p.title from categories c full
outer join new_posts p on p.category=c.pk;
   pk     |         title                |     pk        |     title
--------+-----------------------+--------+---------------
       1 | Database                     |          1 | Indexing PostgreSQL
       1 | Database                     |          2 | Indexing Mysql
       3 | Programming Languages |                 3 | Data types in C++
(NULL) | (NULL)                         |          6 | A new Book
       2 | Unix                       | (NULL) | (NULL)
       5 | Database                   | (NULL) | (NULL)
       4 | New Category                 | (NULL) | (NULL)
(7 rows)
```

Biểu đồ này minh họa cách full outer join hoạt động:

![Hình 5.5: Một full outer join](../assets/part-017-figure-5-5-000.jpg)

*Hình 5.5: Một full outer join*

Một câu hỏi cần xem xét là: **full join khác cross join, mà chúng ta đã thấy ở phần đầu của section về join, như thế nào?**

Full outer join khác cross join vì cross join tạo ra Cartesian product từ tất cả record hiện diện trong các table.

Ví dụ, với một cross join sử dụng cùng data như full join trước đó, chúng ta sẽ nhận được result sau:

```text
forumdb=> select c.pk,c.title,p.pk,p.title from categories c cross join
new_posts p;
 pk |            title           | pk |               title
----+-----------------------+----+---------------------
  1 | Database                   |   1 | Indexing PostgreSQL
  2 | Unix                       |   1 | Indexing PostgreSQL
  3 | Programming Languages |        1 | Indexing PostgreSQL
  4 | New Category               |   1 | Indexing PostgreSQL
  5 | Database                   |   1 | Indexing PostgreSQL
  1 | Database                   |   2 | Indexing Mysql
  2 | Unix                       |   2 | Indexing Mysql
  3 | Programming Languages |        2 | Indexing Mysql
  4 | New Category               |   2 | Indexing Mysql
  5 | Database                   |   2 | Indexing Mysql
  1 | Database                   |   3 | Data types in C++
  2 | Unix                       |   3 | Data types in C++
  3 | Programming Languages |        3 | Data types in C++
  4 | New Category               |   3 | Data types in C++
  5 | Database                   |   3 | Data types in C++
  1 | Database                   |   6 | A new Book
  2 | Unix                       |   6 | A new Book
  3 | Programming Languages |        6 | A new Book
  4 | New Category               |   6 | A new Book
  5 | Database                   |   6 | A new Book
(20 rows)
```

## Sử dụng LATERAL JOIN

Lateral join là một kiểu join trong SQL cho phép bạn join một table với một subquery, trong đó subquery được chạy cho từng row của main table. Subquery được thực thi trước khi các row được join, và result được dùng để join các row. Với join mode này, bạn có thể dùng thông tin từ một table để filter hoặc process data từ table khác.

Hãy thêm một field có tên `likes` vào table `posts` và insert một số data vào field này:

```text
forumdb=> alter table posts add likes integer default 0;
ALTER TABLE
forumdb=> update posts set likes = 3 where title like 'Indexing%';
UPDATE 2
```

Tình trạng hiện tại là:

```text
forumdb=> select title,likes from posts order by likes ;
          title          | likes
---------------------+-------
 Data types in C++     |      0
 Indexing PostgreSQL |        3
 Indexing Mysql        |      3
(3 rows)
```

Bây giờ, giả sử chúng ta muốn search tất cả user có post với số lượt like lớn hơn 2; query giải quyết vấn đề này là:

```text
forumdb=> select u.* from users u where exists (select 1 from posts p
where u.pk=p.author and likes > 2 ) ;
 pk |     username   | gecos |           email
----+--------------+-------+---------------------
  1 | luca_ferrari |          | luca@pgtraining.com
(1 row)
```

Giả sử bây giờ chúng ta cũng muốn có giá trị của field `likes`. Một cách đơn giản để giải quyết vấn đề này là dùng lateral join:

```text
forumdb=> select u.username,q.* from users u join lateral (select author,
title,likes from posts p where u.pk=p.author and likes > 2 ) as q on true;
   username     | author |          title            | likes
--------------+--------+---------------------+-------
 luca_ferrari |        1 | Indexing PostgreSQL |           3
 luca_ferrari |        1 | Indexing Mysql            |     3
(2 rows)
```

Query này rất giống query `EXISTS`, ngoại trừ việc trong main query, chúng ta có thể lấy tất cả value nằm trong subquery và dùng chúng ở phần chính của query.

## Aggregate functions

Aggregate function thực hiện một phép tính trên một tập row và trả về một row duy nhất. PostgreSQL cung cấp tất cả aggregate function chuẩn của SQL:

- `AVG()`: Function này trả về giá trị trung bình.
- `COUNT()`: Function này trả về số lượng value.
- `MAX()`: Function này trả về value lớn nhất.
- `MIN()`: Function này trả về value nhỏ nhất.
- `SUM()`: Function này trả về tổng các value.

Aggregate function được dùng cùng với `group by` clause. Một `group by` clause chia resultset thành các group row, và aggregate function thực hiện phép tính trên chúng. Ví dụ, nếu muốn đếm có bao nhiêu record trong mỗi category, trước tiên PostgreSQL group data rồi đếm data. Biểu đồ sau minh họa process này:

![Hình 5.6: Group by aggregation](../assets/part-017-figure-5-6-000.jpg)

*Hình 5.6: Group by aggregation*

Biểu đồ này minh họa rằng trước khi group data, PostgreSQL sort data internally. Vì vậy, chúng ta phải nhớ rằng một grouping operation luôn bao hàm một ordering operation; điều này sẽ rõ hơn khi chúng ta thảo luận về performance sau này.

Bây giờ khi đã hiểu theory, hãy xem cách thực sự tính số record trong mỗi category:

```text
forumdb=> select category,count(*) from posts group by category;
 category | count
----------+-------
       3 |       1
       1 |       2
(2 rows)
```

Query trước đó đếm số record trong mỗi category của table `posts`.

Một cách khác để viết cùng query là như sau:

```text
forumdb=> select category,count(*) from posts group by 1;
 category | count
----------+-------
       3 |       1
       1 |       2
(2 rows)
```

> Trong PostgreSQL, chúng ta có thể viết điều kiện `group by` bằng tên field hoặc vị trí của chúng trong query.

Một condition khác mà chúng ta có thể dùng là `having` condition. Giả sử chúng ta muốn đếm số record trong mỗi category có count lớn hơn 2. Để làm điều đó, chúng ta phải thêm `having` condition sau `group by` condition, bằng cách viết như sau:

```text
forumdb=> select category,count(*) from posts group by category having
count(*) > 1;
 category | count
----------+-------
       1 |       2
(1 row)
```

Tương tự, chúng ta có thể viết:

```text
forumdb=> select category,count(*) from posts group by 1 having count(*) >
1;
 category | count
----------+-------
       1 |       2
(1 row)
```

Bây giờ hãy xem các aggregate function hoạt động thế nào khi chúng ta thêm alias. Hãy quay lại query đầu tiên và viết như sau:

```text
forumdb=> select category,count(*) as category_count from posts group by
category;
 category | category_count
----------+----------------
       3 |                 1
       1 |                 2
(2 rows)
```

Như có thể thấy ở đây, chúng ta có thể dùng alias trên aggregate function.

Tuy nhiên, nếu muốn dùng alias bên trong một query cũng có `having` condition thì sao? Để trả lời câu hỏi này, hãy thử statement sau:

```text
forumdb=> select category,count(*) as category_count from posts group by
category having category_count > 1;
ERROR:     column "category_count" does not exist
```

Như có thể thấy, chúng ta không thể dùng alias trong `having` condition. Cách đúng để viết query trước đó là:

```text
forumdb=> select category,count(*) as category_count from posts group by
category having count(*) > 1;
    category | category_count
    ----------+----------------
               1 |                 2
    (1 row)
```

Trong chapter tiếp theo, chúng ta sẽ thảo luận chi tiết hơn về aggregate.

## UNION/UNION ALL

UNION operator được dùng để combine resultset của hai hoặc nhiều `SELECT` statement. Chúng ta chỉ có thể dùng `UNION` statement nếu tuân thủ các rule sau:

- Mỗi `SELECT` statement trong `UNION` phải có cùng số lượng column.
- Các column phải có data type tương tự nhau.
- Các column trong mỗi `SELECT` statement phải có cùng thứ tự.

Hãy cùng xem một ví dụ.

Trước tiên, chúng ta cần insert một số data:

```text
forumdb=> insert into tags (tag) values ('Database'),('Operating
Systems');
INSERT 0 2
```

Tình trạng trên table `tags` là:

```text
forumdb=> select tag from tags;
          tag
-------------------
 Database
 Operating Systems
(2 rows)
```

Và trên table `categories` là:

```text
forumdb=> select title from categories;
             title
-----------------------
 Database
 Unix
 Programming Languages
 New Category
 Database
(5 rows)
```

Bây giờ giả sử chúng ta muốn có một resultset là union của `tags` và `categories`; nói cách khác, chúng ta muốn nhận được result sau:

```text
Operating Systems
Database
New Category
Programming Languages
Unix
```

Để đạt được điều này, chúng ta phải dùng UNION operator:

```text
forumdb=> select tag as datalist from tags UNION select title as datalist
from categories;
        datalist
-----------------------
 New Category
 Operating Systems
 Programming Languages
 Database
 Unix
(5 rows)
```

UNION operator combine các value của hai table và loại bỏ duplicate. Nếu không muốn duplicate bị loại bỏ mà muốn chúng vẫn còn trong resultset, chúng ta phải dùng UNION ALL operator:

```text
forumdb=> select tag as datalist from tags UNION ALL select title as
datalist from categories order by 1;
         datalist
-----------------------
 Database
 Database
 Database
 New Category
 Operating Systems
 Programming Languages
 Unix
(7 rows)
```

## EXCEPT/INTERSECT

EXCEPT operator trả về các row bằng cách so sánh resultset của hai hoặc nhiều query. EXCEPT operator trả về các row distinct từ query thứ nhất (bên trái) không có trong output của query thứ hai (bên phải). Tương tự UNION operator, EXCEPT operator cũng có thể compare các query có cùng số lượng field và cùng data type.

Ví dụ, giả sử chúng ta có:

```text
forumdb=> select tag from tags;
        tag
-------------------
 Database
 Operating Systems
(2 rows)


forumdb=> select title from categories;
          title
-----------------------
 Database
 Unix
 Programming Languages
 New Category
 Database
(5 rows)
```

Và chúng ta muốn nhận được result sau:

```text
New Category
Programming Languages
Unix
```

Chúng ta cần lấy tất cả record hiện diện trong table `categories` nhưng không hiện diện trong table `tags`, được order theo field `title`. Để làm điều này, chúng ta dùng query sau:

```text
forumdb=> select title as datalist from categories except select tag as
datalist from tags order by 1;
        datalist
-----------------------
 New Category
 Programming Languages
 Unix
(3 rows)
```

INTERSECT operator thực hiện operation ngược lại. Nó search tất cả record hiện diện trong table thứ nhất và đồng thời hiện diện trong table thứ hai:

```text
forumdb=> select title as datalist from categories intersect select tag as
datalist from tags order by 1;
 datalist
----------
 Database
(1 row)
```

Trong section này, chúng ta đã xem xét chi tiết các instruction cần thiết để search data trong các table bằng nhiều statement và join khác nhau. Trong section tiếp theo, chúng ta sẽ xem cách modify data trong các table theo những cách nâng cao hơn.

## Sử dụng UPSERT

Trong section này, chúng ta sẽ xem cách PostgreSQL thực hiện một UPSERT statement. Không có UPSERT statement trong SQL, nhưng có thể đạt được cùng effect bằng cách dùng một `INSERT` SQL statement.

### UPSERT – cách của PostgreSQL

Trong PostgreSQL, UPSERT statement không tồn tại như trong các DBMS khác. UPSERT statement được dùng khi chúng ta muốn insert một record mới lên trên record hiện có hoặc update một record hiện có. Để làm điều này trong PostgreSQL, chúng ta có thể dùng keyword `ON CONFLICT`:

```text
INSERT INTO table_name(column_list) VALUES(value_list)
ON CONFLICT target action;
```

Ở đây, `ON CONFLICT` có nghĩa là target action được thực thi khi record đã tồn tại (nghĩa là khi một record có cùng primary key đã tồn tại). Target action có thể là:

```text
DO NOTHING
```

Hoặc có thể là:

```text
DO UPDATE SET { column_name = { expression | DEFAULT } |
         ( column_name [, ...] ) = [ ROW ] ( { expression | DEFAULT } [, ...]
 ) |
         ( column_name [, ...] ) = ( sub-SELECT )
         } [, ...]
[ WHERE condition ]
```

Bây giờ, hãy xem một ví dụ để hiểu rõ hơn UPSERT hoạt động thế nào:

1. Ví dụ, bắt đầu với table `j_posts_tags`:

   ```text
   forumdb=> \d j_posts_tags
                   Table "forum.j_posts_tags"
    Column    |   Type   | Collation | Nullable | Default
   ---------+---------+-----------+----------+---------
    tag_pk    | integer |             | not null |
    post_pk | integer |               | not null |
   Foreign-key constraints:
       "j_posts_tags_post_pk_fkey" FOREIGN KEY (post_pk) REFERENCES
   posts(pk)
   ```
