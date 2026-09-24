```text
n_tup_upd            | 200030
n_tup_hot_upd        | 106
n_live_tup           | 100000
n_dead_tup           | 50000
last_vacuum          |
last_autovacuum      | 2023-09-15 15:13:47.424223+00
last_analyze         |
last_autoanalyze | 2023-09-15 15:13:47.60569+00
```

Các column `last_vacuum`, `last_analyze`, `last_autovacuum` và `last_autoanalyze` đặc biệt quan trọng để xác định liệu việc vacuum và analyze thủ công hoặc tự động đã chạy trên table hay chưa; thông tin này có thể rất quan trọng để hiểu các daemon tự động có đang hoạt động đúng hay không. Column `n_live_tup` báo cáo các tuple hiện đang visible theo MVCC (xem Chapter 11, Transactions, MVCC, WALs, and Checkpoints), trong khi column `n_dead_tup` báo cáo số tuple không còn visible nhưng vẫn chiếm chỗ và sẽ được reclaim bởi vacuum thủ công hoặc tự động.

Các column còn lại phần lớn có thể tự giải thích; `seq_scan` và `idx_scan` lần lượt là số lần table được truy cập bằng sequential scan hoặc bằng một index trong số các index hiện có; `n_tup_ins`, `n_tup_upd` và `n_tup_del` cung cấp thông tin về số tuple được insert mới, cũng như số tuple lần lượt được update hoặc delete. Column `n_tup_upd_hot` báo cáo số tuple được update tại chỗ thay vì được tạo mới, nhờ một cơ chế có tên Heap Only Tuple (HOT).

Catalog đặc biệt `pg_stat_user_indexes` cung cấp thông tin chi tiết về việc sử dụng các index hiện có. Cụ thể, các field `idx_scan`, `idx_tup_read` và `idx_tup_fetch` cho biết số lần index được sử dụng, số tuple của index đã được đọc và số tuple của table đã được lấy nhờ index. Để biết thêm thông tin, hãy xem Chapter 13, Query Tuning, Indexes, and Performance Optimization.

Có các catalog đôi khác có tên chứa “all” hoặc “sys”, cho biết chúng tham chiếu đến tất cả table hiện có, bao gồm các table nội bộ của PostgreSQL, hoặc chỉ tham chiếu đến các table sau (system table). Vì vậy, `pg_stat_all_tables` tương tự `pg_stat_user_tables` nhưng cũng bao gồm thông tin về system table, được lưu trong `pg_stat_sys_tables`. Điều tương tự cũng áp dụng cho `pg_stat_all_indexes`; đây là union của `pg_stat_user_indexes` và `pg_stat_sys_indexes`.

## Thống kê bổ sung

PostgreSQL có một tập catalog liên quan đến statistics rất phong phú, và không phải tất cả đều có thể được mô tả ở đây do giới hạn về dung lượng.

Một số catalog quan trọng nhất cần được nhắc đến gồm:

- `pg_stat_replication`, `pg_stat_replication_slots`, `pg_stat_wal_receiver` và `pg_stat_subscription` thu thập thông tin về trạng thái replica của cluster.
- `pg_stat_bgwriter` lấy thông tin về input/output.
- `pg_stat_archiver` lấy thông tin về cách các WAL đang được archive.
- `pg_statio_user_tables`, `pg_statio_user_indexes` cùng các catalog liên quan `pg_statio_all_tables` và `pg_statio_all_indexes` cung cấp thông tin về input/output ở cấp table hoặc index, cho biết số hit và miss từ buffer cache cũng như số page mới được đọc từ storage.
- `pg_stat_database` và `pg_stat_database_conflicts` cung cấp thông tin về trạng thái của một database, bao gồm transaction đã thực thi, conflict, rollback, v.v.

Cũng có nhiều progress statistics chỉ ghi nhận các operation đang diễn ra và trạng thái progress của chúng. Những progress statistics mà bạn có nhiều khả năng muốn sử dụng nhất là:

- `pg_stat_progress_analyze` và `pg_stat_progress_vacuum` cung cấp thông tin lần lượt về mọi operation `ANALYZE` hoặc `VACUUM`.
- `pg_stat_progress_cluster` cung cấp thông tin về progress của mọi operation `CLUSTER` hoặc `VACUUM FULL`.
- `pg_stat_progress_copy` cung cấp thông tin về mọi command `COPY`, vì vậy cũng hữu ích cho các activity liên quan đến `pg_dump`.
- `pg_stat_progress_create_index` cho biết việc tạo index đang được thực hiện như thế nào.
- `pg_stat_progress_basebackup` cho biết thông tin về một base backup, một cách copy cluster đang chạy ở mức physical.

Bạn nên dành thời gian làm quen với tất cả statistics catalog để có thể tự tin monitor cluster của mình.

Trong section tiếp theo, bạn sẽ tìm hiểu về một extension rất tiện dụng, có thể giúp bạn quản lý cluster và kiểm soát các activity của cluster.

## Thống kê nâng cao với pg_stat_statements

Mặc dù PostgreSQL statistics collector rất phong phú và mature, việc monitor connection activity có thể hơi phức tạp vì catalog `pg_stat_activity` không cung cấp thông tin lịch sử. Ví dụ, như đã giải thích trước đó, sẽ chỉ có một tuple chứa statement được thực thi gần nhất, vì vậy sẽ không có history hay chi tiết mở rộng nào được cung cấp.

Extension `pg_stat_statements` giải quyết vấn đề này bằng cách cung cấp một view duy nhất cho bạn toàn bộ history của các statement đã thực thi, timing và những chi tiết nhỏ khác có thể rất hữu ích khi thực hiện introspection. Hơn nữa, `pg_stat_statements` cung cấp số lần cùng một statement đã được thực thi, tạo ra thông tin quan trọng mà các query có thể cần được chú ý để phục vụ mục đích optimization.

Một số monitoring tool yêu cầu `pg_stat_statements` được cài đặt để thu thập data.

Trong các subsection sau, bạn sẽ học cách cài đặt extension này và sử dụng nó.

### Cài đặt extension pg_stat_statements

Extension này được đóng gói cùng PostgreSQL, vì vậy việc duy nhất bạn cần làm là cấu hình database cluster để sử dụng nó. Vì `pg_stat_statements` yêu cầu một shared library, bạn cần cấu hình setting `shared_preload_libraries` trong configuration của mình (file `postgresql.conf`) và restart cluster.

Bước đầu tiên là đặt giá trị sau trong `postgresql.conf`:

```text
shared_preload_libraries = 'pg_stat_statements'
```

Hoặc sử dụng `ALTER SYSTEM` như sau:

```text
ALTER SYSTEM SET shared_preload_libraries to 'pg_stat_statements';
```

Vì `pg_shared_preload_libraries` là một parameter có context `postmaster`, bạn cần restart cluster để áp dụng các thay đổi.

`pg_stat_statements` thu thập thông tin về tất cả cluster của bạn, nhưng chỉ export thông tin đó trong database nơi bạn tạo extension; trong ví dụ của chúng ta, đó là database `forumdb`:

```text
$ psql -U postgres -c "CREATE EXTENSION pg_stat_statements;" forumdb
CREATE EXTENSION
```

Extension hiện đã sẵn sàng để sử dụng.

> Trong Docker image của chapter này, extension `pg_stat_statements` đã được cài đặt và load vào database `forumdb`.

### Sử dụng pg_stat_statements

Khi `pg_stat_statements` được enable, nó sẽ bắt đầu thu thập thông tin. Runtime overhead của extension thực sự rất nhỏ, vì vậy bạn cũng có thể giữ nó được enable trong production system.

Vì `pg_stat_statements` thu thập data từ toàn bộ cluster, việc join special view `pg_stat_statements` với các catalog khác, chẳng hạn `pg_database` và `pg_authid`, sẽ hữu ích để lần lượt thu thập thông tin về database và username nơi một statement đã được thực thi. Query sau đây cung cấp một ví dụ:

```text
forumdb=# SELECT auth.rolname,query, db.datname, calls, min_exec_time,
max_exec_time
 FROM pg_stat_statements
          JOIN pg_authid auth ON auth.oid = userid
          JOIN pg_database db ON db.oid = dbid
 ORDER BY calls DESC;
...
rolname            | postgres
query         | SELECT count(*) FROM forum.posts WHERE last_edited_on >=
CURRENT_DATE - $1
datname            | forumdb
calls              | 17
min_exec_time | 0.037292
max_exec_time | 0.04165
```

Ví dụ trước cho thấy query đã được thực thi 17 lần kể từ khi `pg_stat_statements` bắt đầu thu thập data, và cần từ 0.037 đến 0.042 milliseconds để chạy. Tùy thuộc vào frequency và timing của từng query, việc inspect và optimize query bằng một index có thể đáng làm.

Trong ví dụ trên, query được báo cáo dưới dạng normalized query: mọi parameter, kể cả literal, đã bị loại bỏ và thay thế bằng placemark `$1` (các parameter khác sẽ được đánh dấu là `$2`, `$3`, v.v.): `SELECT count(*) FROM forum.posts WHERE last_edited_on >= CURRENT_DATE - $1`.

Ý tưởng là theo dõi một nhóm query có cùng normalized text, để bạn có thể biết một nhóm như vậy đã được thực thi bao nhiêu lần, ngay cả khi chúng có các argument khác nhau.

Special view `pg_stat_statements` theo dõi các query được thực thi thường xuyên nhất cho đến giá trị của configuration parameter `pg_stat_statements.max`, mặc định là 5000. Khi đạt đến giới hạn, các query được thực thi ít nhất sẽ bị loại bỏ để nhường chỗ cho các query mới. Điều này bảo đảm không gian mà table `pg_stat_statements` chiếm dụng sẽ gần như không đổi, bất kể số statement đã được thực thi.

View `pg_stat_statements` cung cấp nhiều field không thể được thảo luận chi tiết ở đây, từ planning time đến buffer và I/O activity. Extension này rất hữu ích khi bạn muốn xử lý workload của cluster.

### Reset data được thu thập từ pg_stat_statements

Bất kỳ lúc nào, database administrator cũng có thể reset toàn bộ data đã được extension thu thập bằng cách gọi function `pg_stat_statements_reset()`. Function này sẽ xóa toàn bộ data đã được thu thập và cho phép extension thu thập data mới từ đầu. Điều này có thể hữu ích khi bạn muốn test configuration hoặc hardware mới mà không để data đã thu thập bị bias do statistics cũ:

```text
forumdb=# SELECT pg_stat_statements_reset();
```

Theo mặc định, data của `pg_stat_statements` được giữ lại qua các lần shutdown và restart database một cách bình thường.

### Tuning pg_stat_statements

Extension cho phép database administrator giới hạn lượng data được thu thập. Cụ thể, bạn có thể tune các parameter sau trong configuration file `postgresql.conf`:

- `pg_stat_statements.max` cho biết số query riêng lẻ tối đa cần thu thập.
- `pg_stat_statements.save` là một Boolean cho biết content của data đã thu thập có phải tồn tại sau một lần system reboot bình thường hay không. Theo mặc định, setting này là true.
- `pg_stat_statements.track` cho phép bạn chỉ định nesting level cần theo dõi. Với giá trị `top`, extension sẽ thu thập data về query được issue trực tiếp bên trong client và các nested statement được theo dõi. Việc này được kích hoạt bởi execution của các statement khác (ví dụ, trong function statement). Với giá trị `all`, extension sẽ trigger mọi statement và các descendant của chúng, còn với `none`, sẽ không có data nào được thu thập về user statement.
- `pg_stat_statements.track_utility` theo dõi mọi statement không phải `SELECT`, `INSERT`, `UPDATE` hoặc `DELETE` - nói cách khác là các statement “non-ordinary”. Theo mặc định, setting này là `on`.

Thông thường, bạn không cần tune các setting này vì `pg_stat_statements` đã được cấu hình sẵn để theo dõi những gì hầu hết use case cần.

## Tóm tắt

Trong chapter này, bạn đã học cách PostgreSQL quản lý configuration thông qua một file text chính là `postgresql.conf`, file này có thể được chia thành các file nhỏ hơn, bao gồm `postgresql.auto.conf` được load tự động và luôn được load ở cuối quá trình configuration. Mọi configuration option đều có thể được edit trong configuration file và được inspect bên trong database nhờ các system catalog chuyên dụng. Điều này cho phép database administrator không chỉ hiểu rõ configuration hiện đang chạy mà còn tìm kiếm các configuration error và setting được load không chính xác.

PostgreSQL cũng thu thập statistics, tức runtime data được tập hợp trong thời gian cluster hoạt động. Các statistics đó có thể giúp administrator hiểu điều gì đang xảy ra hoặc điều gì đã xảy ra trong thời gian gần đây trên cluster. Nhờ một tập catalog khác được trình bày trong chapter này, bạn đã học cách đào sâu vào chi tiết của toàn bộ thông tin PostgreSQL đã thu thập cho bạn. Khả năng theo dõi và phân tích những gì từng application, user và connection đang thực hiện tại một thời điểm cụ thể đối với cluster cung cấp cho database administrator một cách hữu hiệu để xử lý bottleneck và các vấn đề khác, qua đó giúp cải thiện trải nghiệm trên cluster.

Cuối cùng, bạn đã học về extension `pg_stat_statements`, nhờ đó có thể thu thập historical data về query execution và timing, để áp dụng optimization và phân tích chuyên sâu activity của cluster.

Giờ bạn đã hiểu cách configuration và monitor cluster, đã đến lúc học cách replicate nó. Chapter tiếp theo sẽ cho bạn thấy cách thực hiện physical replication bằng cách cấu hình cluster một cách phù hợp.

## Kiểm tra kiến thức

- **Configuration context là gì?**

  Configuration context xác định cluster sẽ tiếp nhận các thay đổi đối với configuration parameter như thế nào - ví dụ, chỉ tại thời điểm boot hoặc tại connection tiếp theo. Xem section Configuration contexts để biết thêm chi tiết.

- **Sự khác biệt giữa các catalog `pg_settings` và `pg_file_settings` là gì?**

  Catalog `pg_settings` hiển thị giá trị của mọi configuration parameter, cùng các giá trị được chấp nhận và hợp lệ; catalog `pg_file_settings` hiển thị nơi (tức trong file nào và tại dòng nào) một configuration parameter được tìm thấy và load. Xem section Inspecting all configuration parameters để biết thêm chi tiết.

- **Ngoài việc edit configuration file, làm thế nào bạn có thể thay đổi configuration của cluster thông qua SQL statement?**

  Bạn có thể issue command `ALTER STATEMENT` để thay đổi giá trị của một configuration setting. Các thay đổi sẽ được ghi vào file `postgresql.auto.conf`. Xem section Modifying the configuration from a live system để biết thêm chi tiết.

- **Làm thế nào để lấy thông tin về connection, transaction và query đang chạy?**

  Special catalog `pg_stat_activity` cung cấp thông tin về mọi backend process, query đang chạy (hoặc đã chạy gần nhất) và transaction state của process đó. Xem section Information about running queries and connections để biết thêm chi tiết.

- **Extension `pg_stat_statements` thực hiện việc gì?**

  Extension `pg_stat_statements` cung cấp historical view về các query được lặp lại thường xuyên nhất, cùng thông tin về thời gian chạy, số lần execution và các chi tiết khác. Xem section Advanced statistics with pg_stat_statements để biết thêm chi tiết.

## Tài liệu tham khảo

- Tài liệu chính thức về PostgreSQL cluster configuration: https://www.postgresql.org/docs/current/runtime-config.html
- PGConfig online configurator: https://www.pgconfig.org/
- Tài liệu chính thức về PostgreSQL statistics collector: https://www.postgresql.org/docs/current/monitoring-stats.html
- Tài liệu chính thức về PostgreSQL `pg_stat_statements`: https://www.postgresql.org/docs/current/pgstatstatements.html

## Tìm hiểu thêm trên Discord

Để tham gia cộng đồng Discord dành cho cuốn sách này - nơi bạn có thể chia sẻ feedback, đặt câu hỏi cho tác giả và tìm hiểu về các bản phát hành mới - hãy theo QR code bên dưới:

https://discord.gg/jYWCjF6Tku

![Mã QR Discord](../assets/part-064-qr-discord.png)

# 17. Physical Replication

Khi một database, sau khi trải qua các giai đoạn development và testing, đi vào production, vấn đề đầu tiên DBA phải giải quyết là quản lý replica. Replica phải được quản lý theo real time và tự động update. Replica cho phép chúng ta luôn có một bản sao data được update theo real time trên một machine khác. Machine này có thể nằm trong cùng data center với data của chúng ta hoặc ở một data center khác. Chapter này khác với mọi nội dung chúng ta đã xem trước đó ở chỗ chúng ta sẽ nói về physical replication. Trong PostgresSQL, bắt đầu từ version 9.x, physical replication được hỗ trợ native. Chúng ta sẽ nói về physical replication nghĩa là gì, và xem cách tạo replica server cũng như cách quản lý nó. Chúng ta cũng sẽ thấy có thể có replica synchronous hoặc asynchronous, có thể có nhiều replica của cùng một database, cũng như khả năng có các replica theo mô hình cascade.

Trong chapter này, chúng ta sẽ quay lại chủ đề WAL, điều đã được thảo luận trong Chapter 11, Transactions, MVCC, WAL, and Checkpoints. Để thực thi các command sẽ được trình bày trong chapter này, chúng ta cần cài đặt một PostgreSQL server trên hai machine, hoặc cài đặt hai instance PostgreSQL trên cùng một machine nhưng chạy trên các port khác nhau. Trong phần còn lại của chapter, giả định là bạn có hai PostgreSQL installation trên các machine khác nhau để mô phỏng tốt hơn tình huống của một production environment thực tế; bắt đầu từ chapter này, chúng ta sẽ học cách cài đặt và cấu hình một physical replication.
