Hai permission sau chỉ nhằm cho phép bạn cấu hình permission chi tiết hơn đối với một sequence.

Synopsis tổng quát của các command `GRANT` và `REVOKE` như sau:

```text
   GRANT <permission> ON SEQUENCE <sequence> TO <role>;
   REVOKE <permission> ON SEQUENCE <sequence> FROM <role>;
```

Keyword đặc biệt `ALL` bao hàm tất cả permission áp dụng được cho một sequence.

Để hiểu privilege hoạt động như thế nào đối với một sequence, hãy xem xét sequence được dùng để sinh primary key của table `categories`: `categories_pk_seq`.

Trước hết, hãy xóa tất cả privilege khỏi role `luca` để role này không còn có thể tương tác với sequence:

```text
   forumdb=> REVOKE ALL
                 ON SEQUENCE categories_pk_seq
                 FROM luca;
   REVOKE
```

Bây giờ, nếu role `luca` cố lấy một value mới từ sequence, nó sẽ nhận được lỗi `permission denied`:

```text
   forumdb=> SELECT nextval( 'categories_pk_seq' );
   ERROR:      permission denied for sequence categories_pk_seq
```

Cấp privilege `USAGE` cho sequence cho phép role `luca` query sequence lần nữa:

```text
   forumdb=> GRANT USAGE ON SEQUENCE categories_pk_seq TO luca;
   GRANT
```

Bây giờ role này có thể áp dụng thành công function `setval`:

```text
   forumdb=> SELECT setval( 'categories_pk_seq', 10 );
      setval
   --------
          10
   (1 row)


   forumdb=> SELECT nextval( 'categories_pk_seq' );
      nextval
   ---------
              11
   (1 row)
```

Hãy nhớ rằng privilege `USAGE` bao hàm cả privilege `SELECT` và `UPDATE`, vì vậy sau khi cấp `USAGE` cho một role, sequence có thể được query và set về một value cụ thể.

## Permission liên quan đến schema

Một schema là namespace cho nhiều object khác nhau, chủ yếu là table và view, nhưng cũng gồm function, routine và các database object khác. Có hai permission chính có thể áp dụng cho một schema: `CREATE`, cho phép tạo object bên trong schema, và `USAGE`, cho phép role "sử dụng" object trong schema (với điều kiện role có permission phù hợp đối với object đó).

Thoạt đầu điều này có thể hơi khó hiểu, bởi nếu role không có permission `USAGE`, role sẽ không thể truy cập object ngay cả khi nó là owner.

Synopsis tổng quát khi dùng `GRANT` và `REVOKE` ở đây có `ON SCHEMA` clause tường minh (để phân biệt với permission nhắm tới một table):

```text
   GRANT <permission> ON SCHEMA <schema> TO <role>;
   REVOKE <permission> ON SCHEMA <schema> FROM <role>;
```

Cũng như các statement tương tự khác, keyword `ALL` bao hàm tất cả permission. Để hiểu rõ hơn hai permission khác nhau này, hãy tạo một schema `configuration` và xem cách bật quyền truy cập vào nó:

```text
   -- as user forum
   forumdb=> CREATE SCHEMA configuration;
   CREATE SCHEMA
```

Schema được user `forum` tạo, vì vậy user `luca` không có privilege nào trong đó và không thể tạo table:

```text
   -- as user 'luca'
   forumdb=> CREATE TABLE configuration.conf( param text,
                                                          value text,
                                                          UNIQUE (param) );
   ERROR:    permission denied for schema configuration
   LINE 1: CREATE TABLE configuration.conf( param text, value text, UNI...
```

Để cho phép user `luca` tạo object mới bên trong schema, phải cấp permission `CREATE`. Tuy nhiên, nếu không có permission `USAGE`, role sẽ không thể truy cập bất cứ thứ gì trong schema, vì vậy cần cung cấp cả hai permission cùng lúc:

```text
   -- as user 'forum'
   forumdb=> GRANT CREATE ON SCHEMA configuration TO luca;
   GRANT


   forumdb=> GRANT USAGE ON SCHEMA configuration TO luca;
   GRANT
```

Do đó, role `luca` giờ có thể tạo một object mới bên trong schema:

```text
   -- as user 'luca'
   forumdb=> CREATE TABLE configuration.conf( param text,
                                                       value text,
                                                       UNIQUE (param) );
   CREATE TABLE


   forumdb=> INSERT INTO configuration.conf
               VALUES( 'posts_per_page', '10' );
   INSERT 0 1
```

Nếu không có permission `USAGE`, role sẽ không còn có thể truy cập bất kỳ object nào bên trong schema, ngay cả khi nó là owner của object:

```text
   -- as role 'forum'
   forumdb=> REVOKE USAGE ON SCHEMA configuration FROM luca;
   REVOKE
```

Thực tế, user sẽ không còn có thể đọc data của chính mình:

```text
   -- as role 'luca'
   forumdb=> SELECT * FROM configuration.conf;
   ERROR:    permission denied for schema configuration
   LINE 1: SELECT * FROM configuration.conf;
```

Mặt khác, việc cho phép một role thao tác với data nằm trong một schema cụ thể nhưng không cấp cho role khả năng tạo database object mới như table là điều thường gặp.

Đây là một scenario phổ biến trong đó database administrator thiết lập một schema cùng các object của nó, để user cuối xử lý data bên trong schema nhưng không cho phép user sửa đổi chính cấu trúc đó. Có thể đạt được điều này bằng các thiết lập permission chi tiết như sau:

```text
   -- as user 'forum'
   forumdb=> GRANT USAGE ON SCHEMA configuration TO luca;
   GRANT


   forumdb=> REVOKE CREATE ON SCHEMA configuration FROM luca;
   REVOKE
```

Bạn có thể hình dung schema như một container chứa các database object khác. Để truy cập container, bạn phải có permission `USAGE`, còn để tạo object mới, bạn phải có permission `CREATE`. Tuy nhiên, `USAGE` không cung cấp quyền truy cập không giới hạn vào mọi object trong schema. Thay vào đó, nó cung cấp quyền truy cập vào các object tùy theo permission bạn có đối với từng object đó.

## Tất cả object trong schema

Vì schema là các container có tên chứa database object, chúng có thể được dùng như một shortcut để áp dụng các privilege khác nhau cho mọi object nằm trong schema, thông qua clause `ALL <objects> IN SCHEMA`.

Ví dụ, để áp dụng một tập permission giống nhau cho tất cả table trong một schema, bạn có thể làm như sau:

```text
   -- as user 'forum'
   forumdb=> REVOKE ALL
               ON ALL TABLES IN SCHEMA configuration
               FROM luca;
   REVOKE


   forumdb=> GRANT SELECT, INSERT, UPDATE
               ON ALL TABLES IN SCHEMA configuration
               TO luca;
   GRANT
```

Điều này có thể đơn giản hóa đáng kể việc quản lý các schema lớn.

Hiện tại, bạn có thể dùng clause này cho các đối tượng sau:

- Tables, như trong `ON ALL TABLES IN SCHEMA`
- Sequences, như trong `ON ALL SEQUENCES IN SCHEMA`
- Routines, như trong `ON ALL ROUTINES IN SCHEMA` (với các biến thể `ON ALL PROCEDURES IN SCHEMA` và `ON ALL FUNCTIONS IN SCHEMA`)

## Permission liên quan đến programming language

Chỉ có một permission áp dụng cho language: `USAGE`. Permission này cho phép một role sử dụng language. Keyword đặc biệt `ALL`, tồn tại để tương thích với các statement `GRANT` và `REVOKE` khác, đơn giản chỉ áp dụng permission duy nhất đó.

Một thói quen bảo mật tốt là cấp ít permission nhất có thể để ngăn user không đáng tin cậy chạy code bên trong database. Ví dụ, để ngăn mọi role có khả năng thực thi bất kỳ đoạn code PL/Perl nào, bạn cần revoke permission khỏi group đặc biệt `PUBLIC`:

> **Lưu ý:** Đây chỉ là một ví dụ. Nếu language này chưa được cài đặt trên system của bạn, bạn có thể gặp lỗi.

```text
   forumdb=# REVOKE USAGE ON LANGUAGE plperl FROM PUBLIC;
   REVOKE
```

Theo cách này, ngay cả một user đáng tin cậy như `luca` cũng không thể thực thi một đoạn PL/Perl:

```text
   forumdb=> DO LANGUAGE plperl $$ elog( INFO, "Hello World" ); $$;
   ERROR:    permission denied for language plperl
```

Nếu muốn chỉ cho phép role `luca` thực thi code PL/Perl, bạn cần cấp permission này một cách tường minh:

```text
   forumdb=# GRANT USAGE ON LANGUAGE plperl TO luca;
   GRANT
```

## Permission liên quan đến routine

Keyword đặc biệt `ROUTINES` bao gồm cả `FUNCTIONS` và `PROCEDURES`. `ROUTINES` có một permission duy nhất, đó là permission `EXECUTE`, để có thể chạy (execute) code trong routine.

Để minh họa permission này, hãy tạo một routine rất đơn giản, `get_max`, trả về giá trị lớn hơn giữa hai số nguyên:

```text
   forumdb=> CREATE FUNCTION get_max( a int, b int )
   RETURNS int AS $$
   BEGIN
      IF a > b THEN
        RETURN a;
      ELSE
        RETURN b;
      END IF;
   END $$ LANGUAGE plpgsql;
```

Bây giờ, hãy ngăn mọi role ngoài `luca` thực thi routine này:

```text
   forumdb=> REVOKE EXECUTE ON ROUTINE get_max FROM PUBLIC;
   REVOKE
   forumdb=> GRANT EXECUTE ON ROUTINE get_max TO luca;
   GRANT
```

Bất kỳ role nào ngoài `luca` sẽ nhận được lỗi `permission denied` nếu gọi function:

```text
   -- executing as enrico
   forumdb=> SELECT forum.get_max( 10, 20 );
   ERROR:    permission denied for function get_max
```

Vì `get_max` là một function, ta có thể viết permission `GRANT` và `REVOKE` bằng keyword `FUNCTION` thay cho `ROUTINE` bao quát. Đây là vấn đề lựa chọn.

Cụ thể, keyword `ROUTINE` trở nên tiện dụng khi bạn muốn áp dụng permission cho tất cả function và procedure bên trong một schema cùng lúc bằng một statement duy nhất, chẳng hạn như sau:

```text
   - as user forum
   forumdb=> GRANT EXECUTE ON ALL ROUTINES IN SCHEMA forum;
```

## Permission liên quan đến database

Có nhiều permission liên quan đến database: `CONNECT` cho phép hoặc từ chối connection đến mà không liên quan gì đến host-based access control; `TEMP` cho phép tạo temporary object (ví dụ table) trong database; và `CREATE` cho phép tạo object mới bên trong database.

Synopsis tổng quát như sau:

```text
   GRANT <permission> ON DATABASE <database> TO <role>;
   REVOKE <permission> ON DATABASE <database> FROM <role>;
```

Ví dụ, nếu cần khóa mọi user khỏi một database, chẳng hạn vì phải thực hiện maintenance, bạn có thể phát hành command `REVOKE` sau:

```text
   forumdb=# REVOKE CONNECT ON DATABASE forumdb FROM PUBLIC;
   REVOKE
```

Các connection đến mới sẽ bị từ chối với lỗi `permission denied`:

```text
   $ psql -U luca forumdb
   psql: error: could not connect to server: FATAL:              permission denied for
   database "forumdb"
   DETAIL:    User does not have CONNECT privilege.
```

Bây giờ, nếu muốn role `luca` là role duy nhất có thể connect tới database và tạo object nhưng không tạo temporary object, bạn cần phát hành command sau:

```text
   forumdb=# REVOKE ALL ON DATABASE forumdb FROM public;
   REVOKE


   forumdb=# GRANT CONNECT, CREATE ON DATABASE forumdb TO luca;
   GRANT
```

## Các statement `GRANT` và `REVOKE` khác

Có những nhóm `GRANT` và `REVOKE` khác kiểm soát permission cho tablespace, type và foreign data wrapper. Chúng sẽ không được thảo luận ở đây, nhưng có thể tìm thấy trong tài liệu PostgreSQL chính thức; và giờ đây, khi đã có workflow khá rõ ràng để áp dụng permission cho các object khác nhau, chúng sẽ đủ dễ hiểu.

## Gán object owner

Bạn đã thấy owner của một object có tất cả permission khả dụng trên object đó. Đôi khi, bạn có thể muốn thay đổi ownership của một object sang một role khác, và role đó sẽ nhận tất cả permission. Thông thường, thay đổi ownership được thực hiện bằng một statement `ALTER` đặc biệt như sau:

```text
   ALTER <object> OWNER TO <role>;
```

Ví dụ, để thay đổi ownership của một table, bạn có thể phát hành command sau:

```text
   forumdb=# ALTER TABLE forum.categories OWNER TO luca;
   ALTER TABLE
```

Để thay đổi ownership của một function, bạn có thể phát hành command sau:

```text
   -- equivalent to: ALTER FUNCTION get_max OWNER TO luca;
   forumdb=# ALTER ROUTINE forum.get_max OWNER TO luca;
   ALTER ROUTINE
```

Các statement tương tự tồn tại cho mọi loại object khác.

Superuser có thể thay đổi owner của mọi database object bằng cách đặt owner thành bất kỳ user hiện có nào, còn user thông thường chỉ có thể thay đổi ownership thành các role mà họ thuộc về.

## Kiểm tra ACL

Để xem permission nào đã được cấp cho role và object, bạn có thể dùng special `psql` command `\dp` (describe permissions) đã đề cập, command này báo cáo các ACL được cấu hình cho một object cụ thể (chẳng hạn một table). Command thực hiện query trên catalog đặc biệt `pg_class`, trong đó có một field cụ thể tên là `relacl` - một array các ACL. Bạn có thể thấy điều này như sau:

```text
   forumdb=> \dp users
                                          Access privileges
   Schema | Name      | Type    |   Access privileges      |   Column privileges       |
   Policies
   --------+-------+-------+---------------------+-----------------------+---
   -------
   forum     | users | table | forum=arwdDxt/forum | gecos:                          +|
             |        |         |                          |   forum_stats=w/forum |
   (1 row)


   forumdb=> SELECT relname, relacl
                 FROM pg_class WHERE relname = 'users';
   relname |              relacl
   ---------+-----------------------
   users      | {forum=arwdDxt/forum}
```

Như bạn có thể thấy, output từ command `\dp` và query giống nhau, ngoại trừ cách format output.

Bạn cũng có thể dùng special function `aclexplode` để lấy thông tin mô tả chi tiết hơn về ý nghĩa của ACL. Function trả về một set record, mỗi record có OID của grantor và grantee, cùng mô tả dạng text về permission đã cấp. Do đó, có thể xây dựng một query như sau:

```text
   forumdb=> WITH acl AS (
                   SELECT relname,
                           (aclexplode(relacl)).grantor,
                           (aclexplode(relacl)).grantee,
                           (aclexplode(relacl)).privilege_type
                  FROM pg_class )
              SELECT g.rolname AS grantee,
                      acl.privilege_type AS permission,
                      gg.rolname AS grantor
              FROM acl
              JOIN pg_roles g ON g.oid = acl.grantee
              JOIN pg_roles gg ON gg.oid = acl.grantor
              WHERE acl.relname = 'users';
```

Lệnh này trả về tất cả permission riêng lẻ được gán cho table `categories`, như sau:

```text
   grantee | permission | grantor
   --------+------------+---------
   forum     | INSERT        | forum
   forum     | SELECT        | forum
   forum     | UPDATE        | forum
   forum     | DELETE        | forum
   forum     | TRUNCATE      | forum
   forum     | REFERENCES | forum
   forum     | TRIGGER       | forum
```

## RLS

Trong phần trước của chapter, bạn đã thấy cơ chế permission nhờ đó PostgreSQL cho phép các role (cả user và group) truy cập những object khác nhau trong database và data chứa trong các object đó.

Cụ thể, đối với table, bạn đã học cách hạn chế quyền truy cập chỉ còn một danh sách column cụ thể trong tabular data.

PostgreSQL cung cấp một cơ chế thú vị khác để hạn chế quyền truy cập vào tabular data: RLS. Ý tưởng là RLS quyết định role có thể truy cập những tuple nào, ở chế độ đọc hoặc ghi. Vì vậy, nếu permission dựa trên column cung cấp cách giới hạn hình dạng theo chiều dọc của tabular data, thì RLS cung cấp cách hạn chế hình dạng theo chiều ngang của chính data đó.

Khi nào nên dùng RLS? Hãy hình dung bạn có một table chứa data liên quan đến user, và bạn không muốn user can thiệp vào data của user khác. Trong trường hợp đó, giới hạn quyền truy cập của mỗi user chỉ còn các tuple của chính họ sẽ cung cấp sự cô lập tốt, ngăn data bị can thiệp. Một scenario khá phổ biến khác là hệ thống multi-homed, trong đó bạn lưu cùng một data nhưng dành cho các công ty khác nhau trong chính những table đó. Bạn không muốn một công ty có thể do thám hoặc kiểm tra data của công ty khác, vì vậy một lần nữa RLS có thể hữu ích.

Dĩ nhiên, RLS không phải silver bullet, và nhiều giải pháp bạn có thể nghĩ ra có liên quan đến RLS cũng có thể được thực hiện bằng các kỹ thuật khác, nhưng việc nhận thức được feature quan trọng này có thể khiến data của bạn chống lại việc sử dụng sai tốt hơn nhiều.

Infrastructure RLS hoạt động dựa trên các policy. Một policy là một tập rule quy định theo đó một số tuple nhất định sẽ được cung cấp cho user. Tùy theo policy bạn áp dụng, role của bạn (tức là user) sẽ có thể đọc và/hoặc ghi một số tuple nhất định.

Áp dụng RLS cho một table thường là quy trình gồm hai bước: trước tiên, bạn phải định nghĩa một policy (hoặc nhiều policy), sau đó phải bật policy đó trên table. Hãy lưu ý rằng superuser, owner và role có property đặc biệt `BYPASSRLS` sẽ không chịu sự chi phối của RLS.

> **CHÚ Ý:** Trong trường hợp database backup, chẳng hạn bằng `pg_dump`, user thực hiện backup phải có khả năng bypass policy RLS; nghĩa là user phải có property `BYPASSRLS`, nếu không backup sẽ thất bại. Rõ ràng, role superuser (`postgres`) hoặc bất kỳ role nào khác có superuser option đều sẽ thành công.

Một policy định nghĩa việc tuple có sẵn hay không dựa trên một tiêu chí logic, tức là một filtering condition. Một tuple có thể chỉ sẵn có để đọc, chỉ sẵn có để ghi, hoặc sẵn có cho cả hai. Synopsis tổng quát của một policy như sau:

```text
    CREATE POLICY <name>
    ON <table>
    FOR <statement>
```
