```text
"j_posts_tags_tag_pk_fkey" FOREIGN KEY (tag_pk) REFERENCES
tags(pk)
```

2. Trước tiên, hãy thêm một primary key vào table `j_posts_add`:

```text
forumdb=> alter table j_posts_tags add constraint j_posts_tags_pkey
primary key (tag_pk,post_pk);
ALTER TABLE
```

```text
ALTER TABLE

forumdb=> \d j_posts_tags
                Table "forum.j_posts_tags"
 Column    |   Type    | Collation | Nullable | Default
 ---------+---------+-----------+----------+---------
 tag_pk    | integer |                | not null |
 post_pk | integer |                  | not null |
Indexes:
    "j_posts_tags_pkey" PRIMARY KEY, btree (tag_pk, post_pk)
Foreign-key constraints:
    "j_posts_tags_post_pk_fkey" FOREIGN KEY (post_pk) REFERENCES
posts(pk)
    "j_posts_tags_tag_pk_fkey" FOREIGN KEY (tag_pk) REFERENCES
tags(pk)
```

3. Tiếp theo, hãy insert một số record vào table `j_posts_tags`:

```text
forumdb=> insert into j_posts_tags (post_pk ,tag_pk) values
(3,2),(1,1),(2,1);
INSERT 0 3

forumdb=> select * from j_posts_tags ;
 tag_pk | post_pk
--------+---------
       2 |         3
       1 |         1
       1 |         2
(3 rows)
```

4. Bây giờ hãy thử insert một record khác với cùng primary key. Nếu thực hiện một `insert statement` tiêu chuẩn như sau, chúng ta có thể thấy PostgreSQL trả về error vì đang cố insert một record đã tồn tại:

```text
forumdb=>insert into j_posts_tags (post_pk ,tag_pk) values (2,1);
ERROR: duplicate key value violates unique constraint "j_posts_
tags_pkey"
DETAIL:    Key (tag_pk, post_pk)=(1, 2) already exists.
```

5. Bây giờ hãy thử sử dụng option `ON CONFLICT DO NOTHING`:

```text
forumdb=> insert into j_posts_tags (post_pk ,tag_pk) values (2,1) ON
CONFLICT DO NOTHING;
INSERT 0 0

forumdb=> select * from j_posts_tags ;
 tag_pk | post_pk
--------+---------
       2 |         3
       1 |         1
       1 |         2
(3 rows)
```

Trong trường hợp này, PostgreSQL không trả về error; thay vào đó, nó đơn giản là không làm gì.

6. Bây giờ hãy thử option `DO UPDATE set`. Option này hiện thực statement UPSERT, như trong ví dụ sau:

```text
forumdb=> insert into j_posts_tags (post_pk ,tag_pk) values (2,1) ON
CONFLICT (tag_pk,post_pk) DO UPDATE set tag_pk=excluded.tag_pk+1;
INSERT 0 1

forumdb=>    select * from j_posts_tags ;
 tag_pk | post_pk
--------+---------
       2 |         3
       1 |         1
       2 |         2
(3 rows)
```

Các field bên trong condition `ON CONFLICT` phải có một unique constraint hoặc exclusion constraint. Statement trước đó đơn giản thay thế statement sau:

```text
INSERT INTO   j_posts_tags (post_pk ,tag_pk) values (2,1)
```

Nó được thay thế bằng statement này:

```text
UPDATE set tag_pk=tag_pk+1 where tag_pk=1 and post_pk=2
```

## Tìm hiểu clause RETURNING cho INSERT

Trong PostgreSQL, chúng ta có thể thêm keyword `RETURNING` vào `insert statement`. Keyword `RETURNING` trong PostgreSQL cho phép trả về giá trị của bất kỳ column nào từ một `insert` hoặc `update statement` sau khi insert hoặc update được thực hiện. Ví dụ, nếu muốn trả về toàn bộ field của record vừa insert, chúng ta phải thực hiện query như sau:

```text
forumdb=> insert into j_posts_tags (tag_pk,post_pk) values(1,3) returning
*;
 tag_pk | post_pk
--------+---------
      1 |        3
(1 row)

INSERT 0 1
```

Dấu `*` nghĩa là chúng ta muốn trả về tất cả field của record vừa insert; nếu chỉ muốn trả về một số field, chúng ta phải chỉ định những field mà query phải trả về:

```text
forumdb=> insert into j_posts_tags (tag_pk,post_pk) values(1,2) returning
tag_pk;
 tag_pk
--------
      1
(1 row)

INSERT 0 1
```

Tính năng này sẽ đặc biệt hữu ích ở cuối chapter khi chúng ta nói về CTE.

## Trả về tuple từ các query

Trong các chapter trước, chúng ta đã xem xét những update query đơn giản như sau:

```text
forumdb=> update posts set title = 'A view of           Data types in C++' where pk
= 3;
UPDATE 1
```

Bây giờ chúng ta sẽ xem xét một điều phức tạp hơn. Nếu muốn update một số record trong table `posts` có liên quan với nhau theo cách nào đó thì sao?

## UPDATE liên quan đến nhiều record

Hãy bắt đầu với scenario sau:

1. Xem xét table `categories`:

```text
forumdb=> SELECT * FROM categories;
 pk |            title          |             description
----+-----------------------+----------------------------
  1 | Database                  | Database related discussions
  2 | Unix                      | Unix and Linux discussions
  3 | Programming Languages | All about programming languages
  4 | New Category              |
  5 | Database                  | PostgreSQL
(5 rows)
```

2. Hãy xem xét một table category mới, từ đó chúng ta muốn update table `categories` hiện có.

```text
forumdb=> create temp table t_categories as select * from categories
limit 0;
SELECT 0

forumdb=> insert into t_categories (pk,title,description) values
(4,'Machine Learning','Machine Learning discussions'),(5,'Software
engineering','Software engineering discussions');
INSERT 0 2
forumdb=> select * from t_categories ;
  pk |           title          |             description
 ----+----------------------+-----------------------------
     4 | Machine Learning      | Machine Learning discussions
     5 | Software engineering | Software engineering discussions
(2 rows)
```

Giả sử chúng ta muốn lấy các value từ table `t_categories` và dùng chúng để update các value của table `categories`; đây là resultset chúng ta muốn đạt được:

```text
  pk   |          title          |             description
 ------+-----------------------+----------------------------
   1 | Database                 | Database related discussions
   2 | Unix                     | Unix and Linux discussions
   3 | Programming Languages | All about programming languages
   4 | Machine Learning         | Machine Learning discussions
   5 | Software engineering     | Software engineering discussions
```

Query chúng ta phải thực thi là:

```text
forumdb=>update categories c set title=t.title,description=t.description
from t_categories t where c.pk=t.pk;
UPDATE 2

forumdb=> select * from categories;
  pk |           title          |             description
 ----+-----------------------+----------------------------
   1 | Database                 | Database related discussions
   2 | Unix                     | Unix and Linux discussions
   3 | Programming Languages | All about programming languages
   4 | Machine Learning         | Machine Learning discussions
   5 | Software engineering     | Software engineering discussions
(5 rows)
```

Trong query này, PostgreSQL có thể update các field `title` và `description` của table `categories` bằng dữ liệu từ table `t_categories` có match trên field `pk`; khi nói về statement `merge`, chúng ta sẽ thấy một cách khác để đạt được cùng mục tiêu.

## MERGE

Bắt đầu từ PostgreSQL 15, chúng ta có thể đạt được cùng mục tiêu đã đạt được trong section trước bằng cách sử dụng statement `MERGE`; nên ưu tiên sử dụng statement `MERGE` vì nó hiện diện trong SQL 2003 ANSI.

Bây giờ, hãy bắt đầu từ các value trước đó của table `categories`:

```text
forumdb=> select * from categories;
  pk |            title            |              description
 ----+----------------------------+---------------------------
   1 | Database                   | Database related discussions
   2 | Unix                       | Unix and Linux discussions
   3 | Programming Languages | All about programming languages
   4 | Machine Learning           | Machine Learning discussions
   5 | Software engineering       | Software engineering discussions
(5 rows)
```

Sau đó hãy tạo một dataset khác với một số thay đổi mà chúng ta muốn áp dụng vào table `categories`:

```text
forumdb=> create temp table new_data as select * from categories limit 0;
SELECT 0

forumdb=> insert into new_data (pk,title,description) values (1,'Database
Discussions','Database discussions'),(2,'Unix/Linux discussion','Unix and
Linux discussions');
INSERT 0 2

forumdb=> select * from new_data;
  pk |            title            |           description
 ----+----------------------------+----------------------------
   1 | Database Discussions       | Database discussions
   2 | Unix/Linux discussion | Unix and Linux discussions
(2 rows)
```

Bây giờ mục tiêu chúng ta muốn đạt được là merge hai dataset như bên dưới:

```text
 1 | Database Discussions        | Database discussions
 2 | Unix/Linux discussion | Unix and Linux discussions
 3 | Programming Languages | All about programming languages
 4 | Machine Learning            | Machine Learning discussions
 5 | Software engineering        | Software engineering discussions
```

Query chúng ta phải thực hiện để đạt mục tiêu này là:

```text
forumdb=> merge into categories c
using new_data n on c.pk=n.pk
when matched then
  update set title=n.title,description=n.description
when not matched then
  insert (pk,title,description)
  OVERRIDING SYSTEM VALUE values (n.pk,n.title,n.description);
MERGE 2

forumdb=> select * from categories order by 1;
  pk |           title           |              description
 ----+----------------------------+----------------------------
   1 | Database Discussions      | Database discussions
   2 | Unix/Linux discussion | Unix and Linux discussions
   3 | Programming Languages | All about programming languages
   4 | Machine Learning          | Machine Learning discussions
   5 | Software engineering      | Software engineering discussions
(5 rows)
```

Query trên kiểm tra xem có match giữa value của field `PK` của table `new_data` và value của field tương ứng của table `categories` hay không. Nếu có match, `UPDATE` sẽ được thực thi; nếu không, `INSERT` sẽ được thực thi. Clause `OVERRIDING SYSTEM VALUE` được dùng vì trong `INSERT statement`, chúng ta cũng chỉ định insert các value của field `PK` lấy từ table `new_data`, và vì field `PK` trong table `categories` được định nghĩa là `GENERATED ALWAYS`, PostgreSQL sẽ phát sinh error nếu không có clause `OVERRIDING SYSTEM VALUE`.

## Tìm hiểu UPDATE ... RETURNING

Tương tự `INSERT statement`, `update statement` cũng có thể thêm keyword `RETURNING`. `update statement` hoạt động theo cùng cách với `INSERT statement`:

```text
forumdb=> update categories set title='A.I' where pk=4 returning
pk,title,description;
  pk | title |            description
 ----+-------+------------------------------
   4 | A.I   | Machine Learning discussions
(1 row)

UPDATE 1
```

## Tìm hiểu DELETE ... RETURNING

Như đã thấy, `update statement`, giống `INSERT statement`, có thể thêm keyword `RETURNING`; tính năng này cũng có sẵn cho `delete statement`:

```text
forumdb=> delete from t_categories where pk=4 returning
pk,title,description;
  pk |         title          |            description
 ----+------------------+------------------------------
     4 | Machine Learning | Machine Learning discussions
(1 row)
DELETE 1
```

Trong section tiếp theo, chúng ta sẽ nói về CTE, một phương pháp nâng cao để trả về và modify dữ liệu.

## Tìm hiểu CTE

Trong section này, chúng ta sẽ nói về CTE. Section này được chia thành ba phần. Thứ nhất, chúng ta sẽ nói về khái niệm CTE; thứ hai, chúng ta sẽ thảo luận cách CTE được implement bắt đầu từ PostgreSQL 12; và cuối cùng, chúng ta sẽ khám phá một số ví dụ về cách sử dụng CTE.

### Khái niệm CTE

CTE, hay common table expression, là một temporary result lấy từ một SQL statement. Statement này có thể chứa instruction `SELECT`, `INSERT`, `UPDATE` hoặc `DELETE`. Lifetime của CTE bằng với lifetime của query. Đây là một ví dụ về định nghĩa CTE:

```text
WITH cte_name (column_list) AS (
  CTE_query_definition
)
statement;
```

Ví dụ, nếu muốn tạo một temporary dataset với tất cả post do author `enrico_pirozzi` viết, chúng ta phải viết như sau:

```text
forumdb=> with posts_author_1 as
  (select p.* from posts p
  inner join users u on p.author=u.pk
  where username='enrico_pirozzi')
select pk,title from posts_author_1;
  pk |             title
 ----+------------------------------
   3 | A view of   Data types in C++
(1 row)
```

Chúng ta cũng có thể viết cùng điều này bằng cách sử dụng một inline view:

```text
forumdb=> select pk,title from
(select p.* from posts p inner join users u on p.author=u.pk where
u.username='enrico_pirozzi') posts_author_1;
 pk |             title
----+------------------------------
  3 | A view of   Data types in C++
(1 row)
```

Như có thể thấy, result giống nhau. Điểm khác biệt là trong ví dụ đầu tiên, CTE tạo ra một temporary resultset, còn query thứ hai, inline view, thì không.

### CTE trong PostgreSQL từ version 12

Bắt đầu từ PostgreSQL version 12, mọi thứ đã thay đổi, và hai option mới được giới thiệu cho việc execution một CTE, đó là `MATERIALIZED` và `NOT MATERIALIZED`. Nếu muốn thực hiện một CTE materialize một temporary resultset, chúng ta phải thêm keyword `materialized`:

```text
forumdb=> with posts_author_1 as materialized
 (select p.* from posts p
 inner join users u on p.author=u.pk
 where username='enrico_pirozzi')
select pk,title from posts_author_1;
 pk |             title
----+------------------------------
  3 | A view of   Data types in C++
(1 row)
```

Query được viết ở đây materialize một temporary resultset, giống như đã tự động xảy ra trong các version trước của PostgreSQL. Nếu viết query với option `NOT MATERIALIZE`, PostgreSQL sẽ không materialize bất kỳ temporary resultset nào:

```text
forumdb=> with posts_author_1 as not materialized
 (select p.* from posts p
 inner join users u on p.author=u.pk
 where username='enrico_pirozzi')
select pk,title from posts_author_1;
 pk |                  title
----+------------------------------
  3 | A view of     Data types in C++
(1 row)
```

Nếu không chỉ định option nào, mặc định là `NOT MATERIALIZED`, và điều này có thể là một vấn đề nếu đang migrate một database từ một minor version sang PostgreSQL 12. Đó là vì behavior của query planner có thể thay đổi, và performance cũng có thể thay đổi.

Từ version 12, chúng ta phải thêm option `MATERIALIZED` nếu muốn các query có behavior performance giống với behavior đã có ở các version trước.

### CTE – các use case

Bây giờ hãy trình bày một số ví dụ về CTE:

1. Trước tiên, chúng ta sẽ tạo hai table mới:

   - `t_posts`, với tất cả record hiện có trong table post
   - `delete_posts`, với cùng data structure như table `posts`

```text
forumdb=> create temp table t_posts as select * from posts;
SELECT 3

forumdb=> create table delete_posts as select * from posts limit 0;
SELECT 0
```

Các value ban đầu của các table `t_posts` và `delete_posts` như sau:

```text
forumdb=> select pk,title,category from t_posts ;
    pk |              title                 | category
----+------------------------------+----------
     1 | Indexing PostgreSQL                |          1
     2 | Indexing Mysql                     |          1
     3 | A view of    Data types in C++ |              3
(3 rows)
```
