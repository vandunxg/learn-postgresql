```text
      pk |     tag        | parent
----+--------------+--------
    1 | alpine linux |
(1 row)
```

```text
forumdb=> select * from new_tags ;
     pk |     tag        | parent
----+--------------+--------
    1 | alpine linux |
(1 row)
```

Bây giờ hãy xem điều gì xảy ra nếu một record đổi tag từ `alpine linux` thành `bsd unix`:

```text
forumdb=> update new_tags set tag='bsd unix' where tag='alpine linux';
   move_record
 -------------


(1 row)


UPDATE 0


forumdb=> select * from new_tags ;
     pk |   tag     | parent
----+----------+--------
    1 | bsd unix |
(1 row)


forumdb=> select * from new_a_tags ;
     pk | tag | parent
----+-----+--------
(0 rows)


forumdb=> select * from new_b_tags ;
     pk |   tag     | parent
----+----------+--------
    1 | bsd unix |
(1 row)
```

Rule hoạt động! Trong bài tập ngắn này, chúng ta đã thử đưa ra một ví dụ về việc quản lý rule hoàn chỉnh. Đây là một ví dụ mang tính minh họa, và có nhiều cách khác để đạt được cùng mục tiêu.

Trong section tiếp theo, chúng ta sẽ khám phá một cách khác để quản lý event trong PostgreSQL: trigger.

## Quản lý trigger trong PostgreSQL

Ở section trước, chúng ta đã nói về rule. Trong section này, chúng ta sẽ nói về trigger, trigger là gì và cách sử dụng chúng. Chúng ta cần bắt đầu bằng việc hiểu trigger là gì; nếu đã hiểu rule là gì thì việc này sẽ đơn giản. Ở section trước, chúng ta định nghĩa rule là event handler đơn giản; bây giờ chúng ta có thể định nghĩa trigger là event handler phức tạp. Với trigger, cũng như với rule, có các record `NEW` và `OLD`, mang cùng ý nghĩa trong trigger như trong rule. Với trigger, các event có thể quản lý là `INSERT`/`DELETE`/`UPDATE` và `TRUNCATE`. Một khác biệt nữa giữa rule và trigger là với trigger, có thể xử lý các event `INSERT`/`UPDATE`/`DELETE` và `TRUNCATE` trước hoặc sau khi chúng xảy ra. Với trigger, chúng ta cũng có thể sử dụng option `INSTEAD OF`, nhưng chỉ trên view.

Do đó, chúng ta có thể quản lý các event sau:

- `BEFORE INSERT/UPDATE/DELETE/TRUNCATE`
- `AFTER INSERT/UPDATE/DELETE/TRUNCATE`
- `INSTEAD OF INSERT/UPDATE/DELETE`

Với rule, chỉ có thể có record `NEW` cho operation `INSERT`, record `NEW` và `OLD` cho operation `UPDATE`, và record `OLD` cho operation `DELETE`. Hai item đầu tiên trong list cũng có thể được sử dụng trên foreign table cũng như table thực, còn item thứ ba chỉ có thể được sử dụng trên view. Để biết thêm thông tin, xem https://www.postgresql.org/docs/current/sql-createtrigger.html.

Bây giờ chúng ta sẽ thực hiện những bước đầu tiên để sử dụng trigger và tìm hiểu cách đạt được các kết quả giống như khi sử dụng rule. Với trigger, chúng ta có thể làm mọi thứ có thể làm với rule và còn nhiều hơn thế.

Trước khi tiếp tục, chúng ta cần ghi nhớ hai điều:

- Nếu trigger và rule cùng đồng thời tồn tại trên cùng một event trong một table, rule luôn được fire trước trigger.
- Nếu có nhiều trigger trên cùng một event của một table (ví dụ `BEFORE INSERT`), chúng được thực thi theo thứ tự alphabet.

Có một category trigger khác, được gọi là event trigger, sẽ được trình bày trong section *Event triggers*.

## Cú pháp trigger

Như được mô tả trong tài liệu chính thức, cú pháp để định nghĩa một trigger như sau:

```text
CREATE [ CONSTRAINT ] TRIGGER name { BEFORE | AFTER | INSTEAD OF } { event
    [ OR ... ] }
    ON table_name
    [ FROM referenced_table_name ]
    [ NOT DEFERRABLE | [ DEFERRABLE ] [ INITIALLY IMMEDIATE | INITIALLY
    DEFERRED ] ]
    [ REFERENCING { { OLD | NEW } TABLE [ AS ] transition_relation_name } [
    ... ] ]
    [ FOR [ EACH ] { ROW | STATEMENT } ]
    [ WHEN ( condition ) ]
    EXECUTE { FUNCTION | PROCEDURE } function_name ( arguments )

where event can be one of:

    INSERT
    UPDATE [ OF column_name [, ... ] ]
    DELETE
    TRUNCATE
```

Chúng ta sẽ chỉ xem xét những khía cạnh được sử dụng nhiều nhất của cú pháp này; để biết thêm thông tin, xem https://www.PostgreSQL.org/docs/current/sql-createtrigger.html. Các điểm chính về việc thực thi một trigger như sau:

- Event mà chúng ta muốn xử lý, ví dụ `INSERT`, `DELETE` hoặc `UPDATE`.
- Khi nào chúng ta muốn bắt đầu thực thi `TRIGGER` (ví dụ `BEFORE INSERT`).
- Trigger gọi một function để thực hiện một action.

Function được trigger gọi phải được định nghĩa theo một cách cụ thể, như prototype sau:

```text
CREATE OR REPLACE FUNCTION function_name RETURNS trigger as
$$
DECLARE
....
BEGIN


     RETURN
END;
$$
LANGUAGE 'plpgsql';
```

Các function được trigger gọi là những function không có input parameter và phải trả về type `TRIGGER`; các function này nhận parameter từ record `NEW`/`OLD`. Bắt đầu từ prototype của function trước đó, một định nghĩa `TRIGGER` khả dĩ cho event `BEFORE INSERT` có thể được mô tả như sau:

```text
CREATE TRIGGER trigger_name BEFORE INSERT on table_name FOR EACH ROW
EXECUTE PROCEDURE function_name.
```

Cũng có cú pháp sau:

```text
CREATE TRIGGER trigger_name BEFORE INSERT on table_name FOR EACH STATEMENT
EXECUTE PROCEDURE function_name.
```

Sự khác biệt giữa `FOR EACH ROW` và `FOR EACH STATEMENT` là:

- Trigger được định nghĩa với `FOR EACH ROW` được thực thi cho mỗi row tham gia vào operation (ví dụ, cho mỗi row được insert, update hoặc delete) thỏa mãn condition của trigger.
- Trigger được định nghĩa với `FOR EACH STATEMENT` chỉ được thực thi một lần cho mỗi SQL statement thỏa mãn condition của trigger, bất kể operation liên quan đến bao nhiêu row.

Trong section tiếp theo, chúng ta sẽ thử triển khai những gì đã viết với rule, lần này áp dụng trigger.

## Trigger trên `INSERT`

Trong section này, chúng ta sẽ xem cách tạo những trigger đầu tiên:

1. Hãy quay lại rule mà chúng ta đã viết trong section về option *ALSO*; chúng ta đã viết một rule như sau:

   ```text
   create or replace rule r_tags1
       as on INSERT to tags
       where NEW.tag like 'a%' DO ALSO
    insert into new_a_tags(pk,tag,parent)values (NEW.pk,NEW.tag,NEW.
   parent);
   ```

2. Bây giờ hãy xem cách đạt được cùng mục tiêu bằng trigger. Trước hết, hãy quay lại tình trạng ban đầu:

   ```text
   forumdb=> drop table if exists new_tags cascade;
   forumdb=> create table new_tags as select * from tags limit 0;
   forumdb=> truncate table new_a_tags;
   ```

3. Bây giờ chúng ta có thể tạo function, function này sau đó sẽ được trigger gọi:

   ```text
   forumdb=> CREATE OR REPLACE FUNCTION f_tags() RETURNS trigger as
   $$
   BEGIN
       IF lower(substring(NEW.tag from 1 for 1)) = 'a' THEN
    insert into new_a_tags(pk,tag,parent)values (NEW.pk,NEW.tag,NEW.
   parent);
       END IF;
       RETURN NEW;
   END;
   $$
   LANGUAGE 'plpgsql';
   CREATE FUNCTION
   ```

   Hãy xem kỹ hơn ý nghĩa của code:

   - Statement `lower(substring (NEW.tag from 1 for 1))` lấy character đầu tiên của một string và chuyển nó thành chữ thường.
   - Statement `RETURN NEW` truyền record mới từ table đến `INSERT` trong table `new_tags`.

4. Bây giờ hãy định nghĩa trigger trên event `BEFORE INSERT` của table `t_tags`:

   ```text
   forumdb=> CREATE TRIGGER t_tags BEFORE INSERT on new_tags FOR EACH
   ROW EXECUTE PROCEDURE f_tags();
   CREATE TRIGGER
   ```

5. Vì vậy, khi một value được insert vào table `new_tags`, trước khi thực thi `INSERT`, trigger được thực thi và trả record `NEW` về action mặc định (`INSERT` trên table `new_tags`). Bây giờ hãy kiểm tra xem nó có hoạt động không:

   ```text
   forumdb=> insert into new_tags (pk,tag,parent) values (1,'bsd
   unix',NULL);
   INSERT 0 1

   forumdb=> insert into new_tags (pk,tag,parent) values (2,'alpine
   linux',1);
   INSERT 0 1

   forumdb=> select * from new_tags ;
    pk |      tag        | parent
   ----+--------------+--------
     1 | bsd unix        |
     2 | alpine linux |           1
   (2 rows)


   forumdb=> select * from new_a_tags ;
    pk |      tag        | parent
   ----+--------------+--------
     2 | alpine linux |           1
   (1 row)
   ```

   Như chúng ta có thể thấy ở đây, nó hoạt động!

6. Từ đây, chúng ta sẽ tiếp tục từng bước để hiểu rõ hơn sự khác biệt giữa làm việc với rule và làm việc với trigger. Mục tiêu chúng ta muốn đạt được với trigger là nhận được kết quả giống như kết quả có thể đạt được với rule sau:

   ```text
   create or replace rule r_tags2
    as on INSERT to tags
   where NEW.tag ilike 'b%'
   DO INSTEAD insert into new_b_tags(pk,tag,parent)values (NEW.pk,NEW.
   tag,NEW.parent);
   ```

7. Trước mắt, hãy sử dụng cùng cách làm mà chúng ta đã sử dụng trong rule bằng cách tạo một function mới, function này sau đó sẽ được trigger fire:

   ```text
   forumdb=> CREATE OR REPLACE FUNCTION f2_tags() RETURNS trigger as
   $$
   BEGIN
    IF lower(substring(NEW.tag from 1 for 1)) = 'b' THEN
    insert into new_b_tags(pk,tag,parent)values (NEW.pk,NEW.tag,NEW.
   parent);
    RETURN NULL;
    END IF;
    RETURN NEW;
   END;
   $$
   LANGUAGE 'plpgsql';
   CREATE FUNCTION


   forumdb=> CREATE TRIGGER t2_tags BEFORE INSERT on new_tags FOR EACH
   ROW EXECUTE PROCEDURE f2_tags();
   CREATE TRIGGER
   ```

8. Statement `(substring(NEW.tag from 1 for 1)) = 'b'` gần như giống hệt điều chúng ta đã thấy đầu tiên khi nói về rule. Khác biệt nằm ở `RETURN NULL`, nghĩa là nếu value `NEW.tag` bắt đầu bằng b thì một value `NULL` được trả về action mặc định và `INSERT` trên table `new_tags` sẽ không insert value nào. Ngược lại, nếu condition `IF` không được thỏa mãn thì function trả về `NEW` và record được insert vào table `new_tags`.

   Hãy xem nó có hoạt động không:

   ```text
   forumdb=> truncate new_tags;
   TRUNCATE TABLE
   forumdb=> truncate new_a_tags;
   TRUNCATE TABLE
   forumdb=> truncate new_b_tags;
   TRUNCATE TABLE

   forumdb=> insert into new_tags (pk,tag,parent) values (1,'bsd
   unix',NULL);
   INSERT 0 0
   ```

   Như chúng ta có thể thấy, condition `IF` hoạt động, và kết quả `INSERT 0 0` có nghĩa là không có record nào được insert vào table `new_tags`. Điều này xảy ra vì trigger hoạt động trên event `BEFORE INSERT` và condition `IF` đã chuyển record sang table `new_b_tags`.

9. Bây giờ chúng ta sẽ xem cách viết toàn bộ procedure bằng một trigger duy nhất. Trước hết, hãy quay lại các condition ban đầu của environment. Như trước đó, chúng ta xóa dữ liệu trong các table và, sử dụng option `CASCADE`, xóa trigger đã chọn cùng tất cả trigger liên kết với nó:

   ```text
   forumdb=> TRUNCATE new_tags;
   TRUNCATE TABLE
   forumdb=> TRUNCATE new_a_tags;
   TRUNCATE TABLE
   forumdb=> TRUNCATE new_b_tags;
   TRUNCATE TABLE
   forumdb=>    DROP TRIGGER t_tags ON new_tags CASCADE;
   DROP TRIGGER
   forumdb=>    DROP TRIGGER t2_tags ON new_tags CASCADE;
   DROP TRIGGER
   ```

10. Trong bước cuối cùng này, chúng ta sẽ kết hợp những gì đã viết trong các function `f_tags()` và `f2_tags()` thành một function duy nhất, `f3_tags()`, function này sẽ được fire từ trigger `t3_tags` trên event `BEFORE INSERT`:

    ```text
    forumdb=> CREATE OR REPLACE FUNCTION f3_tags() RETURNS trigger as
    $$
    BEGIN
     IF lower(substring(NEW.tag from 1 for 1)) = 'a' THEN
         insert into new_a_tags(pk,tag,parent)values (NEW.pk,NEW.
    tag,NEW.parent);
         RETURN NEW;
     ELSIF lower(substring(NEW.tag from 1 for 1)) = 'b' THEN
         insert into new_b_tags(pk,tag,parent)values (NEW.pk,NEW.
    tag,NEW.parent);
         RETURN NULL;
    ELSE
         RETURN NEW;
    END IF;
    END;
    $$
    LANGUAGE 'plpgsql';
    CREATE FUNCTION


    forumdb=> CREATE TRIGGER t3_tags BEFORE INSERT on new_tags FOR EACH
    ROW EXECUTE PROCEDURE f3_tags();
    CREATE TRIGGER
    ```

Function này chứa logic của hai function đã thấy trước đó. Bằng cách này, chúng ta có thể giải quyết vấn đề một cách gọn gàng hơn bằng cách sử dụng một function duy nhất và một trigger duy nhất. Hãy xem nó có hoạt động không:

```text
forumdb=> insert into new_tags (pk,tag,parent) values (1,'operating
systems',NULL);
INSERT 0 1


forumdb=> insert into new_tags (pk,tag,parent) values (2,'alpine
linux',1);
INSERT 0 1

forumdb=> insert into new_tags (pk,tag,parent) values (3,'bsd
unix',1);
INSERT 0 0


forumdb=> select * from new_tags ;.
 pk |          tag          | parent
----+-------------------+--------
  1 | operating systems |
  2 | alpine linux          |          1
(2 rows)


forumdb=> select * from new_a_tags ;
    pk |       tag        | parent
----+--------------+--------
      2 | alpine linux |              1
   (1 row)


   forumdb=> select * from new_b_tags ;
    pk |     tag     | parent
   ----+----------+--------
     3 | bsd unix |             1
   (1 row)
```

Như có thể thấy, function hoạt động.

## Variable `TG_OP`

Như được trình bày trong tài liệu chính thức tại https://www.PostgreSQL.org/docs/current/plpgsql-trigger.html, có thể điều khiển trigger trong PostgreSQL bằng các special variable; trong số đó có hai variable chúng ta đã thấy (`NEW` và `OLD`). Có một special variable khác tên là `TG_OP`, cho biết trigger được fire từ event nào. Các value khả dĩ của variable `TG_OP` là `INSERT`, `DELETE`, `UPDATE` và `TRUNCATE`.

## Trigger trên `UPDATE` / `DELETE`

Bây giờ hãy quay lại ví dụ chúng ta đã sử dụng trong *Figure 8.1*. Mục tiêu chúng ta muốn đạt được là tạo một function duy nhất có thể xử lý các event `INSERT`, `DELETE` và `UPDATE`. Trước hết, hãy quay lại các condition ban đầu trong environment:

```text
forumdb=> truncate new_tags;
TRUNCATE TABLE
forumdb=> truncate new_a_tags;
TRUNCATE TABLE
forumdb=> truncate new_b_tags;
TRUNCATE TABLE
forumdb=> drop trigger t3_tags on new_tags cascade;
DROP TRIGGER
```

Bây giờ, như trước đó, chúng ta sẽ tiếp tục từng bước. Bước đầu tiên là viết phần code sẽ được thực hiện trong event `INSERT`. Sau đó, chúng ta sẽ xem cách mở rộng function để quản lý các event `DELETE` và `UPDATE`.
