```text
ROLLBACK
forumdb=> INSERT INTO tags( tag ) VALUES ( 'IntelliJIdea IDE' );
INSERT 0 1
forumdb=> COMMIT;
COMMIT


forumdb=> SELECT tag FROM tags WHERE tag like '%IDE';
         tag
------------------
   Eclipse IDE
   IntelliJIdea IDE
(2 rows)
```

Trong transaction trước đó, statement đầu tiên không thuộc về bất kỳ savepoint nào và do đó tuân theo vòng đời của chính explicit transaction. Sau khi savepoint `other_tags` được tạo, tất cả statement tiếp theo tuân theo vòng đời của chính savepoint; vì vậy, khi `ROLLBACK TO SAVEPOINT` được phát hành, các statement bên trong savepoint sẽ bị loại bỏ. Sau đó, các statement khác thuộc về explicit transaction và do đó tuân theo vòng đời của chính transaction. Kết quả cuối cùng là mọi thứ được thực thi bên ngoài savepoint đều được lưu trong table.

Sau khi đã định nghĩa một savepoint, bạn cũng có thể đổi ý và release nó, để các statement bên trong savepoint tuân theo cùng vòng đời với main transaction. Đây là một ví dụ:

```text
   forumdb=> BEGIN;
   BEGIN
   forumdb=> SAVEPOINT editors;
   SAVEPOINT
   forumdb=> INSERT INTO tags( tag ) VALUES ( 'Emacs Editor' );
   INSERT 0 1
   forumdb=> INSERT INTO tags( tag ) VALUES ( 'Vi Editor' );
   INSERT 0 1
   forumdb=> RELEASE SAVEPOINT editors;
   RELEASE
   forumdb=> INSERT INTO tags( tag ) VALUES ( 'Atom Editor' );
   INSERT 0 1
   forumdb=> COMMIT;
   COMMIT

   forumdb=> SELECT tag FROM tags WHERE tag LIKE '%Editor';
             tag
   --------------
     Emacs Editor
     Vi Editor
     Atom Editor
   (3 rows)
```

Khi `RELEASE SAVEPOINT` được phát hành, savepoint giống như đã biến mất, và do đó hai statement `INSERT` tuân theo vòng đời của main transaction. Nói cách khác, giống như savepoint chưa từng được định nghĩa.

Trong một transaction, bạn có thể có nhiều savepoint, nhưng một khi rollback một savepoint, bạn sẽ rollback tất cả savepoint theo sau nó:

```text
   forumdb=> BEGIN;
   BEGIN
   forumdb=> SAVEPOINT perl;
   SAVEPOINT
   forumdb=> INSERT INTO tags( tag ) VALUES ( 'Rakudo Compiler' );
   INSERT 0 1
   forumdb=> SAVEPOINT gcc;
   SAVEPOINT
   forumdb=> INSERT INTO tags( tag ) VALUES ( 'Gnu C Compiler' );
   INSERT 0 1
   forumdb=> ROLLBACK TO SAVEPOINT perl;
   ROLLBACK
   forumdb=> COMMIT;
   COMMIT


   forumdb=> SELECT tag FROM tags WHERE tag LIKE '%Compiler';
     tag
   -----
   (0 rows)
```

Như bạn có thể thấy, ngay cả khi một transaction đã phát hành `COMMIT`, mọi thứ được thực hiện sau savepoint `perl`, là savepoint mà transaction đã rollback về, cũng đã được rollback.

Nói cách khác, rollback về một savepoint có nghĩa là rollback mọi thứ được thực hiện sau khi savepoint đó được khai báo.

Transaction có thể dẫn đến một tình huống trong đó cluster không thể tiếp tục xử lý. Những tình huống này được gọi là deadlock và sẽ được mô tả trong phần tiếp theo.

## Deadlocks

Deadlock là một event xảy ra khi các transaction khác nhau phụ thuộc lẫn nhau theo cách vòng tròn. Ở một mức độ nào đó, deadlock là event bình thường trong một môi trường database concurrent và không phải là điều administrator cần lo lắng, trừ khi chúng xảy ra cực kỳ thường xuyên, nghĩa là có lỗi dependency trong application và transaction.

Khi deadlock xảy ra, không còn lựa chọn nào khác ngoài việc terminate các transaction đang bị lock. PostgreSQL có một deadlock detection engine rất mạnh thực hiện chính xác công việc này: tìm các transaction bị đình trệ và, trong trường hợp có deadlock, terminate chúng (tạo ra một `ROLLBACK`).

Để tạo ra một deadlock, hãy hình dung hai transaction concurrent áp dụng các thay đổi lên chính những tuple đó theo cách xung đột. Ví dụ, transaction thứ nhất có thể làm như sau:

```text
   -- session 1
   forumdb=> BEGIN;
   BEGIN
   forumdb=> SELECT txid_current();
      txid_current
   --------------
              4875
   (1 row)


   forumdb=> UPDATE tags SET tag = 'Perl 5'
             WHERE tag = 'perl';
   UPDATE 1
```

Trong lúc đó, transaction còn lại thực hiện như sau:

```text
   -- session 2
   forumdb=> BEGIN;
   BEGIN
   forumdb=> SELECT txid_current();

     txid_current
   --------------
              4876
   (1 row)


   forumdb=> UPDATE tags SET tag = 'Java and Groovy'
                WHERE tag = 'java';
   UPDATE 1
```

Cho đến lúc này, cả hai transaction đều đã update một tuple mà không xung đột với nhau. Bây giờ, hãy hình dung transaction thứ nhất cố sửa tuple mà transaction kia đã thay đổi; như chúng ta đã thấy trong các example trước, transaction sẽ tiếp tục bị lock và chờ acquire lock trên tuple:

```text
   -- session 1
   forumdb=> UPDATE tags SET tag = 'The Java Language'
                WHERE tag = 'java';
   -- locked
```

Mặt khác, nếu transaction thứ hai cố sửa một tuple đã được transaction thứ nhất chạm tới, nó sẽ bị lock và chờ acquire lock:

```text
   -- session 2
   forumdb=> UPDATE tags SET tag = 'Perl and Raku'
                WHERE tag = 'perl';
   ERROR:     deadlock detected
   DETAIL: Process 78918 waits for ShareLock on transaction 4875; blocked by
   process 80105.
   Process 80105 waits for ShareLock on transaction 4876; blocked by process
   78918.
   HINT:     See server log for query details.
   CONTEXT:     while updating tuple (0,1) in relation "tags"
```

Tuy nhiên, lần này PostgreSQL nhận ra rằng hai transaction không thể tự giải quyết vấn đề vì chúng đang chờ một circular dependency, và do đó quyết định kill transaction thứ hai để transaction thứ nhất có cơ hội hoàn tất. Như bạn có thể thấy từ error message, PostgreSQL biết transaction 4875 đang chờ một lock do transaction 4876 giữ và ngược lại; vì vậy, để tiếp tục, không có giải pháp nào khác ngoài việc kill một trong hai transaction.

Vì là event tự nhiên trong một transactional system concurrent, deadlock là điều bạn phải xử lý, và application của bạn phải sẵn sàng replay một transaction trong trường hợp chúng bị buộc phải `ROLLBACK` bởi deadlock detection.

Deadlock detection là một process phức tạp và tốn nhiều resource; vì vậy, PostgreSQL thực hiện nó theo lịch. Cụ thể, configuration parameter `deadlock_timeout` biểu thị tần suất PostgreSQL nên tìm kiếm dependency giữa các transaction đang bị đình trệ. Mặc định, giá trị này được đặt là 1 second và được biểu diễn bằng milliseconds:

```text
   forumdb=> SELECT name, setting, unit
                FROM pg_settings
                WHERE name like '%deadlock%';
          name          | setting | unit
   ------------------+---------+------
   deadlock_timeout | 1000           | ms
   (1 row)


   forumdb=> SHOW deadlock_timeout;
   deadlock_timeout
   ------------------
   1s
   (1 row)
```

Giảm giá trị này thường là một ý tưởng tồi: application và transaction của bạn sẽ fail sớm hơn (nếu ở trong deadlock condition), nhưng cluster sẽ bị buộc phải tiêu tốn thêm resource cho việc phân tích dependency.

Trong phần tiếp theo, bạn sẽ tìm hiểu cách PostgreSQL bảo đảm data được làm persistent trên storage, ngay cả khi cluster bị crash.

## PostgreSQL xử lý persistency và consistency như thế nào: WALs

Trong các phần trước, bạn đã thấy cách tương tác với transaction và, đáng chú ý nhất, cách PostgreSQL thực thi mọi statement bên trong một transaction, dù là explicit hay implicit.

Về bên trong, PostgreSQL thực hiện những công việc rất phức tạp để bảo đảm consolidated data trong storage phản ánh trạng thái của các transaction đã commit. Nói cách khác, data chỉ có thể được xem là consolidated nếu transaction tạo ra (hoặc sửa đổi) nó đã commit thành công. Nhưng điều này cũng có nghĩa là, một khi transaction đã commit thành công, data của nó là “safe” trên storage, bất kể điều gì xảy ra trong tương lai: nếu một transaction được báo là thành công, data của nó phải được làm persistent, ngay cả khi database hoặc toàn bộ system bị crash.

PostgreSQL quản lý transaction và data consolidation bằng WALs. Phần này giới thiệu cho bạn concept WALs và cách sử dụng chúng bên trong PostgreSQL.

## WALs

Trước khi đi vào chi tiết, cần giải thích ngắn gọn cách PostgreSQL xử lý data ở bên trong. Tuple được lưu trong mass storage, thường là disk, bên dưới thư mục `$PGDATA/base`, trong các file chỉ được đặt tên bằng số. Khi một transaction yêu cầu truy cập một tập tuple cụ thể, PostgreSQL load data được yêu cầu từ thư mục `$PGDATA/base` và đặt nó vào một hoặc nhiều shared buffer. Shared buffers là bản copy trong memory của data trên disk, và tất cả transaction đều truy cập data dùng chung này, vì chúng cung cấp performance cao hơn nhiều và không yêu cầu từng transaction phải seek data từ storage.

Figure tiếp theo cho thấy một vài data page được load vào memory location của shared buffers:

![Hình 11.2: Nạp các data page vào memory location của shared buffers](../assets/part-043-figure-11-2-000.jpg)

*Hình 11.2: Nạp các data page vào memory location của shared buffers*

Khi một transaction sửa đổi data, nó thực hiện việc đó bằng cách sửa đổi bản copy trong memory, nghĩa là sửa đổi vùng “shared buffers”.

Tại thời điểm này, bản copy của data trong memory không tương ứng với version được lưu trữ, và đây là nơi PostgreSQL phải bảo đảm consistency và persistency mà không làm mất performance.

Điều xảy ra là data được giữ trong memory nhưng được đánh dấu là dirty, nghĩa là đó là một bản copy chưa được đồng bộ với source gốc trên disk. Sau khi các thay đổi đối với dirty buffer đã được commit, PostgreSQL consolidate các thay đổi vào WALs và giữ dirty buffer trong memory, để phục vụ nó như bản copy mới nhất có sẵn cho các transaction và connection khác.

Sớm hay muộn, PostgreSQL sẽ đẩy dirty buffer vào storage, thay thế bản copy gốc bằng version đã sửa đổi, nhưng một transaction thường không biết và cũng không quan tâm việc này sẽ xảy ra khi nào.

Diagram sau giải thích workflow trước đó: buffer màu đỏ đã được một transaction sửa đổi và do đó không còn khớp với những gì trên disk. Tuy nhiên, khi transaction phát hành một `COMMIT`, các thay đổi được buộc ghi và flush vào WALs:

![Hình 11.3: Sau một `COMMIT`, các thay đổi được buộc ghi vào WALs](../assets/part-043-figure-11-3-000.jpg)

*Hình 11.3: Sau một `COMMIT`, các thay đổi được buộc ghi vào WALs*

Tại sao WAL space được xem là hiệu quả hơn việc ghi đè data block gốc trong thư mục `$PGDATA/base`? Mẹo nằm ở chỗ để tìm vị trí chính xác trên disk storage nơi block cần được ghi đè, PostgreSQL phải thực hiện thao tác được gọi là random-seek, một operation I/O tốn kém. Mặt khác, WAL được ghi tuần tự như một journal, và do đó không cần thực hiện random-seek. Việc ghi WAL ngăn chặn suy giảm performance I/O và cho phép PostgreSQL ghi đè data block trong tương lai, chẳng hạn khi cluster không bị quá tải và có I/O bandwidth khả dụng.

Mỗi khi một transaction thực hiện `COMMIT`, các action và data đã sửa đổi của nó được lưu vĩnh viễn trong một phần của WAL, cụ thể là một phần nhất định của WAL segment hiện tại (sẽ nói thêm về việc này sau). Vì vậy, PostgreSQL có thể tái tạo transaction và các effect của nó để thực hiện chính xác những thay đổi data tương tự.

Tuy nhiên, điều này vẫn chưa đủ để làm cho PostgreSQL đáng tin cậy: PostgreSQL nỗ lực rất nhiều để bảo đảm data thực sự chạm tới disk storage. Cụ thể, trong khi ghi WAL, PostgreSQL tự cô lập khỏi thế giới bên ngoài bằng cách disable các operating system signal, để nó không thể bị interrupt. Hơn nữa, PostgreSQL phát hành `fsync(2)`, một operating system call cụ thể buộc filesystem cache flush data xuống disk.

PostgreSQL làm tất cả những việc này để bảo đảm data thực sự chạm tới disk layer, nhưng phải hiểu rõ rằng nếu filesystem hoặc disk controller (tức hardware) nói dối, data có thể không thực sự nằm trên disk. Điều này quan trọng, nhưng PostgreSQL không thể làm gì về việc đó và phải tin vào feedback mà operating system (và do đó là hardware) báo lại.

Trong mọi trường hợp, `COMMIT` sẽ trả về success cho transaction gọi nó khi và chỉ khi PostgreSQL đã có thể ghi các thay đổi lên disk. Vì vậy, ở transaction level, nếu một `COMMIT` thành công (tức là không có error), data đã được ghi vào WAL và do đó có thể được xem là an toàn trên storage layer.

WAL được chia thành các chunk gọi là segment. Một segment là một file chứa chính xác 16 MB thay đổi về data. Dù có thể sửa đổi kích thước segment trong `initdb`, chúng tôi mạnh mẽ không khuyến khích việc này và sẽ giả định mọi segment có kích thước 16 MB.

Điều này có nghĩa là PostgreSQL ghi tuần tự, mỗi lần một file duy nhất (tức một WAL segment), và khi file này đạt kích thước 16 MB, nó được đóng lại và một file 16 MB mới được tạo. WAL segment được lưu trong thư mục `pg_wal` bên dưới `$PGDATA`. Mỗi segment có tên được tạo thành từ các chữ số hexadecimal, dài 24 ký tự.

Tám ký tự đầu tiên biểu thị cái gọi là timeline của cluster (một thứ liên quan đến physical backup và replication), tám chữ số tiếp theo biểu thị một sequence number tăng dần có tên là Log Sequence Number (LSN), và tám chữ số cuối cung cấp offset bên trong LSN. Đây là một ví dụ:

```text
   $ ls -1 $PGDATA/pg_wal
   0000000700000247000000A8
   0000000700000247000000A9
   0000000700000247000000AA
   0000000700000247000000AB
   0000000700000247000000AC
   0000000700000247000000AD
   ...
```

Trong danh sách `pg_wal` ở trên, bạn có thể thấy mọi WAL segment đều có cùng timeline, số 7, và LSN là 247. Vì vậy, mỗi file có một offset khác nhau, file đầu tiên là A8, file thứ hai là A9, v.v. Như bạn có thể hình dung, tên WAL segment không được tạo ra cho con người, nhưng PostgreSQL biết chính xác phải tìm kiếm thông tin ở đâu và trong file nào.

Sớm hay muộn, tùy thuộc vào resource memory và usage của cluster, data trong memory sẽ được ghi trở lại các vị trí gốc trên disk, nghĩa là WAL chỉ đóng vai trò storage an toàn tạm thời trên disk. Lý do không chỉ liên quan đến việc tăng performance như đã giải thích, mà còn để cho phép khôi phục data trong trường hợp crash.

## WALs như phương pháp cứu hộ trong trường hợp crash

Khi bạn dừng một cluster đang chạy một cách clean, chẳng hạn bằng `pg_ctl`, PostgreSQL bảo đảm mọi dirty data trong memory được flush vào storage theo đúng thứ tự, rồi tự halt.

Nhưng điều gì xảy ra nếu cluster bị dừng không clean, chẳng hạn do mất điện?

Event này được gọi là crash, và khi PostgreSQL khởi động lại, nó thực hiện cái gọi là crash recovery. Cụ thể, PostgreSQL hiểu rằng nó đã dừng theo cách không clean, và do đó data trên storage có thể không phải là version cuối cùng từng tồn tại trong memory khi cluster kết thúc hoạt động. Nhưng PostgreSQL biết rằng tất cả data đã commit ít nhất đều có mặt trong WAL, và do đó bắt đầu đọc WAL trong quá trình gọi là WAL replay, điều chỉnh data trong storage theo những gì có trong WAL. Cho đến khi crash recovery hoàn tất, cluster không thể được sử dụng và không chấp nhận connection; một khi crash recovery kết thúc, cluster biết rằng data trên storage đã trở nên coherent, và do đó hoạt động bình thường có thể bắt đầu lại.
