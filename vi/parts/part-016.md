Query này tạo một Cartesian product giữa table category và table posts. Nó cũng có thể được gọi là một cross join:

![Hình 5.1: Một cross join](../assets/part-016-figure-5-1-000.png)

*Hình 5.1: Một cross join*

Query tương tự cũng có thể được viết theo cách sau:

```text
forumdb=> select c.pk,c.title,p.pk,p.category,p.title from categories c
CROSS JOIN posts p;
 pk |         title          | pk | category |                 title
----+-----------------------+----+----------+------------
  1 | Database               |     1 |              1 | Indexing PostgreSQL
  2 | Unix                   |     1 |              1 | Indexing PostgreSQL
  3 | Programming Languages |      1 |              1 | Indexing PostgreSQL
  4 | New Category           |     1 |              1 | Indexing PostgreSQL
  5 | Database               |     1 |              1 | Indexing PostgreSQL
  1 | Database               |     2 |              1 | Indexing Mysql
  2 | Unix                   |     2 |              1 | Indexing Mysql
  3 | Programming Languages |      2 |              1 | Indexing Mysql
  4 | New Category           |     2 |              1 | Indexing Mysql
  5 | Database               |     2 |              1 | Indexing Mysql
  1 | Database               |     3 |              3 | Data types in C++
  2 | Unix                   |     3 |              3 | Data types in C++
  3 | Programming Languages |      3 |              3 | Data types in C++
  4 | New Category           |     3 |              3 | Data types in C++
  5 | Database               |     3 |              3 | Data types in C++
(15 rows)
```

## Sử dụng INNER JOIN

Bây giờ giả sử rằng, bắt đầu với tất cả combination khả dĩ tồn tại giữa các row của table category và các row của table posts, chúng ta muốn filter tất cả row có cùng value với field category (`category.pk = posts.category`). Chúng ta muốn có một result giống như result được mô tả trong diagram sau:

![Hình 5.2: Một inner join](../assets/part-016-figure-5-2-000.png)

*Hình 5.2: Một inner join*

> Keyword INNER JOIN chọn các record có value khớp trong cả hai table.

Để thực hiện điều này, chúng ta cần chạy code sau:

```text
forumdb=> select c.pk,c.title,p.pk,p.category,p.title from categories
c,posts p where c.pk=p.category;
 pk |            title            | pk | category |              title
----+-----------------------+----+----------+------------
  1 | Database                   |   1 |             1 | Indexing PostgreSQL
  1 | Database                   |   2 |             1 | Indexing Mysql
  3 | Programming Languages |        3 |             3 | Data types in C++
    (3 rows)
```

Chúng ta cũng có thể viết cùng query bằng operation JOIN tường minh:

```text
forumdb=> select c.pk,c.title,p.pk,p.category,p.title from categories c
inner join posts p on c.pk=p.category;
 pk |            title            | pk | category |              title
----+-----------------------+----+----------+------------
  1 | Database                   |   1 |             1 | Indexing PostgreSQL
  1 | Database                     |   2 |          1 | Indexing Mysql
  3 | Programming Languages |          3 |          3 | Data types in C++
(3 rows)
```

## INNER JOIN so với EXISTS/IN

Nếu muốn search tất cả post thuộc category Database bằng condition INNER JOIN, chúng ta phải viết lại query như sau:

```text
forumdb=> \x
Expanded display is on.


forumdb=> select c.pk,c.title,p.pk,p.category,p.title from categories c
inner join posts p on c.pk=p.category where c.title='Database';
-[ RECORD 1 ]-----------------
pk         | 1
title      | Database
pk         | 1
category | 1
title      | Indexing PostgreSQL
-[ RECORD 2 ]-----------------
pk         | 1
title      | Database
pk         | 2
category | 1
title      | Indexing Mysql
```

> Với condition INNER JOIN, chúng ta có thể viết lại tất cả query có thể được viết bằng condition IN hoặc EXISTS.

Nên sử dụng JOIN condition bất cứ khi nào có thể thay cho IN hoặc EXISTS condition, vì chúng có execution speed tốt hơn, như chúng ta sẽ thấy trong các chapter sau.

## Sử dụng LEFT JOIN

Bây giờ chúng ta sẽ tìm hiểu left join là gì. Ví dụ, chúng ta có thể thực hiện query sau:

```text
forumdb=> select c.*,p.category,p.title from categories c left join posts
p on c.pk=p.category;
-[ RECORD 1 ]--------------------------------
pk            | 1
title         | Database
description | Database related discussions
category      | 1
title         | Indexing PostgreSQL
-[ RECORD 2 ]--------------------------------
pk            | 1
title         | Database
description | Database related discussions
category      | 1
title         | Indexing Mysql
-[ RECORD 3 ]--------------------------------
pk            | 3
title         | Programming Languages
description | All about programming languages
category      | 3
title         | Data types in C++
-[ RECORD 4 ]--------------------------------
pk            | 2
title         | Unix
description | Unix and Linux discussions
category      | (NULL)
title         | (NULL)
-[ RECORD 5 ]--------------------------------
pk            | 5
title         | Database
description | PostgreSQL
category      | (NULL)
title         | (NULL)
-[ RECORD 6 ]--------------------------------
pk            | 4
title         | New Category
description | (NULL)
category      | (NULL)
title         | (NULL)
```

Query này trả về tất cả record của table categories và trả về các record khớp từ table posts. Như chúng ta có thể thấy, nếu table thứ hai (table posts trong ví dụ này) không có match, result sẽ là NULL.

> Keyword left join trả về tất cả record từ table bên trái (table1), và tất cả record từ table bên phải (table2). Result là NULL ở phía bên phải nếu không có match.

Diagram này cho chúng ta hình dung left join hoạt động như thế nào:

![Hình 5.3: Một left join](../assets/part-016-figure-5-3-000.png)

*Hình 5.3: Một left join*

Giả sử bây giờ chúng ta muốn search tất cả category không có post, chúng ta có thể viết như sau:

```text
forumdb=> \x
Expanded display is off.

forumdb=> select * from categories c where c.pk not in (select category
from posts);
 pk |      title       |           description
----+--------------+----------------------------
  2 | Unix             | Unix and Linux discussions
  4 | New Category | (NULL)
  5 | Database         | PostgreSQL
(3 rows)
```

Query này, được viết bằng condition NOT IN, tìm tất cả record trong table categories mà value pk không khớp với field category của table posts. Như chúng ta đã thấy, một cách khác để viết cùng query là dùng condition NOT EXISTS:

```text
forumdb=> select * from categories c where not exists (select 1 from posts
where category=c.pk);
 pk |      title       |           description
----+--------------+----------------------------
  2 | Unix             | Unix and Linux discussions
  4 | New Category | (NULL)
  5 | Database        | PostgreSQL
(3 rows)
```

Nếu bây giờ muốn dùng left join để đạt cùng mục đích, chúng ta sẽ bắt đầu bằng query left join sau:

```text
forumdb=> \x
Expanded display is on.

forumdb=> select c.*,p.category from categories c left join posts p on
p.category=c.pk;
-[ RECORD 1 ]--------------------------------
pk             | 1
title          | Database
description | Database related discussions
category       | 1
-[ RECORD 2 ]--------------------------------
pk             | 1
title          | Database
description | Database related discussions
category       | 1
-[ RECORD 3 ]--------------------------------
pk             | 3
title          | Programming Languages
description | All about programming languages
category       | 3
-[ RECORD 4 ]--------------------------------
pk             | 2
title         | Unix
description | Unix and Linux discussions
category      | (NULL)
-[ RECORD 5 ]--------------------------------
pk            | 5
title         | Database
description | PostgreSQL
category      | (NULL)
-[ RECORD 6 ]--------------------------------
pk            | 4
title         | New Category
description | (NULL)
category      | (NULL)
```

Từ result, có thể thấy ngay rằng tất cả value chúng ta đang tìm là những value mà `p.category` là NULL.

Vì vậy, chúng ta viết lại query theo cách sau:

```text
forumdb=> \x
Expanded display is off.


forumdb=> select c.* from categories c left join posts p on p.category=c.
pk where p.category is null;
 pk |      title       |         description
----+--------------+----------------------------
  2 | Unix             | Unix and Linux discussions
  4 | New Category | (NULL)
  5 | Database         | PostgreSQL
(3 rows)
```

Như thể hiện ở đây, chúng ta nhận được cùng result như khi dùng condition NOT EXISTS hoặc NOT IN.

> Với condition left join, chúng ta có thể viết lại một số query có thể được viết bằng condition IN hoặc EXISTS.

Như đã đề cập trước đó, nên sử dụng JOIN condition bất cứ khi nào có thể thay cho IN hoặc EXISTS condition, vì chúng có execution speed tốt hơn, như chúng ta sẽ thấy trong các chapter sau.

## Sử dụng RIGHT JOIN

Right join là bản song sinh của left join, vì vậy chúng ta sẽ nhận được cùng result nếu viết table A left join table B hoặc table B right join table A. Ví dụ, chúng ta có thể nhận được cùng result nếu viết:

```text
select c.*,p.category from categories c left join posts p on p.category=c.
pk;
```

hoặc nếu viết:

```text
select c.*,p.category,p.title from posts p right join categories c on
c.pk=p.category;
```

như có thể thấy ở đây:

```text
forumdb=> \x
Expanded display is on.


forumdb=> select c.*,p.category,p.title from posts p right join categories
c on c.pk=p.category;
-[ RECORD 1 ]--------------------------------
pk             | 1
title          | Database
description | Database related discussions
category       | 1
title          | Indexing PostgreSQL
-[ RECORD 2 ]--------------------------------
pk             | 1
title          | Database
description | Database related discussions
category       | 1
title          | Indexing Mysql
-[ RECORD 3 ]--------------------------------
pk             | 3
title          | Programming Languages
description | All about programming languages
category      | 3
title         | Data types in C++
-[ RECORD 4 ]--------------------------------
pk            | 2
title         | Unix
description | Unix and Linux discussions
category      | (NULL)
title         | (NULL)
-[ RECORD 5 ]--------------------------------
pk            | 5
title         | Database
description | PostgreSQL
category      | (NULL)
title         | (NULL)
-[ RECORD 6 ]--------------------------------
pk            | 4
title         | New Category
description | (NULL)
category      | (NULL)
title         | (NULL)
```

> Keyword RIGHT JOIN trả về tất cả record từ table bên phải (table2) và tất cả record từ table bên trái (table1) khớp với table bên phải (table2). Result là NULL từ phía bên trái khi không có match.

Diagram này minh họa cách RIGHT JOIN hoạt động:

![Hình 5.4: Một right join](../assets/part-016-figure-5-4-000.png)

*Hình 5.4: Một right join*

## Sử dụng FULL OUTER JOIN

Trong SQL, FULL OUTER JOIN là sự kết hợp của result mà chúng ta có được nếu ghép right join và left join lại với nhau. Chúng ta sẽ kiểm tra điều này qua các bước sau:

1. Tạo một temporary table mới và insert một số data:

   ```text
   forumdb=> create temp table new_posts as select * from posts;
   SELECT 3
   forumdb=> insert into new_posts (pk,title,content,author,category)
   values (6,'A new Book','A new book not present in
   categories....',1,NULL);
   INSERT 0 1
   ```

2. Tình huống hiện tại là như sau:

   ```text
   forumdb=> \x
   Expanded display is off.
   forumdb=> select pk,title,category from new_posts ;
    pk |          title           | category
   ----+---------------------+----------
     1 | Indexing PostgreSQL |                 1
     2 | Indexing Mysql           |            1
     3 | Data types in C++        |            3
     6 | A new Book               |       (NULL)
   ```

3. Bây giờ hãy thử viết query JOIN này:

   ```text
   forumdb=> select c.pk,c.title,p.pk,p.title from categories c inner
   join new_posts p on p.category=c.pk;
    pk |           title              | pk |          title
   ----+-----------------------+----+---------------------
     1 | Database                     |    1 | Indexing PostgreSQL
     1 | Database                     |    2 | Indexing Mysql
     3 | Programming Languages |           3 | Data types in C++
   (3 rows)
   ```

Query này trả về tất cả record có post (trong table new_post) và category.
