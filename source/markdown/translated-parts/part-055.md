Một ví dụ về cấu hình logging trong file `postgresql.conf` có thể như sau:

```text
   logging_collector = on
   log_destination       = 'stderr,csvlog,jsonlog'
   log_directory         = 'log'
   log_filename          = 'postgresql-%Y-%m-%d.log'
   log_rotation_age      = '1d'
   log_rotation_size = '50MB'
```

Với các setting trên, cluster sẽ tạo một log file mới cho mỗi ngày (hoặc mỗi 50 MB thông tin) trong log directory (tương đối so với `PGDATA`) bằng logging collector, và mọi log file sẽ có thông tin về năm, tháng và ngày nó được tạo. Lưu ý rằng, trong ví dụ này, system sẽ đồng thời tạo log ở các format text, JSON và CSV; PostgreSQL sẽ tự động đổi phần extension của log filename thành `.json` và `.csv` tương ứng cho hai format sau.

Với logging configuration ở trên (cũng được sử dụng trong Docker image của chapter), việc kiểm tra log directory sẽ cho output tương tự như sau:

```text
   $ ls -1 /postgres/16/data/log
   postgresql-2023-07-19.csv
   postgresql-2023-07-19.json
   postgresql-2023-07-19.log
   ...
```

File `.log` là file có format text thuần, còn hai file kia chứa các entry ở format CSV và JSON.

### Khi nào ghi log

Điều quan trọng là quyết định khi nào một event phải được ghi vào log. Có rất nhiều option để kiểm soát việc kích hoạt một log action, được chỉ định thông qua một threshold. Logging threshold có thể nhận một giá trị mnemonic cho biết giá trị tối thiểu mà từ đó log event sẽ được chèn vào log.

Các giá trị thường gặp nhất, theo thứ tự, là `info`, `notice`, `warning`, `error`, `log`, `fatal` và `panic`, trong đó `info` là giá trị thấp nhất còn `fatal` là giá trị cao nhất.

Ví dụ, nếu bạn quyết định `warning` là threshold tối thiểu muốn chấp nhận, mọi log event có threshold thấp hơn (chẳng hạn `info` và `notice`) sẽ không được chèn vào log.

Như bạn có thể thấy, threshold tăng dần khi tiến tới các giá trị error như `fatal` và `panic`; các giá trị này luôn được log tự động vì chúng biểu thị những vấn đề không thể phục hồi. Ngoài ra còn có các level thấp nhất mang tên `debug1` đến `debug5` để lấy thông tin development và chi tiết bên trong quá trình thực thi process (tức là chúng thường được sử dụng khi phát triển với PostgreSQL).

Do đó, cluster sẽ tạo ra các log event khác nhau tại những thời điểm khác nhau, tất cả đều có các priority level khác nhau; các event này lần lượt được chèn vào log tùy theo threshold bạn đã cấu hình.

Cụ thể, có hai parameter có thể dùng để tinh chỉnh logging threshold: `log_min_messages` và `client_min_messages`.

Parameter đầu tiên, `log_min_messages`, quyết định threshold của logging system, còn parameter sau quyết định threshold của mọi user connection mới. Chúng khác nhau như thế nào?

`log_min_messages` chỉ định những gì cluster phải chèn vào log mà không quan tâm đến incoming user connection hay setting của chúng. `client_min_messages` quyết định những log event nào client phải báo cáo cho user trong connection. Cả hai setting này đều có thể nhận một giá trị trong danh sách threshold ở trên.

Một use case điển hình trong development hoặc test environment có thể là:

```text
   log_min_messages         = 'info'
   client_min_messages = 'debug1'
```

Với configuration trên, cluster sẽ chỉ log các message `info` trong textual log, tức những message liên quan đến việc thực thi bình thường của process, còn incoming user connection sẽ trả về cho user các message chi tiết hơn, chẳng hạn message dành cho development.

Setting threshold không phải là cách duy nhất để quyết định thời điểm kích hoạt việc chèn log: còn có một cặp setting khác dùng để xử lý duration của statement và utility.

Nếu bạn quan tâm đến việc logging các statement (tức query) do client thực thi, bạn có các logging parameter sau để tinh chỉnh:

- `log_min_duration_statement` chứa một giá trị integer biểu thị số milli-second. Mọi statement mất nhiều thời gian hơn giá trị đã đặt sẽ được log. Vì vậy, đặt giá trị này thành `0` có nghĩa là mọi statement xảy ra trong system đều sẽ được ghi vào log.
- `log_min_duration_sample` và `log_statement_sample_rate` là các parameter hoạt động cùng nhau. `log_min_duration_sample` nhận một số milli-second và chỉ log một sample các statement chạy lâu hơn giá trị milli-second đó. Nói cách khác, nó hoạt động tương tự `log_min_duration_statement`, nhưng thay vì log mọi statement, nó chỉ log một phần trong số đó. Tỷ lệ statement được log do `log_statement_sample_rate` quyết định; parameter này nhận giá trị từ 0 đến 1.
- `log_transaction_sample_rate` là một giá trị từ 0 đến 1 cho biết có bao nhiêu transaction sẽ được log đầy đủ (tức mọi statement trong transaction sẽ xuất hiện trong log), bất kể duration của statement.

Ý tưởng đằng sau các sample parameter là giảm lượng logging activity (và kích thước log), nhưng vẫn cung cấp insight hữu ích về những gì đang xảy ra trong cluster.

Để hiểu rõ hơn các parameter trên, hãy xem configuration sau:

```text
      log_min_duration_statement = 500
      log_min_duration_sample = 100
      log_statement_sample_rate = 0.8
      log_transaction_sample_rate = 0.5
```

Configuration trên sẽ log mọi statement chạy lâu hơn 500 milli-second (`log_min_duration_statement`) và 80% số statement chạy lâu hơn 100 milli-second (`log_min_duration_sample` và `log_statement_sample_rate`). Cuối cùng, nó sẽ log một trong hai transaction (`log_transaction_sample_rate`).

Bạn có thể test điều này bằng workload đơn giản sau:

```text
      forumdb=> BEGIN;
      BEGIN
      forumdb=*> SELECT 'transaction 1';
         ?column?
      ---------------
       transaction 1
      (1 row)


      forumdb=*> ROLLBACK;
      ROLLBACK
      forumdb=> BEGIN;
   BEGIN
   forumdb=*> SELECT 'transaction 2';
       ?column?
   ---------------
    transaction 2
   (1 row)


   forumdb=*> ROLLBACK;
   ROLLBACK
   forumdb=> SELECT pg_sleep( 2 );
    pg_sleep
   ----------


   (1 row)
   forumdb=> BEGIN;
   BEGIN
   forumdb=*> SELECT pg_sleep( 0.120 );           --repeat 10 times
    pg_sleep
   ----------


   (1 row)
   forumdb=*> ROLLBACK;
   ROLLBACK
```

Trong log, bạn sẽ tìm thấy nội dung tương tự như sau:

```text
   LOG:      duration: 0.047 ms    statement: BEGIN;
   LOG:      duration: 0.253 ms    statement: SELECT 'transaction 2';
   LOG:      duration: 0.068 ms    statement: ROLLBACK;
   LOG:      duration: 2003.742 ms     statement: SELECT pg_sleep( 2 );
   LOG:      duration: 121.593 ms    statement: SELECT pg_sleep( 0.120 );
   LOG:      duration: 121.464 ms    statement: SELECT pg_sleep( 0.120 );
   LOG:      duration: 120.459 ms    statement: SELECT pg_sleep( 0.120 );
   LOG:      duration: 121.448 ms    statement: SELECT pg_sleep( 0.120 );
   LOG:      duration: 121.455 ms    statement: SELECT pg_sleep( 0.120 );
   LOG:      duration: 121.416 ms    statement: SELECT pg_sleep( 0.120 );
```

Theo parameter `log_transaction_sample`, chỉ một trong hai transaction được log. Cũng lưu ý rằng `pg_sleep( 2 )` đã được chèn vì nó mất hơn 500 milli-second (`log_min_duration_statement`), cùng với 6 trong 10 lần gọi `pg_sleep( 0.120 )` được chèn vì `log_transaction_sample_rate` được đặt là 0.8 (tức 80% số transaction đang chạy).

Bạn có thể nhận thấy `log_transaction_sample_rate` không phải là một giá trị chính xác: dù configuration yêu cầu PostgreSQL log 80% query, system đã log ít hơn (60%).

### Nội dung nào cần ghi log

Chất lượng của thông tin cần log được cấu hình bằng một tập parameter phong phú, thường là boolean, để bật hoặc tắt việc log một event cụ thể.

Một setting được sử dụng và bị lạm dụng rất nhiều là `log_statement`: nếu bật, nó sẽ log mọi statement được thực thi trên cluster từ mọi connection. Điều này có thể rất hữu ích vì cho phép bạn dựng lại chính xác database đã làm gì và bằng những statement nào, nhưng mặt khác, nó cũng có thể rất nguy hiểm. Logging mọi statement có thể làm cho data private hoặc sensitive xuất hiện trong log, từ đó có thể lọt đến những người không được authorization. Hơn nữa, logging toàn bộ statement có thể nhanh chóng làm đầy log storage, đặc biệt nếu cluster đang chịu heavy load và concurrency cao.

> Thông thường, cấu hình setting `log_min_duration_statement` để chỉ log các statement “chậm” hữu ích hơn nhiều so với log tất cả statement.

Có thể tinh chỉnh category của statement cần log thông qua `log_statement`: setting này có thể nhận giá trị `off`, `ddl`, `mod` hoặc `all`. Ý nghĩa của `off` và `all` khá dễ hiểu, nhưng `ddl` có nghĩa là mọi data definition language statement (ví dụ `CREATE TABLE`, `ALTER TABLE`, v.v.) được log, còn `mod` có nghĩa là mọi data manipulation statement (ví dụ `INSERT`, `UPDATE` và `DELETE`) được log. Mỗi log category là một superset của category trước đó, vì vậy `mod` cũng bao gồm `ddl`, còn `all` bao gồm các category trước đó và cho phép log cả các statement loại `SELECT`. Đáng chú ý là nếu một statement chứa syntax error, nó sẽ không được log thông qua `log_statement`, bất kể setting là gì.

Chất lượng thông tin trong log cũng được xác định bởi parameter `log_line_prefix`. `log_line_prefix` là một pattern string xác định nội dung được chèn vào đầu mỗi log line, do đó có thể dùng để mô tả chi tiết event được log. Pattern được tạo bằng một số placeholder theo cách tương tự `sprintf(3)`, còn việc ghi lại mọi option nằm ngoài phạm vi của cuốn sách.

Chỉ cần nói rằng các placeholder hữu ích và phổ biến nhất là:

- `%a` biểu thị application name (ví dụ `psql`).
- `%u` biểu thị username đang kết nối tới cluster (tên role).
- `%d` là database nơi event xảy ra.
- `%p` là process identifier (PID) của operating system.
- `%h` biểu thị remote host nơi connection tới cluster được thiết lập.
- `%l` là session line number, một auto-increment counter giúp chúng ta hiểu thứ tự của mọi statement được thực thi trong một interactive session.
- `%t` là timestamp tại thời điểm event xảy ra.

Ví dụ, configuration sau sẽ tạo một log line bắt đầu bằng timestamp của event, tiếp theo là process identifier của backend process, rồi counter của command trong session, sau đó là user, database và application được dùng để kết nối tới cluster từ remote host:

```text
   log_line_prefix = '%t [%p]: [%l] user=%u,db=%d,app=%a,client=%h '
```

Kết quả của configuration trên sẽ tương tự như log line sau:

```text
   [3] user=forum,db=forumdb,app=psql,client=[local]LOG:              duration: 3004.132
   ms statement: select pg_sleep( 3 );
```

Nhờ `log_line_prefix`, có thể chèn vào mỗi log entry thông tin về user và database mà event liên quan tới; điều này giúp bạn hiểu và phân tích tốt hơn những gì đã xảy ra trong cluster.

Ngoài ra còn có một số special event có thể kích hoạt việc chèn log; các event này được cấu hình bằng những parameter sau:

- `log_connections` và `log_disconnections`: Các boolean value này chỉ định liệu PostgreSQL có phải chèn một entry vào log mỗi khi user connection được mở hoặc đóng hay không.
- `log_checkpoints`: Boolean setting này yêu cầu PostgreSQL log thông tin về checkpoint (xem Chapter 11, Transactions, MVCC, WALs, and Checkpoints để biết thêm chi tiết).
- `log_temp_files`: Parameter này nhận một integer value chứa kích thước tính bằng kilobyte. Mỗi khi PostgreSQL tạo một temporary file lớn hơn kích thước đã chỉ định, một log entry sẽ được tạo. Vì vậy, đặt parameter này thành `0` có nghĩa là mỗi khi PostgreSQL sử dụng temporary file, một log entry sẽ được thêm vào.
- `log_lock_waits`: Boolean parameter này cho biết một log entry sẽ được tạo mỗi khi user session chờ quá lâu để acquire lock. Threshold là configuration parameter `deadlock_timeout`.

Sau khi đã tìm hiểu toàn bộ về logging, chúng ta sẽ chuyển sang trích xuất thông tin từ các log đã tạo bằng một tool đặc biệt có tên pgBadger.

## Trích xuất thông tin từ log – pgBadger

Nhờ tập thông tin phong phú có thể được đưa vào log, có thể tự động hóa việc phân tích và trích xuất thông tin từ log. Có một số tool phục vụ mục đích này, và một trong những tool phổ biến và đầy đủ nhất là pgBadger.

pgBadger là một application Perl 5 self-contained, đọc và trích xuất cẩn thận thông tin từ PostgreSQL log, rồi tạo một web dashboard tóm tắt toàn bộ thông tin tìm thấy trong log. Mục đích của application này là cung cấp cho bạn insight hữu ích hơn về log mà không cần tự tìm kiếm thủ công những thông tin cụ thể.

Việc sử dụng pgBadger không bắt buộc; cluster của bạn vẫn hoạt động bình thường khi không có nó và bạn vẫn có thể tìm thông tin cũng như vấn đề trong log. Tuy nhiên, sử dụng pgBadger cung cấp cho bạn các gợi ý hữu ích hơn về những gì server đã thực hiện.

Điều quan trọng cần lưu ý là sử dụng pgBadger, cũng như thực hiện bất kỳ việc phân tích log tự động hoặc thủ công nào, không cung cấp thông tin real-time mà chỉ cho thấy hoạt động của server trong quá khứ.

Trong các subsection sau, bạn sẽ học cách cài đặt và sử dụng pgBadger.

### Cài đặt pgBadger

pgBadger yêu cầu Perl 5 được cài đặt trên system nơi nó sẽ chạy, và đó là dependency duy nhất của nó. Bạn có thể chạy pgBadger trên cùng host với PostgreSQL cluster hoặc trên một remote system (như sẽ trình bày ở một subsection sau). Trong section này, chúng ta giả định pgBadger sẽ được cài đặt và thực thi trên chính machine nơi PostgreSQL cluster đang chạy.

Cách dễ nhất để cài đặt pgBadger là dùng package manager của operating system, chẳng hạn trên các system dựa trên GNU/Debian và Ubuntu:

```text
      $ sudo apt install pgbadger
```

Cũng có thể cài đặt pgBadger từ source bằng các bước sau:

```text
   $ wget https://github.com/darold/pgbadger/archive/v12.0.tar.gz
   $ tar xzvf v12.0.tar.gz
   $ cd pgbadger-12.0
   $ perl Makefile.PL
   $ make
   $ sudo make install
```

Sau khi cài đặt pgBadger, bạn có thể test xem nó hoạt động hay không bằng cách nhập:

```text
   $ pgbadger --version
   pgBadger version 12.0
```

Nếu program trả về version number, mọi thứ sẽ ổn và sẵn sàng để sử dụng.

### Cấu hình logging của PostgreSQL để sử dụng pgBadger

pgBadger đủ thông minh để hiểu PostgreSQL log trong nhiều trường hợp, nhưng có một số tình huống bạn cần chỉ định một vài configuration option để PostgreSQL tạo ra log dễ hiểu hơn.

Trước hết, pgBadger cần có quyền truy cập vào PostgreSQL log, nghĩa là bạn nên sử dụng `logging_collector` để tạo log. Nếu thay đổi `log_line_prefix`, bạn nên truyền cùng configuration setting đó cho pgBadger để nó có thể parse chính xác log prefix. Cuối cùng, bạn nên bật càng nhiều logging context càng tốt.

Sau đây là một ví dụ về các configuration parameter khiến PostgreSQL tạo log mà pgBadger có thể hiểu chính xác:

```text
   logging_collector = on
   log_destination       = 'stderr,csvlog,jsonlog'
   log_directory         = 'log'
   log_filename          = 'postgresql-%Y-%m-%d.log'
   log_rotation_age      = '1d'
   log_rotation_size = '50MB'

       log_min_duration_statement = 500
       log_min_duration_sample = 100
       log_statement_sample_rate = 0.8
       log_transaction_sample_rate = 0.5

       log_min_duration_statement = 0
```

> pgBadger đã được cài đặt sẵn trong Docker image của chapter này.

Sau khi server được cấu hình để nhận logging configuration mới, bạn có thể bắt đầu sử dụng pgBadger.

### Sử dụng pgBadger

Khi PostgreSQL bắt đầu tạo log, bạn có thể phân tích kết quả bằng pgBadger. Trước khi chạy pgBadger, đặc biệt trên test system, bạn nên tạo (hoặc chờ) một lượng traffic và statement (cũng như transaction), nếu không dashboard được tạo sẽ rỗng.

Trước khi bắt đầu sử dụng pgBadger, nên tạo một location để lưu các report và mọi thứ liên quan. Việc này không bắt buộc, nhưng đơn giản hóa việc maintenance và archiving report về sau khi bạn cần giữ chúng. Hãy tạo một directory và gán ownership của directory cho cùng Postgres user đang chạy cluster (một lần nữa, việc này không bắt buộc nhưng giúp workflow đơn giản hơn một chút):

```text
      $ sudo mkdir /data/html
      $ sudo chown postgres:www-data /data/html
```

Đã đến lúc khởi chạy pgBadger lần đầu:

```text
   $ pgbadger -o /data/html/first_report.html \
                   /postgres/16/data/log/postgresql
   -2023-07-19.log
   [========================>] Parsed 261891612 bytes of 261891612 (100.00%),
   queries: 1428472, events: 2
   7
   LOG: Ok, generating html report...
```

Argument đầu tiên, `-o`, chỉ định tên file nơi report sẽ được lưu. pgBadger tạo đúng một file cho mỗi lần chạy, vì vậy bạn cần đổi filename nếu muốn tạo report khác mà không ghi đè report hiện có.

Argument thứ hai là PostgreSQL log file cần phân tích; bạn cũng có thể chỉ định file JSON hoặc CSV và pgBadger sẽ parse chúng tương ứng.

Program chạy trong vài giây hoặc vài phút tùy thuộc vào kích thước log file, đồng thời báo cáo một số thông tin thống kê về những gì nó tìm thấy trong log file (trong ví dụ này là 1,4 triệu statement). Bạn có thể kiểm tra generated report file khá dễ dàng:

> Nếu bạn định phân tích các log file lớn hoặc nhiều log file, bạn có thể sử dụng parallel mode của pgBadger với option `-j`, theo sau là số parallel process cần spawn. Ví dụ, truyền `-j 4` có nghĩa là mọi log file sẽ được chia thành bốn phần, mỗi phần do một process phân tích. Nhờ parallelism, bạn có thể tận dụng tất cả core của machine và nhận kết quả nhanh hơn khi có lượng log lớn.

```text
   $ ls -1s /data/html/first_report.html
   1172 /data/html/first_report.html
```
