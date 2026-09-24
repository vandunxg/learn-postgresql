Function xử lý cả ba event sẽ là function `fcopy_tags()`; function này sẽ được trigger `tcopy_tags` gọi. Function `fcopy_tags()` sử dụng variable `TG_OP` để có thể phân biệt giữa các event `INSERT`, `UPDATE` và `DELETE`.

Bắt đầu bằng cách viết function `fcopy_tags()` để xử lý event `INSERT`:

```text
   forumdb=> CREATE OR REPLACE FUNCTION fcopy_tags() RETURNS trigger as
   $$
   BEGIN
   IF TG_OP = 'INSERT' THEN
          IF lower(substring(NEW.tag from 1 for 1)) = 'a' THEN
              insert into new_a_tags(pk,tag,parent)values (NEW.pk,NEW.tag,NEW.
   parent);
          ELSIF lower(substring(NEW.tag from 1 for 1)) = 'b' THEN
              insert into new_b_tags(pk,tag,parent)values (NEW.pk,NEW.tag,NEW.
   parent);
          END IF;
          RETURN NEW;
   END IF;
   END;
   $$
   LANGUAGE 'plpgsql';
   CREATE FUNCTION
```

```text
   forumdb=> CREATE TRIGGER tcopy_tags_ins BEFORE INSERT on new_tags FOR EACH
   ROW EXECUTE PROCEDURE fcopy_tags();
   CREATE TRIGGER
```

Bây giờ hãy xem code này có hoạt động với event `INSERT` hay không:

```text
   forumdb=> insert into new_tags (pk,tag,parent) values (1,'operating
   systems',NULL);
   INSERT 0 1
   forumdb=> insert into new_tags (pk,tag,parent) values (2,'alpine
   linux',1);
   INSERT 0 1
   forumdb=> insert into new_tags (pk,tag,parent) values (3,'bsd unix',1);
   INSERT 0 1


   forumdb=> select * from new_a_tags ;
       pk |      tag         | parent
   ----+--------------+--------
        2 | alpine linux |              1
   (1 row)


   forumdb=> select * from new_b_tags ;
       pk |    tag      | parent
   ----+----------+--------
        3 | bsd unix |          1
   (1 row)


   forumdb=> select * from new_tags ;
       pk |           tag           | parent
   ----+-------------------+--------
        1 | operating systems |
        2 | alpine linux            |       1
        3 | bsd unix                |       1
   (3 rows)
```

Rõ ràng là code hoạt động!

Tiếp theo, hãy xử lý event `DELETE`. Chúng ta cần làm những việc sau:

- Thêm một số dòng code vào function để quản lý operation `DELETE`.
- Thêm một trigger mới có khả năng xử lý event `DELETE`.

Function sẽ trở thành như sau:

```text
   forumdb=> CREATE OR REPLACE FUNCTION fcopy_tags() RETURNS trigger as
   $$
   BEGIN
   IF TG_OP = 'INSERT' THEN
            IF lower(substring(NEW.tag from 1 for 1)) = 'a' THEN
                insert into new_a_tags(pk,tag,parent)values (NEW.pk,NEW.tag,NEW.
   parent);
            ELSIF lower(substring(NEW.tag from 1 for 1)) = 'b' THEN
                insert into new_b_tags(pk,tag,parent)values (NEW.pk,NEW.tag,NEW.
   parent);
            END IF;
            RETURN NEW;

   END IF;
   IF TG_OP = 'DELETE' THEN
          IF lower(substring(OLD.tag from 1 for 1)) = 'a' THEN
                    DELETE FROM new_a_tags WHERE pk = OLD.pk;
              ELSIF lower(substring(OLD.tag from 1 for 1)) = 'b' THEN
                    DELETE FROM new_b_tags WHERE pk = OLD.pk;
          END IF;
          RETURN OLD;
   END IF;
   END;
   $$
   LANGUAGE 'plpgsql';
   CREATE FUNCTION
```

Đoạn code sau đã được thêm:

```text
   IF TG_OP = 'DELETE' THEN
          IF lower(substring(OLD.tag from 1 for 1)) = 'a' THEN
              DELETE FROM new_a_tags WHERE pk = OLD.pk;
          ELSIF lower(substring(OLD.tag from 1 for 1)) = 'b' THEN
              DELETE FROM new_b_tags WHERE pk = OLD.pk;
          END IF;
      RETURN OLD;
   END IF;
```

Đoạn code này xóa dữ liệu trong các table `a_tags` và `b_tags` nếu record bị xóa bắt đầu bằng chữ a hoặc b. Bây giờ chúng ta phải tạo một trigger mới có khả năng xử lý các event `DELETE`:

```text
   forumdb=> CREATE TRIGGER tcopy_tags_del
   AFTER DELETE on new_tags FOR EACH ROW EXECUTE PROCEDURE fcopy_tags();
   CREATE TRIGGER
```

Trigger được thực thi `AFTER DELETE`; trong trường hợp này, sẽ không có khác biệt nếu chúng ta tạo các function `TRIGGER` `BEFORE` hoặc `AFTER INSERT`. Hãy xem trigger trên event `DELETE` này có hoạt động không:

```text
   forumdb=> delete from new_tags where pk=2;
   DELETE 1
   forumdb=> delete from new_tags where pk=3;
   DELETE 1

   forumdb=> select * from new_a_tags ;
    pk | tag | parent
   ----+-----+--------
   (0 rows)


   forumdb=> select * from new_b_tags ;
    pk | tag | parent
   ----+-----+--------
   (0 rows)


   forumdb=> select * from new_tags ;
    pk |            tag         | parent
   ----+-------------------+--------
     1 | operating systems |
   (1 row)
```

Như chúng ta có thể thấy, `TRIGGER` hoạt động.

Ở bước cuối cùng, chúng ta cần xử lý event `UPDATE`. Hãy viết function và các trigger thành một phiên bản hoàn chỉnh từ đầu. Một lần nữa, hãy đưa environment về các condition ban đầu:

```text
   forumdb=> truncate new_tags ;
   TRUNCATE TABLE
   forumdb=> truncate new_a_tags ;
   TRUNCATE TABLE
   forumdb=> truncate new_b_tags ;
   TRUNCATE TABLE


   forumdb=> insert into new_tags (pk,tag,parent) values (1,'operating
   systems',NULL),(2,'alpine linux',1),(3,'bsd unix',1);
   INSERT 0 3
```

Bây giờ chúng ta có thể viết code hoàn chỉnh cho event `UPDATE`:

```text
   forumdb=> CREATE OR REPLACE FUNCTION fcopy_tags() RETURNS trigger as
   $$
   BEGIN
   IF TG_OP = 'INSERT' THEN
            IF lower(substring(NEW.tag from 1 for 1)) = 'a' THEN
                 insert into new_a_tags(pk,tag,parent)values (NEW.pk,NEW.tag,NEW.
   parent);
           ELSIF lower(substring(NEW.tag from 1 for 1)) = 'b' THEN
                 insert into new_b_tags(pk,tag,parent)values (NEW.pk,NEW.tag,NEW.
   parent);
           END IF;
           RETURN NEW;
       END IF;
   IF TG_OP = 'DELETE' THEN
           IF lower(substring(OLD.tag from 1 for 1)) = 'a' THEN
                 DELETE FROM new_a_tags WHERE pk = OLD.pk;
           ELSIF lower(substring(OLD.tag from 1 for 1)) = 'b' THEN
                 DELETE FROM new_b_tags WHERE pk = OLD.pk;
           END IF;
           RETURN OLD;
   END IF;
   IF TG_OP = 'UPDATE' THEN
          IF (lower(substring(OLD.tag from 1 for 1)) in( 'a','b') ) THEN
                 DELETE FROM new_a_tags WHERE pk=OLD.pk;
                 DELETE FROM new_b_tags WHERE pk=OLD.pk;
                 DELETE FROM new_tags WHERE pk = OLD.pk;
                 INSERT into new_tags(pk,tag,parent) values (NEW.pk,NEW.tag,NEW.
   parent);
           END IF;
           RETURN NEW;
   END IF;
   END;
   $$
   LANGUAGE 'plpgsql';
   CREATE FUNCTION


   forumdb=> CREATE TRIGGER tcopy_tags_upd
          AFTER UPDATE on new_tags FOR EACH ROW EXECUTE PROCEDURE fcopy_tags();
   CREATE TRIGGER
```

Trong trường hợp này, trigger phải được định nghĩa với `AFTER UPDATE` chứ không phải `BEFORE UPDATE` vì trong phần `UPDATE`, chúng ta có instruction `DELETE FROM new_tags WHERE pk = OLD.pk`; nếu trigger được định nghĩa với `BEFORE UPDATE`, chúng ta sẽ gặp lỗi vì đã cố xóa một record đang được dành cho `UPDATE`.

Hãy xem function hoàn chỉnh có hoạt động không:

```text
   forumdb=> select * from new_tags;
    pk |           tag           | parent
   ----+-------------------+--------
     1 | operating systems |
     2 | alpine linux            |       1
     3 | bsd unix                |       1
   (3 rows)


   forumdb=> select * from new_a_tags;
    pk |       tag        | parent
   ----+--------------+--------
     2 | alpine linux |              1
   (1 row)



   forumdb=> select * from new_b_tags;
    pk |     tag     | parent
   ----+----------+--------
     3 | bsd unix |          1
   (1 row)


   forumdb=> update new_tags set tag='apple dos' where pk=3;
   UPDATE 1



   forumdb=> select * from new_a_tags;
    pk |       tag        | parent
   ----+--------------+--------
        2 | alpine linux |           1
        3 | apple dos      |         1
   (2 rows)



   forumdb=> select * from new_tags;
       pk |         tag          | parent
   ----+-------------------+--------
        1 | operating systems |
        2 | alpine linux         |        1
        3 | apple dos            |        1
   (3 rows)
```

Như kết quả cho thấy, cách tiếp cận dùng trigger hoạt động. Trong section này, chúng ta đã thấy cách sửa đổi các event thuộc Data Manipulation Level (DML) bằng cách sử dụng rule và trigger. Trong section tiếp theo, chúng ta sẽ thấy cũng có thể intercept và sửa đổi các event liên quan đến operation DDL bằng event trigger.

## Event trigger

Rule và trigger hoạt động như các statement DML, nghĩa là chúng được kích hoạt bởi một thứ làm thay đổi data nhưng không làm thay đổi data layout hoặc các property của table. PostgreSQL cung cấp cái gọi là event trigger, là các trigger đặc biệt fire trên các statement DDL. Vì vậy, mục đích của event trigger là quản lý và phản ứng với các event sẽ thay đổi data structure thay vì data content. Trigger có thể được sử dụng theo nhiều cách để enforce các policy cụ thể trên các database.

Sau khi được fire, event trigger nhận một event và một command tag, cả hai đều hữu ích cho việc introspection và cung cấp thông tin về thứ đã fire trigger. Cụ thể, command tag chứa mô tả của command (ví dụ `CREATE` hoặc `ALTER`), còn event chứa category đã fire trigger, cụ thể gồm các event sau:

- `ddl_command_start` và `ddl_command_end` lần lượt chỉ thời điểm bắt đầu và hoàn tất của DDL command.
- `sql_drop` chỉ thời điểm một command `DROP` sắp hoàn tất.
- `table_rewrite` chỉ thời điểm một lần rewrite toàn bộ table sắp bắt đầu.

Cũng như DML trigger, có các command cụ thể để tạo, xóa và sửa đổi một event trigger:

- `CREATE EVENT TRIGGER` để thêm một event trigger mới.
- `DROP EVENT TRIGGER` để xóa một trigger hiện có.
- `ALTER EVENT TRIGGER` để sửa đổi một trigger hiện có.

Dưới đây là synopsis để tạo một event trigger mới:

```text
   CREATE EVENT TRIGGER name
        ON event
        [ WHEN filter_variable IN (filter_value [, ... ]) [ AND ... ] ]
        EXECUTE { FUNCTION | PROCEDURE } function_name()
```

Tương tự các trigger đối tác DML, event trigger được gắn với một tên mnemonic và một function để thực thi khi chúng được fire. Tuy nhiên, không giống trigger thông thường, event trigger không chỉ định table mà chúng được gắn vào; thực tế là event trigger không liên quan đến bất kỳ table cụ thể nào mà liên quan đến các command DDL.

Event trigger phải được database administrator tạo và có database scope, nghĩa là chúng tồn tại và hoạt động trong database nơi chúng được định nghĩa.

Có một vài special function có thể giúp developer thực hiện introspection bên trong event trigger để hiểu chính xác event nào đã fire trigger. Các function quan trọng nhất như sau:

- `pg_event_trigger_commands()`, trả về một tuple cho mỗi command đã được thực thi trong DDL statement.
- `pg_event_trigger_dropped_objects()`, báo cáo một tuple cho mỗi object bị drop trong cùng DDL statement.

Cùng với các utility function nói trên, điều quan trọng là phải đọc kỹ tài liệu về event trigger để hiểu khi nào một command sẽ fire event trigger và khi nào không. Việc giải thích event trigger chi tiết hơn nằm ngoài phạm vi của section này; thay vào đó, chúng ta sẽ xem một ví dụ thực tế trong section tiếp theo. Để biết thêm thông tin về event trigger, hãy tham khảo tài liệu chính thức hoặc cuốn sách PostgreSQL 11 Server-Side Programming của Packt.

## Ví dụ về event trigger

Để hiểu rõ hơn cách event trigger hoạt động, hãy xây dựng một ví dụ đơn giản về một trigger ngăn mọi command dạng `ALTER TABLE` trong một database.

Bước đầu tiên là định nghĩa một function sẽ được thực thi khi trigger được fire; function này cần kiểm tra các property của DDL statement để hiểu liệu nó có được gọi bằng một command `ALTER TABLE` hay không. Việc introspection được thực hiện bằng special function `pg_event_trigger_ddl_commands()`, function này trả về một tuple cho mỗi DDL statement được thực thi trong cùng command. Các tuple đó chứa một field tên là `command_tag`, báo cáo command group (chữ hoa), và `object_type`, báo cáo object type (chữ thường) mà DDL statement được thực thi trên đó. Function phải trả về một trigger type, cụ thể là event trigger type; do đó, function có thể được định nghĩa như sau:

```text
   forumdb=> CREATE OR REPLACE FUNCTION
   f_avoid_alter_table()
   RETURNS EVENT_TRIGGER
   AS
   $code$
   DECLARE
   event_tuple record;
   BEGIN
      FOR event_tuple IN SELECT * FROM 		                         pg_event_trigger_ddl_
   commands() LOOP
           IF event_tuple.command_tag = 'ALTER TABLE' AND event_tuple.object_
   type = 'table' THEN
                 RAISE EXCEPTION 'Cannot execute an ALTER TABLE!';
             END IF;
        END
   $code$
   LANGUAGE plpgsql;
   CREATE FUNCTION
```

Như bạn có thể thấy, nếu function phát hiện command đã thực thi có tag `ALTER TABLE` và object type là table, nó raise một exception, khiến toàn bộ statement thất bại.

Khi function đã được tạo, có thể gắn nó vào một event trigger, nhưng vì event trigger xử lý các statement DDL nên chỉ superuser mới có thể tạo event trigger; do đó, trước tiên hãy kết nối với database `forum` bằng superuser:

```text
   forumdb=> \q
   postgres@learn_postgresql:~$ psql forumdb
```

Sau đó hãy thực thi:

```text
   psql (15.2 (Debian 15.2-1.pgdg110+1))
   Type "help" for help.


   forumdb=#
```

```text
   forumdb=# CREATE EVENT TRIGGER tr_avoid_alter_table ON ddl_command_end
   EXECUTE FUNCTION forum.f_avoid_alter_table();
   CREATE EVENT TRIGGER
```

Hãy nhớ rằng chúng ta đã kết nối với database `forumdb` bằng user `postgres`, vì vậy phải chỉ định schema nơi user `postgres` có thể tìm thấy function `f_avoid_alter_table()`.

Tại thời điểm này, trigger đang active và function sẽ được fire cho mỗi DDL command khi system tiến gần đến cuối một command.

Bây giờ có thể kiểm tra trigger và xem user có được phép thực thi `ALTER TABLE` hay không:

```text
   forumdb=> ALTER TABLE tags ADD COLUMN thumbs_up int DEFAULT 0;
   ERROR:    Cannot execute an ALTER TABLE!
   CONTEXT:    PL/pgSQL function f_avoid_alter_table() line 9 at RAISE
```

Như chúng ta có thể thấy, một exception được raise ngay khi command `ALTER TABLE` được thực thi, và chúng ta có behavior này không chỉ với non-superuser (như vừa thấy) mà cả superuser; đó là vì event trigger chúng ta viết intercept command alter table và sửa đổi behavior của nó:

```text
   forumdb=# ALTER TABLE forum.tags ADD COLUMN thumbs_up int DEFAULT 0;
   ERROR:    Cannot execute an ALTER TABLE!
   CONTEXT:    PL/pgSQL function forum.f_avoid_alter_table() line 9 at RAISE
```

Mặc dù event trigger có thể được sử dụng như trong ví dụ trước để ngăn user thực thi các command cụ thể, một chiến lược tốt hơn là tránh việc thực thi command không phù hợp bằng permission khi có thể. Event trigger rất phức tạp và được dùng để cung cấp hỗ trợ cho những thứ như logical replication, auditing và các infrastructure khác.

## Tóm tắt

Trong chapter này, chúng ta đã trình bày chủ đề trigger và rule. Chúng ta đã khám phá rule và trigger bằng một số ví dụ giống nhau. Chúng ta đã xác lập rằng rule là event handler đơn giản còn trigger là event handler phức tạp.
