```text
--------+-----------+-------+-------------------+-------------------+-----
-----
forum    | perm_test | table |                             |                          |
(1 row)
```

Vì không có ACL nào gắn với table, làm thế nào PostgreSQL biết role nào được phép làm gì trên object? Câu trả lời nằm ở default privileges: PostgreSQL áp dụng một tập default privileges cho object và kiểm tra dựa trên danh sách mặc định đó.

Đáng chú ý nhất là nếu role là owner của object thì role đó có tất cả privilege khả dụng cho object như vậy. Nếu role không phải owner, các permission của `PUBLIC` sẽ được kiểm tra, tức là tất cả permission được gán cho role đặc biệt `PUBLIC` đối với loại object đó sẽ được sử dụng.

Vì lý do bảo mật, danh sách privilege gắn với `PUBLIC` khá ngắn và có thể tóm tắt như sau:

- Permission Execute (X) trên routine.
- Kết nối đến database và tạo temporary object trong database (cT).
- Sử dụng language, type và domain (U).

Như bạn có thể thấy, theo mặc định, tập privilege của `PUBLIC` không cho phép một role thực hiện điều gì thực sự nguy hiểm, vì vậy cách duy nhất để cấp quyền cho một role thực hiện action trên object là cẩn thận `GRANT` và `REVOKE` permission.

Lần đầu tiên thực hiện `GRANT` trên một object, PostgreSQL cũng đưa vào default ACL cho owner của object đó. Trong trường hợp của table foo ở trên, owner sẽ có một ACL như `luca=arwdDxt/luca` (giả sử role `luca` là owner). Vì vậy, giả sử chúng ta cấp permission thao tác data cho `enrico`:

```text
forumdb=> \dp perm_test
                                      Access privileges
Schema |      Name      | Type    | Access privileges | Column privileges |
Policies
--------+-----------+-------+-------------------+-------------------+-----
-----
forum    | perm_test | table |                             |                          |
(1 row)


    forumdb=> GRANT SELECT, INSERT,
             UPDATE, DELETE
    ON perm_test TO enrico;
    GRANT
forumdb=> \dp perm_test
                                      Access privileges
Schema |      Name    | Type    |   Access privileges      | Column privileges |
Policies
--------+-----------+-------+---------------------+-------------------+---
-------
forum     | perm_test | table | forum=arwdDxt/forum+|                               |
          |            |         | enrico=arwd/forum        |                       |
(1 row)
```

Như bạn có thể thấy, sau `GRANT`, ACL gồm hai entry: entry chúng ta vừa cấp cho user `enrico` và entry được áp dụng ngầm cho table owner `luca`.

Cũng cần lưu ý rằng ACL lưu những gì một role có thể làm, chứ không phải những gì role không thể làm. Mọi thứ không được liệt kê trong ACL đều bị từ chối. Để hiểu rõ hơn, hãy xem xét việc revoke permission của role `enrico`:

```text
forumdb=> REVOKE TRUNCATE ON perm_test FROM enrico;
REVOKE


forumdb=> \dp perm_test
                                      Access privileges
Schema |       Name    | Type    |   Access privileges      | Column privileges |
Policies
--------+-----------+-------+---------------------+-------------------+---
-------
forum     | perm_test | table | forum=arwdDxt/forum+|                               |
          |            |         | enrico=arwd/forum        |                       |
(1 row)
```

Như bạn có thể thấy, việc revoke này không thay đổi dòng ACL của role `enrico`. Role đó không có permission này; do đó việc revoke không có tác động lên ACL.

Tương tự, revoke permission của `PUBLIC` không ảnh hưởng đến các ACL đã tồn tại. Nếu chúng ta xóa permission `INSERT` khỏi mọi user, `enrico` vẫn giữ permission riêng của mình vì ACL được lưu theo kiểu cộng dồn:

```text
forumdb=> REVOKE INSERT ON perm_test FROM PUBLIC;

```

```text
forumdb=> \dp perm_test
                                      Access privileges
Schema |      Name     | Type    |   Access privileges      | Column privileges |
Policies
--------+-----------+-------+---------------------+-------------------+---
-------
forum     | perm_test | table | forum=arwdDxt/forum+|                                   |
         |             |         | enrico=arwd/forum        |                          |
(1 row)
```

Tóm lại, ACL luôn rỗng đối với một object mới được tạo. Trong tình huống này, object owner có mọi permission khả dụng, còn các role khác có default permission gắn với `PUBLIC`. `GRANT` hoặc `REVOKE` đầu tiên được thực thi trên object đó cũng sẽ tạo explicit owner ACL và, trong trường hợp là `GRANT`, thêm một ACL tương ứng.

ACL được lưu dưới dạng privilege đã cấp. Bất kỳ thứ gì không được đặt rõ ràng trong ACL đều mặc nhiên bị từ chối, như thể đã bị revoke.

## Tìm hiểu default ACL

Giờ đã rõ rằng owner của một object có tất cả permission khả dụng liên quan đến object đó. Nhưng các role khác thì sao? Có thể inspect default ACL được cung cấp khi một object được instantiate thông qua special function `acldefault`.

Function này nhận hai argument: type của object (ví dụ relation/table, function, v.v.) và giá trị OID của role được cho là sẽ tạo object. Function sẽ trả về ACL sẽ có sau khi object được tạo.

Ví dụ, để xem permission được cung cấp khi role của bạn tạo một table mới (type `r`, viết tắt của relation), bạn có thể thực hiện query sau:

```text
forumdb=> SELECT acldefault( 'r', r.oid )
             FROM pg_roles r
             WHERE r.rolname = CURRENT_ROLE;
      acldefault
---------------------
   {forum=arwdDxt/forum}
(1 row)
```

Không có gì mới ở đây, nhưng việc tạo một function (type `f`) thì sao? Bây giờ dễ dàng thấy được điều sau:

```text
forumdb=> SELECT acldefault( 'f', r.oid )
              FROM pg_roles r
              WHERE r.rolname = CURRENT_ROLE;
          acldefault
-----------------------
 {=X/forum,forum=X/forum}
(1 row)
```

Lần này có hai ACL được tạo: ACL đầu tiên cấp permission executable cho mọi user, còn ACL sau chỉ rõ owner là role `forum`, cũng với permission executable.

Bạn có thể inspect tất cả default ACL của một user cụ thể bằng OID của user đó và type của object; các type chính là `r` cho table, `c` cho column, `l` cho language và `f` cho routine và procedure. Có những type khác nữa. Hãy tham khảo tài liệu chính thức. Đã đến lúc xem cách thao tác ACL và permission trong thực tế. Trong section tiếp theo, bạn sẽ học cách xử lý permission management.

## Cấp và thu hồi permission

Như đã thấy trong Chapter 3, Managing Users and Connections, một role gắn với một tập permission, được cung cấp bằng statement `GRANT` và bị xóa bằng statement `REVOKE`. Permission được lưu nội bộ dưới dạng ACL, như đã thấy trong section trước.

Section này xem lại statement `GRANT` và `REVOKE` để giúp bạn hiểu rõ hơn cách sử dụng chúng với những database object khác nhau.

Statement `GRANT` có synopsis sau:

```text
GRANT <permission, permission, ...> ON <database-object> TO <role>;
```

Ở đây, bạn liệt kê tất cả permission muốn gắn với target role cho database object được chỉ định. Cũng có thể mở rộng statement `GRANT` bằng clause `WITH GRANT OPTION`, khiến target role có thể cấp cùng các permission mà nó đã nhận cho một role khác.

Statement `REVOKE` có synopsis tương tự:

```text
REVOKE <permission, permission, ..> ON <database-object> FROM <role>;
```

Có một role đặc biệt tên là `PUBLIC`, có thể được sử dụng khi quản lý permission. Đây không phải một role cụ thể, mà là một marker để chỉ “tất cả role khả dụng”. Nói cách khác, nếu bạn cấp một permission cho `PUBLIC`, bạn đang ngầm cấp permission đó cho mọi role khả dụng.

Nhưng “tất cả role khả dụng” nghĩa là gì? Nó có nghĩa là tất cả role hiện có và sẽ tồn tại trong tương lai. Role `PUBLIC` đại diện cho bất kỳ role nào từng hiện diện trong system, tại thời điểm permission được quản lý và cả trong tương lai.

Theo đó, để ngăn mọi user truy cập object của bạn, bạn nên luôn xóa toàn bộ permission khỏi role đặc biệt `PUBLIC`, sau đó chọn lọc cấp những permission cần thiết cho các role cụ thể.

Trong các section sau, chúng ta sẽ trình bày chi tiết những permission khác nhau để gán và xóa grouping, đồng thời phân loại chúng tùy theo database object. Theo nguyên tắc chung, danh sách permission phụ thuộc vào action bạn có thể thực hiện trên database object.

Trong nhiều trường hợp, keyword đặc biệt `ALL` là cách thay thế cho mọi permission liên quan đến database object.

## Permission liên quan đến table

Chúng ta đã thấy những permission chính liên quan đến một database table. Chúng tương ứng với các statement chính có thể chạy trên một table object, chẳng hạn `SELECT`, `INSERT`, `UPDATE`, `DELETE` và `TRUNCATE`. Ngoài ra, có thể sử dụng các keyword đặc biệt `TRIGGER` và `REFERENCES` để tạo trigger và foreign key trong một table.

Dĩ nhiên, keyword đặc biệt `ALL` bao gồm tất cả permission vừa nêu.

Ví dụ, để cấp cho role `forum_stats` permission đọc, update và insert data vào table `categories`, mà không cấp permission thực hiện các action khác, bạn có thể làm như sau sau khi kết nối với tư cách user `forum`:

```text
      forumdb=> REVOKE ALL
                ON forum.categories FROM forum_stats;
      REVOKE


        forumdb=> GRANT SELECT, INSERT, UPDATE
                  ON forum.categories TO forum_stats;
    GRANT


   forumdb=> \dp categories
                                        Access privileges
   Schema |         Name    | Type    |    Access privileges       | Column privileges |
   Policies
   --------+------------+-------+-----------------------+-------------------
   +----------
   forum     | categories | table | forum=arwdDxt/forum           +|                        |
             |              |         | forum_stats=arw/forum |                             |
   (1 row)
```

Statement `REVOKE` đầu tiên không bắt buộc, nhưng là một practice tốt. Vì chúng ta muốn bảo đảm role có chính xác những permission sắp cấp chứ không có thêm gì khác, việc xóa toàn bộ permission khỏi role bảo đảm rằng mọi statement `GRANT` trước đó sẽ không còn hiệu lực.

Như bạn có thể thấy, ACL của user `forum_stats` phản ánh các permission chúng ta đã cấp.

## Permission theo column

Vì một số statement liên quan đến table object có thể trực tiếp nhắm đến column, chẳng hạn `SELECT` và `UPDATE`, nên cũng có thể cấp hoặc revoke permission theo column. Synopsis vẫn giống vậy, nhưng bạn có thể liệt kê các column mà permission áp dụng.

Column privilege chỉ có thể được áp dụng cho các permission `SELECT`, `UPDATE`, `INSERT` và `REFERENCES` vì đó là những permission có thể tham chiếu rõ ràng đến column; keyword đặc biệt `ALL` bao hàm toàn bộ danh sách permission.

Ví dụ, hãy xét tình huống user `forum_stats` chỉ có thể tương tác với table `users` thông qua các column `gecos` và `username`, có thể đọc cả hai nhưng chỉ update column đầu tiên. User `forum` có thể gán permission như sau:

```text
   forumdb=> REVOKE ALL ON forum.users
                  FROM forum_stats;
   REVOKE


   forumdb=> GRANT SELECT (username, gecos),
                        UPDATE (gecos)
                 ON forum.users TO forum_stats;
   GRANT
```

Như đã nhấn mạnh, nên đưa statement `REVOKE` đầu tiên vào để bảo đảm permission của role được reset trước khi gán các permission mong muốn. Sau đó, chúng ta cấp permission `SELECT` và `UPDATE`, chỉ rõ các column mà mỗi statement có thể tương tác.

Side effect của statement `GRANT` trước đó là role `forum_stats` không còn có thể thực hiện `SELECT` hoặc `UPDATE` với column list rộng hơn list được chỉ định trong `GRANT`:

```text
   forumdb=> SELECT current_role;
   current_role
   --------------
   luca
   (1 row)


   -- denied, not all the columns can be read!
   forumdb=> SELECT * FROM forum.users;
   ERROR:    permission denied for table users


   -- allowed
   forumdb=> SELECT gecos, username FROM forum.users;
          gecos        | username
   ----------------+-----------
      LUCA FERRARI     | fluca1978
      ENRICO PIROZZI | sscotty71
   (2 rows)


   -- denied, the 'username' column cannot be updated!
   forumdb=> UPDATE users SET username = upper( username );
   ERROR:    permission denied for table users


   -- allowed
   forumdb=> UPDATE forum.users SET gecos = lower( gecos );
   UPDATE 2
```

Bây giờ hãy inspect permission của table `users`:

```text
   forumdb=> \dp forum.users
                                        Access privileges
   Schema | Name      | Type   |   Access privileges     |    Column privileges         |
   Policies
   --------+-------+-------+---------------------+------------------------+--
   --------
   forum     | users | table | forum=arwdDxt/forum | username:                         +|
            |        |        |                         |    forum_stats=r/forum +|
            |        |        |                         | gecos:                      +|
            |        |        |                         |    forum_stats=rw/forum |
            |        |        |                                  | email:
   +|
            |        |        |                                  | forum_emails=r/forum
   |


   (1 row)
```

Có hai điểm quan trọng ở đây khác với tất cả ví dụ trước. Thứ nhất, column `Access privileges` không bao gồm entry nào liên quan đến role `forum_stats`, dù chúng ta đã cấp permission rõ ràng. Thứ hai, column `Column privileges` giờ có đầy các row liên quan đến role `forum_stats`.

Mỗi row trong `Column privileges` tham chiếu chính xác đến một column của table và chứa một ACL cho mỗi role được phép. Ví dụ, column `username` có ACL `forum_stats=r/forum`, nghĩa là role `forum_stats` có read permission (tức `SELECT`) trên column đó. Column `gecos` có ACL `forum_stats=rw/forum`, được hiểu là role `forum_stats` có thể vừa đọc vừa ghi trên column (tức `SELECT` và `UPDATE`).

Tóm lại, nếu role được cấp một hoặc nhiều permission trên toàn bộ column, ACL được đặt trong column `Access privileges`; còn nếu permission liên quan đến các column cụ thể, ACL được hiển thị trong column `Column privileges`.

Bạn phải cẩn thận để không làm các permission xung đột với nhau. Ví dụ, giả sử chúng ta cấp nhầm permission `SELECT` cho role `forum_stats`:

```text
   forumdb=> GRANT SELECT
                 ON forum.users TO forum_stats;
   GRANT
```

Nếu inspect permission sau statement như vậy, chúng ta có thể thấy ACL đã được chèn thành một access privilege:

```text
   forumdb=> \dp users
                                        Access privileges
   Schema | Name      | Type   |   Access privileges     |    Column privileges          |
   Policies
   --------+-------+-------+---------------------+------------------------+--
   --------
   forum     | users | table | forum=arwdDxt/forum+| username:                            +|
            |         |         | forum_stats=r/forum |        forum_stats=r/forum +|
            |         |         |                         | gecos:                       +|
            |         |         |                         |    forum_stats=rw/forum |
   (1 row)
```

Permission nào sẽ được xét trong trường hợp có statement `SELECT`?

Có thể dễ dàng kiểm tra và thấy rằng PostgreSQL coi permission được cấp sau cùng là rộng hơn permission được cấp cho column. Vì vậy, role đã được cấp khả năng select mọi column trên table:

```text
   forumdb=> SELECT * FROM users;
      pk | username    |       gecos       |          email
   ----+-----------+----------------+---------------------
       1 | fluca1978 | luca ferrari        | fluca1978@gmail.com
       2 | sscotty71 | enrico pirozzi | sscotty71@gmail.com
   (2 rows)
```

Sửa vấn đề có thể không đơn giản như bạn nghĩ. Revoke read permission trên các column mà bạn không muốn role truy cập có thể không cho kết quả như mong đợi, ngay cả khi được thực hiện bởi table owner (user `forum`):

```text
   forumdb=> REVOKE SELECT (pk, email)
                ON users FROM forum_stats;
   REVOKE
```

Nếu bạn nhớ, `REVOKE` không lưu ACL mà sửa đổi các ACL hiện có. Trong trường hợp cụ thể này, vì không có gì liên quan đến các column `pk` và `email` nói trên, statement `REVOKE` không thay đổi gì:

```text
   forumdb=> \dp users
```

```text
   forumdb=> \dp users
                                        Access privileges
   Schema | Name      | Type   |   Access privileges       |    Column privileges         |
   Policies
   --------+-------+-------+---------------------+------------------------+--
   --------
   forum     | users | table | forum=arwdDxt/forum+| username:                           +|
            |        |        | forum_stats=r/forum |          forum_stats=r/forum +|
            |        |        |                           | gecos:                      +|
            |        |        |                           |    forum_stats=rw/forum |
   (1 row)
```

Nguyên tắc chung là mọi statement `GRANT` cụ thể đều bị hủy bởi statement đối ứng `REVOKE`. Trong ví dụ này, vì statement `GRANT` cuối cùng được phát hành mà không có danh sách column cụ thể, chúng ta cần phát hành statement `REVOKE` từ user `forum` mà không có danh sách column:

```text
   forumdb=> REVOKE SELECT
                 ON users FROM forum_stats;
   REVOKE
```

Tuy nhiên, việc này cũng xóa các grant permission theo column, vì vậy sau `REVOKE`, role `forum_stats` sẽ không còn có thể thực hiện `SELECT` trên các column `username` và `gecos`. Để cấp lại cho role, bạn phải phát hành lại statement `GRANT` cho các column đích.

Ví dụ trước cho thấy việc áp dụng permission ở mức fine-grain đòi hỏi sự chú ý và cẩn thận, vì một statement `GRANT` hoặc `REVOKE` quá rộng có thể tạo ra kết quả mà thoạt nhìn bạn không mong đợi.

## Permission liên quan đến sequence

Sequence là một object giống table, tạo ra một stream các value mới an toàn với transaction, thường được dùng cho các key tự sinh (synthetic).

Có ba permission chính gắn với một sequence: `USAGE` cho phép query value mới từ sequence; privilege `SELECT` cho phép query value cuối cùng hoặc hiện tại từ sequence (nhưng không lấy value mới); và cuối cùng, privilege `UPDATE` là một extension đặc thù của PostgreSQL cho phép set và/hoặc reset value của sequence.

Vì privilege `USAGE` là privilege duy nhất được SQL standard công nhận, nếu bạn cấp nó cho một role thì role đó sẽ tự động có thể thực hiện các action yêu cầu privilege `SELECT` và `UPDATE`.
