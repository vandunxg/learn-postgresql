## Yêu cầu kỹ thuật

Các ví dụ trong chapter có thể chạy trên Docker image `chapter_10` có trong GitHub repository của sách: https://github.com/PacktPublishing/Learn-PostgreSQL-Second-Edition.

## Tìm hiểu về role

Trong Chapter 3, *Managing Users and Connections*, bạn đã thấy cách tạo role mới, một kiểu có thể hoạt động như một user đơn lẻ hoặc một group user. Statement `CREATE ROLE` được dùng để tạo role, và bạn đã tìm hiểu các property chính có thể gắn với một role.

Section này mở rộng các concept bạn đã đọc trong Chapter 3, *Managing Users and Connections*, bằng cách giới thiệu những property thú vị hơn và liên quan đến security của một role.

Nhắc lại nhanh, synopsis để tạo role mới như sau:


```text
   CREATE ROLE name [ [ WITH ] option [ ... ] ]
```

Tên được gán cho role phải là duy nhất trong toàn bộ cluster.

Một option có thể được chỉ định ở dạng dương, tức là gắn một property với role, hoặc ở dạng phủ định với prefix `NO`, prefix này loại bỏ một property khỏi role. Một số property không được gán cho role mới theo mặc định, vì vậy bạn nên dành thời gian tham khảo documentation của statement `CREATE ROLE` để biết giá trị mặc định của từng property. Nếu không chắc chắn, hãy gắn rõ các property bạn cần và phủ định những property mà bạn hoàn toàn không muốn role của mình có.

### Các property liên quan đến object mới

Có hai capability chính mà một role có thể có để tạo object mới, và cả hai chỉ nên được cấp cho các đối tượng đáng tin cậy:

- `CREATEROLE` cho phép role tạo và thao tác với các role khác (và do đó là database account và group).
- `CREATEDB` cho phép role tạo database khác trong cluster.

Theo mặc định, nếu không được chỉ định rõ, role mới được tạo mà không có các capability này, vì vậy:

```text
   postgres=# CREATE ROLE luca;
   Hoàn toàn tương đương với command sau:
   postgres=# CREATE ROLE luca
                  WITH NOCREATEROLE
                        NOCREATEDB;
```

Trong chapter này, bạn sẽ thấy các command được nhập xen kẽ bởi user thông thường, với command prompt `forumdb=>`, và các command được nhập bởi database administrator, với prompt `forumdb=#`. Nếu không chỉ định rõ, tất cả ví dụ liên quan đến việc cấp và thu hồi permission sẽ được chạy với database user `forum`.

### Các property liên quan đến superuser

Với property `SUPERUSER`, một role được tạo như cluster administrator, tức là role có mọi quyền trên mọi object trong cluster, đáng chú ý nhất là capability thêm, xóa và thay đổi user; thay đổi PostgreSQL configuration; terminate user connection; và dừng cluster.

Trong một cluster có thể có bao nhiêu superuser tùy ý. Tuy nhiên, vì đây là một nhóm user không có bất kỳ hạn chế nào, nên tránh cấp toàn bộ permission cho user không đáng tin cậy trừ khi thực sự cần thiết là một thói quen tốt. Tránh sử dụng superuser role bất cứ khi nào có thể cũng là một thói quen tốt, giúp ngăn ngừa thiệt hại do vô tình gây ra cho cluster và dữ liệu của nó.

### Các property liên quan đến replication

Property `REPLICATION` được dùng để chỉ định rằng role mới có thể sử dụng replication protocol, một protocol mạng riêng mà PostgreSQL dùng để replicate dữ liệu từ cluster này sang cluster khác.

`REPLICATION` là một option cho phép role truy cập toàn bộ dữ liệu trong cluster mà không có hạn chế cụ thể nào. Vì vậy, option này thường chỉ được cấp cho các role dùng cho replication.

Do các hệ quả về security, nếu không chỉ định khác đi thì option `NOREPLICATION` sẽ được thiết lập.

### Các property liên quan đến RLS

`RLS` là một cơ chế enforcement policy, ngăn một số role truy cập các tuple cụ thể trong các table cụ thể. Nói cách khác, cơ chế này áp dụng security constraint ở cấp row của table, vì vậy có tên là row-level security.

Có một option duy nhất điều khiển `RLS`: `BYPASSRLS`. Nếu role có option này, role sẽ bypass (nghĩa là không chịu) mọi security constraint đối với mọi row trong cluster. Như bạn có thể hình dung, mặc định của option này là phủ định nó (tức là `NOBYPASSRLS`) để role chịu sự enforcement security bất cứ khi nào có thể.

Cần lưu ý rằng cluster superuser luôn có thể bypass policy `RLS`.

Bạn sẽ tìm hiểu thêm về `RLS` trong section RLS của chapter này.

## Thay đổi property của role hiện có: statement ALTER ROLE

Như bạn có thể hình dung, role không bất biến sau khi được tạo: bạn có thể thêm hoặc xóa property khỏi một role bằng statement `ALTER ROLE`. Synopsis của statement này rất giống synopsis dùng để tạo role, như sau:

```text
      ALTER ROLE name [ [ WITH ] option [ ... ] ]
```

Ở đây, `name` là tên role duy nhất và các option được chỉ định chính xác như trong statement `CREATE ROLE`.

Ví dụ, giả sử bạn muốn cấp cho role `luca` capability tạo database và role mới. Bạn có thể chạy hai statement `ALTER ROLE`, hoặc gộp các option như sau:

```text
      forumdb=# ALTER ROLE luca WITH CREATEDB;
      ALTER ROLE


      forumdb=# ALTER ROLE luca WITH CREATEROLE;
      ALTER ROLE


      -- same as the above two statements
      forumdb=# ALTER ROLE luca CREATEROLE CREATEDB;
      ALTER ROLE
```

Và nếu sau đó đổi ý, bạn có thể xóa một hoặc cả hai option bằng cách gán dạng phủ định:

```text
      forumdb=# ALTER ROLE luca NOCREATEROLE NOCREATEDB;
      ALTER ROLE
```

Statement `ALTER ROLE` luôn có thể được thực thi bởi cluster superuser, nhưng cũng có thể được thực thi bởi một non-superuser role có option `CREATEROLE` (tức là có thể tạo và do đó thao tác với role khác), miễn là statement được áp dụng cho một non-superuser role.

## Đổi tên role hiện có

Statement `ALTER ROLE` cũng cho phép thay đổi tên role: clause `RENAME` cho phép thay role bằng một tên role duy nhất khác. Ví dụ, hãy đổi username ngắn của một role thành tên dài hơn:

```text
   forumdb=# ALTER ROLE luca RENAME TO fluca1978;
   ALTER ROLE
```

Rõ ràng, bạn không thể đổi tên role hiện có thành một tên role đích đã được sử dụng.

Có thể đổi role trở lại giá trị trước đó bằng cùng command:

```text
   forumdb=# ALTER ROLE fluca1978 RENAME TO luca;
   ALTER ROLE
```

## SESSION_USER và CURRENT_USER

Statement `ALTER ROLE` thao tác trên một role hiện có được chỉ định bằng tên role. Tuy nhiên, có thể tham chiếu role hiện tại bằng hai keyword đặc biệt: `SESSION_USER` và `CURRENT_USER`.

> Lưu ý cách dùng `user` trong các keyword đặc biệt `SESSION_USER` và `CURRENT_USER`. Chúng vẫn tham chiếu concept role, nhưng vì backward compatibility nên sử dụng nomenclature `user`. Mặc dù có keyword `CURRENT_ROLE`, không có keyword `SESSION_ROLE` tương đương.

`SESSION_USER` là tên role của role đã kết nối tới database, tức user đã mở một session tới database.

`CURRENT_USER` (hoặc `CURRENT_ROLE`) là tên role của role được chỉ định rõ bằng statement `SET ROLE`.

Sau khi một connection được thiết lập, hai keyword này tham chiếu cùng một role, chính là role đã mở connection (role được chỉ định trong connection parameter hoặc connection string). Nếu role thực hiện một operation `SET ROLE` rõ ràng, `SESSION_USER` vẫn không thay đổi, còn `CURRENT_USER` phản ánh role được chỉ định gần nhất.

Hãy xem điều này trong thực tế. Giả sử user `luca` mở một connection tới database. Ban đầu, `SESSION_USER` và `CURRENT_USER` có cùng giá trị:

```text
   $ psql -U luca forumdb


   forumdb=> SELECT current_user, session_user;
    current_user | session_user
   --------------+--------------
    luca         | luca
   (1 row)
```

Giả sử role `luca` là member của một group tên là `forum_stats`, vì vậy có thể thực hiện chuyển đổi rõ ràng sang role đó:

```text
      forumdb=> SET ROLE forum_stats;
      SET
      forumdb=> SELECT current_user, session_user;
       current_user | session_user
       --------------+--------------
       forum_stats   | luca
      (1 row)
```

Như bạn thấy, sau statement `SET ROLE`, `CURRENT_USER` thay đổi giá trị để phản ánh role mà user thực sự đang đóng vai, còn `SESSION_USER` giữ giá trị ban đầu mà user đã dùng để connect tới database.

Tóm lại, `CURRENT_USER` (`CURRENT_ROLE`) theo dõi role hiện đang thực thi, còn `SESSION_USER` giữ role đã được dùng để mở database connection.

## Configuration parameter theo role

Bên cạnh role property và permission được cấp, role cũng có thể được gắn với một số configuration parameter để ghi nhận cách sử dụng của chúng. Về cơ bản, có thể gắn một danh sách command `SET` với một role để mỗi khi role connect tới database, các command đó được thực thi ngầm.

Giả sử user `luca` thực thi một command `SET` cho giá trị `client_min_messages` mỗi lần connect tới database:

```text
      $ psql -U luca forumdb


      forumdb=> SET client_min_messages TO 'DEBUG';
      SET
```

Điều này có thể gây phiền phức và quan trọng hơn là có rủi ro. User có thể quên thực thi command `SET`, trong khi command này cần thiết để connection hoạt động như mong đợi. Có thể thay đổi role để command `SET` được tự động thực thi ngay khi connection được thiết lập:

```text
      forumdb=# ALTER ROLE luca
                 IN DATABASE forumdb
                 SET client_min_messages TO 'DEBUG';
      ALTER ROLE
```

Và bây giờ, mỗi khi role `luca` connect tới database `forumdb`, command `SET` sẽ được tự động thực thi:

```text
   $ psql -U luca forumdb


   forumdb=> SHOW client_min_messages;


    client_min_messages
   ---------------------
    debug
   (1 row)
```

Cú pháp tổng quát để thay đổi runtime parameter cho một role như sau:

```text
ALTER ROLE name IN DATABASE dbname SET parameter_name TO parameter_value
```

Ở đây, bạn phải chỉ định tên role hoặc keyword đặc biệt `ALL` cho mọi role hiện có, tên database, cùng tên và giá trị của parameter muốn thay đổi.

Cũng có thể loại bỏ mọi per-role configuration bằng clause `RESET ALL`, như trong ví dụ sau:

```text
   forumdb=# ALTER ROLE luca
               IN DATABASE forumdb
               RESET ALL;
   ALTER ROLE
```

## Kiểm tra role

Có nhiều cách kiểm tra role hiện có và lấy thông tin về property của chúng. Một cách nhanh, như đã thấy trong Chapter 3, *Managing Users and Connections*, là dùng command `\du` trong `psql`:

```text
   forumdb=> \du
                                         List of roles
      Role name     |                               Attributes
   --------------+----------------------------------------------------------
   --
    book_authors | Cannot login
    enrico       |
    forum        |
    forum_admins | Cannot login
    forum_emails | No inheritance, Cannot login
    forum_stats  | No inheritance, Cannot login
    luca         | 1 connection
    postgres     | Superuser, Create role, Create DB, Replication, Bypass RLS
```

Cột `Attributes` cung cấp mô tả dễ nhớ về các role property: ví dụ, role `luca` bị giới hạn ở một connection duy nhất.

Bên cạnh các special command của `psql`, superuser luôn có thể query system catalog để lấy thông tin về các role hiện có. Entry point chính là table `pg_authid`, table này chứa một row cho mỗi role hiện có, với một column phản ánh mọi property của role (tức những gì bạn đã định nghĩa qua statement `CREATE ROLE` hoặc `ALTER ROLE`), ví dụ:

```text
      forumdb=# \x
      Expanded display is on.
      forumdb=# SELECT * FROM pg_authid WHERE rolname = 'luca';
      -[ RECORD 1 ]--+------------------------------------
      oid            | 16384
      rolname        | luca
      rolsuper       | f
      rolinherit     | t
      rolcreaterole  | f
      rolcreatedb    | f
      rolcanlogin    | t
      rolreplication | f
      rolbypassrls   | f
      rolconnlimit   | 1
      rolpassword    | SCRAM-SHA-256$4096:...f2QU/7KAVM=
      rolvaliduntil  |
```

Mỗi role có một tên duy nhất và một giá trị OID, đại diện cho role dưới dạng giá trị số. Điều này tương tự cách user được biểu diễn trong Unix system (và nhiều system khác), nơi giá trị số của role chỉ được dùng nội bộ.

Nhiều role property có giá trị Boolean, trong đó `f` nghĩa là false (tức là không có option) và `t` nghĩa là true (tức là có option).

Ví dụ, trong ví dụ trước, bạn có thể thấy `rolcreatedb` là false, nghĩa là role đã được tạo (hoặc thay đổi) với option `NOCREATEDB`.

Password của role (field `rolpassword`) được biểu diễn dưới dạng hash, cùng identifier của algorithm được sử dụng (trong ví dụ trên là `SCRAM-SHA-256`).

Có một catalog khả dụng khác tên là `pg_roles`, hiển thị cùng thông tin với `pg_authid`:

```text
   forumdb=> SELECT * FROM pg_roles WHERE rolname = 'luca';
   -[ RECORD 1 ]--+---------
   rolname        | luca
   rolsuper       | f
   rolinherit     | t
   rolcreaterole  | f
   rolcreatedb    | f
   rolcanlogin    | t
   rolreplication | f
   rolconnlimit   | 1
   rolpassword    | ********
   rolvaliduntil  |
   rolbypassrls   | f
   rolconfig      |
   oid            | 16384
```

Tại sao cần hai view tương tự của cùng một dữ liệu? Chỉ cluster superuser mới có thể query `pg_authid`, còn mọi user đều có thể query `pg_roles`, vì không có rủi ro password của role bị lộ (như bạn có thể thấy, field password đã được mask).

Còn group membership thì sao? Bạn có thể query catalog đặc biệt `pg_auth_members` để lấy thông tin role nào là member của role nào khác. Ví dụ, query sau cung cấp một danh sách group:

```text
   forumdb=> SELECT r.rolname, g.rolname AS group,
                         m.admin_option AS is_admin
                FROM pg_auth_members m
                     JOIN pg_roles r ON r.oid = m.member
                     JOIN pg_roles g ON g.oid = m.roleid
                ORDER BY r.rolname;
```

```text
        rolname     |        group            | is_admin
       ------------+----------------------+----------
        enrico       | book_authors            | f
        enrico       | forum_admins            | f
        luca         | forum_stats             | f
        luca         | book_authors            | f
        pg_monitor   | pg_read_all_settings   | f
        pg_monitor   | pg_read_all_stats      | f
        pg_monitor   | pg_stat_scan_tables    | f
        test         | forum_stats             | f
       (8 rows)
```

## Role kế thừa từ role khác

Chúng ta đã thấy trong Chapter 3, *Managing Users and Connections*, rằng một role có thể chứa các role khác, qua đó hoạt động như một group.

Khi một role trở thành member của role khác, nó nhận được tất cả permission của role chứa nó (group role). Tuy nhiên, có trường hợp các privilege đó được cấp động, nghĩa là member role sẽ tự động có các privilege, và có trường hợp privilege được cấp tĩnh, nghĩa là member role cần chủ động trở thành group role để sử dụng privilege của group. Property `INHERIT` của role phân biệt cách role sử dụng privilege theo mặc định. Statement `GRANT` có clause tùy chọn `WITH INHERIT`, có thể được chỉ định khi thêm một role vào group: nếu clause có giá trị true, role được thêm sẽ ngay lập tức và tự động nhận toàn bộ permission của group, nếu không thì sẽ không nhận.

Nếu không chỉ định option `WITH INHERIT`, property `INHERIT` của role sẽ được dùng ngầm. Để hiểu sự khác biệt và hệ quả, hãy xem các role `forum_admins` và `forum_stats` có thể được xây dựng như thế nào:

```text
      forumdb=# CREATE ROLE forum_admins WITH NOLOGIN;
      CREATE ROLE


      forumdb=# CREATE ROLE forum_stats WITH NOLOGIN;
      CREATE ROLE


      forumdb=# REVOKE ALL ON forum.users FROM forum_stats;
      REVOKE


    forumdb=# REVOKE ALL ON forum.users FROM forum_admins;
    REVOKE


    forumdb=# GRANT ALL ON SCHEMA forum TO forum_admins;
    GRANT


    forumdb=# GRANT USAGE ON SCHEMA forum TO forum_stats;
    GRANT


    forumdb=# GRANT ALL ON forum.users TO forum_admins;
    GRANT


    forumdb=# GRANT SELECT (username, gecos) ON forum.users TO forum_stats;
    GRANT


    forumdb=# GRANT forum_admins TO enrico;
    GRANT ROLE


    forumdb=# GRANT forum_stats          TO luca;
    GRANT ROLE
```

Trước hết, hai role được tạo mà không có capability login trực tiếp; đó là vì chúng ta không muốn group được dùng như một user. Thay vào đó, chúng ta muốn các user thuộc group có thể login vào database. Sau đó, bằng `REVOKE`, chúng ta xóa mọi permission của `forum_stats` trên table `users`.

Đây là một thói quen tốt: thu hồi toàn bộ permission cho phép bạn chỉ thiết lập những permission thực sự muốn có, mà không vô tình gán những permission không muốn cho group. Tương tự, chúng ta cấp toàn bộ permission trên table `users` cho role `forum_admins`. Sau đó, chúng ta tinh chỉnh permission bằng cách cấp toàn bộ permission trên table `users` cho `forum_admins`, và chỉ cấp permission `SELECT` trên hai column cho group `forum_stats`. Cuối cùng, chúng ta biến `enrico` thành member của role `forum_admins` bằng cách GRANT role `forum_admins` cho role `enrico`, và tương tự GRANT role `forum_stats` cho `luca`, khiến `luca` trở thành member của group `forum_stats`.

Khá dễ thấy role `enrico` có thể thực hiện những gì role `forum_admins` cho phép trên table `users`: vì là member của group `forum_admins`, role `enrico` có thể thực hiện mọi action trên table `users`.
