Rõ ràng có thể thu được cùng thông tin từ `pg_settings`, với một query dài hơn và cần chuyển giá trị chính xác sang dạng dễ đọc đối với con người (lưu ý memory value được biểu diễn dưới dạng các chunk 8kB):

```text
forumdb=> SELECT name, setting, unit FROM pg_settings WHERE name =
'shared_buffers';
      name         | setting | unit
----------------+---------+------
shared_buffers | 16384        | 8kB
(1 row)
```

Vì vậy, nếu chỉ cần xem nhanh một configuration parameter, `SHOW` là command phù hợp; còn nếu cần thông tin chính xác và đầy đủ hơn về giá trị chính xác, nơi parameter được đặt trong configuration file, v.v., bạn nên query catalog `pg_settings`.

## Tìm lỗi configuration

PostgreSQL cung cấp một catalog rất hữu ích có tên `pg_file_settings`, cho phép database administrator xem nhanh tất cả configuration parameter và file mà chúng được load từ đó, đồng thời cung cấp thông tin về các lỗi. Query sau đây trích xuất toàn bộ thông tin từ catalog, còn output đã được rút gọn cung cấp một số thông tin quan trọng:

```text
postgres=# SELECT name, setting, sourcefile, sourceline, applied, error
FROM pg_file_settings where name = 'log_destination';
-[ RECORD 1 ]--------------------------------------
name          | log_destination
setting       | stderr
sourcefile | /postgres/16/data/postgresql.conf
sourceline | 444
applied       | f
error         |
-[ RECORD 2 ]--------------------------------------
name          | log_destination
setting       | csvlog
sourcefile | /postgres/16/data/postgresql.conf
sourceline | 818
applied       | f
error         |
-[ RECORD 3 ]--------------------------------------
name          | log_destination
setting       | stderr
sourcefile | /postgres/16/data/postgresql.auto.conf
sourceline | 4
applied       | t
error         |
```

Như bạn có thể thấy trong installation mẫu ở trên, configuration parameter `log_destination` đã được load nhiều lần: chính xác là ba lần, từ các source file khác nhau. Parameter được apply là configuration setting từ file `/postgres/16/data/postgresql.auto.conf`, trên line 4, như được báo cáo bởi trạng thái của column `applied`. Trong trường hợp parameter chứa lỗi, column `error` cung cấp gợi ý về vấn đề.

Việc một parameter được định nghĩa nhiều lần trong cùng một file hoặc trong các file khác nhau không phải là lỗi, mà là một dạng ghi đè parameter đó. Special view `pg_file_settings` giúp tìm hiểu tại sao parameter được định nghĩa trong một file lại chưa được load và những định nghĩa nào đã bị các định nghĩa rải rác khác ghi đè.

Trong trường hợp không thể apply một parameter vì nó chứa lỗi, column `error` sẽ đưa ra gợi ý về vấn đề và column `applied` sẽ có giá trị false.

## Nesting configuration files

Bạn không bị buộc phải configure mọi parameter bên trong file `postgresql.conf`: bạn có thể định nghĩa các configuration file nhỏ và tập trung theo từng mục đích, rồi instruct PostgreSQL đọc và thêm nội dung của chúng vào configuration. Nhờ vậy, bạn có thể tạo một tập hợp các configuration file nhỏ hơn và sạch hơn cho những task cụ thể, giúp maintenance đơn giản hơn.

PostgreSQL cung cấp ba directive chính để include các configuration file khác:

- `include_file`: Include một file duy nhất trong configuration
- `include_dir`: Include tất cả file nằm trong directory được chỉ định
- `include_if_exists`: Chỉ include một file nếu file đó tồn tại

Directive cuối cùng rất tiện dụng vì nếu included file không tồn tại, PostgreSQL sẽ báo lỗi; còn với `include_if_exists`, cluster sẽ không cảnh báo bạn nếu file cần include chưa được tạo. Điều này hữu ích cho provisioning, chẳng hạn khi bạn có thể thiết lập một main configuration file include nhiều file và chỉ ship những file đó tới các system thực sự yêu cầu configuration như vậy.

Để có một ví dụ cụ thể, hãy xét một file tên `memory.conf` được đặt trong directory `PGDATA`, với nội dung như sau:

- `shared_buffers = 321 MB`
- `work_mem = 16 MB`

Sau đó thêm directive sau vào cuối file `postgresql.conf`:

```text
include_if_exists = 'memory.conf'
```

Theo cách này, sau khi cluster được restart, file `postgresql.conf` sẽ instruct cluster load một configuration file khác có tên `memory.conf`; file này lần lượt sẽ ghi đè một vài memory setting (hãy nhớ rằng definition cuối cùng của một configuration parameter là definition được chọn để apply). Có thể xem kết quả cuối cùng bằng cách query catalog `pg_file_settings`:

```text
postgres=# SELECT * FROM pg_file_settings WHERE name IN ('shared_buffers',
'work_mem' );
             sourcefile                      | sourceline | seqno |              name        |
setting | applied | error
-----------------------------------+------------+-------+----------------
+---------+---------+-------
/postgres/16/data/postgresql.conf |                    127 |       3 | shared_buffers |
128MB   | f       |
/postgres/16/data/memory.conf              |             1 |      15 | shared_buffers |
321MB   | t       |
/postgres/16/data/memory.conf              |             2 |      16 | work_mem            |
16MB    | t       |
(3 rows)
```

Như bạn có thể thấy, parameter `shared_buffers` đã bị ghi đè và được apply từ memory file vừa tạo, còn `work_mem`, vốn được comment out trong default installation, cũng đã được apply (mà không ghi đè bất kỳ definition nào khác) từ included file.

## Configuration contexts

Mỗi configuration parameter thuộc về một context, tức một group xác định khi nào thay đổi đối với parameter đó có thể được apply. Một số parameter có thể được thay đổi và có hiệu lực trong vòng đời của cluster. Tuy nhiên, một số khác thì không thể và yêu cầu cluster được restart; context của một configuration parameter giúp system administrator hiểu khi nào các thay đổi sẽ có hiệu lực.

Có thể trích xuất configuration context từ catalog `pg_settings`, như trong ví dụ sau:

```text
forumdb=> SELECT distinct context FROM pg_settings ORDER BY context;
          context
-------------------
    backend
    internal
    postmaster
    sighup
    superuser
    superuser-backend
    user
(7 rows)
```

Như bạn có thể thấy, các configuration context được cho phép là:

- `internal`: Configuration value này phụ thuộc vào PostgreSQL source code và được thiết lập tại compile time, vì vậy không thể thay đổi trừ khi bạn quyết định compile lại từ đầu. Chẳng hạn, kích thước của mỗi memory page được định nghĩa trong source code.
- `postmaster`: Process này chịu trách nhiệm nhận các thay đổi. Nói cách khác, toàn bộ cluster (và main process của nó, `postmaster`) phải được restart để thay đổi điều này.
- `sighup`: Với context này, cluster sẽ nhận biết các thay đổi khi được cung cấp hang-up signal, thường là một lần reload operating system service.
- `superuser-backend` và `backend`: Các thay đổi sẽ được apply cho cả client connection và administrator connection. Những thay đổi như vậy sẽ có thể nhận thấy từ connection tiếp theo của một trong hai loại.
- `user` và `superuser`: Các thay đổi này sẽ được apply ngay lập tức cho connection hiện tại, bất kể đó là unprivileged connection hay connection từ một superuser.

## Main configuration settings

PostgreSQL có rất nhiều configuration option, và việc mô tả tất cả chúng ở đây sẽ cần đến cả một cuốn sách. Hơn nữa, configuration phụ thuộc vào nhiều yếu tố khác nhau, bao gồm workload của cluster và connection concurrency. Nhiều parameter có thể dẫn đến behavior khác nhau cho các parameter khác. Vì vậy, không thể cung cấp một step-by-step guide đơn giản và hiệu quả cho configuration, nhưng có thể đưa ra một số suggestion để giúp bạn bắt đầu tuning cluster.

Trong các subsection sau, bạn sẽ tìm hiểu về những configuration parameter chính, tùy theo category chính mà chúng thuộc về. Hãy dành thời gian hiểu rõ từng setting thực hiện điều gì trước khi apply thay đổi, và nhớ rằng các configuration context có thể khiến bạn không thấy được kết quả ngay lập tức.

## WAL settings

WAL có vai trò nền tảng để cluster hoạt động đúng và có thể recover sau crash. Vì vậy, các setting liên quan đến WAL có ý nghĩa sống còn đối với vòng đời của cluster.

Các setting chính gồm:

- `fsync` yêu cầu cluster gọi operating system call `fsync(2)` mỗi khi một `COMMIT` được thực hiện; tức là mỗi khi có thứ gì đó phải được lưu trong WAL segment.
- `wal_level` cho biết lượng information mà cluster phải giữ trong WAL segment.
- `wal_sync_method` cho PostgreSQL biết cần dùng operating system call `fsync(2)` hiệu quả nào.
- `synchronous_commit` cho PostgreSQL biết mỗi `COMMIT` có phải được theo sau bởi một `fsync(2)` tức thời và synchronous hay không, hoặc việc flush có thể được trì hoãn theo khoảng thời gian được định nghĩa trong `wal_writer_delay` hay không.
- `wal_writer_delay` và `wal_writer_flush_after` xác định tần suất một process, được gọi là WAL writer, phải flush data xuống disk khi hoạt động ở asynchronous `COMMIT` mode. Sau mỗi khoảng thời gian tính bằng milliseconds tương ứng với `wal_writer_delay`, hoặc sau khi đã tích lũy số megabytes data tương ứng với `wal_writer_flush_after`, các asynchronous commit sẽ được flush xuống disk.
- `checkpoint_timeout`, `checkpoint_completion_target` và `max_wal_size` kiểm soát việc checkpoint, như đã thảo luận trong Chapter 11, Transactions, MVCC, WALs, and Checkpoints, khi chúng ta giải thích về transaction và WAL.

Các fsync setting phải luôn được đặt thành `on`, vì việc disable sẽ khiến cluster có nguy cơ mất data: filesystem sẽ không flush data xuống disk tại thời điểm `COMMIT`, do đó PostgreSQL không có guarantee rằng data đã thực sự được lưu trên disk và, trong trường hợp crash (ví dụ mất điện), data có thể bị mất. Có rất ít scenario mà việc đặt option này thành `off` có ý nghĩa, nhưng hãy nhớ rằng (nếu bạn thực sự tìm được một lý do như vậy) disable option này vẫn khiến cluster của bạn không thể tồn tại sau crash.

Setting `wal_level` cho biết lượng information PostgreSQL phải tích lũy trong WAL segment. Mục đích chính của WAL là giúp cluster có thể tồn tại sau crash, nhưng WAL cũng được dùng để propagate thay đổi sang các cluster khác trong replication scenario.

Setting `wal_level` có thể được đặt thành `minimal`, tức một cluster đơn lẻ với toàn bộ information cần thiết để tồn tại sau crash; hoặc `replica` (default), khiến WAL cũng hữu ích cho các physical replication scenario; và cuối cùng có thể chuyển thành `logical`, khiến WAL chứa information cho cả các logical replication scenario.

`wal_sync_method` cho phép administrator configure một operating system call cụ thể để sync dirty buffer. Tất cả POSIX operating system đều implement `fsync(2)`, nhưng một số hệ thống cung cấp các flavor đặc biệt hoạt động nhanh hơn hoặc tốt hơn tùy thuộc vào filesystem. Có thể chỉ định chính xác tên của system call cần dùng thông qua `wal_sync_method`. Thông thường, PostgreSQL được ship với configuration phù hợp cho operating system.

Nhưng làm thế nào bạn có thể phát hiện implementation `fsync(2)` tốt nhất (hoặc chỉ những implementation khả dụng) phù hợp với operating system của mình? Bạn có thể launch program `pg_test_fsync` trên machine để có một phỏng đoán tốt về các method khả dụng, cũng như method tốt nhất. Ví dụ, trên một machine FreeBSD, program cung cấp output sau:

```text
$ pg_test_fsync
5 seconds per test
O_DIRECT supported on this platform for open_datasync and open_sync.

Compare file sync methods using one 8kB write:
(in wal_sync_method preference order, except fdatasync is Linux's default)
          open_datasync                                                n/a
          fdatasync                                   6845.727 ops/sec           146 usecs/
op
          fsync                                       3685.769 ops/sec           271 usecs/
op
          fsync_writethrough                                           n/a
          open_sync                                   2521.228 ops/sec           397 usecs/
op
...
```

Bạn nên so sánh các option khả dụng và chọn option nhanh nhất. Vì vậy, trong ví dụ trước, `wal_sync_method = open_datasysnc` là lựa chọn tốt nhất.

`synchronous_commit` là một option multiple-choice cho biết cần write bao nhiêu WAL xuống disk trước khi trả về trạng thái “success” cho transaction phát hành `COMMIT`. Theo mặc định, setting này có giá trị `on`, cho biết từng bit phải chạm tới disk trước khi transaction được phép thành công.

Đặt parameter thành `off` có nghĩa transaction sẽ thành công ngay cả khi WAL chưa được flush xuống disk. Không giống setting `fsync`, việc chuyển `synchronous_commit` thành `off` là an toàn và không gây mất data, vì asynchronous commit được điều khiển bởi `wal_writer_delay`, nghĩa là transaction sẽ được consolidate nhưng ở thời điểm muộn hơn. Ngoài ra còn có các giá trị khác cho parameter này, tất cả đều hàm ý behavior `on`: `local`, `remote_apply` và `remote_write`. Các setting này chỉ có ý nghĩa trong replication scenario khi cluster này hoạt động như một primary và được một (hoặc nhiều) secondary cluster theo sau (được replicate). Trong scenario này, `local` có nghĩa transaction sẽ thành công ngay khi primary đã flush từng bit xuống disk (tức behavior `on` mặc định); ngược lại, `remote_write` sẽ chờ các standby xác nhận rằng chúng đã nhận cùng WAL information và sắp replicate nó, nghĩa là primary đã consolidate transaction và standby sẽ sớm làm điều tương tự. Cuối cùng, `remote_write` sẽ chờ transaction thành công cho đến khi cả primary và standby đã flush toàn bộ data xuống disk.

## Memory-related settings

PostgreSQL tận dụng RAM volatile của system để cache data đến từ permanent storage và quản lý data sẽ được lưu sau đó.

Các setting chính liên quan đến memory management gồm:

- `shared_buffers` là lượng memory PostgreSQL sẽ dùng để cache data trong memory.
- `work_mem` là lượng memory PostgreSQL sẽ cung cấp, on-demand, để thực hiện các activity cụ thể trên data.
- `hash_mem_multiplier` được dùng để xác định một threshold về lượng memory mà một connection có thể dùng cho các hash-based operation.
- `maintenance_work_mem` là lượng memory PostgreSQL dành riêng cho các internal operation.
- `wal_buffers` là cache được dùng cho WAL segment.

`shared_buffers` có lẽ là setting quan trọng nhất ở đây vì nó xác định tổng lượng memory PostgreSQL sẽ dùng. Memory này sẽ được dành riêng cho PostgreSQL và các process do nó spawn; các service khác đang chạy trên cùng machine sẽ không thể dùng memory đó. Thông thường, bạn nên bắt đầu với một giá trị nằm trong khoảng 25% đến 45% tổng RAM của system. Giá trị quá thấp sẽ khiến PostgreSQL load và flush data từ permanent storage và vào permanent storage, còn giá trị quá cao sẽ khiến PostgreSQL cạnh tranh với filesystem cache của operating system, dẫn đến vấn đề performance có thể xảy ra.

`work_mem` là lượng memory mà mỗi connection có thể dùng để thực hiện một hoạt động rearrange data cụ thể, chẳng hạn như việc được thực hiện trong một `SORT` hoặc một hash join. Khi xử lý các hash-based task, một connection được phép tiêu thụ memory bằng `work_mem * hash_mem_multiplier` trước khi process chuyển sang swap trên disk. Trong mọi trường hợp, khi process không còn cách nào dùng thêm memory, nó sẽ bắt đầu swap xuống disk, chẳng hạn chuyển một in-memory `SORT` thành một on-disk merge `SORT`.

`maintanance_work_mem` thiết lập lượng memory trên mỗi session dành cho các command đặc biệt intensive như `VACUUM` và `CREATE INDEX`. Vì chỉ một trong các command đó có thể active tại một thời điểm trong một connection, bạn có thể tăng giá trị tùy theo số administrative connection mà bạn dự kiến sẽ phục vụ.

`wal_buffers` có lẽ là setting dễ tune nhất liên quan đến memory: nó cho biết cần dùng bao nhiêu memory để cache WAL segment. Vì WAL segment thường được write thành các chunk 16 megabytes, đây chính xác là giá trị optimal cho setting như vậy.

## Process information settings

PostgreSQL là một multi-process system và spawn một process để phục vụ mỗi incoming connection. Có một vài setting có thể hỗ trợ monitoring, xét từ góc nhìn của operating system, đối với mỗi process liên quan đến PostgreSQL:

- `update_process_title` khiến mỗi process report việc nó đang làm; ví dụ query mà nó đang thực thi khi được các operating system tool như `ps(1)` và `top(1)` yêu cầu.
- `cluster_name` là một mnemonic name dùng để nhận diện cluster mà mỗi process thuộc về trong trường hợp có nhiều cluster đang chạy trên cùng machine.

Cần lưu ý rằng các setting này có thể khiến system hoạt động chậm hơn trên một số operating system nhất định, chẳng hạn FreeBSD.

Các log-related setting đã được giải thích chi tiết trong Chapter 14, Logging and Auditing, vì vậy sẽ không được thảo luận lại ở đây.

## Networking-related settings

Thông thường, PostgreSQL lắng nghe trên một TCP/IP address cho các incoming connection; address này được chỉ định bởi một nhóm network-related setting. Các setting chính cho việc này gồm:

- `listen_addresses` chỉ định các TCP/IP address cần lắng nghe.
- `port` chỉ định TCP/IP port mà `postmaster` sẽ chờ incoming connection.
- `max_connections`, `reserved_connections` và `superuser_reserved_connections` chỉ định số incoming connection được cho phép.
- `authentication_timeout` và `ssl` cho biết authentication timeout và encrypted mode.

`listen_addresses` có thể chứa nhiều address, được phân tách bằng dấu phẩy, trong trường hợp server là multi-homed. Nó thậm chí có thể được chỉ định bằng giá trị đặc biệt `*` để cho biết server phải listen trên mọi address khả dụng. `port` chỉ định số TCP/IP port, mặc định là 5432.

`max_connections` là giới hạn tối đa cho incoming connection: sẽ không cho phép thêm connection nào trên cluster nếu đạt tới threshold này. Một superuser connection được tính là `superuser_reserved_connection`, vì trong tình huống khẩn cấp, superuser vẫn phải có cách connect tới cluster. Cuối cùng, `reserved_connections` đếm số connection được thiết lập bởi user có role đặc biệt `pg_use_reserved_connection`, đồng thời cho biết một tập user đặc biệt (không phải superuser) có các reserved connection slot. Vì vậy, số connection còn trống mà một normal user có thể sử dụng là `max_connections – superuser_reserved_connection – reserved_connections`.

`authentication_timeout` là khoảng thời gian trước khi một lần thử authentication hết hạn, còn `ssl` cho phép server xử lý SSL handshake trên connection (SSL sẽ không được giải thích ở đây).

> Có rất nhiều parameter để fine-tune SSL và authentication phase không được đề cập trong cuốn sách này vì chúng cũng yêu cầu nền tảng chuyên sâu về các chủ đề đó.

## Archive and replication settings

Có nhiều archiving và replication setting liên quan đến cách cluster archive WAL và giao tiếp với các cluster khác với tư cách master hoặc slave. Tất cả setting sẽ được trình bày chi tiết trong Chapter 17, Physical Replication, và Chapter 18, Logical Replication; ở đây chúng được liệt kê sơ lược:

- `wal_level` (đã được thảo luận trong section trước) cho biết information trong WAL sẽ được sử dụng như thế nào. Nó có thể là `minimal` (đối với standalone system), `replica` (đối với replicated system), hoặc `logical` (đối với logical replication).
- `archive_mode`, `archive_command`, `archive_library` và `archive_timeout` quản lý archiving mode, tức lưu WAL tới các location khác để point-in-time recovery hoặc replication.
- `primary_conninfo` và `primary_slot_name` được dùng để xác định connection từ standby node tới primary node.
- `hot_standby`, khi được dùng trên một replicating system, cho phép thực hiện read-only query.
- `max_standby_archive_delay` và `max_standby_streaming_delay` xác định khoảng thời gian trước khi một conflicting query trên standby phải bị cancel do một action khác đã xảy ra trên primary.
- `recovery_min_apply_delay` tạo delay trên standby node để nó có thể theo primary với một timeshift.
- `max_replication_slots` và `max_wal_senders` được dùng để xác định số replication slot sẽ được chấp nhận và sử dụng, cũng như số process sẽ quản lý replication.
- `synchronous_standby_names` xác định node nào được xem là synchronous trong replication, và vì vậy primary phải nhận feedback liên tục trước khi apply các thay đổi.

Các setting này và những replication-related setting khác sẽ được thảo luận trong Chapter 17, Configuration and Monitoring, và Chapter 18, Replication.

## Vacuum and autovacuum-related settings

Có nhiều setting có thể được dùng để xác định và tune vacuum cũng như autovacuum setting. Những setting này đã được thảo luận trong Chapter 11, Transactions, MVCC, WALs, and Checkpoints.

## Optimizer settings

PostgreSQL optimizer được điều khiển bằng cost-based approach. Có thể tune các cost này, như đã thảo luận trong Chapter 13, Query Tuning, Indexes, and Performance Optimization.

## Statistics collector

PostgreSQL tận dụng statistics collector để thu thập các fact về những gì đã xảy ra trong cluster, như bạn sẽ tìm hiểu sau trong chapter này, ở section Monitoring the cluster.

Vì việc thu thập những con số đó có rất ít runtime impact, có thể loại bỏ hoàn toàn việc collection hoặc filter statistics collector để chỉ thu thập những fact mà bạn thực sự quan tâm. Các setting chính cho việc này gồm:

- `track_activities` cho phép các process khác monitor command hoặc query hiện tại đang được execute.
- `track_counts` thu thập thông tin đếm về table và việc sử dụng index.
