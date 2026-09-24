PostgreSQL xử lý các data type NoSQL sau:

- hstore
- xml
- json/jsonb

Bây giờ chúng ta sẽ nói về hstore và json.

## Data type hstore

`hstore` là data type NoSQL đầu tiên được implement trong PostgreSQL. Data type này được dùng để lưu các cặp key-value trong một value duy nhất. Trước khi làm việc với data type `hstore`, chúng ta cần enable extension `hstore` trên server:

```text
forumdb=> create extension hstore ;
CREATE EXTENSION
```

Hãy xem cách sử dụng data type `hstore` qua một ví dụ. Giả sử chúng ta muốn hiển thị tất cả post cùng với username và category của chúng:

```text
forumdb=> select p.pk,p.title,u.username,c.title as category
from posts p
inner join users u on p.author=u.pk
left join categories c on p.category=c.pk
order by 1;
-[ RECORD 1 ]--------------------------
pk         | 5
title      | Indexing PostgreSQL
username | luca_ferrari
category | Database
-[ RECORD 2 ]--------------------------
pk         | 6
title      | Indexing Mysql
username | luca_ferrari
category | Database
-[ RECORD 3 ]--------------------------
pk         | 7
title      | A view of   Data types in C++
username | enrico_pirozzi
category | Programming Languages
```

Bây giờ giả sử các table `posts`, `users` và `categories` là những table rất lớn, và chúng ta muốn lưu toàn bộ thông tin về username và category trong một field duy nhất nằm bên trong table `posts`. Nếu làm được điều này, chúng ta sẽ không còn cần join ba table lớn nữa. Trong trường hợp này, `hstore` có thể giúp chúng ta:

```text
forumdb=> select p.pk,p.title,hstore(ARRAY['username',u.
username,'category',c.title]) as options
from posts p
inner join users u on p.author=u.pk
left join categories c on p.category=c.pk
order by 1;
-[ RECORD 1 ]--------------------------
pk        | 5
title     | Indexing PostgreSQL
options | "category"=>"Database", "username"=>"luca_ferrari"
-[ RECORD 2 ]--------------------------
pk        | 6
title     | Indexing Mysql
options | "category"=>"Database", "username"=>"luca_ferrari"
-[ RECORD 3 ]--------------------------
pk        | 7
title     | A view of     Data types in C++
options | "category"=>"Programming Languages", "username"=>"enrico_
pirozzi"
```

Query trước hết đưa các value của field username và category vào một array, sau đó chuyển chúng thành `hstore`. Bây giờ, nếu muốn lưu data vào một table mới tên là `posts_options`, chúng ta phải thực hiện như sau:

```text
forumdb=> create table posts_options as
select p.pk,p.title,hstore(ARRAY['username',u.username,'category',c.
title]) as options
from posts p
inner join users u on p.author=u.pk
left join categories c on p.category=c.pk
order by 1;
SELECT 3
```

Bây giờ chúng ta có một table mới với structure sau:

```text
forumdb=> \d posts_options
                  Table "forum.posts_options"
   Column    |    Type   | Collation | Nullable | Default
---------+---------+-----------+----------+---------
   pk        | integer |              |             |
   title     | text      |            |             |
   options | hstore      |            |             |
```

Tiếp theo, giả sử chúng ta muốn tìm tất cả record có `category = 'Database'`. Chúng ta phải execute câu lệnh sau:

```text
forumdb=> select * from posts_options where options->'category'
='Database';
-[ RECORD 1 ]--------------------------
pk          | 5
title       | Indexing PostgreSQL
options | "category"=>"Database", "username"=>"luca_ferrari"
-[ RECORD 2 ]--------------------------
pk          | 6
title       | Indexing Mysql
options | "category"=>"Database", "username"=>"luca_ferrari"
```

Vì `hstore`, cũng như các data type `json/jsonb`, không phải là structured data type, chúng ta có thể insert bất kỳ key-value nào khác mà không cần định nghĩa nó trước. Ví dụ:

```text
forumdb=> insert into posts_options (pk,title,options) values (7,'my last
post','"enabled"=>"false"') ;
INSERT 0 1
```

Kết quả của việc select trên toàn bộ table sẽ như sau:

```text
forumdb=>        select * from posts_options;
-[ RECORD 1 ]--------------------------
pk          | 5
title       | Indexing PostgreSQL
options | "category"=>"Database", "username"=>"luca_ferrari"
-[ RECORD 2 ]--------------------------
pk          | 6
title     | Indexing Mysql
options | "category"=>"Database", "username"=>"luca_ferrari"
-[ RECORD 3 ]--------------------------
pk        | 7
title     | A view of      Data types in C++
options | "category"=>"Programming Languages", "username"=>"enrico_
pirozzi"
-[ RECORD 4 ]--------------------------
pk        | 7
title     | my last post
options | "enabled"=>"false"
```

Như đã nói ở đầu section này, NoSQL không phải là chủ đề của cuốn sách, nhưng vẫn đáng để xem qua một cách ngắn gọn. Để biết thêm thông tin về data type `hstore`, hãy tham khảo documentation chính thức tại https://www.postgresql.org/docs/current/hstore.html.

## Data type JSON

Trong section này, chúng ta sẽ xem nhanh data type JSON. JSON là viết tắt của JavaScript Object Notation. JSON là một format open standard, được tạo thành từ các cặp key-value. PostgreSQL hỗ trợ native data type JSON. Nó cung cấp nhiều function và operator dùng để thao tác với data JSON. Ngoài data type json, PostgreSQL còn hỗ trợ data type jsonb. Khác biệt giữa hai data type này là data type thứ nhất được biểu diễn nội bộ dưới dạng text, trong khi data type thứ hai được biểu diễn nội bộ theo dạng binary và có thể index. Hãy xem cách sử dụng data type json/jsonb qua một ví dụ.

Giả sử chúng ta muốn hiển thị tất cả post và tag hiện có trong database `forumdb`. Theo cách SQL relational cổ điển, chúng ta sẽ viết như sau:

```text
forumdb=> \x
Expanded display is off.
forumdb=> select p.pk,p.title,t.tag
from posts p
left join j_posts_tags jpt on p.pk=jpt.post_pk
left join tags t on jpt.tag_pk=t.pk
order by 1;
 pk |                 title                  |           tag
----+------------------------------+-------------------
  5 | Indexing PostgreSQL                | Operating Systems
  5 | Indexing PostgreSQL                | Database
  6 | Indexing Mysql                     | Database
  6 | Indexing Mysql                     | Operating Systems
  7 | A view of    Data types in C++ | Database
(5 rows)
```

Bây giờ giả sử chúng ta muốn có một result như sau:

```text
          pk      title                         tag
          5       Indexing PostgreSQL           Operating Systems,Database
          6       Indexing PostgreSQL           Database,Operating Systems
          7       A view of Data types in C++   Database
```

Theo cách relational, chúng ta phải aggregate data bằng hai field đầu tiên và thực hiện như sau:

```text
forumdb=> \x
Expanded display is on.
forumdb=> select p.pk,p.title,string_agg(t.tag,',') as tag
from posts p
left join j_posts_tags jpt on p.pk=jpt.post_pk
left join tags t on jpt.tag_pk=t.pk
group by 1,2
order by 1;
-[ RECORD 1 ]-----------------------
pk     | 5
title | Indexing PostgreSQL
tag    | Operating Systems,Database
-[ RECORD 2 ]-----------------------
pk     | 6
title | Indexing Mysql
tag    | Database,Operating Systems
-[ RECORD 3 ]-----------------------
pk     | 7
title | A view of      Data types in C++
tag      | Database
```

Bây giờ hãy hình dung chúng ta muốn generate một JSON structure đơn giản; chúng ta sẽ execute query sau:

```text
forumdb=> select row_to_json(q) as json_data from (
 select p.pk,p.title,string_agg(t.tag,',') as tag
 from posts p
 left join j_posts_tags jpt on p.pk=jpt.post_pk
 left join tags t on jpt.tag_pk=t.pk
group by 1,2 order by 1) Q;
-[ RECORD 1 ]-----------------------
json_data | {"pk":5,"title":"Indexing PostgreSQL","tag":"Operating
Systems,Database"}
-[ RECORD 2 ]-----------------------
json_data | {"pk":6,"title":"Indexing Mysql","tag":"Database,Operating
Systems"}
-[ RECORD 3 ]-----------------------
json_data | {"pk":7,"title":"A view of           Data types in
C++","tag":"Database"}
```

Như có thể thấy, chỉ với một query đơn giản, chúng ta có thể chuyển từ biểu diễn SQL cổ điển sang biểu diễn NoSQL. Bây giờ hãy tạo một table mới tên là `post_json`. Table này sẽ chỉ có một field jsonb tên là `jsondata`:

```text
forumdb=> create table post_json (jsondata jsonb);
CREATE TABLE
forumdb=> \d post_json
                 Table "forum.post_json"
  Column    | Type   | Collation | Nullable | Default
----------+-------+-----------+----------+---------
 jsondata | jsonb |                  |             |
```

Bây giờ hãy insert một số data vào table `post_json`:

```text
forumdb=> insert into post_json(jsondata)
select row_to_json(q) as json_data from (
   select p.pk,p.title,string_agg(t.tag,',') as tag
   from posts p
   left join j_posts_tags jpt on p.pk=jpt.post_pk
   left join tags t on jpt.tag_pk=t.pk
group by 1,2 order by 1) Q;
INSERT 0 3
```

Bây giờ table `post_json` có các record sau:

```text
forumdb=> select jsonb_pretty(jsondata) from post_json;
-[ RECORD 1 ]+-----------------------
jsonb_pretty | {                                                       +
                |      "pk": 5,                                        +
                |      "tag": "Operating Systems,Database",            +
                |      "title": "Indexing PostgreSQL"                  +
                | }
-[ RECORD 2 ]+-----------------------
jsonb_pretty | {                                                       +
                |      "pk": 6,                                        +
                |      "tag": "Database,Operating Systems",            +
                |      "title": "Indexing Mysql"                       +
                | }
-[ RECORD 3 ]+-----------------------
jsonb_pretty | {                                                       +
                |      "pk": 7,                                        +
                |      "tag": "Database",                              +
                |      "title": "A view of       Data types in C++"+
                | }
```

Nếu muốn tìm tất cả data có `tag = "Database"`, chúng ta có thể dùng operator `@>` của jsonb. Operator này kiểm tra liệu JSON value bên trái có chứa các entry JSON path/value bên phải ở top level hay không; query sau cho phép thực hiện việc tìm kiếm này:

```text
forumdb=> select jsonb_pretty(jsondata) from post_json where jsondata @>
'{"tag":"Database"}';


-[ RECORD 1 ]+-----------------------
jsonb_pretty | {                                                       +
                |      "pk": 7,                                        +
                |      "tag": "Database",                              +
                |      "title": "A view of     Data types in C++"+
                | }
```

Những gì chúng ta vừa viết chỉ là một phần rất nhỏ trong những việc có thể làm với NoSQL data model. JSON được dùng rộng rãi khi làm việc với các table lớn và khi cần một data structure giảm thiểu số lượng join phải thực hiện trong giai đoạn tìm kiếm. Thảo luận chi tiết về thế giới NoSQL nằm ngoài scope của cuốn sách này, nhưng chúng tôi muốn mô tả ngắn gọn rằng PostgreSQL cũng mạnh đến mức nào trong cách tiếp cận unstructured data. Để biết thêm thông tin, hãy xem documentation chính thức tại https://www.postgresql.org/docs/current/functions-json.html.

Sau khi hiểu data type là gì và những data type nào có thể được dùng trong PostgreSQL, trong section tiếp theo chúng ta sẽ xem cách sử dụng data type bên trong function.

## Khám phá function và language

PostgreSQL có khả năng execute server-side code. Có nhiều cách cung cấp cho PostgreSQL code cần được execute. Ví dụ, user có thể tạo function bằng các programming language khác nhau. Các language chính được PostgreSQL hỗ trợ như sau:

- SQL
- PL/pgSQL
- C

Các language được liệt kê này là built-in language; ngoài ra còn có những language khác mà PostgreSQL có thể quản lý, nhưng trước khi sử dụng chúng, chúng ta cần install chúng trên system. Một số language được hỗ trợ khác như sau:

- PL/Python
- PL/Perl
- PL/tcl
- PL/Java

Trong section này, chúng ta sẽ nói về function SQL và PL/pgSQL.

## Functions

Cấu trúc command dùng để định nghĩa một function như sau:

```text
CREATE FUNCTION function_name(p1 type, p2 type,p3 type, ....., pn type)
    RETURNS type AS
BEGIN
   -- function logic
END;
LANGUAGE language_name
```

Các bước sau luôn áp dụng cho bất kỳ loại function nào mà chúng ta muốn tạo:

1. Chỉ định tên function sau các keyword `CREATE FUNCTION`.
2. Lập danh sách các parameter được phân tách bằng dấu phẩy.
3. Chỉ định return data type sau keyword `RETURNS`.
4. Với language PL/pgSQL, đặt code vào giữa block `BEGIN` và `END`.
5. Với language PL/pgSQL, function phải kết thúc bằng keyword `END`, theo sau là dấu chấm phẩy.
6. Xác định language mà function được viết bằng, ví dụ sql hoặc plpgsql, plperl, plpython, v.v.

Đây là scheme cơ bản mà chúng ta sẽ tham chiếu về sau trong chapter; scheme này có thể có một vài biến thể nhỏ trong một số trường hợp cụ thể.

## SQL functions

SQL function là cách dễ nhất để viết function trong PostgreSQL, và chúng ta có thể sử dụng bất kỳ SQL command nào bên trong chúng.

## Basic functions

Section này sẽ chỉ cho bạn những bước đầu tiên trong thế giới SQL function. Ví dụ, function sau thực hiện phép cộng giữa hai số:

```text
forumdb=> CREATE OR REPLACE FUNCTION my_sum(x integer, y integer) RETURNS
integer AS $$
   SELECT x + y;
$$ LANGUAGE SQL;
CREATE FUNCTION



forumdb=> select my_sum(1,2);
   my_sum
--------
        3
(1 row)
```

Như có thể thấy trong ví dụ trước, code function được đặt giữa `$$`; chúng ta có thể xem `$$` như các label. Function có thể được gọi bằng statement `SELECT` mà không cần bất kỳ clause `FROM` nào. Các argument của SQL function có thể được tham chiếu trong function body bằng số (cách cũ) hoặc bằng tên của chúng (cách mới). Ví dụ, chúng ta có thể viết cùng function theo cách này:

```text
CREATE OR REPLACE FUNCTION my_sum(integer, integer) RETURNS integer AS $$
 SELECT $1 + $2;
$$ LANGUAGE SQL;
```

Trong function trước, chúng ta thấy cách cũ để tham chiếu parameter bên trong function. Theo cách cũ, các parameter được tham chiếu theo vị trí, vì vậy value `$1` tương ứng với parameter thứ nhất của function, `$2` tương ứng với parameter thứ hai, v.v. Trong code của SQL function, chúng ta có thể sử dụng tất cả SQL command, bao gồm những command đã thấy trong các chapter trước.

## SQL functions trả về một set các element

Trong section này, chúng ta sẽ xem cách tạo một SQL function trả về một result set của một data type. Ví dụ, giả sử chúng ta muốn viết một function nhận `p_title` làm parameter và xóa tất cả record có `title=p_title`, đồng thời trả về tất cả key của các record đã xóa. Function sau sẽ thực hiện được điều đó:

```text
forumdb=> CREATE OR REPLACE FUNCTION delete_posts(p_title text) returns
setof integer as $$
delete from posts where title=p_title returning pk;
$$
LANGUAGE SQL;
CREATE FUNCTION
```

Đây là tình trạng trước khi chúng ta gọi function `delete_posts`:

```text
forumdb=> select pk,title from posts order by pk;
 pk |                title
----+------------------------------
   5 | Indexing PostgreSQL
   6 | Indexing Mysql
   7 | A view of     Data types in C++
(3 rows)
```
