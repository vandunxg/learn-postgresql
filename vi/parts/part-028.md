```text
where NEW.tag ilike 'f%'
DO INSTEAD insert into f_tags(pk,tag,parent)values (NEW.pk,NEW.
tag,NEW.parent);
```

Lần này, trong rule, chúng ta chỉ nói với PostgreSQL rằng mỗi khi một record được chèn vào với giá trị tag bắt đầu bằng chữ f hoặc chữ F viết hoa, record đó phải được chuyển vào table `f_tags`.

3. Bây giờ hãy thực hiện query sau:

```text
forumdb=> insert into tags (tag) values ('Fedora Linux');
INSERT 0 0
```

Ngay từ câu trả lời `INSERT 0 0`, chúng ta có thể đoán rằng không có gì được chèn vào table `tags`.

4. Bây giờ chúng ta sẽ thực hiện statement sau:

```text
forumdb=> select * from tags;
 pk |           tag           | parent
----+-------------------+--------
  1 | Operating Systems |
  2 | Linux                  |        1
  3 | Ubuntu                 |        2
  4 | OpenBSD                |
(4 rows)
```

5. Như có thể thấy trong snippet trước, value `Fedora Linux` không xuất hiện trong table `tags`, còn trong table `f_tags`, chúng ta sẽ có:

```text
forumdb=> select * from f_tags ;
 pk |        tag        | parent
----+--------------+--------
  6 | Fedora Linux |
(1 row)
```

Rule chúng ta đã định nghĩa bảo đảm rằng record không được chèn vào table `tags` mà được chèn vào table `f_tags`.

6. Là ví dụ cuối cùng về rule INSERT, giả sử chúng ta không muốn có gì được chèn vào mỗi khi một record được chèn với field `tag` bắt đầu bằng chữ R hoặc r.

7. Như trước, hãy thực hiện rule:

```text
forumdb=> create or replace rule r_tags3
    as on INSERT to tags
    where NEW.tag ilike 'r%'
    DO INSTEAD NOTHING;
    CREATE RULE
```

Lần này, chúng ta đã nói với PostgreSQL rằng mỗi khi table `tags` nhận một record có field `tag` bắt đầu bằng chữ r hoặc R, record này không được xem xét. Hãy thử điều chúng ta vừa nói:

```text
forumdb=> insert into tags (tag) values ('Red Hat Linux');
INSERT 0 0
```

8. Lần này câu trả lời từ server vẫn là `INSERT 0 0`, và chúng ta có thể kiểm tra rằng record chưa được chèn vào bất kỳ table nào:

```text
forumdb=> select pk,tag,parent,'tags' as tablename
from tags
union all
select pk,tag,parent,'f_tags' as tablename
from f_tags
order by tablename, tag;
 pk |          tag           | parent | tablename
----+-------------------+--------+-----------
  6 | Fedora Linux           |            | f_tags
  2 | Linux                  |          1 | tags
  4 | OpenBSD                |            | tags
  1 | Operating Systems |                 | tags
  3 | Ubuntu                 |          2 | tags
(5 rows)
```

Như có thể thấy, record không xuất hiện trong bất kỳ table nào. Trong query trước, chúng ta đã sử dụng `UNION ALL`. Nó bao gồm result của hai query. Điều quan trọng là các field type phải tương thích với nhau.

## Rule trên DELETE/UPDATE

Trong section trước, chúng ta đã xem cách sử dụng rule trên các event INSERT. Trong section này, chúng ta sẽ xem cách sử dụng rule trên các event DELETE và UPDATE.

Bây giờ chúng ta sẽ xem một ví dụ hoàn chỉnh về cách sử dụng rule, bắt đầu từ các concept được mô tả ở trên.

Mục tiêu chúng ta muốn đạt được được mô tả trong các bước sau:

1. Tạo một table có tên `new_tags` giống table `tags`; table này sẽ giúp chúng ta có một environment sạch để thực hiện các test.
2. Tạo hai table: một table có tên `new_a_tags` để copy tất cả record có tag bắt đầu bằng chữ a, và một table có tên `new_b_tags` để copy tất cả record có tag bắt đầu bằng chữ b.
3. Tạo tất cả rule INSERT/DELETE/UPDATE để mọi thứ hoạt động.

Hãy bắt đầu.

## Tạo table new_tags

Bước đầu tiên là tạo một table `new_tags` mới. Chúng ta sẽ tạo table này dựa trên table `tags` hiện có:

```text
forumdb=> create table new_tags as select * from tags limit 0;
SELECT 0

forumdb=# \d new_tags
                     Table "public.new_tags"
   Column | Type          | Collation | Nullable | Default
--------+---------+-----------+----------+---------
   pk        | integer |                 |             |
   tag       | text       |              |             |
   parent | integer |                    |             |
```

Statement trước copy structure của các field trong table `tags` vào table `new_tags`, nhưng không copy các constraint hoặc index. Bây giờ chúng ta phải tạo constraint primary key trên table mới:

```text
forumdb=> alter table new_tags alter pk set not null ;
ALTER TABLE
forumdb=> alter table new_tags add constraint new_tags_pk primary key
(pk);
ALTER TABLE
forumdb=# \d new_tags
```

```text
                      Table "public.new_tags"
     Column | Type          | Collation | Nullable | Default
    --------+---------+-----------+----------+---------
     pk       | integer |              | not null |
     tag      | text       |           |            |
     parent | integer |                |            |
    Indexes:
          "new_tags_pk" PRIMARY KEY, btree (pk)
```

Như vậy, bước 1 đã hoàn tất.

## Tạo hai table

Tương tự như vừa làm, chúng ta hãy tạo các table `new_a_tags` và `new_b_tags`. Với table `new_a_tags`, chúng ta sẽ có:

```text
forumdb=> create table new_a_tags as select * from tags limit 0;
SELECT 0
forumdb=> alter table new_a_tags alter pk set not null ;
ALTER TABLE
forumdb=> alter table new_a_tags add constraint new_a_tags_pk primary key
(pk);
ALTER TABLE
forumdb=> \d new_a_tags
                     Table "forum.new_a_tags"
     Column |     Type     | Collation | Nullable | Default
    --------+---------+-----------+----------+---------
     pk       | integer |              | not null |
     tag      | text       |           |            |
     parent | integer |                |            |
    Indexes:
          "new_a_tags_pk" PRIMARY KEY, btree (pk)
```

Tương tự, chúng ta sẽ tạo table `new_b_tags`:

```text
forumdb=>     create table new_b_tags as select * from tags limit 0;
SELECT 0
forumdb=> alter table new_b_tags alter pk set not null ;
ALTER TABLE
forumdb=> alter table new_b_tags add constraint new_b_tags_pk primary key
(pk);
ALTER TABLE
forumdb=> \d new_b_tags
                     Table "forum.new_b_tags"
      Column |    Type   | Collation | Nullable | Default
    --------+---------+-----------+----------+---------
     pk       | integer |             | not null |
     tag      | text     |             |           |
     parent | integer |               |           |
    Indexes:
           "new_b_tags_pk" PRIMARY KEY, btree (pk)
```

Bước 2 đã hoàn tất, và chúng ta đã có mọi thứ cần thiết để bắt đầu ví dụ hoàn chỉnh.

## Quản lý rule trên các event INSERT, DELETE và UPDATE

Mục tiêu chúng ta muốn đạt được được minh họa trong hình sau:

**Hình 8.1: Quản lý rule**

Sơ đồ cho thấy table `new_tags` (`pk` là primary key kiểu `integer`, `tag` kiểu `text`, `parent` kiểu `integer`) được nối tới `new_b_tags` với nhãn "COPY HERE ALL TAGS STARTING WITH 'b'", và được nối tới `new_a_tags` với nhãn "COPY HERE ALL TAGS STARTING WITH 'a'". Hai table đích cũng có `pk` là primary key cùng các column `tag`, `parent` như table `new_tags`.

Chúng ta muốn tất cả tag bắt đầu bằng chữ a được lưu trong table `new_tags` và đồng thời được copy vào table `new_a_tags`; với các tag bắt đầu bằng chữ b cũng tương tự.

Chúng ta phải quản lý rule cho các event INSERT, DELETE và UPDATE theo những cách sau:

- Rule INSERT phải nhận diện tất cả tag bắt đầu bằng chữ a hoặc b và copy các record đó vào table tương ứng, `new_a_tags` và `new_b_tags`.
- Rule DELETE phải nhận diện tất cả tag bắt đầu bằng chữ a hoặc b và xóa các record đó trong table tương ứng, `new_a_tags` và `new_b_tags`.
- Rule UPDATE phải nhận diện tất cả tag bắt đầu bằng chữ a hoặc b; nếu một record thay đổi tag, rule phải kiểm tra xem record đó cần được copy vào hay xóa khỏi các table `new_a_tags` và `new_b_tags`.

## Rule INSERT

Hãy bắt đầu bằng cách tạo hai rule INSERT:

```text
forumdb=# create or replace rule r_new_tags_insert_a as on INSERT to new_
tags where NEW.tag like 'a%' DO ALSO insert into new_a_tags(pk,tag,parent)
values (NEW.pk,NEW.tag,NEW.parent);
CREATE RULE

forumdb=# create or replace rule r_new_tags_insert_b as on INSERT to new_
tags where NEW.tag like 'b%' DO ALSO insert into new_b_tags(pk,tag,parent)
values (NEW.pk,NEW.tag,NEW.parent);
CREATE RULE
```

Như có thể thấy, table `new_tags` hiện có hai rule mới:

```text
forumdb=# \d new_tags
                        Table "forum.new_tags"
       Column |      Type     | Collation | Nullable | Default
    --------+---------+-----------+----------+---------
        pk        | integer |                 | not null |
        tag       | text       |           |            |
        parent | integer |                    |            |
    Indexes:
         "new_tags_pk" PRIMARY KEY, btree (pk)
    Rules:
             r_new_tags_insert_a AS
             ON INSERT TO new_tags
       WHERE new.tag ~~ 'a%'::text DO               INSERT INTO new_a_tags (pk, tag,
    parent)
        VALUES (new.pk, new.tag, new.parent)
          r_new_tags_insert_b AS
          ON INSERT TO new_tags
       WHERE new.tag ~~ 'b%'::text DO          INSERT INTO new_b_tags (pk, tag,
    parent)
        VALUES (new.pk, new.tag, new.parent)
```

Để kiểm tra xem các rule có hoạt động hay không, hãy chèn một số data:

```text
forumdb=> insert into new_tags values(1,'linux',NULL);
INSERT 0 1
forumdb=> insert into new_tags values(2,'alpine linux',1);
INSERT 0 1

forumdb=> insert into new_tags values(3,'bsd unix',NULL);
INSERT 0 1
```

Tiếp theo hãy kiểm tra parent table:

```text
forumdb=> select * from new_tags ;
   pk |     tag        | parent
  ----+--------------+--------
      1 | linux          |
      2 | alpine linux |            1
      3 | bsd unix       |
  (3 rows)
```

Bây giờ hãy xem những gì có trong child table `table_a`:

```text
forumdb=> select * from new_a_tags ;
   pk |     tag        | parent
  ----+--------------+--------
      2 | alpine linux |            1
  (1 row)
```

Và đây là những gì có trong child table `table_b`:

```text
forumdb=> select * from new_b_tags ;
   pk |   tag      | parent
  ----+----------+--------
  3 | bsd unix |
  (1 row)
```

Chúng ta có thể thấy hai rule hoạt động.

## Rule DELETE

Bây giờ hãy tạo các rule DELETE. Chúng ta cần các rule sao cho nếu một record bị xóa khỏi table `new_tags` và bắt đầu bằng chữ a hoặc b, bản copy của nó trong table `new_a_tags` hoặc `new_b_tags` cũng phải bị xóa. Với tất cả record bắt đầu bằng chữ a, chúng ta cần rule sau:

```text
forumdb=> create or replace rule r_new_tags_delete_a as on delete to new_
tags where OLD.tag like 'a%' DO ALSO delete from new_a_tags where pk=OLD.
pk;
CREATE RULE
```

Tương tự, chúng ta cần rule này cho các record bắt đầu bằng chữ b:

```text
forumdb=> create or replace rule r_new_tags_delete_b as on delete to new_
tags where OLD.tag like 'b%' DO ALSO delete from new_b_tags where pk=OLD.
pk;
CREATE RULE
```

Trạng thái hiện tại của table `new_tags` như sau:

```text
forumdb=> \d new_tags
                     Table "forum.new_tags"
     Column |    Type     | Collation | Nullable | Default
    --------+---------+-----------+----------+---------
     pk       | integer |                | not null |
     tag      | text       |              |            |
     parent | integer |                  |            |
    Indexes:
          "new_tags_pk" PRIMARY KEY, btree (pk)
    Rules:
          r_new_tags_delete_a AS
          ON DELETE TO new_tags
        WHERE old.tag ~~ 'a%'::text DO         DELETE FROM new_a_tags
      WHERE new_a_tags.pk = old.pk
          r_new_tags_delete_b AS
          ON DELETE TO new_tags
        WHERE old.tag ~~ 'b%'::text DO       DELETE FROM new_b_tags
       WHERE new_b_tags.pk = old.pk
          r_new_tags_insert_a AS
          ON INSERT TO new_tags
       WHERE new.tag ~~ 'a%'::text DO         INSERT INTO new_a_tags (pk, tag,
    parent)
        VALUES (new.pk, new.tag, new.parent)
          r_new_tags_insert_b AS
          ON INSERT TO new_tags
       WHERE new.tag ~~ 'b%'::text DO         INSERT INTO new_b_tags (pk, tag,
    parent)
        VALUES (new.pk, new.tag, new.parent)
```

Hãy kiểm tra xem hai rule mới có hoạt động hay không:

```text
forumdb=> delete from new_tags where tag = 'alpine linux';
DELETE 1
forumdb=> delete from new_tags where tag = 'bsd unix';
DELETE 1

forumdb=> select * from new_tags ;
   pk |   tag   | parent
  ----+-------+--------
      1 | linux |
  (1 row)

forumdb=> select * from new_a_tags ;
   pk | tag | parent
  ----+-----+--------
  (0 rows)

forumdb=> select * from new_b_tags ;
   pk | tag | parent
  ----+-----+--------
  (0 rows)
```

Từ đây chúng ta có thể thấy các rule mới hoạt động.

## Rule UPDATE

Bây giờ chúng ta cần giới thiệu một rule kiểm tra xem tag có được update bằng một từ bắt đầu bằng a hoặc b hay không. Cách đơn giản là trước tiên tạo một function thực hiện việc kiểm tra này, rồi tạo một rule dựa trên function đó. Hãy bắt đầu bằng cách tạo function:

```text
forumdb=> create or replace function move_record (p_pk integer, p_tag
text, p_parent integer,p_old_pk integer,p_old_tag text ) returns void
language plpgsql as
$$
BEGIN
     if left(lower(p_tag),1) in ('a','b') THEN
           delete from new_tags where pk = p_old_pk;
           insert into new_tags values(p_pk,p_tag,p_parent);
   end if;
END;
$$;
CREATE FUNCTION
```

Function này nhận năm parameter làm input; ba parameter đầu tiên là các value `NEW` đến từ update, còn hai parameter cuối là các value `OLD` của record hiện có trong record. Function kiểm tra xem record trong table có bắt đầu bằng chữ a hoặc b hay không, rồi xóa record cũ và chèn record mới.

Cuối cùng, rule là:

```text
forumdb=> create or replace rule r_new_tags_update_a as on UPDATE to new_
tags DO ALSO select move_record(NEW.pk,NEW.tag,NEW.parent,OLD.pk,OLD.tag);
CREATE RULE
```

Rule gọi function khi có một update. Hãy xem rule này có hoạt động hay không:

```text
forumdb=> update new_tags set tag='alpine linux' where tag='linux';
 move_record
-------------


(1 row)
UPDATE 0

forumdb=> select * from new_a_tags ;
```
