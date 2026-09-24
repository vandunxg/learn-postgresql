Quy trình này cho phép cluster phần nào tự phục hồi sau một sự kiện bên ngoài khiến vòng đời bình thường của nó bị dừng lại. Điều này cho thấy rõ mục tiêu chính của WALs không phải là tránh suy giảm hiệu năng mà là bảo đảm cluster có thể recovery sau một crash. Để làm được điều đó, data phải được ghi bền vững vào storage; tuy nhiên, nhờ cách WALs được ghi tuần tự, data được persist với ít chi phí I/O hơn.

## Checkpoints

Sớm hay muộn, cluster cũng phải làm cho mọi thay đổi đã được ghi vào WALs trở nên khả dụng trong các data file; tức là nó phải ghi các tuple theo cách phân tán I/O. Những lần ghi này xảy ra tại các thời điểm rất cụ thể, gọi là checkpoint. Checkpoint là một thời điểm mà tại đó database nỗ lực thêm để bảo đảm mọi thứ đã có trong WALs cũng được ghi vào đúng vị trí trong storage data.

Diagram sau giúp hiểu điều gì xảy ra trong một `CHECKPOINT`:

![Hình 11.4: Một ví dụ về `CHECKPOINT`](../assets/part-044-figure-11-4-000.jpg)

*Hình 11.4: Một ví dụ về `CHECKPOINT`*

Nhưng tại sao database phải thực hiện nỗ lực đồng bộ hóa này?

Nếu việc đồng bộ hóa không xảy ra, WALs sẽ là nguồn duy nhất chứa các thay đổi giữa trạng thái trong memory và trạng thái trên disk, do đó chúng sẽ tiếp tục tăng lên và tiêu tốn storage space. Hơn nữa, nếu database crash vì bất kỳ lý do nào, WAL replay sẽ phải kiểm tra một tập WAL rất dài.

Ngược lại, nhờ checkpoint, cluster biết rằng trong trường hợp crash, nó chỉ phải đồng bộ data giữa storage và WAL sau khi checkpoint cuối cùng đã được thực hiện thành công. Nói cách khác, cả storage space lẫn thời gian cần để replay WAL đều được giảm từ thời điểm crash về checkpoint cuối cùng.

Tuy nhiên, còn một lợi ích khác: vì sau một checkpoint, PostgreSQL biết rằng data trong WAL đã được đồng bộ với data trong storage, nó có thể loại bỏ các WAL đã được đồng bộ. Thực tế, ngay cả trong trường hợp crash, PostgreSQL hoàn toàn không cần bất kỳ phần WAL nào đứng trước checkpoint cuối cùng. Vì vậy, PostgreSQL thực hiện *WAL recycling*: sau một checkpoint, một WAL segment được tái sử dụng như một segment rỗng cho các thay đổi tiếp theo.

Nhờ cơ chế này, space cần để lưu WAL segment về cơ bản sẽ giữ nguyên trong suốt vòng đời của cluster, vì tại mỗi checkpoint, các segment sẽ được tái sử dụng. Đáng chú ý nhất là trong trường hợp crash, số WAL segment cần replay sẽ là tổng số segment được tạo ra kể từ checkpoint cuối cùng.

> PostgreSQL có thể cung cấp cho bạn một số thông tin về việc một query cụ thể sẽ tiêu thụ bao nhiêu WAL segment, tức là bao nhiêu data được đưa vào WALs do việc thực thi một query. Command đặc biệt `EXPLAIN` (được trình bày chi tiết trong Chapter 13, *Indexes and Performance Optimization*) có thể cung cấp thông tin WAL. Ngoài ra, bạn có thể query các catalog đặc biệt và cả log để lấy thông tin về checkpoint cũng như lượng WAL được tạo ra và recycle.

## Các parameter configuration của checkpoint

Database administrator có thể fine-tune checkpoint, nghĩa là họ có thể quyết định khi nào và với tần suất bao nhiêu một checkpoint có thể xảy ra. Vì checkpoint là các điểm hợp nhất, checkpoint xảy ra càng thường xuyên thì thời gian recovery khi có crash càng ngắn. Mặt khác, việc thực thi checkpoint liên tục sẽ cần tài nguyên I/O và có thể làm database system chậm lại.

Thực tế, khi đạt đến một checkpoint, database phải force mọi dirty buffer từ memory xuống disk, và điều này thường tạo ra một I/O spike; trong lúc spike đó, các hoạt động database đồng thời khác, chẳng hạn lấy data mới từ storage, sẽ bị ảnh hưởng vì bandwidth I/O tạm thời bị hoạt động checkpoint sử dụng hết.

Vì những lý do trên, việc tune checkpoint một cách cẩn thận là rất quan trọng; đặc biệt, việc tuning phải phản ánh workload của cluster.

Checkpoint có thể được tune bằng ba configuration parameter chính tương tác với nhau, được giải thích trong các subsection sau.

### `checkpoint_timeout` và `max_wal_size`

Tần suất checkpoint có thể được điều chỉnh bằng hai parameter trực giao: `max_wal_size` và `checkpoint_timeout`.

Parameter `max_wal_size` quy định directory `pg_wal` có thể chiếm bao nhiêu space. Vì tại mỗi checkpoint, WAL segment được recycle, directory `pg_wal` cuối cùng có xu hướng chiếm cùng một lượng space. Việc tuning parameter `max_wal_size` chỉ định sau bao nhiêu thay đổi data thì checkpoint phải hoàn tất, do đó parameter này là một *đặc tả về lượng*.

`checkpoint_timeout` biểu thị sau bao nhiêu thời gian thì checkpoint phải được force.

Hai parameter này trực giao, nghĩa là điều nào xảy ra trước sẽ kích hoạt việc thực thi checkpoint: database của bạn tạo ra lượng thay đổi data vượt quá parameter `max_wal_size`, hoặc thời gian `checkpoint_timeout` đã trôi qua.

Ví dụ, hãy xét một system với các setting mặc định:

```text
   forumdb=> SHOW checkpoint_timeout;
   checkpoint_timeout
   --------------------
   5min
   (1 row)


   forumdb=> SHOW max_wal_size ;
   max_wal_size
   --------------
   1GB
   (1 row)
```

```text
   -- or you can query the pg_settings
   forumdb=> SELECT name, setting, unit
               FROM pg_settings
               WHERE name IN ( 'checkpoint_timeout', 'max_wal_size' );
             name          | setting | unit
   --------------------+---------+------
     checkpoint_timeout | 300          | s
     max_wal_size          | 1024      | MB
   (2 rows)
```

Sau 300 giây (5 phút), một checkpoint sẽ được trigger, trừ khi trong khoảng thời gian đó đã tạo ra 1.024 MB WAL data. Mục tiêu của hai parameter này là bảo đảm không có quá nhiều thời gian hoặc quá nhiều data thay đổi giữa hai checkpoint liên tiếp, qua đó giảm khác biệt giữa trạng thái data trong memory và trạng thái được lưu an toàn trên disk.

Vì WAL segment được tạo ra bằng cách ghi transaction, setting `max_wal_size` tỷ lệ với lượng user data đã thay đổi trong database. Lượng data được tạo ra trong WALs không chính xác bằng lượng user data được tạo ra, vì WAL segment cũng lưu checksum và các thông tin khác hữu ích cho database trong trường hợp recovery hoặc replica, nhưng bạn có thể ước lượng rằng lượng WAL được tạo ra phản ánh lượng data đã thay đổi trong database.

Do đó, ý nghĩa của `max_wal_size` là: một khi database đã tạo ra lượng thay đổi data tương ứng, checkpoint sẽ xảy ra, và trạng thái trong memory được phản ánh rồi đồng bộ xuống disk. Mặt khác, nếu database của bạn không bận và vì thế không tạo đủ data để đạt `max_wal_size`, `checkpoint_timeout` sẽ được trigger; điều này bảo đảm rằng ngay cả workload thấp cũng sẽ được đồng bộ sau một khoảng thời gian cụ thể.

Trong configuration mặc định ở trên, checkpoint sẽ được phát hành mỗi 5 phút hoặc sau khi đã tạo ra 1 GB data mới (WAL).

Lưu ý rằng checkpoint chỉ xảy ra nếu trạng thái đã thay đổi kể từ checkpoint trước; trong trường hợp hiếm khi database chưa tạo ra data mới nào (tức là hoàn toàn không có load), checkpoint sẽ không được trigger ngay cả khi thời gian `checkpoint_timeout` đã trôi qua. Thực tế, nếu không có data nào thay đổi kể từ checkpoint trước thì không có gì cần đồng bộ, và vì vậy không có công việc nào để thực hiện bằng checkpoint.

### Throttling checkpoint

Không có yêu cầu phải hoàn tất checkpoint ngay lập tức: nếu system không đồng bộ toàn bộ data trong memory xuống disk và xảy ra failure, system sẽ replay tất cả WAL segment cho đến checkpoint đã hoàn tất trước đó. Dựa trên điều này, PostgreSQL cung cấp một configuration parameter hướng dẫn system checkpoint phải hoàn tất nhanh đến mức nào.

Để tránh I/O spike khi thực thi checkpoint, PostgreSQL sử dụng `checkpoint_completion_target`, parameter này chấp nhận các value từ 0 đến 1. Parameter này chỉ ra khoảng thời gian checkpoint có thể trì hoãn việc ghi dirty buffer. Cụ thể, thời gian được cung cấp để hoàn tất checkpoint được tính bằng `checkpoint_timeout x checkpoint_completion_target`.

Ví dụ, nếu `checkpoint_completion_target` được đặt thành 0.2 và `checkpoint_timemout` là 300 giây, system sẽ có 60 giây để ghi toàn bộ data. System sẽ hiệu chỉnh bandwidth I/O của storage cần thiết để hoàn tất việc ghi dirty buffer.

Bạn đặt `checkpoint_completion_target` càng gần 0 thì càng thấy các I/O spike vào thời điểm thực thi checkpoint, kéo theo mức sử dụng bandwidth I/O cao; ngược lại, đặt parameter gần 1 sẽ tránh I/O spike và thay vào đó tạo ra hoạt động I/O liên tục với mức tiêu thụ bandwidth thấp. Hình sau minh họa concept trên:

![Hình 11.5: Mức tiêu thụ bandwidth I/O](../assets/part-044-figure-11-5-000.jpg)

*Hình 11.5: Mức tiêu thụ bandwidth I/O*

Theo mặc định, `checkpoint_completion_target` được đặt thành 0.9, nghĩa là checkpoint sẽ cố gắng hoàn tất chậm nhất có thể để tránh I/O spike và tiêu thụ resource:

```text
   forumdb=> show checkpoint_completion_target;
   checkpoint_completion_target
   ------------------------------
   0.9
   (1 row)
```

### Phát hành checkpoint thủ công

Cluster administrator luôn có thể khởi động thủ công một tiến trình checkpoint: statement PostgreSQL `CHECKPOINT` khởi động tất cả hoạt động vốn thường được trigger tại `checkpoint_timeout` hoặc `max_wal_size`.

Vì checkpoint là một operation có tác động lớn như vậy, tại sao lại muốn thực hiện nó thủ công? Một lý do có thể là để bảo đảm toàn bộ data trên disk đã được đồng bộ, chẳng hạn trước khi bắt đầu streaming replication hoặc file-level backup.

Trong section sau, bạn sẽ tìm hiểu process `VACUUM`, kỹ thuật cho phép PostgreSQL reclaim space chưa sử dụng bằng cách loại bỏ các tuple không còn visible.

## VACUUM

Trong các section trước, bạn đã tìm hiểu cách PostgreSQL tận dụng MVCC để lưu các version khác nhau của cùng một data (tuple), mà các transaction khác nhau có thể perceive tùy thuộc vào snapshot đang active của chúng. Tuy nhiên, việc giữ nhiều version khác nhau của cùng các tuple cần thêm space so với version active cuối cùng, và space này sớm hay muộn cũng có thể làm đầy storage. Để ngăn điều đó và reclaim space trong storage, PostgreSQL cung cấp một tool nội bộ tên là `VACUUM`, với mục tiêu phân tích các version tuple đã lưu và loại bỏ những version không còn perceivable.

> **Ghi nhớ:** Một tuple không perceivable (visible) khi không còn transaction active nào có thể tham chiếu đến version đó, nghĩa là version tuple không còn nằm trong snapshot của chúng. Một tuple không perceivable thường được gọi là dead tuple, thể hiện rằng nó không còn cần thiết trong vòng đời của database.

`VACUUM` có thể là một operation sử dụng nhiều I/O, vì nó phải reclaim và giải phóng space trên disk, do đó có thể là một operation có tác động lớn. Vì lý do này, bạn không nên chạy `VACUUM` thủ công quá thường xuyên; PostgreSQL cũng cung cấp một background job tên là autovacuum, có thể chạy `VACUUM` thay bạn tùy theo activity hiện tại của database.

Các subsection sau sẽ trình bày cả `VACUUM` thủ công và tự động.

### VACUUM thủ công

`VACUUM` thủ công có thể được chạy trên một table, một subset column của table hoặc toàn bộ database; synopsis như sau:

```text
VACUUM [ FULL ] [ FREEZE ] [ VERBOSE ] [ ANALYZE ] [ table_and_columns [,
...] ]
```

Có ba phiên bản chính của `VACUUM`, thực hiện việc refactor data ngày càng mạnh hơn:

- Plain `VACUUM` (mặc định) thực hiện micro-space-reclaim, nghĩa là loại bỏ các version của dead tuple nhưng không de-fragment table; vì vậy, kết quả cuối cùng là không có space nào được reclaim.
- `VACUUM FULL` thực hiện rewrite toàn bộ table, loại bỏ dead tuple và xóa fragmentation, nhờ đó cũng reclaim disk space một cách mạnh mẽ.
- `VACUUM FREEZE` đánh dấu các tuple đã được consolidate là frozen, ngăn vấn đề xid wraparound.

`VACUUM` không thể được thực thi bên trong transaction, cũng không thể được thực thi trong function hoặc procedure. Các option bổ sung `VERBOSE` và `ANALYZE` lần lượt cung cấp verbose output và thực hiện cập nhật statistics của nội dung table (điều này hữu ích để tăng performance).

Để xem các effect của `VACUUM`, hãy xây dựng một example đơn giản. Trước hết, bảo đảm autovacuum được đặt thành off. Nếu chưa, hãy edit configuration file `$PGDATA/postgresql.conf`, đặt parameter thành off rồi restart cluster. Sau đó, inspect size của table tags:

```text
   forumdb=> SHOW autovacuum;
       autovacuum
   ------------
       off
   (1 row)
```

```text
   forumdb=> SELECT relname, reltuples, relpages, pg_size_pretty( pg_
   relation_size( 'tags' ) )
   FROM pg_class WHERE relname = 'tags' AND relkind = 'r';
     relname | reltuples | relpages | pg_size_pretty
   ---------+-----------+----------+----------------
     tags     |           6 |           1 | 8192 bytes
   (1 row)
```

Như bạn thấy, table chỉ có sáu tuple và chiếm một data page duy nhất trên disk, có size 8 KB. Bây giờ, hãy populate table bằng khoảng 1 triệu tuple ngẫu nhiên:

```text
   forumdb=> INSERT INTO tags( tag )
   SELECT 'FAKE-TAG-#' || x
   FROM generate_series( 1, 1000000 ) x;
   INSERT 0 1000000
```

Vì chúng ta đã dừng autovacuum, PostgreSQL không biết size thực của table; do đó, cần thực hiện `ANALYZE` thủ công để thông báo cho cluster về data mới trong table:

```text
   forumdb=> ANALYZE tags;
   ANALYZE
   forumdb=> SELECT relname, reltuples, relpages, pg_size_pretty( pg_
   relation_size( 'tags' ) )
   FROM pg_class WHERE relname = 'tags' AND relkind = 'r';
     relname |    reltuples     | relpages | pg_size_pretty
   ---------+-------------+----------+----------------
     tags     | 1.00001e+06 |          6370 | 50 MB
```

Bây giờ là lúc invalidate toàn bộ tuple chúng ta đã insert, chẳng hạn bằng cách overwrite chúng với một `UPDATE` (do MVCC, thao tác này sẽ duplicate các tuple):

```text
   forumdb=> UPDATE tags SET tag = lower( tag ) WHERE tag LIKE 'FAKE%';
   UPDATE 1000000
```

Table hiện vẫn có khoảng 1 triệu tuple hợp lệ, nhưng size gần như tăng gấp đôi vì mỗi tuple hiện tồn tại ở hai version, trong đó một version là dead:

```text
   forumdb=> ANALYZE tags;
   ANALYZE
   forumdb=> SELECT relname, reltuples, relpages, pg_size_pretty( pg_
   relation_size( 'tags' ) )
   FROM pg_class WHERE relname = 'tags' AND relkind = 'r';
     relname |    reltuples     | relpages | pg_size_pretty
   ---------+-------------+----------+----------------
      tags    | 1.00001e+06 |         12739 | 100 MB
   (1 row)
```

Đến đây chúng ta đã xây dựng được một thứ có thể dùng làm test lab cho `VACUUM`. Nếu thực thi plain `VACUUM`, mọi data page sẽ được giải phóng dead tuple nhưng các page sẽ không được tái cấu trúc, vì vậy số lượng data page vẫn giữ nguyên và size cuối cùng của table trên storage cũng giữ nguyên:

```text
   forumdb=> VACUUM VERBOSE tags;
   ...
   INFO: "tags": found 1000000 removable, 1000006 nonremovable row versions
   in 12739 out of 12739 pages


   VACUUM
   forumdb=> ANALYZE tags;
   ANALYZE


   forumdb=> SELECT relname, reltuples, relpages, pg_size_pretty( pg_
   relation_size( 'tags' ) )
   FROM pg_class WHERE relname = 'tags' AND relkind = 'r';
     relname |    reltuples     | relpages | pg_size_pretty
   ---------+-------------+----------+----------------
      tags    | 1.00001e+06 |         12739 | 100 MB
   (1 row)
```

`VACUUM` cho chúng ta biết rằng có thể remove an toàn 1 triệu tuple, trong khi 1 triệu tuple (cộng với 6 tuple ban đầu) không thể bị remove vì chúng đại diện cho version active cuối cùng. Tuy nhiên, sau lần thực thi này, size của table không thay đổi: mọi data page đã được de-fragment bên trong, nhưng không có storage space nào được giải phóng vì tổng số page không thay đổi.

Vậy mục tiêu của plain `VACUUM` là gì? Loại `VACUUM` này tạo ra free space mới trên từng page, nhờ đó table về cơ bản có thể chứa 1 triệu tuple mới mà không thay đổi size của chính nó. Chúng ta có thể chứng minh điều này bằng cách thực hiện lại việc invalidate tuple như đã làm:

```text
   forumdb=> UPDATE tags SET tag = upper( tag ) WHERE tag LIKE 'fake%';
   UPDATE 1000000
   forumdb=> ANALYZE tags;
```

```text
   ANALYZE
   forumdb=> SELECT relname, reltuples, relpages, pg_size_pretty( pg_
   relation_size( 'tags' ) )
   FROM pg_class WHERE relname = 'tags' AND relkind = 'r';
     relname | reltuples | relpages | pg_size_pretty
   ---------+-----------+----------+----------------
     tags      | 1.00001e+06 |         12739 | 100 MB
   (1 row)
```

Như bạn thấy, số lượng tuple, page và size của table không thay đổi. Về cơ bản, quá trình diễn ra như sau: ban đầu chúng ta tạo 1 triệu tuple mới, sau đó update tất cả chúng, khiến 1 triệu trở thành 2 triệu; tiếp theo, chúng ta dùng `VACUUM` trên table, giảm số lượng trở lại 1 triệu nhưng giữ lại free space đã được allocate, khiến table chiếm space cho 2 triệu tuple nhưng chỉ một nửa storage đó được lấp đầy. Sau đó, chúng ta tạo 1 triệu version tuple mới nhưng system không cần allocate thêm space vì đã có đủ free space, dù space đó nằm rải rác trên toàn bộ table.

Mặt khác, `VACUUM FULL` không chỉ giải phóng space bên trong table mà còn reclaim toàn bộ space đó, compact table về size nhỏ nhất. Nếu thực thi `VACUUM FULL` ngay lúc này, ít nhất 50 MB data space sẽ được reclaim vì 1 triệu tuple sẽ bị loại bỏ:

```text
   forumdb=> VACUUM FULL VERBOSE tags;
   INFO:     vacuuming "public.tags"
   INFO: "tags": found 1000000 removable, 1000006 nonremovable row versions
   in 12739 pages
   DETAIL:     0 dead row versions cannot be removed yet.
   CPU: user: 0.18 s, system: 0.61 s, elapsed: 1.03 s.
   VACUUM
   forumdb=> ANALYZE tags;
   ANALYZE
   forumdb=> SELECT relname, reltuples, relpages, pg_size_pretty( pg_
   relation_size( 'tags' ) )
   FROM pg_class WHERE relname = 'tags' AND relkind = 'r';
     relname | reltuples | relpages | pg_size_pretty
   ---------+-------------+----------+----------------
     tags      | 1.00001e+06 |          6370 | 50 MB
   (1 row)
```
