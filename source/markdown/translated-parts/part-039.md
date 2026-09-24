```text
TO <role>
USING <filtering condition>
WITH CHECK <writing condition>
```

Ở đây, các điểm sau được áp dụng:

- `name` là tên của policy; tên này được dùng để tìm policy trong system.
- `table` là table mà bạn muốn áp dụng policy.
- `statement` có thể là một trong các statement `SELECT`, `UPDATE`, `DELETE`, `INSERT`, hoặc keyword đặc biệt `ALL` để chỉ tất cả statement có sẵn.
- `filtering condition` là một condition dùng để hạn chế result set của các tuple có thể truy xuất, thường là những tuple mà bạn muốn role có thể lấy từ table.
- `writing condition` là một clause tùy chọn cung cấp restriction khi ghi tuple.

Có thể xóa một policy bằng command `DROP POLICY` và viết lại policy bằng một command `ALTER POLICY` cụ thể.

Bây giờ hãy xem một vài ví dụ để hiểu rõ hơn cách xây dựng một policy. Giả sử chúng ta muốn cho phép một database user chỉ xem những tuple trong table `posts` thuộc về user đó. Vì vậy, condition cần đối chiếu user với một statement `SELECT`.

Policy có thể có dạng như sau:

```text
   forumdb=> CREATE POLICY show_only_my_posts
                  ON posts
                  FOR SELECT
                  USING ( author = ( SELECT pk FROM users
                                       WHERE username = CURRENT_ROLE ) );
   CREATE POLICY
```

Policy được đặt tên là `show_only_my_posts` và áp dụng trên table `posts` cho mọi statement `SELECT`. Một tuple chỉ được trả về trong result set cuối cùng nếu match với clause `USING`, tức là chỉ khi `author` được tìm thấy trong table `users` và là database user hiện tại.

Việc tạo policy không có nghĩa là policy đã active; bạn cần enable policy trên table mà nó tham chiếu bằng một command `ALTER TABLE` cụ thể:

```text
   forumdb=> ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
   ALTER TABLE
```

`ALTER TABLE` nói trên sẽ enable tất cả policy đã tạo cho table đó, trong trường hợp của chúng ta hiện chỉ có một policy, nhưng bạn cần lưu ý rằng nếu có các policy khác thì chúng cũng sẽ được activate. Không có cách enable có chọn lọc một policy duy nhất cho table: hoặc tất cả policy cùng được enable, hoặc tất cả cùng bị disable.

> Bạn phải là owner của table để enable hoặc disable RLS.

Bây giờ role đã bị giới hạn chỉ được “xem” các post của chính mình, nhưng việc tạo post mới thì sao? Vì policy không có restriction nào về write permission, user có thể tạo mọi tuple trong table `posts`. Chúng ta có thể giới hạn khả năng write của user, chẳng hạn quy định rõ rằng họ chỉ được sửa các post thuộc về mình và nằm trong một khoảng thời gian nhất định, giả sử là một ngày. Kết quả là một policy như sau:

```text
   forumdb=> CREATE POLICY manage_only_my_posts
                ON posts
                FOR ALL
                USING ( author = ( SELECT pk FROM users
                                         WHERE username = CURRENT_ROLE ) )
               WITH CHECK ( author = ( SELECT pk FROM users
                                         WHERE username = CURRENT_ROLE )
                              AND
                              last_edited_on + '1 day'::interval >= CURRENT_
   TIMESTAMP );
   CREATE POLICY
```

> Vì RLS đã được activate cho table `posts`, policy vừa tạo sẽ active ngay lập tức.

Trong trường hợp này, bất kể user thực thi statement nào trên table, họ chỉ thấy các post của chính mình (clause `USING`) và sẽ không thể write (tức là `INSERT`, `UPDATE` hoặc `DELETE`) bất kỳ tuple nào không thuộc về họ và không nằm trong khoảng thời gian một ngày (clause `CHECK`).

Điều gì xảy ra bên dưới? PostgreSQL âm thầm áp dụng các clause `USING` và `CHECK` vào mọi query bạn issue trên table để filter các tuple có thể được trả về.

Ví dụ, nếu quan sát query plan của một command `SELECT` không có filter, bạn sẽ thấy filter `CURRENT_ROLE` được áp dụng như trong clause `USING`:

```text
   forumdb=> EXPLAIN SELECT * FROM posts;
                                                  QUERY PLAN
   --------------------------------------------------------------------------
   --------------
      Seq Scan on posts    (cost=8.17..76.17 rows=1000 width=74)
        Filter: (author = $0)
        InitPlan 1 (returns $0)
        -> Index Scan using users_username_key on users              (cost=0.15..8.17
   rows=1 width=4)
                Index Cond: (username = (CURRENT_ROLE)::text)
```

Filter đã được PostgreSQL áp dụng ngay cả khi query không đề cập đến nó. Điều này có nghĩa là PostgreSQL luôn bị “buộc” phải execute query và filter result giúp bạn, vì vậy bạn không thể kỳ vọng có performance gain khi dùng RLS. Sau cùng, các tuple vẫn phải bị loại ở đâu đó!

Bây giờ, nếu cố sửa tuple theo cách vi phạm condition `CHECK`, PostgreSQL sẽ báo lỗi và không cho phép thực hiện thay đổi:

```text
   forumdb=> UPDATE posts
               SET last_edited_on = last_edited_on - '2 weeks'::interval;
   ERROR:    new row violates row-level security policy for table "posts"
```

Bạn luôn có thể inspect RLS thông qua command đặc biệt `\dp` trong `psql` (output sau đã được rút gọn để vừa với giới hạn của trang):

```text
   forumdb=> \dp posts


   Access privileges
   |                                                                 Policies
   +-------------------------------------------------------------------------
   -------------------------------------------
   | show_only_my_posts (r):
   +
   |    (u): (author = ( SELECT users.pk
   +
   |     FROM users
   +
   |   WHERE (users.username = (CURRENT_ROLE)::text)))
   +
   | manage_only_my_posts:
   +
   |   (u): (author = ( SELECT users.pk
   +
   |     FROM users
   +
   |   WHERE (users.username = (CURRENT_ROLE)::text)))
   +
   |   (c): ((author = ( SELECT users.pk
   +
   |     FROM users
   +
   |   WHERE (users.username = (CURRENT_ROLE)::text))) AND ((last_edited_on +
   '1 day'::interval) >= CURRENT_TIMESTAMP))
   (1 row)
```

Cuối cùng, bạn có thể disable hoặc enable lại các policy trên table bằng cách issue một command `ALTER TABLE` cụ thể, chẳng hạn như sau:

```text
    forumdb=> ALTER TABLE posts DISABLE ROW LEVEL SECURITY;
    ALTER TABLE


    -- to enable the RLS again
    forumdb=> ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
    ALTER TABLE
```

Các policy có thể được kết hợp tùy thuộc vào statement cụ thể mà user issue. Theo mặc định, policy được tạo dưới dạng *permissive*, nghĩa là chúng được kết hợp bằng phép logic “OR.” Điều này có nghĩa là chỉ cần một policy grant operation là statement có thể thành công. Ngược lại, các policy được tạo dưới dạng *restrictive* sẽ được merge bằng phép logic “AND,” vì vậy mọi policy đều phải thành công thì statement mới được execute.

Kiểu permissiveness của một policy chỉ có thể được thiết lập tại thời điểm tạo, vì vậy, chẳng hạn để biến policy `show_only_my_posts` thành restrictive, bạn cần xóa rồi tạo lại policy với permissiveness được chỉ định một cách tường minh:

```text
    forumdb=> DROP POLICY show_only_my_posts ON posts;
    DROP POLICY

    forumdb=> CREATE POLICY show_only_my_posts
               ON posts
               AS restrictive
               FOR SELECT
               USING ( author = ( SELECT pk FROM users
                                       WHERE username = CURRENT_ROLE ) );
    CREATE POLICY
```

## Mã hóa password của role

Password đăng nhập gắn với role luôn được lưu dưới dạng encrypted, ngay cả khi role được tạo mà không có property `ENCRYPTED PASSWORD`. PostgreSQL xác định algorithm dùng để encrypt password thông qua option `password_encryption` trong configuration file `postgresql.conf`. Mặc định, giá trị của option này là `scram-sha-256`:

```text
      forumdb=> show password_encryption;
      password_encryption
      ---------------------
      scram-sha-256
      (1 row)
```

PostgreSQL giới thiệu encryption algorithm SCRAM-SHA-256 trong version 10; trước đó, encryption algorithm được đặt là `md5`, kém robust hơn, và cũng là option còn lại duy nhất (nhưng hiện đã bị discourage).

Điều quan trọng cần lưu ý là bạn không thể thay đổi password encryption algorithm của một live system mà không reset toàn bộ password của các role đang active. Nói cách khác, nếu quyết định migrate từ `md5` cũ sang SCRAM-SHA-256 mới hơn (hoặc ngược lại), bạn cần issue các statement `ALTER ROLE` thích hợp để thiết lập password mới cho mọi role đã định nghĩa trong database.

> Vì field `pg_authid.rolpassword` bắt đầu bằng encryption algorithm, hoặc `md5` hoặc SCRAM-SHA-256, nên việc inspect system catalog và tìm các role chưa được update bằng encryption algorithm mới là đơn giản.

## Kết nối SSL

Secure Sockets Layer (SSL) cho phép PostgreSQL chấp nhận các network connection được encrypt, nghĩa là mọi phần dữ liệu trong mỗi packet đều được encrypt và do đó được bảo vệ khỏi network spoofing, miễn là bạn xử lý key và certificate đúng cách.

Để enable SSL extension, trước tiên bạn cần configure server, sau đó chấp nhận các SSL connection đến, và cuối cùng configure client để connect ở SSL mode.

### Configure cluster cho SSL

Để SSL thực hiện việc encryption, server phải có private certificate và public certificate. Việc tạo và quản lý certificate nằm ngoài phạm vi cuốn sách này và là một chủ đề phức tạp; bạn có thể xem PostgreSQL official documentation để biết các bước cần thiết nhằm tạo certificate của riêng mình. Khi bạn hoặc tổ chức của bạn đã có certificate, việc duy nhất cần làm là import certificate và key file vào PostgreSQL server.

Giả sử certificate và key file của bạn lần lượt có tên `server.crt` và `server.key`, bạn phải configure các parameter sau trong configuration file `postgresql.conf`:

```text
   ssl = on
   ssl_key_file = '/postgres/16/data/ssl/server.key'
   ssl_cert_file = '/postgres/16/data/ssl/server.crt'
```

Tất nhiên, việc này được thực hiện với absolute path đến các file của bạn. Dòng đầu tiên bảo PostgreSQL enable SSL, còn hai dòng kia cho server biết nơi tìm các file cần thiết để thiết lập encrypted connection. Tất nhiên, các file đó phải readable bởi user chạy PostgreSQL cluster (thường là operating-system user `postgres`).

Sau khi enable SSL, bạn cần điều chỉnh file `pg_hba.conf` để cho phép host-based access machinery xử lý các connection dựa trên SSL. Cụ thể, nếu không muốn chấp nhận plain connection, bạn cần thay mọi entry `host` bằng `hostssl`, ví dụ:

```text
   hostssl       all   luca         venkman             scram-sha-256
   hostssl       all   forum     192.168.222.1/32 scram-sha-256
```

Nếu muốn chấp nhận cả plain connection lẫn encrypted connection, bạn có thể giữ `host` làm connection method.

### Connect tới cluster qua SSL

Khi connect tới PostgreSQL, client sẽ tự động chuyển sang SSL connection nếu host-based access có entry `hostssl`; nếu không, client sẽ mặc định dùng standard plain connection.

Nếu `pg_hba.conf` có dòng `host`, điều đó có nghĩa là file có thể chấp nhận cả SSL connection và plain connection. Vì vậy, bạn cần buộc connection dùng SSL khi khởi tạo connection. Trong `psql`, điều này chỉ có thể thực hiện bằng cách dùng connection string và chỉ định parameter `sslmode=require` để enable SSL. Nếu server chấp nhận connection, nó sẽ báo protocol SSL đang được sử dụng:

```text
   $ psql "postgresql://forum@localhost:5432/forumdb?sslmode=require"
   psql (16.0)
   SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, bits:
   256, compression: off)
   Type "help" for help.


   forumdb=>
```

Nếu bỏ parameter `sslmode` hoặc dùng các parameter connection chuẩn của `psql`, connection sẽ được chuyển thành SSL nếu file `pg_hba.conf` có một dòng `hostssl` match. Ví dụ, ba connection sau cho cùng một kết quả (một encrypted connection):

```text
   $ psql -h localhost -U forum forumdb
   psql (16.0)
   SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, bits:
   256, compression: off)
   Type "help" for help.


   forumdb=> \q


   $ psql "postgresql://forum@localhost:5432/forumdb"
   psql (16.0)
   SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, bits:
   256, compression: off)
   Type "help" for help.


   forumdb=> \q


   $ psql "postgresql://forum@localhost:5432/forumdb?sslmode=require"
   psql (16.0)
   SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, bits:
   256, compression: off)
   Type "help" for help.


   forumdb=>
```

Tương tự, bạn có thể chỉ định rằng mình hoàn toàn không muốn SSL connection bằng cách đặt `sslmode=disable`. Lần này, nếu `pg_hba.conf` có mode `hostssl`, connection sẽ bị reject, còn nếu file `pg_hba.conf` có dòng `host` thì connection sẽ được phục vụ dưới dạng không encrypted:

```text
   $ psql "postgresql://forum@localhost:5432/forumdb?sslmode=require"
   psql: error: could not connect to server: FATAL:  no pg_hba.conf entry for
   host "127.0.0.1", user "forum", database "forumdb", SSL off
```

Từ error này, bạn có thể thấy rõ rằng trong file `pg_hba.conf` không có dòng nào chấp nhận plain connection (mode `host`), hoặc ngược lại, file chỉ có các dòng `hostssl`.

Cuối cùng, nếu yêu cầu connection dùng SSL nhưng PostgreSQL server chưa được configure để dùng SSL, một error message về sự không khớp sẽ được báo cáo:

```text
   $ psql "postgresql://forum@localhost:5432/forumdb?sslmode=disable"
   psql: error: could not connect to server: server does not support SSL, but
   SSL was required
```

## Tóm tắt

Trong chapter này, chúng ta đã học rằng PostgreSQL cung cấp một infrastructure rất phong phú để quản lý permission gắn với role. Bên trong, PostgreSQL quản lý permission cho các database object khác nhau bằng ACL, và mỗi ACL chứa thông tin về tập permission, user được grant permission, và user đã grant permission đó. Đối với tabular data, thậm chí có thể định nghĩa permission theo column và permission theo row để ngăn user truy cập các subset cụ thể của data.

Permission được grant bởi các nested role theo cách inherit động hoặc theo yêu cầu, cho bạn tùy chọn fine-tune cách một role sử dụng privilege.

Cuối cùng, khi được configure phù hợp, server có thể xử lý network connection qua SSL, qua đó encrypt toàn bộ network traffic và data.

Trong chapter tiếp theo, bạn sẽ học toàn bộ về transaction và cách PostgreSQL quản lý chúng trong một scenario concurrent, cung cấp sự ổn định vững chắc cho data.

## Kiểm tra kiến thức

- **Role là gì?**

  Một role có thể là một user đơn lẻ hoặc một group user có quyền truy cập cluster và các database của cluster. Role là unit cơ bản để grant access và định nghĩa permission. Xem section *Understanding roles* để biết thêm chi tiết.

- **Clause `INHERITS` làm gì?**

  Clause `INHERITS` khiến một role inherit, tức là nhận được ngay lập tức và một cách dynamic toàn bộ permission được grant cho role mà nó inherit. Không có clause `INHERITS`, role vẫn có permission của role mà nó thuộc về, nhưng cần `SET ROLE` tường minh để sử dụng các permission đó. Xem section *Roles that inherit from other roles* để biết thêm chi tiết.

- **Access Control List (ACL) là gì?**

  ACL là specification của một tập permission gắn với một database object, và là cách PostgreSQL implement và lưu trữ permission. Xem section *ACLs* để biết thêm chi tiết.

- **Các statement để thêm permission cho một role hoặc xóa permission khỏi một role là gì?**

  Statement `GRANT` thêm permission cho một role, còn statement `REVOKE` xóa permission khỏi một role. Keyword đặc biệt `ALL` có thể được dùng để grant hoặc revoke tất cả permission có sẵn cho object, trong khi có thể chỉ định nhiều permission cùng lúc ở cả hai command. Xem section *Granting and revoking permissions* để biết thêm chi tiết.

- **Row-Level Security (RLS) là gì?**

  RLS là cách hạn chế result set của một query tùy thuộc vào role đang execute query đó. RLS có thể được áp dụng cho cả read query và write query. Xem section *RLS* để biết thêm chi tiết.

## Tài liệu tham khảo

- Tài liệu chính thức về statement `CREATE ROLE`: https://www.postgresql.org/docs/current/sql-createrole.html
- Tài liệu chính thức về statement `ALTER ROLE`: https://www.postgresql.org/docs/current/sql-alterrole.html
- Tài liệu chính thức về statement `DROP ROLE`: https://www.postgresql.org/docs/current/sql-droprole.html
- Tài liệu chính thức về statement `GRANT`: https://www.postgresql.org/docs/current/sql-grant.html
- Tài liệu chính thức về statement `REVOKE`: https://www.postgresql.org/docs/current/sql-revoke.html
- Chi tiết catalog `pg_roles` của PostgreSQL: https://www.postgresql.org/docs/current/view-pg-roles.html
- Chi tiết catalog `pg_authid` của PostgreSQL: https://www.postgresql.org/docs/current/catalog-pg-authid.html
- Tài liệu ACL của PostgreSQL: https://www.postgresql.org/docs/current/ddl-priv.html
- Chi tiết rule host-based access của PostgreSQL: https://www.postgresql.org/docs/current/auth-pg-hba-conf.html
- Các utility function ACL của PostgreSQL: https://www.postgresql.org/docs/current/functions-info.html

## Tìm hiểu thêm trên Discord

Để tham gia cộng đồng Discord của cuốn sách, nơi bạn có thể chia sẻ feedback, đặt câu hỏi cho tác giả và tìm hiểu về các bản phát hành mới, hãy quét QR code bên dưới:

https://discord.gg/jYWCjF6Tku

![QR code Discord](../assets/part-039-qr-discord.png)
