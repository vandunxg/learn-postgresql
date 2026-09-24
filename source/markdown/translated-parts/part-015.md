## Sử dụng `ilike`

Trong PostgreSQL, có thể thực hiện một query `like` không phân biệt chữ hoa chữ thường bằng cách sử dụng operator `ilike`.

Trong trường hợp này, query của chúng ta sẽ trở thành như sau:

```text
forumdb=> select * from categories where description ilike '%DISCUSS%';
   pk |   title   |              description
----+----------+------------------------------
    1 | Database | Database related discussions
    2 | Unix      | Unix and Linux discussions
(2 rows)
```

Đây là cách PostgreSQL giải quyết vấn đề query `like` không phân biệt chữ hoa chữ thường mà chúng ta đã gặp trước đó.

## Sử dụng `distinct`

Bây giờ chúng ta sẽ thảo luận về một loại query khác: query `distinct`. Tuy nhiên, trước tiên chúng ta cần giới thiệu một function rất hữu ích khác dành cho DBA, gọi là function `coalesce`. Function `coalesce`, khi nhận hai hoặc nhiều parameter, sẽ trả về giá trị đầu tiên không phải `NULL`.

Ví dụ, hãy sử dụng function `coalesce` với giá trị test:

```text
forumdb=> select coalesce(NULL,'test');
   coalesce
----------
   test
(1 row)
```

Trong query trên, function `coalesce` trả về `test` vì argument đầu tiên là `NULL` còn argument thứ hai không phải `NULL`.

Bây giờ, hãy insert một category mới:

```text
forumdb=> insert into categories (title) values ('New Category');
INSERT 0 1
```

Sau đó hãy thực hiện query sau:

```text
forumdb=# \pset null (NULL)
Null display is "(NULL)".
```

```text
forumdb=> select pk,title,description from categories;
 pk |            title             |              description
 ----+-----------------------+----------------------------
  1 | Database                     | Database related discussions
  2 | Unix                         | Unix and Linux discussions
  3 | Programming Languages       | All about programming languages
  4 | New Category                | (NULL)
(4 rows)
```

Trong ví dụ trên, field `description` có giá trị `NULL` đối với title `New Category`.

Bây giờ hãy thử sử dụng function `coalesce` để hiển thị giá trị `No Description` thay vì `NULL`.

```text
forumdb=> select pk,title,coalesce(description,'No description') from
categories;
 pk |            title             |               coalesce
 ----+-----------------------+----------------------------
  1 | Database                     | Database related discussions
  2 | Unix                         | Unix and Linux discussions
  3 | Programming Languages       | All about programming languages
  4 | New Category                | No description
(4 rows)
```

Trong đoạn code trên, function `coalesce` biến mọi giá trị `NULL` thành string `No description`. Một điểm khác ở function `coalesce` không thân thiện với người dùng là tên của field được tạo khi gọi một function không phải là tên mà chúng ta mong muốn. Trong trường hợp này, field thứ hai của result set được gọi là `coalesce`, không phải tên mà chúng ta thích; đó là vì nếu làm việc trong một team, tên dễ đọc đối với con người sẽ được ưu tiên.

Trong PostgreSQL, có thể gán alias cho bất kỳ field nào trong một query. Ví dụ, chúng ta có thể gán alias cho field `coalesce` như sau:

```text
forumdb=> select pk,title,coalesce(description,'No description') as
description from categories;
 pk |            title             |              description
 ----+-----------------------+---------------------------------
  1 | Database                     | Database related discussions
  2 | Unix                         | Unix and Linux discussions
  3 | Programming Languages       | All about programming languages
  4 | New Category                | No description
(4 rows)
```

Bây giờ result set có field `description` thay vì field `coalesce`.

Nếu muốn sử dụng alias có khoảng trắng hoặc chữ in hoa, chúng ta phải đặt alias trong dấu ngoặc kép `""`, như trong ví dụ sau:

```text
forumdb=> select pk,title,coalesce(description,'No description') as
"Description" from categories;
 pk |           title           |              Description
----+---------------------------+---------------------------------
  1 | Database                  | Database related discussions
  2 | Unix                      | Unix and Linux discussions
  3 | Programming Languages    | All about programming languages
  4 | New Category             | No description
(4 rows)
```

Result set không có alias là `Description` (chữ in hoa), mà có alias là `description` (chữ thường), điều này có vẻ không đúng. Bây giờ hãy insert một record khác như sau:

```text
forumdb=> insert into categories (title,description) values
('Database','PostgreSQL');
INSERT 0 1
```

Và hãy thực hiện query này:

```text
forumdb=> select title from categories order by title;
            title
-----------------------
 Database
 Database
 New Category
 Programming Languages
 Unix
(5 rows)
```

Như có thể thấy trong query trên, có 2 record có cùng giá trị `Database`; nếu muốn hiển thị tất cả các giá trị distinct, chúng ta phải sử dụng clause `DISTINCT`:

```text
forumdb=> select distinct title from categories order by title;
            title
-----------------------
 Database
 New Category
 Programming Languages
 Unix
(4 rows)
```

Trong query trên, chúng ta đã sử dụng statement `select distinct`. Statement `select distinct` được dùng để chỉ trả về các giá trị distinct (khác nhau). Về bên trong, statement `distinct` thực hiện việc sort dữ liệu đối với các table lớn, nghĩa là nếu một query sử dụng statement `distinct`, query đó có thể chậm hơn khi số lượng record tăng lên.

## Sử dụng `limit` và `offset`

Clause `limit` là cách PostgreSQL giới hạn số row được trả về bởi một query, trong khi clause `offset` được dùng để bỏ qua một số row cụ thể do query trả về.

`limit` và `offset` được dùng để trả về một phần dữ liệu từ result set do một query tạo ra; clause `limit` dùng để giới hạn số record trong output, còn clause `offset` cung cấp cho PostgreSQL vị trí trong result set mà từ đó bắt đầu trả về dữ liệu.

Chúng có thể được sử dụng độc lập hoặc cùng nhau.

Bây giờ hãy kiểm tra `limit` và `offset` bằng các query sau:

```text
forumdb=> select * from categories order by pk limit 1;
 pk |    title    |            description
 ----+----------+------------------------------
  1 | Database    | Database related discussions
(1 row)
```

Query trên chỉ trả về record đầu tiên mà chúng ta đã insert; đó là vì field `pk` có kiểu integer với giá trị mặc định luôn được tạo dưới dạng identity.

Nếu muốn xem hai record đầu tiên đã được insert, chúng ta phải thực hiện query sau:

```text
forumdb=> select * from categories order by pk limit 2;
 pk |    title    |            description
 ----+----------+------------------------------
  1 | Database    | Database related discussions
  2 | Unix        | Unix and Linux discussions
(2 rows)
```

Nếu chỉ muốn record thứ hai đã được insert, chúng ta phải thực hiện query sau:

```text
forumdb=> select * from categories order by pk offset 1 limit 1;
 pk | title |            description
----+-------+----------------------------
  2 | Unix  | Unix and Linux discussions
(1 row)
```

`offset` và `limit` rất hữu ích khi muốn trả về dữ liệu theo cách phân trang.

Một chức năng hữu ích khác của `limit` là có thể tạo một table mới từ một table hiện có. Ví dụ, nếu muốn tạo một table có tên `new_categories` bắt đầu từ table `categories`, chúng ta phải thực thi statement sau:

```text
forumdb=> create table new_categories as select * from categories limit 0;
SELECT 0
```

Statement này sẽ chỉ copy data structure của table `categories` vào table `new_categories`.

Clause `SELECT 0` có nghĩa là không có dữ liệu nào được copy vào table `new_categories`; chỉ data structure được replicate, như chúng ta có thể thấy ở đây:

```text
forumdb=> \d new_categories
               Table "forum.new_categories"
  Column     |   Type     | Collation | Nullable | Default
-------------+---------+-----------+----------+---------
 pk           | integer |               |            |
 title        | text       |            |            |
 description | text       |            |            |
```

## Sử dụng subquery

Trong section này, chúng ta sẽ nói về subquery. Subquery có thể được mô tả là query lồng nhau - chúng ta có thể lồng một query bên trong một query khác bằng cách sử dụng dấu ngoặc đơn. Subquery có thể trả về một giá trị đơn hoặc một record set, giống như các query thông thường. Chúng ta sẽ bắt đầu giới thiệu subquery bằng operator `IN`/`NOT IN`.

### Subquery và điều kiện `IN`/`NOT IN`

Hãy bắt đầu với operator `IN`; chúng ta có thể sử dụng operator `IN` bên trong clause `where` thay vì sử dụng nhiều điều kiện `OR`. Ví dụ, nếu muốn tìm kiếm tất cả category có giá trị `pk=1` hoặc giá trị `pk=2`, bạn phải thực hiện statement sau:

```text
forumdb=> select * from categories where pk=1 or pk=2;
 pk |    title    |            description
 ----+----------+------------------------------
  1 | Database    | Database related discussions
  2 | Unix        | Unix and Linux discussions
(2 rows)
```

Một cách khác để đạt được cùng kết quả là:

```text
forumdb=> select * from categories where pk in (1,2);
 pk |    title    |            description
 ----+----------+------------------------------
  1 | Database    | Database related discussions
  2 | Unix        | Unix and Linux discussions
(2 rows)
```

Một operator tương tự operator `IN` nhưng có chức năng ngược lại là operator `NOT IN`. Ví dụ, nếu muốn tìm kiếm tất cả category không có `pk=1` hoặc `pk=2`, chúng ta phải thực thi như sau:

```text
forumdb=> select * from categories where pk not in (1,2);
 pk |            title             |             description
 ----+-----------------------+----------------------------
  3 | Programming Languages       | All about programming languages
  4 | New Category                | (NULL)
  5 | Database                    | PostgreSQL
(3 rows)
```

Bây giờ chúng ta có thể insert một ít dữ liệu vào table `users` và table `posts`:

```text
forumdb=> insert into users (username,email) values ('luca_ferrari','luca@
pgtraining.com'),('enrico_pirozzi','enrico@pgtraining.com');
INSERT 0 2
```

Các statement sau đây insert dữ liệu vào table `posts`:

```text
forumdb=> insert into posts (title,content,author,category) values
('Indexing PostgreSQL','Btree in PostgreSQL is....',1,1);
INSERT 0 1
forumdb=> insert into posts (title,content,author,category) values
('Indexing Mysql','Btree in Mysql is....',1,1);
INSERT 0 1
forumdb=> insert into posts (title,content,author,category) values ('Data
types in C++','Data type in C++ are ..' ,2,3);
INSERT 0 1
```

Các record hiện có trong table `posts` lúc này là như sau:

```text
forumdb=> \x
Expanded display is on.
forumdb=> select pk,title,content,author,category from posts;
-[ RECORD 1 ]------------------------
pk        | 1
title     | Indexing PostgreSQL
content   | Btree in PostgreSQL is....
author    | 1
category  | 1
-[ RECORD 2 ]------------------------
pk        | 2
title     | Indexing Mysql
content   | Btree in Mysql is....
author    | 1
category  | 1
-[ RECORD 3 ]------------------------
pk        | 3
title     | Data types in C++
content   | Data type in C++ are ..
author    | 2
category  | 3
```

Giả sử bây giờ chúng ta muốn tìm kiếm tất cả post thuộc category `Database`. Có thể thực hiện việc này bằng một số phương pháp.

Phương pháp sau sử dụng subquery:

```text
forumdb=> select pk,title,content,author,category from posts where
category in (select pk from categories where title ='Database');
-[ RECORD 1 ]------------------------
pk         | 1
title      | Indexing PostgreSQL
content    | Btree in PostgreSQL is....
author     | 1
category   | 1
-[ RECORD 2 ]------------------------
pk         | 2
title      | Indexing Mysql
content    | Btree in Mysql is....
author     | 1
category   | 1
```

Subquery được biểu diễn như sau:

```text
forumdb=> \x
Expanded display is off.

forumdb=> select pk from categories where title ='Database';
 pk
----
  1
  5
(2 rows)
```

Statement này trích xuất các giá trị `pk=1` và `pk=5` từ category table, còn query bên ngoài tìm các record trong table `posts` có `pk=1` hoặc `pk=5`. Tương tự, nếu muốn tìm tất cả post không thuộc category `Database`, chúng ta phải thực hiện statement sau:

```text
forumdb=> \x
Expanded display is on.

forumdb=> select pk,title,content,author,category from posts where
category not in (select pk from categories where title ='Database');
-[ RECORD 1 ]---------------------
pk       | 3
title    | Data types in C++
content  | Data type in C++ are ..
author   | 2
category | 3
```

### Subquery và điều kiện `EXISTS`/`NOT EXISTS`

Statement `EXISTS` được sử dụng khi muốn kiểm tra xem một subquery có trả về kết quả hay không (`TRUE`), còn statement `NOT EXISTS` được sử dụng khi muốn kiểm tra xem một subquery không trả về kết quả (`FALSE`). Ví dụ, nếu muốn viết các điều kiện giống như các điều kiện đã viết trước đó bằng điều kiện `EXISTS`/`NOT EXISTS`, chúng ta phải thực hiện như sau:

```text
forumdb=> select pk,title,content,author,category from posts where exists
(select 1 from categories where title ='Database' and posts.category=pk);
-[ RECORD 1 ]------------------------
pk         | 1
title      | Indexing PostgreSQL
content    | Btree in PostgreSQL is....
author     | 1
category   | 1
-[ RECORD 2 ]------------------------
pk         | 2
title      | Indexing Mysql
content    | Btree in Mysql is....
author     | 1
category   | 1
```

Query trên trả về cùng kết quả với query được viết bằng điều kiện `IN`.

Tương tự, nếu muốn tìm tất cả post không thuộc category `Database` bằng điều kiện `NOT EXISTS`, chúng ta phải viết như sau:

```text
forumdb=> select pk,title,content,author,category from posts where not
exists (select 1 from categories where title ='Database' and posts.
category=pk);
-[ RECORD 1 ]------------------
pk       | 3
title    | Data types in C++
content  | Data type in C++ are ..
author   | 2
category | 3
```

Cả hai query được viết bằng điều kiện `IN` và bằng điều kiện `EXISTS` đều được gọi là query semi-join, và chúng ta sẽ xem xét các join trong section tiếp theo.

## Tìm hiểu về join

Hãy xem xét join là gì, có bao nhiêu loại join và chúng được dùng để làm gì. Chúng ta có thể coi join là sự kết hợp các row từ hai hoặc nhiều table.

Ví dụ, query sau trả về mọi tổ hợp từ các row của table category và các row của table `posts`:

```text
forumdb=> select c.pk,c.title,p.pk,p.category,p.title from categories
c,posts p;
 pk |           title            | pk | category |             title
 ----+-----------------------+----+----------+------------
  1 | Database                   |  1 |          1 | Indexing PostgreSQL
  2 | Unix                       |  1 |          1 | Indexing PostgreSQL
  3 | Programming Languages     |  1 |          1 | Indexing PostgreSQL
  4 | New Category              |  1 |          1 | Indexing PostgreSQL
  5 | Database                  |  1 |          1 | Indexing PostgreSQL
  1 | Database                  |  2 |          1 | Indexing Mysql
  2 | Unix                      |  2 |          1 | Indexing Mysql
  3 | Programming Languages    |  2 |          1 | Indexing Mysql
  4 | New Category             |  2 |          1 | Indexing Mysql
  5 | Database                 |  2 |          1 | Indexing Mysql
  1 | Database                  |  3 |          3 | Data types in C++
  2 | Unix                      |  3 |          3 | Data types in C++
  3 | Programming Languages    |  3 |          3 | Data types in C++
  4 | New Category             |  3 |          3 | Data types in C++
  5 | Database                 |  3 |          3 | Data types in C++
(15 rows)
```
