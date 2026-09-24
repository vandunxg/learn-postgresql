# 11. Transactions, MVCC, WALs và Checkpoints

Chapter này giới thiệu về transaction, một thành phần nền tảng của mọi hệ thống database cấp enterprise. Transaction là cách để database quản lý nhiều operation và biến chúng thành một operation atomic duy nhất. PostgreSQL có cơ chế transaction rất phong phú và tuân thủ standard, cho phép user xác định cụ thể các property của transaction, bao gồm cả transaction lồng nhau.

PostgreSQL phụ thuộc rất nhiều vào transaction để giữ data nhất quán giữa các connection đồng thời và các hoạt động song song; nhờ Write-Ahead Logs (WALs), PostgreSQL cố gắng hết sức để giữ data an toàn và đáng tin cậy. Hơn nữa, PostgreSQL triển khai Multi-Version Concurrency Control (MVCC), một cách để duy trì concurrency cao giữa các transaction.

Chapter này có thể được chia thành hai phần: phần đầu thiên về thực hành hơn và cung cấp các ví dụ cụ thể về transaction, cách sử dụng transaction cũng như cách hiểu MVCC. Phần thứ hai mang tính lý thuyết hơn nhiều, giải thích WAL hoạt động như thế nào và cách WAL cho phép PostgreSQL khôi phục ngay cả sau một crash.

Trong chapter này, bạn sẽ tìm hiểu các chủ đề sau:

- Các property của transaction
- Các isolation level của transaction
- MVCC là gì và hoạt động như thế nào
- Savepoint
- Deadlock
- Cách PostgreSQL xử lý persistency và consistency: WAL
- VACUUM

## Yêu cầu kỹ thuật

Để tiếp tục, bạn cần biết những nội dung sau:

- Cách phát hành SQL statement qua `psql`
- Cách connect tới cluster và một database
- Cách kiểm tra và sửa đổi configuration của cluster

Các example trong chapter có sẵn trong code repository của cuốn sách và có thể chạy trên standalone Docker image trong GitHub repository của cuốn sách: https://github.com/PacktPublishing/Learn-PostgreSQL-Second-Edition.

## Giới thiệu transaction

**Transaction là một unit công việc atomic, hoặc thành công hoặc thất bại.** Transaction là một feature quan trọng của mọi database system và là thứ cho phép database triển khai các property Atomicity, Consistency, Isolation và Durability (ACID). Nhìn chung, các property ACID có nghĩa là database phải có khả năng xử lý trọn vẹn các unit công việc (atomicity), lưu data theo cách bền vững (durability), không có các thay đổi xen kẽ trên data (consistency), và theo cách để các action đồng thời được thực thi như thể chúng đang chạy một mình (isolation).

Bạn có thể hình dung transaction là một nhóm các statement có liên quan, cuối cùng hoặc đều thành công hoặc đều thất bại. Transaction hiện diện ở khắp nơi trong database, và bạn đã sử dụng chúng từ trước dù có thể không nhận ra: các lời gọi function, các statement đơn lẻ, v.v. được thực thi trong một transaction block (nhỏ). Nói cách khác, mọi action bạn phát hành tới database đều được thực thi bên trong một transaction, ngay cả khi bạn không yêu cầu rõ ràng. Nhờ tự động bọc mọi statement độc lập vào một transaction, database engine có thể bảo đảm data của nó luôn nhất quán và được bảo vệ khỏi corruption; phần sau của chapter sẽ cho thấy PostgreSQL bảo đảm điều này như thế nào.

Tuy nhiên, đôi khi bạn không muốn database kiểm soát các statement của mình; thay vào đó, bạn muốn tự xác định boundary của transaction, và database cho phép bạn làm việc đó. Vì lý do này, chúng ta dùng implicit transaction để chỉ những transaction do database tự khởi động mà bạn không cần yêu cầu, và explicit transaction cho những transaction mà bạn yêu cầu database khởi động.

Trước khi kiểm tra hai loại transaction và so sánh chúng, chúng ta cần có thêm một chút background về các concept của transaction.

Trước hết, mỗi transaction được gán một số duy nhất, gọi là transaction identifier, viết tắt là `xid`. System tự động gán một `xid` cho các transaction mới được tạo, dù là implicit hay explicit, và bảo đảm không có hai transaction có cùng `xid` tồn tại đồng thời trong database.

Concept chính khác mà chúng ta cần sớm hiểu trong phần giải thích về transaction là PostgreSQL lưu `xid` tạo ra và/hoặc sửa đổi một tuple bên trong chính tuple đó. Lý do sẽ trở nên rõ ràng khi chúng ta xem PostgreSQL xử lý concurrency của transaction như thế nào, nên trong phạm vi phần này, hãy tạm giả định rằng mọi tuple trong mọi table đều tự động được gắn nhãn bằng giá trị `xid` của transaction đã tạo tuple đó.

Bạn có thể inspect transaction hiện tại bằng special function `txid_current()`. Ví dụ, nếu yêu cầu system thực hiện một vài statement đơn giản như thời gian hiện tại, bạn sẽ thấy mỗi statement `SELECT` được thực thi như một transaction khác nhau:

```text
   forumdb=> SELECT current_time, txid_current();
         current_time       | txid_current
   --------------------+--------------
     16:51:35.042584+01 |                4813
   (1 row)


   forumdb=> SELECT current_time, txid_current();
         current_time       | txid_current
   --------------------+--------------
     16:52:23.028124+01 |                4814
   (1 row)
```

Như bạn có thể thấy từ example trước, system đã gán hai transaction identifier khác nhau, lần lượt là 4813 và 4814, cho mỗi statement, xác nhận rằng các statement đó đã được thực thi trong những implicit transaction khác nhau. Trên system của bạn, các con số có thể sẽ khác.

Nếu inspect hidden column đặc biệt `xmin` trong một table, bạn có thể lấy thông tin về transaction đã tạo các tuple; hãy xem example sau:

```text
   forumdb=> SELECT xmin, * FROM categories;
     xmin | pk |              title             |              description
   ------+----+-----------------------+---------------------------------
      561 |   1 | DATABASE                     | Database related discussions
      561 |   2 | UNIX                         | Unix and Linux discussions
      561 |   3 | PROGRAMMING LANGUAGES | All about programming languages
   (3 rows)
```

Như bạn có thể thấy, tất cả tuple trong table trước đó đều được tạo bởi cùng một transaction, số 561.

> PostgreSQL quản lý một vài hidden column khác nhau mà bạn phải yêu cầu rõ ràng khi query table thì mới có thể thấy chúng. Cụ thể, mọi table đều có các hidden column `xmin`, `xmax`, `cmin` và `cmax`. Công dụng và mục đích của chúng sẽ được giải thích ở phần sau của chapter.

Bây giờ bạn đã biết mỗi transaction đều được đánh số và các số đó được dùng để gắn nhãn cho tuple trong mọi table, chúng ta có thể tiếp tục xem sự khác nhau giữa implicit và explicit transaction.

## So sánh implicit và explicit transaction

Implicit transaction là transaction bạn không yêu cầu nhưng system áp dụng cho các statement của bạn. Nói cách khác, PostgreSQL quyết định khi nào transaction bắt đầu và kết thúc (transaction boundary), và quy tắc rất đơn giản: mỗi statement được thực thi trong transaction riêng của nó.

Để hiểu rõ hơn concept này, hãy insert một vài record vào một table:

```text
   forumdb=> INSERT INTO tags( tag ) VALUES( 'linux' );
   INSERT 0 1
   forumdb=> INSERT INTO tags( tag ) VALUES( 'BSD' );
   INSERT 0 1
   forumdb=> INSERT INTO tags( tag ) VALUES( 'Java' );
   INSERT 0 1
   forumdb=> INSERT INTO tags( tag ) VALUES( 'Perl' );
   INSERT 0 1
   forumdb=> INSERT INTO tags( tag ) VALUES( 'Raku' );
   INSERT 0 1
```

Và hãy query data trong table:

```text
   forumdb=> SELECT xmin, * FROM tags;
     xmin | pk |     tag    | parent
   ------+----+-------+--------
     4824 |    9 | linux |
     4825 | 10 | BSD        |
     4826 | 11 | Java       |
     4827 | 12 | Perl       |
     4828 | 13 | Raku       |
   (5 rows)
```

Như bạn có thể thấy, field `xmin` có một giá trị khác nhau (tự tăng) cho mỗi tuple được insert, nghĩa là một transaction identifier (`xid`) mới đã được gán cho tuple, hay chính xác hơn là cho statement thực thi `INSERT`. Điều này có nghĩa mỗi statement được thực thi trong transaction bọc riêng cho một statement duy nhất.

> Việc bạn thấy các instance của `xid` tăng một đơn vị là vì trên machine được dùng cho các example, không có concurrency, tức là không có activity database nào khác đang diễn ra. Tuy nhiên, bạn không thể dự đoán `xid` tiếp theo trong một live system có các connection đồng thời khác nhau và các statement đang chạy.

Điều gì sẽ xảy ra nếu chúng ta insert tất cả tag trước đó trong một lần, bảo đảm rằng nếu chỉ một tag không thể được lưu vì bất kỳ lý do nào thì tất cả chúng sẽ biến mất? Để đạt mục tiêu này, chúng ta có thể dùng explicit transaction. Explicit transaction là một nhóm statement có transaction boundary được xác lập rõ: bạn phát hành statement `BEGIN` để đánh dấu điểm bắt đầu transaction, rồi dùng `COMMIT` hoặc `ROLLBACK` để kết thúc transaction. Nếu phát hành `COMMIT`, transaction được đánh dấu là thành công; do đó, data đã sửa đổi được lưu vĩnh viễn. Ngược lại, nếu phát hành `ROLLBACK`, transaction được xem là thất bại và mọi thay đổi biến mất.

Hãy xem điều này trong thực tế: thêm một nhóm tag khác, nhưng lần này nằm trong một explicit transaction duy nhất:

```text
   forumdb=> BEGIN;
   BEGIN
   forumdb=*> INSERT INTO tags( tag ) VALUES( 'PHP' );
   INSERT 0 1
   forumdb=*> INSERT INTO tags( tag ) VALUES( 'C#' );
   INSERT 0 1
   forumdb=*> COMMIT;
   COMMIT
```

Điểm khác biệt duy nhất so với nhóm statement `INSERT` trước đó là việc sử dụng rõ ràng `BEGIN` và `COMMIT`; vì transaction đã commit, data phải được lưu trong table:

```text
   forumdb=> SELECT xmin, * FROM tags;
      xmin | pk |    tag   | parent
   ------+----+-------+--------
      4824 |   9 | linux |
      4825 | 10 | BSD      |
      4826 | 11 | Java     |
      4827 | 12 | Perl     |
      4828 | 13 | Raku     |
      4829 | 14 | PHP      |
      4829 | 15 | C#       |
   (7 rows)
```

Như bạn có thể thấy, không chỉ data được lưu như mong đợi, mà hai row cuối còn có cùng transaction identifier, tức là 4829. Điều này có nghĩa PostgreSQL đã bằng cách nào đó gộp hai statement khác nhau thành một statement duy nhất.

> Khi bạn phát hành explicit transaction, `psql` thay đổi prompt bằng cách thêm một dấu hoa thị để nhắc rằng bạn đang ở trong một transaction đang mở (tức là transaction chưa hoàn tất). Nếu transaction bị abort do một error, dấu hoa thị sẽ được đổi thành dấu chấm than.

Hãy xem điều gì xảy ra nếu transaction kết thúc bằng statement `ROLLBACK`: kết quả cuối cùng là các thay đổi không được lưu. Ví dụ, hãy đổi value tag của mọi tuple thành chữ hoa hoàn toàn:

```text
   forumdb=> BEGIN;
   BEGIN
   forumdb=*> UPDATE tags SET tag = upper( tag );
   UPDATE 7
   forumdb=*> SELECT tag FROM tags;
      tag
   -------
     LINUX
     BSD
     JAVA
     PERL
     RAKU
     PHP
     C#
   (7 rows)

   forumdb=*> ROLLBACK;
   ROLLBACK
   forumdb=> SELECT tag FROM tags;
      tag
   -------
     linux
     BSD
     Java
     Perl
     Raku
     PHP
     C#
   (7 rows)
```

Đầu tiên chúng ta đã đổi tất cả mô tả thành chữ hoa, và statement `SELECT` chứng minh database đã thực hiện công việc đó, nhưng cuối cùng chúng ta đổi ý và phát hành `ROLLBACK`. Tại thời điểm này, PostgreSQL loại bỏ các thay đổi của chúng ta và giữ lại state trước transaction.

Vì vậy, chúng ta có thể tóm tắt rằng mỗi statement luôn được thực thi như một implicit transaction; còn nếu cần kiểm soát nhiều hơn đối với những gì cần thay đổi một cách atomic, bạn phải mở (`BEGIN`) và đóng (`COMMIT` hoặc `ROLLBACK`) một explicit transaction.

Việc kiểm soát một explicit transaction không có nghĩa là bạn luôn có quyền lựa chọn cách kết thúc nó; đôi khi PostgreSQL sẽ không cho phép bạn dùng `COMMIT` để hoàn tất transaction vì transaction chứa các error không thể recovery.

Ví dụ tầm thường nhất là khi bạn nhập một syntax error:

```text
   forumdb=> BEGIN;
   BEGIN
   forumdb=*> UPDATE tags SET tag = uppr( tag );
   ERROR:    function uppr(text) does not exist
   LINE 1: UPDATE tags SET tag = uppr( tag );
                                         ^
   HINT: No function matches the given name and argument types. You might
   need to add explicit type casts.
   Forumdb=!> COMMIT;
   ROLLBACK
```

Khi PostgreSQL gặp error, nó abort transaction hiện tại. Abort một transaction có nghĩa là trong khi transaction vẫn đang mở, PostgreSQL sẽ không chấp nhận bất kỳ command nào tiếp theo, kể cả `COMMIT`, và sẽ tự động phát hành command `ROLLBACK` ngay khi bạn đóng transaction. Vì vậy, ngay cả khi cố tiếp tục làm việc sau một mistake, PostgreSQL cũng sẽ từ chối các statement của bạn:

```text
   forumdb=> BEGIN;
   BEGIN
   forumdb=*> INSERT INTO tags( tag ) VALUES( 'C#' );
   INSERT 0 1
   forumdb=*> INSERT INTO tags( tag ) VALUES( PHP );
   ERROR:    column "php" does not exist
   LINE 1: INSERT INTO tags( tag ) VALUES( PHP );
   forumdb=!> INSERT INTO tags( tag ) VALUES( 'Ocaml' );
   ERROR: current transaction is aborted, commands ignored until end of
   transaction block
   forumdb=!> COMMIT;
   ROLLBACK
```

Dù vậy, xử lý syntax error hoặc tên object bị viết sai không phải là những vấn đề duy nhất bạn có thể gặp khi chạy transaction; hơn nữa, các vấn đề đó khá dễ sửa, nhưng bạn cũng có thể thấy transaction không thể tiếp tục vì có một data constraint ngăn statement hoàn tất thành công. Hãy tưởng tượng chúng ta không cho phép bất kỳ tag nào có description ngắn hơn hai ký tự:

```text
   forumdb=> ALTER TABLE tags
                ADD CONSTRAINT constraint_tag_length
                CHECK ( length( tag ) >= 2 );
   ALTER TABLE
```

Hãy xem xét một unit công việc thực hiện hai statement `INSERT` khác nhau như sau:

```text
   forumdb=> BEGIN;
   BEGIN
   forumdb=*> INSERT INTO tags( tag ) VALUES( 'C' );
   ERROR: new row for relation "tags" violates check constraint "constraint_
   tag_length"
   DETAIL:    Failing row contains (17, C, null).
   Forumdb=!> INSERT INTO tags( tag ) VALUES( 'C++' );
   ERROR: current transaction is aborted, commands ignored until end of
   transaction block
   forumdb=!> COMMIT;
   ROLLBACK
```

Như bạn đã thấy, ngay khi một DML statement thất bại, PostgreSQL abort transaction và từ chối xử lý bất kỳ statement nào khác. Cách duy nhất để bạn thoát khỏi tình huống này là kết thúc explicit transaction, và bất kể bạn kết thúc theo cách nào (dùng `COMMIT` hay `ROLLBACK`), PostgreSQL sẽ loại bỏ các thay đổi của bạn, rollback transaction hiện tại. Logic hoàn toàn tương tự áp dụng cho implicit transaction: khi một statement thất bại (vì bất kỳ lý do nào), PostgreSQL rollback implicit transaction bọc statement đó, và kết quả cuối cùng là data hoàn toàn không được persist.

Trong các example trước, chúng ta luôn cho thấy việc kết thúc transaction bằng `COMMIT`, nhưng rõ ràng là khi bạn không chắc về data, các thay đổi đã thực hiện hoặc gặp một error không thể recovery, bạn nên phát hành `ROLLBACK`. Chúng ta cho thấy `COMMIT` để làm rõ rằng PostgreSQL sẽ ngăn công việc sai kết thúc thành công.

Vậy khi nào bạn nên dùng explicit transaction? Mỗi khi có một workload phải hoặc thành công hoặc thất bại, bạn phải bọc nó trong một explicit transaction. Cụ thể, khi việc mất một phần công việc có thể gây ảnh hưởng đến data còn lại thì đó là thời điểm phù hợp để dùng transaction. Ví dụ, hãy hình dung một ứng dụng mua sắm online: chắc chắn bạn không muốn charge client trước khi đã cập nhật cart của họ và kiểm tra availability của sản phẩm trong kho. Mặt khác, với tư cách một client, tôi sẽ không muốn nhận message nói rằng order của mình đã được xác nhận, rồi chỉ sau đó phát hiện payment đã thất bại vì một lý do nào đó.

Vì vậy, do tất cả step và action phải được thực hiện một cách atomic (kiểm tra availability của sản phẩm, cập nhật cart, nhận payment, xác nhận order), explicit transaction là thứ chúng ta cần để giữ data nhất quán.
