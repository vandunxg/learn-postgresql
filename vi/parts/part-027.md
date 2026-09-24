## Các statement xử lý exception

PL/pgSQL cũng có thể xử lý exception. Block `BEGIN...END` của một function cho phép option `EXCEPTION`, hoạt động như một catch cho các exception. Ví dụ, nếu viết một function để chia hai số, chúng ta có thể gặp vấn đề khi chia cho 0:

```text
forumdb=> CREATE OR REPLACE FUNCTION my_first_except (x real, y real )
returns real as
$$
DECLARE
   ret real;
BEGIN
   ret := x / y;
   return ret;
END;
$$
language 'plpgsql';
CREATE FUNCTION
```

Function này hoạt động tốt nếu `y <> 0`, như có thể thấy ở đây:

```text
forumdb=> \x
Expanded display is off.
forumdb=> select my_first_except(4,2);
   my_first_except
-----------------
                  2
(1 row)
```

Tuy nhiên, nếu `y` nhận value 0, chúng ta gặp vấn đề:

```text
forumdb=> select my_first_except(4,0);
ERROR:    division by zero
CONTEXT: PL/pgSQL function my_first_except(real,real) line 5 at
assignment
```

Để giải quyết vấn đề này, chúng ta phải xử lý exception. Để làm vậy, chúng ta phải viết lại function theo cách sau:

```text
forumdb=> CREATE OR REPLACE FUNCTION my_second_except (x real, y real )
returns real as
$$
DECLARE
   ret real;
BEGIN
   ret := x / y;
   return ret;
EXCEPTION
   WHEN division_by_zero THEN
         RAISE INFO 'DIVISION BY ZERO';
         RAISE INFO 'Error % %', SQLSTATE, SQLERRM;
         RETURN 0;
END;
$$
language 'plpgsql' ;
CREATE FUNCTION
```

Các variable `SQLSTATE` và `SQLERRM` chứa status và message gắn với error được tạo ra. Bây giờ, khi thực thi function thứ hai, chúng ta không còn nhận error từ PostgreSQL nữa:

```text
forumdb=> select my_second_except(4,0);
INFO:      DIVISION BY ZERO
INFO:      Error 22012 division by zero
 my_second_except
------------------
                     0
(1 row)
```

Danh sách các error mà PostgreSQL có thể quản lý có tại https://www.postgresql.org/docs/current/errcodes-appendix.html.

## Security definer

Option này cho phép user invoke một function như thể họ là owner của function đó. Nó có thể hữu ích trong mọi trường hợp chúng ta muốn hiển thị data mà average user không có quyền access.

Ví dụ, trong PostgreSQL có một system view tên là `pg_stat_activity`, cho phép chúng ta xem PostgreSQL hiện đang làm gì.

Với user forum, hãy thực thi statement này:

```text
postgres@learn_postgresql:~$ psql -U forum forumdb
forumdb=>

forumdb=> select pid,query from pg_stat_activity          ;
   pid |                       query
-----+------------------------------------------
    74 | <insufficient privilege>
    75 | <insufficient privilege>
   217 | select pid,query from pg_stat_activity ;
   [..]
```

Như có thể thấy ở trên, có một số result là `<insufficient privilege>`. Dưới đây là các bước để giải quyết vấn đề này:

- Kết nối tới database với user postgres:

  ```text
  postgres@learn_postgresql:~$ psql forumdb
  forumdb=#
  ```

- Bây giờ hãy thực thi function `my_stat_activity()` được viết ở đây:

  ```text
  forumdb=# create function forum.my_stat_activity()
  returns table (pid integer,query text)
  as $$
          select pid, query   from pg_stat_activity;
  $$ language 'sql'
  security definer;
  ```

- Hãy cấp execute permission trên function `forum.my_stat_activity` cho user forum. Chúng ta sẽ tìm hiểu feature này trong Chapter 10, Granting and Revoking Permissions:

  ```text
  forumdb=# grant execute on function forum.my_stat_activity TO forum;
  ```

- Kết nối lại tới database với user forum:

  ```text
  postgres@learn_postgresql:~$ psql -U forum forumdb
  forumdb=>
  ```

- Bây giờ hãy thực thi query bên dưới:

  ```text
  forumdb=> select * from my_stat_activity();
   pid |                 query
  -----+-----------------------------------
     74 |
     75 |
    271 | select * from my_stat_activity();
    [..]
  ```

Chúng ta không còn gặp vấn đề trước đó. Đó là vì security definer cho phép function `forum.my_stat_activity()` được thực thi với permission của user đã tạo nó; trong trường hợp này, user tạo function là user postgres.

## Tổng kết

Trong chapter này, chúng ta đã giới thiệu thế giới của server-side programming. Chủ đề này rộng đến mức có những cuốn sách riêng chỉ viết về nó. Chúng ta đã cố gắng giúp bạn hiểu rõ hơn các concept chính của server-side programming. Chúng ta đã nói về các data type chính được PostgreSQL quản lý, sau đó xem cách có thể tạo data type mới bằng composite data type. Chúng ta cũng đề cập đến SQL function và polymorphic function, và cuối cùng cung cấp một số thông tin về ngôn ngữ PL/pgSQL.

Trong chapter tiếp theo, chúng ta sẽ dùng các concept này để giới thiệu event management trong PostgreSQL. Chúng ta sẽ nói về event management thông qua việc sử dụng trigger và các function gắn với chúng.

## Kiểm tra kiến thức

- Có thể mở rộng feature và data type trong PostgreSQL không?

  Có, có thể mở rộng PostgreSQL về data type và function.

  Xem section The concept of extensibility để biết thêm chi tiết.

- PostgreSQL có chỉ support relational database không?

  Không, PostgreSQL cũng support NoSQL database.

  Xem section The NoSql data type để biết thêm chi tiết.

- PostgreSQL có support SQL function không?

  Có, chúng ta có thể viết mọi loại SQL function.

  Xem section SQL functions để biết thêm chi tiết.

- PostgreSQL có một procedural language built-in mặc định không?

  Có, PostgreSQL có một procedural language built-in mặc định tên là PL/pgSQL.

  Xem section PL/pgSQL functions để biết thêm chi tiết.

- Với tư cách user không có administrative privilege, chúng ta có thể đọc một table cần administrative permission để đọc không?

  Có; với tư cách administrator user, hãy tạo một function đọc table, định nghĩa function bằng clause security definer, và cấp execution permission của function cho non-administrator user.

  Xem section Security definer để biết thêm chi tiết.

## Tài liệu tham khảo

- PostgreSQL – data types official documentation: https://www.postgresql.org/docs/current/datatype.html
- PostgreSQL – SQL functions official documentation: https://www.postgresql.org/docs/current/xfunc-sql.html
- PostgreSQL – PL/pgSQL official documentation: https://www.postgresql.org/docs/current/plpgsql.html
- PostgreSQL 11 Server Side Programming Quick Start Guide: https://subscription.packtpub.com/book/data/9781789342222/1

## Tìm hiểu thêm trên Discord

Để tham gia cộng đồng Discord của cuốn sách này, nơi bạn có thể chia sẻ feedback, đặt câu hỏi cho tác giả và tìm hiểu về các bản phát hành mới, hãy follow QR code bên dưới:

https://discord.gg/jYWCjF6Tku

# 8 Triggers và Rules

Trong chapter trước, chúng ta đã nói về server-side programming. Trong chapter này, chúng ta sẽ dùng các concept được giới thiệu ở chapter trước để quản lý việc lập trình các event trong PostgreSQL.

Điều đầu tiên chúng ta cần xử lý là event trong PostgreSQL thực sự là gì. Trong PostgreSQL, các event có thể là các statement `SELECT`/`INSERT`/`UPDATE` và `DELETE`. Ngoài ra còn có các event liên quan đến thao tác data definition language (DDL); tuy nhiên, chúng ta sẽ nói về các event đó trong Chapter 17, Event Triggers.

Trong PostgreSQL có hai cách để xử lý event:

- Rules
- Triggers

Trong chapter này, chúng ta sẽ khám phá cả hai cách và xem khi nào nên dùng cách này thay vì cách kia. Như một điểm bắt đầu, chúng ta có thể nói generally rằng rules thường là các event handler đơn giản, trong khi triggers là các event handler phức tạp hơn. Triggers và rules thường được dùng để update accumulator và modify hoặc delete record thuộc các table khác với table nơi chúng ta modify record. Chúng là các tool rất mạnh, cho phép chúng ta thực hiện operation trên các table khác với table nơi chúng ta modify data. Triggers và rules cũng sẽ được dùng trong chapter tiếp theo khi chúng ta nói về partitioning. Đó là vì trong PostgreSQL vẫn còn một partitioning model dựa trên trigger và rule.

Trong chapter này, chúng ta sẽ nói về các nội dung sau:

- Khám phá rules trong PostgreSQL
- Quản lý triggers
- Event triggers

## Yêu cầu kỹ thuật

Trước khi bắt đầu, hãy nhớ khởi động Docker container tên `chapter_08`, như minh họa bên dưới:

```text
$ bash run-pg-docker.sh chapter_08
postgres@learn_postgresql:~$ psql -U forum forumdb
```

## Khám phá rules trong PostgreSQL

Như đã đề cập trước đó, rules là các event handler đơn giản. Ở user level, có thể quản lý tất cả event thực hiện write operation, như sau:

- `INSERT`
- `DELETE`
- `UPDATE`

Concept nền tảng phía sau rules là modify flow của một event. Nếu có một event, khi một số condition xảy ra, chúng ta có thể làm những việc sau:

- Không làm gì rồi undo action của event đó.
- Trigger một event khác thay cho event mặc định.
- Trigger một event khác cùng với event mặc định.

Vì vậy, với một write operation, chẳng hạn operation `INSERT`, chúng ta có thể thực hiện một trong ba action sau:

- Cancel operation.
- Thực hiện một operation khác thay cho `INSERT`.
- Execute `INSERT` và thực hiện một operation khác trong cùng transaction.

## Tìm hiểu các biến OLD và NEW

Trước khi bắt đầu làm việc với rules rồi đến triggers, chúng ta cần hiểu concept về các variable `OLD` và `NEW`.

Các variable `OLD` và `NEW` biểu diễn state của row trong table trước hoặc sau event. Các value `OLD` và `NEW` là cursor biểu diễn toàn bộ record. Để hiểu rõ hơn, hãy xét một operation `UPDATE`; trong trường hợp này, variable `OLD` chứa value của record đã có trong table, còn variable `NEW` chứa value mà record của table sẽ có sau operation `UPDATE`.

Ví dụ, hãy xét table tags với các record sau:

```text
forumdb=> select * from tags;
 pk |            tag           | parent
----+-------------------+--------
  1 | Operating Systems |
  2 | Linux                    |        1
  3 | Ubuntu                   |        2
  [..]
```

Giả sử chúng ta muốn thay đổi tag có `pk=3`, từ Ubuntu thành Fedora, bằng operation `UPDATE` sau:

```text
forumdb=> update tags set tag='Fedora' where pk=3;
UPDATE 1
```

Variable `OLD` sẽ có các value sau:

```text
                                  pk        tag        parent
                                  3        Ubuntu        1
```

Variable `NEW` sẽ có các value sau:

```text
                                  pk        tag        parent
                                  3        Fedora         1
```

Về mặt logic, với một số operation, cả variable `OLD` và variable `NEW` đều có thể tồn tại, nhưng với các operation khác thì chỉ một trong hai có thể tồn tại. Dưới đây là cách thể hiện chi tiết hơn:

```text
               Operation/Variable                 NEW                      OLD

                      INSERT                     present                  absent
                      DELETE                     absent                   present
                      UPDATE                     present                  present
```

Bây giờ mọi thứ đã rõ hơn, chúng ta có thể bắt đầu làm việc với rules.

## Rules trên INSERT

Hãy bắt đầu bằng việc giới thiệu syntax của rules:

```text
CREATE [ OR REPLACE ] RULE name AS ON event
     TO table [ WHERE condition ]
     DO [ ALSO | INSTEAD ] { NOTHING | command | ( command ; command ... )
}
```

Như có thể thấy, rule definition cực kỳ đơn giản. Có ba option khi quyết định dùng một rule:

- Option ALSO
- Option INSTEAD
- Option INSTEAD NOTHING

### Option ALSO

Giả sử từ table tags, chúng ta muốn copy tất cả record có value của field tag bắt đầu bằng chữ a vào table a_tag:

1. Trước hết, hãy tạo một table mới tên là `O_tags`:

   ```text
   forumdb=> create table O_tags (
        pk integer not null primary key,
        tag text,
        parent integer);
   CREATE TABLE
   ```

2. Sau đó, hãy tạo rule mới như sau:

   ```text
   forumdb=> create or replace rule r_tags1
        as on INSERT to tags
        where NEW.tag ilike 'O%' DO ALSO
       insert into O_tags(pk,tag,parent)values (NEW.pk,NEW.tag,NEW.
   parent);
   CREATE RULE
   ```

   Trong rule vừa định nghĩa, chúng ta chỉ nói với PostgreSQL rằng mỗi khi một record được insert với value tag bắt đầu bằng chữ “O,” ngoài việc được insert vào table tags, nó cũng phải được insert vào table O_tags.

3. Bây giờ hãy thực hiện query sau:

   ```text
   forumdb=> insert into tags (tag) values ('OpenBSD');
   INSERT 0 1
   ```

4. Sau đó kiểm tra các record trong table tags và các record trong O_tags. Trong table tags, chúng ta sẽ thấy như sau:

   ```text
   forumdb=> select * from tags;
    pk |           tag           | parent
   ----+-------------------+--------
     1 | Operating Systems |
     2 | Linux                   |       1
     3 | Ubuntu                  |       2
     4 | OpenBSD                 |
   (4 rows)
   ```

   Trong table O_tags, chúng ta sẽ thấy như sau:

   ```text
   forumdb=> select * from O_tags;
    pk |     tag    | parent
   ----+---------+--------
     5 | OpenBSD |
   (1 row)
   ```

Record hiện diện trong cả hai table. Một câu hỏi đáng đặt ra là rules được execute trước hay sau event. Ví dụ, rule mới tạo được execute trước `INSERT` hay sau `INSERT`? Câu trả lời là rules trong PostgreSQL luôn được execute trước event.

### Option INSTEAD OF

Bây giờ, giả sử chúng ta muốn move tất cả record có field tag bắt đầu bằng chữ F hoặc f vào table F_tags:

1. Trước hết, hãy tạo một table mới tên là `F_tags`:

   ```text
   forumdb=> create table F_tags (
    pk integer not null primary key ,
    tag text,
    parent integer);
   CREATE TABLE
   ```

2. Sau đó, hãy tạo rule mới:

    ```text
    forumdb=> create or replace rule r_tags2
         as on INSERT to tags
    ```
