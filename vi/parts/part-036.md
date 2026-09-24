Điều này có thể được minh họa bằng một vài lệnh đơn giản:

```text
      $ psql -U enrico forumdb


      forumdb=> SELECT * FROM forum.users;
       pk | username    |       gecos     |          email
       ----+-----------+----------------+---------------------
         1 | fluca1978 | Luca Ferrari      | fluca1978@gmail.com
         2 | sscotty71 | Enrico Pirozzi | sscotty71@gmail.com
       (2 rows)


      forumdb=> UPDATE forum.users SET gecos = upper( gecos );
      UPDATE 2


      forumdb=> SELECT * FROM forum.users;
       pk | username    |       gecos     |          email
       ----+-----------+----------------+---------------------
         1 | fluca1978 | LUCA FERRARI      | fluca1978@gmail.com
         2 | sscotty71 | ENRICO PIROZZI | sscotty71@gmail.com
       (2 rows)
```

Như bạn thấy, user `enrico` đã thực sự thay đổi tên và họ của các user hiện có thành một chuỗi toàn chữ hoa. Bây giờ hãy xem user còn lại có thể làm gì:

```text
      $ psql -U luca forumdb


       forumdb=> SELECT * FROM forum.users;
       ERROR:    permission denied for table forum.users
       forumdb=> SELECT username, gecos FROM forum.users;
        username    |       gecos
        -----------+----------------
        fluca1978 | LUCA FERRARI
        sscotty71 | ENRICO PIROZZI
        (2 rows)


        forumdb=> UPDATE forum.users SET gecos = lower( gecos );
        ERROR:    permission denied for table forum.users
```

Như bạn thấy, user `luca` không thể thực hiện bất cứ việc gì ngoài các permission được cấp cho role `forum_stats`, tức là một group mà user này là thành viên.

Có thể thay đổi privilege của user `luca` bằng cách cấp các grant mới cho role hoặc thêm một group khác có nhiều privilege hơn. Ví dụ, nếu muốn tất cả user trong group `forum_stats` không thể đọc gì ngoài các column `username` và `gecos`, đồng thời cung cấp cho `luca` một grant đặc biệt dù user này thuộc group đó, có thể explicitly đặt permission cho riêng `luca`:

```text
   forumdb=# GRANT SELECT ON forum.users TO luca;
   GRANT
```

Sau khi permission được cấp, role `luca` có thể sử dụng nó:

```text
   % psql -U luca forumdb


   forumdb=> SELECT * FROM forum.users;
    pk | username      |      gecos         |           email
    ----+-----------+----------------+---------------------
      1 | fluca1978 | LUCA FERRARI          | fluca1978@gmail.com
      2 | sscotty71 | ENRICO PIROZZI | sscotty71@gmail.com
    (2 rows)
```

Như bạn thấy, permission đặc biệt được cấp cho `luca` có hiệu lực cao hơn permission restrictive hơn được cấp cho group `forum_stats`, mà `luca` là thành viên.

Để có thể cấu hình user và group, bạn cần hiểu privilege chain.

## Tìm hiểu cách privilege được resolve

Khi một role thực hiện một SQL statement, PostgreSQL kiểm tra xem role đó có được phép thực hiện task trên object hay không. Ví dụ, khi user `luca` thực hiện `SELECT` trên table `users`, PostgreSQL xác minh xem role đó đã được cấp permission để làm việc này hay chưa.

Nếu role chưa được cấp permission explicitly (tức là bằng một statement `GRANT`), PostgreSQL sẽ tìm trong tất cả group mà role đó là thành viên. Nếu một trong các group có permission được yêu cầu, operation được cho phép. Nếu không group nào có permission được yêu cầu và permission đó cũng chưa được đặt cho special role catch-all `PUBLIC`, operation bị từ chối.

Tuy nhiên, đó mới chỉ là một phần của vấn đề: khi system kiểm tra các group mà một role là thành viên, nó dừng tìm permission nếu containing role được cấp cho role hiện tại mà không có property `INHERIT`. Thực tế, các statement `GRANT` cho phép sử dụng clause `WITH INHERIT` (tùy chọn và phải chứa giá trị true hoặc false). Nếu clause được chỉ định và giá trị là true, role sẽ dynamically inherit các permission từ containing group; nếu không thì role sẽ không inherit. Nếu option bị bỏ qua, system sẽ sử dụng giá trị của property `INHERIT` của role: nếu role có property `NOINHERIT`, `GRANT` sẽ implicitly sử dụng clause `WITH INHERIT false`; nếu không, nó sẽ implicitly sử dụng clause `WITH INHERIT true`. Vì vậy, luôn có thể quản lý cách permission được resolve thông qua các statement `GRANT`.

Trước PostgreSQL 16, statement `GRANT` không hỗ trợ clause `WITH INHERIT`; do đó, thay đổi property `INHERIT` của role là cách duy nhất để quyết định cách propagate permission.

Trong section trước, bạn đã thấy behavior mặc định của `INHERITS` hoạt động. Role `luca` inherit các permission cho phép nó thực hiện `SELECT` chỉ trên hai column của table `users`. Dù role `luca` không được cấp permission đó, system vẫn kiểm tra tất cả group mà role này là thành viên để tìm permission, và tìm thấy nó trong group `forums_stats`. Vì permission được propagate động từ một role đến tất cả role được chứa trong nó, tức là từ group đến các member của group, điều này tương đương với việc `luca` có permission đó được đặt trực tiếp trên role của mình, nên operation được cho phép. Do đó, tạo một role với property `INHERITS` (mặc định) có nghĩa là tất cả permission được cấp cho role đó sẽ được propagate động đến mọi role được chứa trong nó.

Để hiểu rõ hơn, hãy giới thiệu một group khác tên là `forum_emails`, có thể đọc column `email` trên table `users`, rồi gán group đó cho `forum_stats`. Ta có thể kỳ vọng rằng `forum_stats`, vì là member của `forum_emails`, sẽ đọc được column `email`, nhưng vì group `forum_emails` được tạo với property `NOINHERIT`, điều đó không xảy ra:

```text
    -- remove any explicit SELECT permission
    -- so luca will have only those from its group
    forumdb=# REVOKE SELECT ON forum.users FROM luca;
    REVOKE


    -- create the new group
    forumdb=# CREATE ROLE forum_emails
                 WITH NOLOGIN NOINHERIT;
    CREATE ROLE


    forumdb=# GRANT USAGE ON SCHEMA forum TO forum_emails;
    GRANT


    -- assign permissions
    forumdb=# GRANT SELECT (email)
                 ON forum.users TO forum_emails;
    GRANT


    -- assign the role to the group
    -- implicitly uses WITH INHERIT false
    forumdb=# GRANT forum_emails TO forum_stats;
    GRANT ROLE
```

Bây giờ, `luca` là member của `forum_stats` và `forum_emails`, nhưng vì group sau không dynamically propagate permission của nó đến các member, `luca` không thể nhận permission để đọc column `email`:

```text
    % psql -U luca forumdb


    forumdb=> SELECT username, gecos, email FROM forum.users;
    ERROR:    permission denied for table forum.users
```

Tuy nhiên, là member của một role khác có nghĩa là một role luôn có thể explicitly trở thành chính group đó, impersonate group và nhờ vậy nhận được tất cả permission được cấp cho group. Điều này giống như role ban đầu đang hành động thay mặt cho group role. Để có thể hành động thay mặt containing group, role phải thực hiện một statement `SET ROLE` explicit. Rõ ràng, một role không thể trở thành bất kỳ role tùy ý nào khác: nó chỉ có thể hành động thay mặt các role được cấp explicit và chỉ thay mặt các containing group. Vì vậy, nếu user `luca` thực hiện `SET ROLE` explicit để trở thành role `forum_emails`, user này sẽ có thể query column `email` trong table `users`:

```text
    forumdb=> SELECT current_role;
     current_role
     --------------
     luca
    (1 row)


    forumdb=> SET ROLE TO forum_emails;
    SET


    forumdb=> SELECT current_role;
        current_role
       --------------
        forum_emails
       (1 row)


       forumdb=> SELECT email FROM forum.users;
                 email
       ---------------------
        fluca1978@gmail.com
        sscotty71@gmail.com
       (2 rows)


       forumdb=> SELECT gecos FROM forum.users;
       ERROR:    permission denied for table users
```

Bây giờ hãy thay đổi property `INHERIT` của `GRANT` để permission được propagate động:

```text
       forumdb=# GRANT forum_emails TO forum_stats
                   WITH INHERIT true;
       GRANT ROLE
```

Và bây giờ hãy xem role `luca` có thể sử dụng đồng thời cả hai privilege của các group `forum_stats` và `forum_emails` hay không:

```text
       $ psql -U luca forumdb


       forumdb=> SELECT gecos, username, email FROM forum.users;
            gecos        | username   |          email
       ----------------+-----------+---------------------
        LUCA FERRARI     | fluca1978 | fluca1978@gmail.com
        ENRICO PIROZZI | sscotty71 | sscotty71@gmail.com
       (2 rows)
```

Tuyệt! Bây giờ role có thể sử dụng privilege của cả hai group cùng lúc mà không cần explicitly thay đổi current role của nó.

## Tổng quan về role inheritance

Khi một role là member của một hoặc nhiều role khác, việc resolve privilege diễn ra như sau:

- Nếu role có privilege được yêu cầu, không cần kiểm tra thêm gì và operation được cho phép (ví dụ, một `GRANT` explicit cho role đã được thực hiện).
- Nếu role không có privilege được yêu cầu, privilege sẽ được tìm trong các containing group (nếu có). Nếu privilege được tìm thấy trong một group và group đó được cấp với property `INHERIT` (implicit hoặc explicit), permission sẽ được áp dụng động. Ngược lại, nếu permission được tìm thấy trong bất kỳ parent group nào nhưng không được cấp với option `INHERIT`, permission sẽ không được propagate động (tức là phải sử dụng `SET ROLE`).

Trong mọi trường hợp, role luôn có thể sử dụng privilege của một group mà nó là member thông qua statement `SET ROLE` explicit. Điều này có nghĩa là property `INHERIT` chỉ được dùng để propagate privilege động, nhờ đó role không cần tự chuyển thành một role khác.

Điều đáng chú ý là việc thay đổi role thông qua `SET ROLE` explicit là một tuyên bố rằng user sẽ thực hiện một task cụ thể cần các privilege cụ thể.

## ACLs

PostgreSQL lưu các permission được cấp cho role và object dưới dạng ACL, và khi cần, nó kiểm tra ACL cho một role cụ thể cùng một database object để xác định command hoặc query có thể được thực hiện hay không. Trong section này, bạn sẽ tìm hiểu ACL là gì, chúng được lưu như thế nào và cách diễn giải chúng để hiểu một ACL cung cấp những permission nào.

Điều quan trọng cần lưu ý là ACL, và do đó cả permission, gắn chặt với role và database object. Điều này có nghĩa là việc cấp một permission cụ thể cho một object không đồng nghĩa grantee role sẽ có cùng permission trong một database khác, ngay cả khi một object có cùng tên và bản chất tồn tại trong database đó. Ví dụ, cho phép một role chạy code PL/Perl trong một database không tự động cho phép role đó chạy code PL/Perl trong các database khác.

Một ACL là biểu diễn của một nhóm permission với cấu trúc sau:

```text
   grantee=flags/grantor
```

Trong đó:

- `grantee` là tên của role mà các permission được áp dụng cho.
- `flags` là string biểu diễn các permission.
- `grantor` là user đã cấp các permission.

Bất cứ khi nào `grantor` và `grantee` có cùng tên, role đó là owner của database object.

Các flag có thể sử dụng trong một ACL được liệt kê trong bảng sau. Như bạn thấy, không phải mọi flag đều áp dụng cho mọi object: ví dụ, permission “delete” cho một function không có ý nghĩa, và permission “execute” cho một table cũng không có ý nghĩa:


| Flag | Mô tả | Statements | Áp dụng cho |
| --- | --- | --- | --- |
| a | Thêm hoặc insert dữ liệu mới | `INSERT` | Tables và columns |
| r | Đọc hoặc lấy dữ liệu | `SELECT` | Tables, columns và sequences |
| w | Ghi hoặc update dữ liệu | `UPDATE` | Tables |
| d | Xóa dữ liệu | `DELETE` | Tables |
| D | Xóa toàn bộ dữ liệu | `TRUNCATE` | Tables |
| C | Tạo object mới | `CREATE` | Databases, schemas và tablespaces |
| c | Kết nối tới database |  | Databases |
| t | Trigger hoặc phản ứng với thay đổi dữ liệu | `CREATE TRIGGER` | Tables |
| T | Tạo temporary object | `CREATE TEMP` | Tables |
| x | Tham chiếu chéo giữa dữ liệu | `FOREIGN KEY` | Tables |
| X | Thực thi code có thể chạy | `CALL` và `SELECT` | Functions, routines và procedures |
| U | Sử dụng nhiều object khác nhau |  | Sequences, schemas, foreign objects, types và languages |

*Table 10.1: Các flag của ACL*

Khi đã nắm danh sách các flag khả dĩ, việc decode một ACL như sau sẽ trở nên dễ dàng; ACL này liên quan đến một table object:

```text
   luca=arw/enrico
```

Trước hết, hãy xác định các role liên quan: `luca` và `enrico`. `luca` là role đứng trước dấu bằng; do đó, đây là role mà ACL tham chiếu đến, nghĩa là ACL này mô tả các permission mà role `luca` có. Role còn lại, `enrico`, đứng sau dấu gạch chéo và do đó là role đã cấp các permission cho role `luca`. Xét các flag, ACL cung cấp permission append (a), read (r) và write (w). Nội dung trên có thể đọc là “`enrico` đã cấp cho `luca` permission thực hiện `INSERT`, `UPDATE` và `SELECT` trên table.”

Bây giờ hãy xem một ví dụ về ACL của một table trong database: có thể dùng command `\dp` đặc biệt của `psql` để lấy thông tin về một table:

```text
   forumdb=> \dp categories
                                               Access privileges
    Schema |        Name      | Type    |    Access privileges           | Column privileges
   | Policies
   --------+------------+-------+-----------------------+--------------------
   +----------
      forum | categories | table | enrico=arwdDxt/forum+|                                          |
            |                |         | luca=arw/forum            +|                              |
            |                |         | =d/forum                   |                              |
   (1 row)
```

Các ACL được báo cáo rõ ràng trong column `Access privileges` của command output. Dòng đầu tiên của ACL nói về owner của table `categories`: vì grantee và grantor giống nhau (`forum`), đây là owner của table. Table owner `forum` có tất cả permission: append (a), read (r), write (w), delete (d), truncate (D), trigger (t) và cross-reference (x). Vì vậy, có thể hiểu dòng này là “table owner có thể làm mọi thứ trên table đó.”

Dòng thứ hai của ACL là dòng đã được decode ở trên, có nghĩa là “`luca` có thể `INSERT`, `UPDATE` và `SELECT` data.” Dòng thứ ba của ACL khó hiểu hơn một chút: grantor vẫn là role `forum`, nhưng không có grantee trước dấu bằng. Điều này có nghĩa là ACL tham chiếu đến mọi role. Vì ACL chỉ chứa permission delete (d), điều đó có nghĩa là mọi role trong database đều có thể delete row khỏi table, như user `forum` mong muốn.

ACL được xử lý để tìm một match. Hãy hình dung role `luca` muốn delete một row khỏi table và do đó phát hành một statement `DELETE`. Statement đó được cho phép hay bị từ chối?

Đọc ACL liên quan đến role `luca` (`luca=arw/forum`), rõ ràng role này không thể delete bất cứ thứ gì khỏi table. Tuy nhiên, có một ACL “catch-all” cho phép mọi role thực hiện operation `DELETE` (`=d/forum`); vì vậy, ngay cả role `luca` cũng được phép xóa tuple.

Mặt khác, một role khác (ví dụ `forum_stats`) không được phép thực hiện `INSERT` trên table vì không có permission cụ thể nào cho role đó hoặc cho bất kỳ role nào khác không được chỉ rõ.

Nhưng các ACL đó được tạo ra như thế nào? Trước hết, tất cả chúng đều được tạo bởi user `enrico`; vì vậy, giả sử user này là người đang kết nối tới database, chuỗi statement `GRANT` sẽ như sau:

```text
   -- generates ACL: luca=arw/forum
   forumdb=> GRANT SELECT, UPDATE, INSERT
                ON forum categories
                TO luca;
   GRANT


   -- generates ACL: =d/forum
   forumdb=> GRANT DELETE ON forum categories
                TO PUBLIC;
   GRANT
```

Bây giờ, sau khi đã thấy cách PostgreSQL quản lý ACL và cách nó chuyển các command `GRANT` và `REVOKE` thành ACL, đã đến lúc xem các permission mặc định được cấp cho một role.

## Default ACLs

Điều gì xảy ra nếu một object được tạo nhưng không áp dụng `GRANT` hoặc `REVOKE` cho nó? System không lưu ACL cho object đó, như bạn có thể thấy bằng cách tạo một table rỗng đơn giản và kiểm tra privilege của nó:

```text
   forumdb=> CREATE TABLE perm_test( t text );
   CREATE TABLE


   forumdb=> \dp perm_test
                                        Access privileges
   Schema |      Name      | Type   | Access privileges | Column privileges |
   Policies
```
