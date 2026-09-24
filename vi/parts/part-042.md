Trong lúc đó, hãy thực thi các statement sau trong một session khác:

```text
-- session 2
forumdb=> BEGIN;
BEGIN
forumdb=> SELECT txid_current(), txid_current_snapshot();
   txid_current | txid_current_snapshot
--------------+------------------------
       4931 | 4930:4930:
(1 row)


forumdb=> UPDATE tags SET tag = lower( tag );
-- LOCKED!!!!
```

Transaction 4931 bị lock vì PostgreSQL không thể quyết định nên áp dụng data manipulation nào. Một mặt, transaction 4930 áp dụng việc đổi tất cả tag thành chữ hoa, nhưng đồng thời, transaction 4931 lại áp dụng việc đổi chính data đó thành chữ thường.

Vì hai thay đổi xung đột, và kết quả cuối cùng (tức là kết quả sẽ được consolidate trong database) phụ thuộc vào thứ tự chính xác mà các thay đổi được áp dụng (đặc biệt là thay đổi nào được áp dụng sau cùng), PostgreSQL không thể cho phép cả hai transaction tiếp tục. Vì 4930 đã áp dụng các thay đổi trước 4931, transaction sau bị suspend và chờ transaction 4930 hoàn tất, dù thành công hay thất bại. Ngay khi bạn kết thúc transaction đầu tiên, transaction thứ hai sẽ được unblock (hiển thị status message cho statement `UPDATE`):

```text
-- session 1
forumdb=> COMMIT;
COMMIT


-- session 2
UPDATE 6
-- unblocked, can proceed further ...
forumdb=>
```

Vì vậy, MVCC không phải là silver bullet chống lại việc sử dụng lock, nhưng cho phép concurrency tốt hơn trong hoạt động tổng thể của database.

Tuy nhiên, MVCC có một cost: vì system phải duy trì các version khác nhau của tuple tùy theo các transaction đang active và snapshot của chúng, storage sẽ thực sự tăng lên vượt quá kích thước hiệu dụng của data đã được consolidate.

Để ngăn vấn đề này, một tool chuyên biệt có tên `VACUUM`, cùng với "người anh em" chạy nền là `autovacuum`, chịu trách nhiệm scan các table (và index) để tìm những version của tuple có thể bị loại bỏ, từ đó reclaim storage space. Nhưng khi nào một tuple version đủ điều kiện bị `VACUUM` hủy? Đó là khi không còn transaction nào tham chiếu đến tuple xid (tức là `xmin`), nghĩa là khi tuple không còn được consolidate nữa.

## Các isolation level của transaction

Trong một database system concurrent, bạn có thể gặp ba vấn đề khác nhau:

- **Dirty reads:** Dirty read xảy ra khi database cho phép một transaction thấy data đang được xử lý từ các transaction khác chưa hoàn tất. Nói cách khác, data chưa được consolidate đã hiển thị với các transaction khác. Không database nào sẵn sàng cho production cho phép điều đó, và PostgreSQL cũng không ngoại lệ: bạn có thể yên tâm rằng transaction của mình chỉ thấy data đã được consolidate; và để được consolidate, các transaction đã tạo ra data đó phải hoàn tất.
- **Unrepeatable reads:** Unrepeatable read xảy ra khi cùng một query, bên trong cùng một transaction, được thực thi nhiều lần nhưng thấy một tập data khác nhau. Về bản chất, điều này có nghĩa data đã thay đổi giữa hai lần thực thi liên tiếp của cùng một query trong cùng transaction. PostgreSQL không cho phép loại vấn đề này nhờ snapshot: mỗi transaction có thể thấy snapshot của data hiện có, tùy thuộc vào các transaction boundary cụ thể.
- **Phantom reads:** Phantom read khá giống unrepeatable read, nhưng thứ thay đổi giữa các lần thực thi liên tiếp của cùng một query là kích thước của result set. Điều này có nghĩa data không thay đổi, nhưng data mới đã được "append" vào result set của lần thực thi trước.

SQL standard cung cấp bốn isolation level mà một transaction có thể chọn để ngăn các vấn đề trước đó:

- **Read uncommitted:** Level thấp nhất có thể.
- **Read committed:** Isolation level mặc định trong PostgreSQL.
- **Repeatable read:** Hữu ích cho các job dài, vì system không thấy effects của các transaction concurrent; điều này cho phép chúng ta làm việc trên một snapshot nhất quán trong toàn bộ thời gian thực thi transaction.
- **Serializable:** Isolation level mạnh nhất hiện có.

Mỗi level cung cấp isolation tăng dần trên level trước đó; ví dụ, `READ COMMITTED` bao hàm behavior của `READ UNCOMMITTED`, `REPEATABLE READ` bao hàm `READ COMMITTED` (và `READ UNCOMMITTED`), còn `SERIALIZABLE` bao hàm tất cả level trước đó.

PostgreSQL không hỗ trợ tất cả level trước đó, như bạn sẽ thấy chi tiết trong các subsection sau. Bạn luôn có thể chỉ định isolation level mong muốn cho một explicit transaction ngay khi transaction bắt đầu; mọi isolation level đều có cùng tên như trong danh sách trước đó. Ví dụ, lệnh sau bắt đầu một transaction ở mode `READ` committed:

```text
forumdb=> BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
BEGIN
```

Bạn có thể bỏ keyword tùy chọn `TRANSACTION`, dù theo chúng tôi việc giữ nó giúp dễ đọc hơn. Cũng có thể set isolation level của transaction một cách rõ ràng bằng statement `SET TRANSACTION`. Ví dụ, snippet sau tạo ra cùng effect như ví dụ trước:

```text
forumdb=> BEGIN;
BEGIN
forumdb=> SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
SET
```

Cần lưu ý rằng không thể thay đổi isolation level của transaction một khi transaction đã bắt đầu. Để có effect, statement `SET TRANSACTION` phải là statement đầu tiên được thực thi trong một transaction block. Mọi statement `SET TRANSACTION` tiếp theo nếu thay đổi isolation level đã được set sẽ tạo ra failure và đưa transaction vào state đang abort; nếu `SET TRANSACTION` tiếp theo không thay đổi isolation level, nó sẽ không có effect và cũng không tạo error.

Để hiểu rõ hơn trường hợp này, sau đây là một workflow không đúng, trong đó isolation level được thay đổi sau khi transaction đã thực thi một statement, dù statement đó không thay đổi data:

```text
forumdb=> BEGIN;
BEGIN
forumdb=> SELECT count(*) FROM tags;
   count
-------
     7
(1 row)
-- a query has been executed, the SET TRANSACTION
-- is not anymore the very first command
forumdb=> SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
ERROR:        SET TRANSACTION ISOLATION LEVEL must be called before any query
```

Trong các section sau, chúng ta sẽ thảo luận chi tiết từng isolation level.

## READ UNCOMMITTED

Isolation level `READ UNCOMITTED` cho phép transaction gặp vấn đề dirty reads, nghĩa là nó có thể thấy data chưa được consolidate từ các transaction chưa hoàn tất khác.

PostgreSQL không hỗ trợ isolation level này vì suy cho cùng, đây không phải là một isolation level thực sự. Thực tế, `READ UNCOMMITTED` có nghĩa là không có isolation giữa các transaction, và đây chắc chắn là tình huống xảy ra data corruption do data bị interleave.

Bạn có thể set isolation level một cách rõ ràng, nhưng PostgreSQL sẽ bỏ qua yêu cầu của bạn và âm thầm set nó thành `READ COMMITTED` mạnh mẽ hơn.

## READ COMMITTED

Isolation level `READ COMMITTED` là level mặc định được PostgreSQL sử dụng; nếu bạn không set level, mọi transaction (implicit hoặc explicit) đều sẽ có isolation level này.

Level này ngăn dirty reads và cho phép transaction hiện tại thấy toàn bộ data đã được consolidate mỗi khi một statement đơn lẻ trong transaction được thực thi. Chúng ta đã thấy behavior này trong thực tế ở ví dụ về concurrent session.

## REPEATABLE READ

Isolation level `REPEATABLE READ` quy định rằng mọi statement trong một transaction chỉ thấy data đã được consolidate tại thời điểm transaction bắt đầu hoặc, chính xác hơn, tại thời điểm statement đầu tiên của transaction bắt đầu.

## SERIALIZABLE

Isolation level `SERIALIZABLE` áp dụng level `REPEATABLE READ` và bảo đảm rằng hai transaction concurrent có thể hoàn tất thành công, nhưng chỉ khi kết quả cuối cùng sẽ giống với trường hợp hai transaction chạy theo thứ tự tuần tự.

Nói cách khác, nếu hai (hoặc nhiều) transaction có isolation level `SERIALIZABLE` và cố sửa cùng một subset data theo cách xung đột, PostgreSQL sẽ bảo đảm chỉ một transaction có thể hoàn tất và khiến transaction còn lại thất bại.

Hãy xem điều này trong thực tế bằng cách tạo một transaction ban đầu và sửa một subset data:

```text
-- session 1
forumdb=> BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
BEGIN
forumdb=> UPDATE tags SET tag = lower( tag );
UPDATE 7
```

Để mô phỏng concurrency, hãy tạm dừng transaction này và mở một transaction mới trong session khác, áp dụng các thay đổi khác lên cùng set data:

```text
-- session 2
forumdb=> BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
BEGIN
forumdb=> UPDATE tags SET tag = '[' || tag || ']';
-- blocked
```

Vì set data bị thao tác là như nhau, transaction thứ hai bị lock, như chúng ta đã thấy ở một ví dụ khác. Bây giờ, giả sử transaction đầu tiên hoàn tất thành công:

```text
-- session 1
forumdb=> COMMIT;
COMMIT
```

PostgreSQL nhận ra rằng nếu cũng cho transaction kia tiếp tục thì sẽ phá vỡ promise của `SERIALIZABLE`, vì việc áp dụng các transaction theo thứ tự tuần tự sẽ tạo ra những kết quả khác nhau, tùy theo thứ tự của chúng.

Vì vậy, ngay khi transaction đầu tiên commit, transaction thứ hai tự động bị abort với một serializable error:

```text
-- session 2
forumdb=> UPDATE tags SET tag = '[' || tag || ']';
ERROR:     could not serialize access due to concurrent update
```

Điều gì xảy ra nếu transaction thao tác trên data có vẻ không liên quan? Một transaction vẫn có thể thất bại; thực tế, hãy sửa một tuple duy nhất từ một transaction:

```text
-- session 1
forumdb=> BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
BEGIN
forumdb=> UPDATE tags SET tag = '{' || tag || '}' WHERE tag = 'java';
UPDATE 1
```

Trong lúc đó, hãy sửa chính xác một tuple khác từ một session khác:

```text
-- session 2
forumdb=> BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
BEGIN
forumdb=> UPDATE tags SET tag = '[' || tag || ']' WHERE tag = 'perl';
UPDATE 1
```

Lần này, transaction thứ hai không bị lock vì các tuple bị chạm tới hoàn toàn khác nhau. Tuy nhiên, ngay khi transaction đầu tiên thực thi `COMMIT`, transaction thứ hai không còn có thể tự `COMMIT` được nữa:

```text
-- session 2 (assume session 1 has issued COMMIT)
forumdb=> COMMIT;
ERROR:     could not serialize access due to read/write dependencies among
transactions
DETAIL: Reason code: Canceled on identification as a pivot, during commit
attempt.
HINT:     The transaction might succeed if retried.
```

Đây là một scenario khá phổ biến khi sử dụng serializable transaction: application hoặc user phải sẵn sàng thực thi transaction của mình lặp đi lặp lại vì PostgreSQL có thể khiến nó thất bại do tính serializable của các workflow.

## Giải thích MVCC

`xmin` chỉ là một phần trong câu chuyện quản lý MVCC. PostgreSQL gắn nhãn cho mọi tuple trong database bằng bốn field khác nhau có tên `xmin` (đã mô tả), `xmax`, `cmin` và `cmax`. Tương tự như những gì bạn đã học về `xmin`, để làm cho các field đó xuất hiện trong query result, bạn cần reference chúng một cách rõ ràng, chẳng hạn:

```text
forumdb=> SELECT xmin, xmax, cmin, cmax, * FROM tags ORDER BY tag;
   xmin | xmax | cmin | cmax | pk | tag         | parent
    ------+------+------+------+----+------+--------
   4854 |    0 |      0 |      0 | 24 | c++     |
   4853 |    0 |      0 |      0 | 23 | java |
   4852 |    0 |      0 |      0 | 22 | perl |
   4855 |    0 |      0 |      0 | 25 | unix |
(4 rows)
```

Ý nghĩa của `xmin` đã được mô tả trong section trước: nó chỉ transaction identifier của transaction đã tạo tuple. Mặt khác, field `xmax` chỉ xid của transaction đã invalidate tuple, chẳng hạn vì transaction đó đã xóa data. Các field `cmin` và `cmax` lần lượt chỉ command identifier đã tạo và invalidate tuple trong cùng transaction (PostgreSQL đánh số mọi statement trong một transaction, bắt đầu từ 0).

Tại sao việc theo dõi statement identifier (`cmin`, `cmax`) lại quan trọng? Vì isolation level thấp nhất mà PostgreSQL áp dụng là `READ COMMITTED`, mọi statement (tức command) trong một transaction phải thấy snapshot của data đã được consolidate tại thời điểm command bắt đầu.

Bạn có thể thấy cách sử dụng `cmin` và `cmax` trong cùng một transaction ở ví dụ sau. Trước hết, chúng ta bắt đầu một explicit transaction, sau đó insert một vài tuple bằng hai statement `INSERT` khác nhau; điều này có nghĩa các tuple được tạo sẽ có `cmin` khác nhau:

```text
   forumdb=> BEGIN;
   BEGIN


   forumdb=> SELECT xmin, xmax, cmin, cmax, tag, txid_current()
               FROM tags ORDER BY tag;


      xmin | xmax | cmin | cmax | tag        | txid_current
   ------+------+------+------+------+--------------
     4854 |     0 |     0 |     0 | c++   |           4856
     4853 |     0 |     0 |     0 | java |            4856
     4852 |     0 |     0 |     0 | perl |            4856
     4855 |     0 |     0 |     0 | unix |            4856
   (4 rows)


   -- first writing command (number 0)
   forumdb=> INSERT INTO tags( tag ) values( 'raku' );
   INSERT 0 1


   -- second writing command (number 1)
   forumdb=> INSERT INTO tags( tag ) values( 'lua' );
   INSERT 0 1


   -- fourth command within transaction (number 3)
   forumdb=> SELECT xmin, xmax, cmin, cmax, tag, txid_current()
              FROM tags ORDER BY tag;


     xmin | xmax | cmin | cmax | tag      | txid_current
   ------+------+------+------+------+--------------
     4854 |     0 |     0 |     0 | c++   |           4856
     4853 |     0 |     0 |     0 | java |            4856
     4856 |     0 |     1 |     1 | lua   |           4856
     4852 |     0 |     0 |     0 | perl |             4856
     4856 |     0 |     0 |     0 | raku |             4856
     4855 |     0 |     0 |     0 | unix |             4856
   (6 rows)
```

Cho đến đây, trong cùng một transaction, hai tuple mới được insert có `xmin` giống `txid_current()`; hiển nhiên, các tuple đó được tạo bởi cùng một transaction. Tuy nhiên, hãy lưu ý rằng tuple thứ hai, vì nằm trong writing command thứ hai, có `cmin` chứa 1 (việc đếm command bắt đầu từ 0).

Vì vậy, PostgreSQL biết thời điểm mọi tuple được tạo bằng cách dựa trên một transaction và một command bên trong transaction đó.

Hãy tiếp tục với transaction của chúng ta: khai báo một cursor chứa query trên table `tags`, rồi xóa tất cả tuple trừ hai tuple. Session của transaction tiếp tục như sau:

```text
   forumdb=> DECLARE tag_cursor CURSOR FOR SELECT xmin, xmax, cmin, cmax,
   tag, txid_current() FROM tags ORDER BY tag;
   DECLARE CURSOR


   forumdb=> DELETE FROM tags WHERE tag NOT IN ( 'perl', 'raku' );
   DELETE 4


   forumdb=> SELECT xmin, xmax, cmin, cmax, tag, txid_current()
               FROM tags ORDER BY tag;
      xmin | xmax | cmin | cmax | tag        | txid_current
   ------+------+------+------+------+--------------
      4852 |    0 |      0 |      0 | perl |             4856
      4856 |    0 |      0 |      0 | raku |             4856
   (2 rows)
```

Như bạn thấy, table hiện chỉ còn hai tuple, đây vốn là behavior được mong đợi sau thao tác trên.

Tuy nhiên, cursor đã được khởi động trước statement `DELETE`, nên nó phải thấy data như trước statement `DELETE`. Thực tế, nếu hỏi cursor xem nó có thể lấy data nào, chúng ta thấy nó trả về toàn bộ tuple như trước statement `DELETE`:

```text
   forumdb=> FETCH ALL FROM tag_cursor;
      xmin | xmax | cmin | cmax | tag        | txid_current
   ------+------+------+------+------+--------------
      4854 | 4856 |      2 |      2 | c++    |             4856
      4853 | 4856 |      2 |      2 | java |             4856
      4856 | 4856 |      0 |      0 | lua    |             4856
      4852 |    0 |      0 |      0 | perl |             4856
      4856 |    0 |      0 |      0 | raku |             4856
      4855 | 4856 |      2 |      2 | unix |             4856
   (6 rows)
```

Có một điểm quan trọng cần lưu ý: mọi tuple đã bị delete đều có value trong `xmax` chứa transaction identifier hiện tại (4856), nghĩa là chính transaction này đã delete các tuple đó. Tuy nhiên, transaction vẫn chưa commit; vì vậy, các tuple vẫn còn đó nhưng được đánh dấu là gắn với snapshot kết thúc ở 4856.

Hơn nữa, các tuple đã bị delete có `cmax` chứa value 2, nghĩa là các tuple đã bị delete bởi writing command thứ ba trong transaction.

Vì cursor được define trước statement, nó có thể "thấy" các tuple như trước đó, ngay cả khi PostgreSQL biết chính xác chúng đã biến mất từ thời điểm nào.

> Người đọc có thể đã nhận thấy `cmin` và `cmax` chứa cùng một value; đó là vì các field này overlap cùng một storage.

Trong section tiếp theo, bạn sẽ thấy cách disassemble một transaction thành các phần nhỏ hơn bằng savepoint.

## Savepoint

Một transaction là một block công việc phải thành công hoặc thất bại toàn bộ. Savepoint là cách chia một transaction thành các block nhỏ hơn có thể được rollback độc lập với nhau. Nhờ savepoint, bạn có thể chia một transaction lớn (một transaction có nhiều statement) thành các chunk nhỏ hơn, cho phép một subset của transaction lớn thất bại mà không làm toàn bộ transaction thất bại. PostgreSQL không xử lý transaction nesting, nên bạn không thể phát hành một tập statement `BEGIN` hoặc `COMMIT`/`ROLLBACK` lồng nhau. Tuy nhiên, savepoint cho phép PostgreSQL mô phỏng việc nesting của các transaction block.

Savepoint được đánh dấu bằng một mnemonic name, có thể dùng name đó để commit hoặc rollback. Name phải unique trong transaction; nếu bạn sử dụng lặp đi lặp lại cùng một name, các savepoint trước đó có cùng name sẽ bị loại bỏ. Hãy xem một ví dụ:

```text
   forumdb=> BEGIN;
   BEGIN
   forumdb=> INSERT INTO tags( tag ) VALUES ( 'Eclipse IDE' );
   INSERT 0 1
   forumdb=> SAVEPOINT other_tags;
   SAVEPOINT
   forumdb=> INSERT INTO tags( tag ) VALUES ( 'Netbeans IDE' );
   INSERT 0 1
   forumdb=> INSERT INTO tags( tag ) VALUES ( 'Comma IDE' );
   INSERT 0 1
   forumdb=> ROLLBACK TO SAVEPOINT other_tags;
```
