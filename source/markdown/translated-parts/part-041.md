## Time trong transaction

Transaction có tính *time-discrete*: time không thay đổi trong suốt một transaction. Bạn có thể dễ dàng thấy điều này bằng cách mở một transaction và query current time nhiều lần:

```text
   forumdb=> BEGIN;
   BEGIN
   forumdb=*> SELECT CURRENT_TIME;
         current_time
   --------------------
      14:51:50.730287+01
   (1 row)


   forumdb=*> SELECT pg_sleep_for( '5 seconds' );
      pg_sleep_for
   --------------


   (1 row)


   forumdb=*> SELECT CURRENT_TIME;
         current_time
   --------------------
      14:51:50.730287+01
   (1 row)


   forumdb=*> ROLLBACK;
   ROLLBACK
```

Nếu thực sự cần một nguồn thời gian liên tục trong khi đang chạy transaction, bạn có thể dùng `clock_timestamp()`:

```text
   forumdb=> BEGIN;
   BEGIN
   forumdb=*> SELECT CURRENT_TIME, clock_timestamp()::time;
         current_time      | clock_timestamp
   --------------------+-----------------
      14:53:17.479177+01 | 14:53:22.152435
   (1 row)


   forumdb=*> SELECT pg_sleep_for( '5 seconds' );
     pg_sleep_for
   --------------


   (1 row)


   forumdb=*> SELECT CURRENT_TIME, clock_timestamp()::time;
         current_time       | clock_timestamp
   --------------------+-----------------
     14:53:17.479177+01 | 14:53:33.022884



   forumdb=*> ROLLBACK;
   ROLLBACK
```

Làm thế nào để phân biệt transaction này với transaction khác? Mỗi transaction nhận một identifier, như sẽ giải thích trong phần tiếp theo.

## Thêm về transaction identifier – vấn đề xid wraparound

Như đã giải thích, mỗi transaction được gắn với một numeric identifier gọi là `xid` (trong đó `x` là viết tắt của transaction còn `id` là viết tắt của identifier). Counter này sử dụng phép toán modulo `2^31`, nên với mọi giá trị `xid` hiện tại sẽ có `2^31` transaction trong tương lai, tức là có giá trị cao hơn. Mặt khác, có `2^31` transaction trong quá khứ, tức là có giá trị thấp hơn. Vì vậy, counter `xid` là một giá trị cyclic.

PostgreSQL không cho phép hai transaction dùng chung một `xid` trong bất kỳ trường hợp nào. Tuy nhiên, vì là một counter tự động tăng, sớm hay muộn `xid` cũng sẽ wraparound, nghĩa là nó sẽ bắt đầu đếm lại. Đây được gọi là vấn đề xid wraparound, và PostgreSQL thực hiện rất nhiều công việc để ngăn điều này xảy ra, như bạn sẽ thấy sau. Nhưng nếu database ở gần wraparound, PostgreSQL sẽ bắt đầu cảnh báo trong log bằng những message như sau:

```text
   WARNING: database "forumdb" must be vacuumed within 177009986
   transactions
   HINT: To avoid a database shutdown, execute a database-wide VACUUM in
   "forumdb".
```

Nếu đọc kỹ warning message, bạn sẽ thấy system đang nói với system administrator rằng nó sẽ shutdown ngay khi phát hiện nguy cơ xid wraparound. Lý do là trong những hoàn cảnh như vậy, data có thể bị mất; để ngăn điều đó, system sẽ tự động shutdown khi xid wraparound đến gần.

Tuy nhiên, có một cách để tránh automatic shutdown này: buộc thực hiện cleanup bằng tool PostgreSQL có tên `VACUUM`. Như bạn sẽ thấy ở phần sau của chapter, một trong các capability của `VACUUM` là freeze các tuple cũ để ngăn side effect của xid wraparound, qua đó cho phép database service tiếp tục hoạt động. Nhưng xid wraparound gây ra những effect gì?

Để hiểu những vấn đề này, chúng ta phải nhớ rằng mỗi transaction được gán một `xid` duy nhất, và `xid` tiếp theo có thể gán được lấy bằng cách tăng `xid` cuối cùng đã được gán lên một đơn vị.

Điều này có nghĩa là một transaction có `xid` cao hơn đã bắt đầu muộn hơn một transaction có `xid` thấp hơn, ngay cả khi hai transaction có thể đang chạy song song. Vì mọi tuple trong mọi table đều lưu transaction identifier đã tạo ra tuple đó (trong hidden field `xmin`), một tuple có `xid` cao hơn chắc chắn được tạo sau một tuple có `xid` tạo ra thấp hơn.

Nhưng khi `xid` overflow và do đó bắt đầu lại việc đánh số từ các số thấp, những transaction bắt đầu muộn hơn sẽ xuất hiện với `xid` thấp hơn các transaction đang chạy từ trước, và vì vậy đột nhiên có vẻ như chúng nằm trong quá khứ. Kết quả là các tuple có `xmin` transaction cao hơn sẽ có vẻ như được tạo trong tương lai, và do đó sẽ xuất hiện sự không khớp giữa diễn tiến theo thời gian và storage của tuple.

Để tránh xid wraparound, PostgreSQL triển khai cơ chế gọi là *tuple freezing*: một khi tuple đã được freeze, `xmin` của nó phải luôn được xem là nằm trong quá khứ so với mọi transaction đang chạy, ngay cả khi giá trị `xmin` của nó cao hơn `xid` của mọi transaction đang chạy hiện tại. Thực tế, mọi tuple đều chứa một bit thông tin đặc biệt cho PostgreSQL biết tuple đã được freeze hay chưa.

Vì vậy, khi `xid` overflow đến gần, `VACUUM` thực hiện một đợt freeze trên diện rộng, đánh dấu tất cả tuple trong quá khứ là frozen, để ngay cả khi `xid` bắt đầu đếm lại từ những số thấp hơn, các tuple đã có trong database vẫn luôn xuất hiện trong quá khứ.

> Counter `xid` bắt đầu ở giá trị đặc biệt là 3 và giữ các giá trị thấp hơn chỉ cho mục đích nội bộ. Vì vậy, không thể có transaction đang chạy với `xid` thấp hơn 3. Trong các version PostgreSQL cũ hơn, `VACUUM` thực sự xóa giá trị `xmin` của các tuple cần freeze, thay giá trị đó bằng giá trị đặc biệt 2; vì thấp hơn giá trị nhỏ nhất có thể sử dụng là 3, giá trị này cho biết tuple nằm trong quá khứ. Tuy nhiên, khi cần forensic analysis, việc có `xmin` ban đầu là hữu ích, và vì vậy PostgreSQL hiện dùng một status bit để cho biết tuple đã được freeze hay chưa.

## Virtual và real transaction identifier

Vì transaction identifier là một resource quan trọng, PostgreSQL đủ thông minh để tránh lãng phí các số transaction identifier. Cụ thể, khi một transaction được khởi tạo, cluster sử dụng một virtual xid, một thứ hoạt động giống `xid` nhưng không lấy từ transaction identifier counter. Nhờ vậy, mỗi transaction không tiêu thụ một số `xid` ngay từ đầu, làm giảm nhu cầu freeze. Khi transaction đã thực hiện một số công việc liên quan đến data manipulation và các thay đổi, virtual xid được chuyển thành real xid, tức là một `xid` lấy từ xid counter. Nói cách khác, workload “read-only” sẽ không tiêu thụ transaction identifier, còn mọi workload có ghi data thì sẽ tiêu thụ.

Nhờ công việc bổ sung này, PostgreSQL không lãng phí transaction identifier cho những transaction không thực sự cần định danh mạnh. Ví dụ, không cần lãng phí một `xid` cho một transaction block như sau:

```text
   forumdb=> BEGIN;
   BEGIN
   forumdb=> ROLLBACK;
   ROLLBACK
```

Vì transaction ngay trước đó hoàn toàn không làm gì, tại sao PostgreSQL phải đưa toàn bộ xid machinery vào? Không có lý do gì để dùng một `xid` sẽ không được gắn vào tuple nào trong database và do đó không can thiệp vào bất kỳ active snapshot nào.

Tuy nhiên, có một điều quan trọng cần lưu ý: việc sử dụng function `txid_current()` luôn materialize một `xid`, ngay cả khi transaction chưa có `xid`. Vì lý do đó, PostgreSQL cung cấp một introspection function khác có tên `txid_current_if_assigned()`, trả về `NULL` nếu transaction vẫn đang ở virtual xid space và vì vậy chưa thực hiện writable work nào. Điều quan trọng cần lưu ý là PostgreSQL sẽ không gán một real `xid` trừ khi transaction đã thao tác trên một số data; điều này có thể dễ dàng được chứng minh bằng workflow sau:

```text
      forumdb=> BEGIN;
      BEGIN
      forumdb=> SELECT txid_current_if_assigned();
       txid_current_if_assigned
      --------------------------


      (1 row)


      forumdb=> SELECT count(*) FROM tags;
       count
      -------
           7
      (1 row)


      forumdb=> SELECT txid_current_if_assigned();
       txid_current_if_assigned
      --------------------------


      (1 row)


      forumdb=> UPDATE tags SET tag = upper( tag );
      UPDATE 7
      forumdb=> SELECT txid_current_if_assigned();
       txid_current_if_assigned
      --------------------------
                             4837

   (1 row)


   forumdb=> SELECT txid_current();
     txid_current
   --------------
              4837
   (1 row)


   forumdb=> ROLLBACK;
   ROLLBACK
```

Ở đầu transaction, chưa có `xid` nào được gán, và thực tế `txid_current_if_assigned()` trả về `NULL`. Ngay cả sau một lần đọc data (tức là `SELECT`), `xid` vẫn chưa được gán. Tuy nhiên, ngay khi transaction thực hiện một số hoạt động ghi (ví dụ một `UPDATE`), `xid` được gán, và kết quả của cả `txid_current_if_assigned()` lẫn `txid_current()` đều giống nhau.

## Multi-version concurrency control

Điều gì xảy ra nếu hai transaction, dù là implicit hay explicit, cố thực hiện các thay đổi xung đột trên cùng một data? PostgreSQL phải bảo đảm data luôn nhất quán, và do đó phải có cách lock (tức là block và bảo vệ) data đang chịu các thay đổi xung đột. Lock là một cơ chế tốn kém, làm giới hạn concurrency của system: bạn có càng nhiều lock, các transaction của bạn càng phải chờ để acquire lock. Để giảm nhẹ vấn đề này, PostgreSQL triển khai MVCC, một kỹ thuật nổi tiếng được dùng trong các database cấp enterprise.

MVCC quy định rằng thay vì sửa đổi một tuple hiện có bên trong database, system phải replicate tuple đó, áp dụng các thay đổi rồi invalidate tuple ban đầu. Bạn có thể so sánh điều này với cơ chế copy-on-write được dùng trong các filesystem của hệ điều hành như ZFS.

Để hiểu rõ hơn điều này có nghĩa là gì, hãy giả sử table `categories` có ba tuple và chúng ta update một tuple để thay đổi description của nó.

Điều xảy ra là một tuple mới, được tạo ra từ tuple mà chúng ta sẽ áp dụng `UPDATE`, được insert vào table, còn tuple ban đầu bị invalidate:

![Hình 11.1: Cập nhật một tuple tạo ra một tuple mới và invalidate tuple cũ](../assets/part-041-figure-11-1-000.jpg)

*Hình 11.1: Cập nhật một tuple tạo ra một tuple mới và invalidate tuple cũ*

Tại sao PostgreSQL và MVCC lại thực hiện thêm công việc này thay vì in-place update tuple? Lý do là theo cách này, database có thể xử lý nhiều version của cùng một tuple, và mỗi version hợp lệ trong một time window cụ thể. Điều này có nghĩa là cần ít lock hơn để sửa đổi data, vì database có thể xử lý nhiều version của cùng data tại cùng một time, và các transaction khác nhau có thể nhìn thấy các value khác nhau.

Để MVCC hoạt động đúng, PostgreSQL phải xử lý concept snapshot: snapshot cho biết time window mà trong đó một transaction nhất định được phép nhìn thấy data. Về cơ bản, snapshot là range các transaction `xid` xác định boundary của data mà transaction hiện tại có thể truy cập: mọi row trong database được gắn nhãn bằng một `xid` nằm trong range sẽ có thể được transaction hiện tại nhìn thấy và sử dụng. Nói cách khác, mỗi transaction nhìn thấy một subset riêng của toàn bộ data hiện có trong database. MVCC machinery và các phép kiểm tra để quyết định một tuple có visible hay không phức tạp hơn nhiều so với mô tả trên, nhưng ý tưởng cốt lõi là như đã giải thích.

Special function `txid_current_snapshot()` trả về transaction identifier nhỏ nhất và lớn nhất xác định các time boundary của transaction hiện tại. Việc chứng minh concept này bằng hai parallel session trở nên khá dễ dàng.

Trong session đầu tiên, hãy chạy một explicit transaction, lấy identifier và snapshot để tham chiếu về sau, rồi thực hiện một operation:

```text
      -- session 1
   forumdb=> BEGIN;
   BEGIN
   forumdb=> SELECT txid_current(), txid_current_snapshot();
     txid_current | txid_current_snapshot
   --------------+------------------------
       4928 | 4928:4928:
   (1 row)


   forumdb=> UPDATE tags SET tag = lower( tag );
   UPDATE 5
```

Như bạn có thể thấy trong example trước, transaction là số 4928, và snapshot của nó được giới hạn ở chính nó, nghĩa là transaction sẽ nhìn thấy mọi thứ đã được consolidate trong database.

Bây giờ hãy tạm dừng session này một chút và mở một session khác kết nối tới cùng database – thực hiện một `INSERT` đơn lẻ được bọc trong một implicit transaction rồi lấy lại thông tin về `xid` của nó:

```text
   forumdb=> INSERT INTO tags( tag ) VALUES( 'KDE' ) RETURNING txid_current();
     txid_current
   --------------
       4929
   (1 row)
```

Single-shot transaction đã được gán `xid` 4929, dĩ nhiên là `xid` tiếp theo có thể dùng sau explicit transaction trước đó (system không chạy concurrent transaction nào khác để việc theo dõi cách đánh số được đơn giản hơn).

Quay lại session đầu tiên và kiểm tra lại thông tin về transaction snapshot:

```text
   -- session 1
   forumdb=> SELECT txid_current(), txid_current_snapshot();
     txid_current | txid_current_snapshot
   --------------+------------------------
       4928         | 4928:4930:
   (1 row)
```

Lần này, transaction đã mở rộng snapshot từ chính nó đến transaction 4930, transaction vẫn chưa được bắt đầu (`txid_current_snapshot()` báo upper bound của nó là non-inclusive). Nói cách khác, transaction hiện tại giờ nhìn thấy data đã được consolidate ngay cả từ một transaction bắt đầu sau nó, là 4929. Điều này còn rõ hơn nếu transaction query table:

```text
   -- session 1
   forumdb=> SELECT xmin, tag FROM tags;
         xmin      |   tag
   ------------+-------
      4928 | linux
      4928 | bsd
      4928 | java
      4928 | perl
      4928 | raku
      4929 | KDE
   (6 rows)
```

Như bạn có thể thấy, tất cả tuple trừ tuple cuối đã được tạo bởi transaction hiện tại, còn tuple cuối được tạo bởi `xid` 4929. Nhưng transaction trước đó chỉ là một phần của câu chuyện; trong khi transaction đầu tiên vẫn chưa hoàn tất, hãy inspect cùng table từ một parallel session khác:

```text
   forumdb=> SELECT xmin, tag FROM tags;
         xmin      |   tag
   ------------+-------
      4922 | linux
      4923 | BSD
      4924 | Java
      4925 | Perl
      4926 | Raku
      4929 | KDE
   (6 rows)
```

Tất cả tuple trừ tuple cuối có description khác nhau và đáng chú ý nhất là có giá trị `xmin` khác với giá trị mà transaction 4928 đang nhìn thấy. Điều đó có nghĩa gì? Nghĩa là trong khi table đã trải qua việc rewrite gần như toàn bộ mọi tuple (một `UPDATE` trên tất cả tuple trừ tuple cuối), các transaction concurrent khác vẫn có thể truy cập data trong table mà không bị một lock block. Đây chính là bản chất của MVCC: mỗi transaction nhận thấy một view khác nhau của storage, và view đó hợp lệ tùy theo time window (snapshot) gắn với transaction.

Sớm hay muộn, data trên storage cũng phải được consolidate, và vì vậy, khi transaction 4928 `COMMIT` công việc của mình, data trong table sẽ trở thành sự thật mà mọi transaction từ đó về sau nhìn thấy:

```text
   -- session 1
   forumdb=> COMMIT;
   COMMIT


   -- out from the transaction now
   -- we all see consolidated data
   forumdb=> SELECT xmin, tag FROM tags;
         xmin     |   tag
   ------------+-------
     4928 | linux
     4928 | bsd
     4928 | java
     4928 | perl
     4928 | raku
     4929 | KDE
   (6 rows)
```

MVCC không phải lúc nào cũng ngăn việc sử dụng lock: nếu hai hoặc nhiều transaction concurrent bắt đầu thao tác trên cùng một tập data, system phải áp dụng các thay đổi theo thứ tự và do đó phải force một lock trên mọi transaction concurrent để chỉ một transaction có thể tiếp tục. Điều này khá dễ chứng minh bằng hai parallel session tương tự example trước:

```text
   -- session 1
   forumdb=> BEGIN;
   BEGIN
   forumdb=> SELECT txid_current(), txid_current_snapshot();
     txid_current | txid_current_snapshot
   --------------+------------------------
       4930 | 4930:4930:
   (1 row)


   forumdb=> UPDATE tags SET tag = upper( tag );
   UPDATE 6
```
