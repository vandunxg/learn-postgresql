```text
           Workers Launched: 2
          Buffers: shared hit=487 read=7264
         -> Hash Join (cost=8.30..12803.38 rows=1 width=0) (actual
  time=44.493..134.889 rows=7 loops=3)
                 Inner Unique: true
                 Hash Cond: (p.author = u.pk)
                 Buffers: shared hit=487 read=7264
                 Worker 0:    actual time=132.750..132.751 rows=0 loops=1
                    Buffers: shared hit=238 read=3192
                 Worker 1:    actual time=0.667..134.246 rows=4 loops=1
                    Buffers: shared hit=162 read=2120
               -> Parallel Seq Scan on forum.posts p (cost=0.00..12792.33
  rows=1042 width=4) (actual time=0.132..133.575 rows=6667 loops=3)
                     Output: p.pk, p.title, p.content, p.author, p.category,
  p.reply_to, p.created_on, p.last_edited_on, p.editable, p.likes



           ;
          Finalize Aggregate (cost=114848.33..114848.34 rows=1 width=8)
  (actual time=5190.322..5190.323 rows=1 loops=1)
            -> Gather (cost=114848.12..114848.33 rows=2 width=8) (actual
  time=5189.678..5193.226 rows=3 loops=1)
                       Workers Planned: 2
                       Workers Launched: 2
                    -> Partial Aggregate (cost=113848.12..113848.13 rows=1
  width=8) (actual time=4861.705..4861.712 rows=1 loops=3)
                          -> Hash Join (cost=8.30..113848.09 rows=10
  width=0) (actual time=2477.949..4861.639 rows=27 loops=3)
  ...
```

Như bạn có thể thấy, output giờ đây bao gồm cùng thông tin mà `EXPLAIN ANALYZE` sẽ report.

## Tóm tắt

PostgreSQL có một query planner và optimizer dựa trên cost rất phức tạp, luôn cố gắng cung cấp access nhanh nhất tới underlying data.

Nhờ command `EXPLAIN`, database administrator có thể monitor query để theo dõi cost và thời gian thực thi, rồi quyết định cách cải thiện chúng để có kết quả nhanh hơn. Thông thường, tạo index là lựa chọn ít can thiệp nhất trong query tuning, và PostgreSQL có một index interface rất phong phú, expressive, cho phép tạo single-column, multi-column và partial index thuộc nhiều type và technology khác nhau. Khi index không đủ, query rewriting có thể là một giải pháp khả dĩ để thực hiện query tuning.

Cost mà planner sử dụng dựa trên statistical data cần được giữ cho up to date nhiều nhất có thể. Dù daemon auto-analyze hướng tới việc này, DBA luôn có thể dựa vào command `ANALYZE` thủ công để cập nhật statistics.

Hiểu một query plan, biết những node nào tham gia và chúng tác động thế nào đến query execution, hiểu khi nào statistics đã out of date, cũng như có khả năng thử nghiệm các query access method khác nhau là những công việc phức tạp mà mọi DBA đều nên học.

Chúng ta cũng đã tìm hiểu extension auto-explain, có thể dùng để tự động hóa việc thu thập thông tin về các plan do optimizer chọn, nhờ đó DBA dễ dàng kiểm tra query nào đang chạy kém.

Điều quan trọng cần nhấn mạnh là performance tuning là một trong những công việc phức tạp nhất trong database administration và không có silver bullet hay giải pháp one-size-fits-all, vì vậy cần có kinh nghiệm và rất nhiều thực hành. Trong chapter tiếp theo, chúng ta sẽ bắt đầu tích lũy kinh nghiệm đó bằng cách thử thực hiện logging và auditing.

## Kiểm tra kiến thức

- **Làm thế nào để inspect plan của một query?**

  Command đặc biệt `EXPLAIN` cho phép bạn inspect cách PostgreSQL sẽ thực thi một query nhất định, bằng cách hiển thị một “node” cho mỗi execution step. Xem phần *The EXPLAIN statement* để biết thêm chi tiết.

- **Sự khác biệt giữa `EXPLAIN` và `EXPLAIN EXPLAIN’` là gì?**

  Command `EXPLAIN` sẽ không thực thi query mà chỉ tính access plan; ngược lại, command `EXPLAIN ANALYZE` sẽ thực thi query và in query plan vào output. Xem phần *EXPLAIN ANALYZE* để biết thêm chi tiết.

- **PostgreSQL giữ statistics up to date bằng cách nào?**

  Statistics được cập nhật mỗi khi command `ANALYZE` thủ công được thực thi hoặc daemon auto-vacuum (auto-analyze) chạy trên một table. Xem phần *ANALYZE và cách cập nhật statistics* để biết thêm chi tiết.

- **PostgreSQL quyết định sử dụng một access method cụ thể (ví dụ index) bằng cách nào?**

  Optimizer quyết định path tới data dựa trên cost của từng access method: method có cost thấp nhất sẽ thắng và được dùng để access underlying data. Xem phần *Optimizer* để biết thêm chi tiết.

- **Extension auto_explain là gì?**

  Extension auto_explain cho phép system tự động output query execution plan vào log bất cứ khi nào query đạt một threshold đã định nghĩa (ví dụ, execution time vượt quá một giới hạn được đặt trước). Nhờ đó, DBA có thể tự động lấy thông tin về các query có vấn đề. Xem phần *Auto-explain* để biết thêm chi tiết.

## Tài liệu tham khảo

- Tài liệu chính thức của PostgreSQL về `CREATE INDEX`: https://www.postgresql.org/docs/current/sql-createindex.html
- Tài liệu chính thức của PostgreSQL về `pg_stats`: https://www.postgresql.org/docs/current/view-pg-stats.html
- Tài liệu chính thức của PostgreSQL về `EXPLAIN`: https://www.postgresql.org/docs/current/using-explain.html
- Tài liệu chính thức của PostgreSQL về `ANALYZE`: https://www.postgresql.org/docs/current/sql-analyze.html
- Tài liệu chính thức về Auto-explain: https://www.postgresql.org/docs/current/auto-explain.html

## Tìm hiểu thêm trên Discord

Để tham gia cộng đồng Discord của cuốn sách này – nơi bạn có thể chia sẻ feedback, đặt câu hỏi cho tác giả và tìm hiểu về các bản phát hành mới – hãy theo dõi QR code bên dưới:

https://discord.gg/jYWCjF6Tku

# 14. Logging và Auditing

PostgreSQL cung cấp một logging infrastructure rất phong phú. Có khả năng kiểm tra log là một kỹ năng then chốt đối với mọi database administrator – log cung cấp gợi ý và thông tin về những gì cluster đã làm, đang làm và những gì đã xảy ra trong quá khứ. Chapter này sẽ giải thích các khái niệm cơ bản về PostgreSQL log configuration, cung cấp cho bạn lời giải thích về cách configure logging machinery để lấy thông tin cần thiết về cluster activity. Log có thể được phân tích thủ công, nhưng database administrator thường cũng tận dụng các tool tự động để có được insight rộng hơn về cluster activity. Chủ đề auditing có liên quan đến logging, đây là khả năng theo dõi ai đã làm gì trên data nào. Auditing thường được áp dụng do luật của chính phủ yêu cầu, thay vì do nhu cầu của database administrator. Tuy nhiên, một auditing system tốt cũng có thể giúp administrator xác định điều gì đã xảy ra trong database.

Trong chapter này, bạn sẽ tìm hiểu các chủ đề sau:

- Giới thiệu về logging
- Trích xuất thông tin từ log bằng pgBadger
- Triển khai auditing

## Yêu cầu kỹ thuật

Bạn cần biết những nội dung sau:

- Cách quản lý PostgreSQL configuration
- Cách start, restart và monitor PostgreSQL, cũng như tương tác với các file `PGDATA`

Các ví dụ trong chapter có thể chạy trên Docker image `chapter_14`, có thể tìm thấy trong GitHub repository của cuốn sách: https://github.com/PacktPublishing/Learn-PostgreSQL-Second-Edition. Để biết cách install và sử dụng các Docker image có sẵn cho cuốn sách này, hãy tham khảo phần hướng dẫn trong Chapter 1, *Introduction to PostgreSQL*.

## Giới thiệu về logging

Giống như nhiều service và database khác, PostgreSQL cung cấp logging infrastructure của riêng mình để administrator luôn có thể inspect daemon process đang làm gì và trạng thái hiện tại của database system. Dù log không thiết yếu đối với data và các hoạt động database, chúng đại diện cho thông tin rất quan trọng về những gì đã hoặc đang xảy ra trong toàn bộ system, đồng thời cung cấp một manh mối quan trọng nhờ đó administrator có thể hành động.

PostgreSQL có log infrastructure rất linh hoạt và có thể configure, cho phép thực hiện nhiều kiểu logging configuration, rotation, archiving và post-analysis khác nhau.

Log được lưu dưới dạng text, nhờ vậy có thể dễ dàng phân tích bằng các log analysis tool phổ biến, bao gồm các operating system utility như `grep(1)`, `sed(1)` và text editor.

> **Lưu ý:** Thuật ngữ “log” trong chapter này chỉ system textual log, không phải Write-Ahead Logs (WALs), vốn lại rất quan trọng trong life cycle của database (xem Chapter 11, *Transactions, MVCC, WALs, and Checkpoints*).

Trong một installation mặc định, log nằm trong một sub-folder cụ thể của directory `PGDATA`, nhưng như bạn sẽ thấy trong các subsection sau, bạn được tự do chuyển log tới gần như bất kỳ nơi nào bạn muốn trong storage của operating system.

Mọi event xảy ra trong database đều được log trên một dòng text riêng trong log, đây là một khía cạnh quan trọng và hữu ích khi bạn muốn phân tích log bằng các line-oriented tool như những Unix command phổ biến (ví dụ `grep(1)`). Dĩ nhiên, ghi một lượng thông tin khổng lồ vào log cũng có nhược điểm; việc này cần system resource và có thể lấp đầy storage nơi log được đặt. Vì lý do đó, điều quan trọng là quản lý logging infrastructure phù hợp với mục đích của cluster, tức chỉ log lượng thông tin tối thiểu có thể dùng cho post-analysis.

> **Lưu ý:** Log có thể nhanh chóng làm đầy disk storage nếu bạn không configure chúng phù hợp, vì vậy bạn nên bảo đảm cluster không tạo ra nhiều log hơn khả năng system có thể xử lý.

Theo triết lý Unix phổ biến, PostgreSQL cho phép gửi log tới một component bên ngoài có tên syslog. Ý tưởng là trong infrastructure của riêng bạn có thể có một component hoặc một machine chịu trách nhiệm thu thập log từ mọi service hiện có, bao gồm database, web server, application server, v.v. Vì vậy, bạn có thể redirect PostgreSQL log tới cùng syslog facility chung và thu thập cluster log tại chính nơi bạn đã thu thập log của các service khác. Tuy nhiên, đây không phải lúc nào cũng là lựa chọn tốt, đó là lý do PostgreSQL cung cấp component riêng có tên logging collector để lưu log.

Thực tế, dưới tải nặng, centralized collector của syslog có thể bắt đầu loại bỏ (và do đó làm mất) các log entry, trong khi PostgreSQL logging collector được thiết kế rõ ràng để không làm mất một mẩu thông tin log nào. Vì vậy, logging collector đi kèm PostgreSQL thường là cách được ưu tiên để theo dõi log, nhờ đó bạn có thể chắc chắn rằng khi bắt đầu phân tích log, bạn có toàn bộ thông tin cluster đã tạo ra và không thiếu gì.

PostgreSQL logging được configure thông qua các tunable nằm trong main cluster configuration, cụ thể là file `postgresql.conf`. Trong các subsection sau, bạn sẽ được giới thiệu về PostgreSQL logging configuration và thấy cách tune log của riêng mình cho phù hợp với nhu cầu.

## Ghi log ở đâu

Bước đầu tiên khi configure logging system là quyết định nơi và cách lưu textual log. Parameter chính điều khiển logging system là `log_destination`, có thể nhận một hoặc nhiều giá trị sau:

- `stderr` nghĩa là cluster log sẽ được gửi tới standard error của postmaster process, thường có nghĩa chúng sẽ xuất hiện trên console nơi cluster được start.
- `syslog` nghĩa là log sẽ được gửi tới một syslog component bên ngoài.
- `csvlog` nghĩa là log sẽ được tạo dưới dạng comma-separated value, hữu ích cho việc tự động phân tích log (sẽ nói thêm về việc này sau).
- `jsonlog` nghĩa là log sẽ được tạo dưới dạng JSON tuple, một format khác rất hữu ích cho việc tự động phân tích log (sẽ nói thêm về việc này sau).
- `eventlog` là một component đặc biệt chỉ có trên platform Microsoft Windows, dùng để thu thập log của rất nhiều service.

Có thể thiết lập logging destination bằng nhiều giá trị, nhờ đó sẽ tạo ra các destination và type log khác nhau.

Một setting quan trọng khác của logging infrastructure là `log_collector`, một giá trị boolean kích hoạt một process (có tên logging collector) để thu thập mọi log được gửi tới standard error và lưu chúng ở nơi bạn muốn. Nói ngắn gọn, đặt `log_destination = stderr` sẽ buộc PostgreSQL gửi mọi log message tới standard error, tức console nơi service được launch. Thông thường không có console được gắn vào vì daemon được launch ở background, hơn nữa không nhiều người muốn giữ một console mở chỉ để xem log message cuộn trên màn hình. Vì lý do đó, `logging_collector = on` enable PostgreSQL logging capture process, process này đọc mọi message được tạo trên standard error và gửi chúng tới destination phù hợp. Thông thường, destination sẽ là text file, file Comma-Separated Values (CSV), hoặc một thứ khác. Vì vậy, `log_destination` quyết định nơi PostgreSQL emit log message, còn `logging_collector` kích hoạt một process chuyên dụng để capture các log đã emit đó và gửi chúng đi nơi khác. Điều quan trọng cần lưu ý là một số logging destination cũng yêu cầu logging collector phải được bật: `cvslog` và `jsonlog` yêu cầu `logging_collector` được enable.

Tóm lại, hai parameter nêu trên có phần phụ thuộc lẫn nhau: bạn cần chọn nơi gửi các log mà PostgreSQL luôn tạo ra (`log_destination`), và trong trường hợp bạn chỉ gửi chúng (hoặc gửi thêm) tới standard error hoặc một custom format (như `csvlog`), bạn cần bật một process chuyên dụng (giá trị `logging_collector`) để bắt mọi log entry và lưu chúng trên disk. Điều này có nghĩa logging configuration của bạn sẽ luôn có dạng tương tự như sau:

```text
   log_destination = 'stderr'
   logging_collector = on
```

Ở đây, dòng đầu tiên bảo cluster gửi log đã tạo tới standard error, nhưng từ đó chúng sẽ được một process chuyên dụng có tên logging collector quản lý và lưu trữ.

Trong phần còn lại của section này, chúng ta sẽ tập trung vào việc configure logging collector. Logging collector có thể được configure để đặt log trong directory bạn muốn, đặt tên log file theo ý muốn và tự động rotate chúng. Log rotation là một feature khá phổ biến trong mọi logging system và có nghĩa là khi một log file đã tăng tới size được chỉ định, hoặc khi đủ thời gian đã trôi qua, log file sẽ được đóng lại và một file mới (với tên khác) được tạo ra. Ví dụ, bạn có thể quyết định tự động rotate log file khi một file đạt 100 MB hoặc sau mỗi 2 ngày: điều kiện nào xảy ra trước sẽ trigger rotation, để PostgreSQL tạo một log file khác ít nhất hai ngày một lần hoặc sau mỗi 100 MB thông tin text.

> **Lưu ý:** Log rotation hữu ích vì cho phép tạo các log file nhỏ hơn, có thể giới hạn trong một khoảng thời gian cụ thể. Một mặt, việc này sẽ phân tán log qua nhiều file (có thể nhỏ); mặt khác, nó không tạo ra một log file duy nhất (có thể rất lớn), vốn có thể khó phân tích.

Sau khi enable logging collector, bạn phải configure nó để lưu log theo cách và tại nơi bạn muốn. Thực tế, bạn có thể dùng các parameter sau để configure logging collector process bằng cách đặt giá trị phù hợp cho từng setting trong PostgreSQL configuration file:

- `log_directory`: Đây là directory nơi các log file riêng lẻ phải được lưu. Nó có thể là relative path, được tính tương đối với `PGDATA`, hoặc absolute path (nơi process phải có khả năng ghi). Rõ ràng, đây phải là path mà operating system user chạy cluster có quyền write.
- `log_filename`: Đây là một filename đơn lẻ hoặc một pattern để chỉ định tên của mọi log file (bên trong `log_directory`). Pattern có thể được chỉ định theo `strftime(3)` để format nó bằng date và time. Ví dụ, giá trị `postgresql-%Y-%m-%d.log` sẽ tạo filename có date (tương ứng là year, month và day), chẳng hạn `postgresql-2022-07-19.log`.
- `log_rotation_age`: Giá trị này cho biết log phải chờ bao lâu trước khi áp dụng automatic log rotation. Ví dụ, `1d` nghĩa là 1 day và chỉ định log sẽ được rotate mỗi ngày một lần.
- `log_rotation_size`: Giá trị này chỉ định size của log file trước khi nó được rotate sang file mới. Ví dụ, `50MB` nghĩa là log file sẽ được rotate khi đạt size 50 MB.
- `log_truncate_on_rotation`: Boolean parameter này quyết định PostgreSQL phải truncate (tức làm rỗng và bắt đầu lại) một file hiện có khi rotation hay thay vào đó append log data mới vào file hiện có.

> **Lưu ý:** Hãy nhớ rằng log rotation không chính xác tuyệt đối: log file có thể vượt quá một chút so với size hoặc age dùng để rotation, tùy thuộc vào logging activity của cluster.

Mọi setting liên quan đến rotation đều yêu cầu `logging_collector` được bật: sau cùng, PostgreSQL chỉ có thể quản lý rotation khi nó chịu trách nhiệm về việc logging.
