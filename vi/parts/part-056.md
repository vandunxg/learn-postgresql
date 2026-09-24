Cho dù cluster của bạn đã thực hiện bao nhiêu activity và các file pgBadger tạo ra có kích thước bao nhiêu, một khi đã có report, bạn có thể trỏ web browser tới các file local (hoặc serve kết quả qua web server). Bạn sẽ thấy report như bên dưới. Report cung cấp một cái nhìn nhanh về activity của cluster, bao gồm số statement, thời gian dùng để phục vụ các statement đó, và các graph thể hiện traffic của statement theo khoảng thời gian:

![Hình 14.1: Trang đầu của dashboard pgBadger](../assets/part-056-figure-14-1-000.jpg)

*Hình 14.1: Trang đầu của dashboard pgBadger*

Nếu đang dùng Docker image cho chapter này, bạn có thể trỏ web browser tới URL `http://localhost:8080/first_report.html` và xem report.

Ở đầu web page có một menu bar gồm nhiều menu, cho phép bạn xem các graph và dashboard khác nhau.

Ví dụ, menu Connections cho phép bạn lấy thông tin về số connection concurrent mà bạn có, như trong ví dụ sau:

![Hình 14.2: Ví dụ về dashboard Connections](../assets/part-056-figure-14-2-000.jpg)

*Hình 14.2: Ví dụ về dashboard Connections*

Menu Queries cho phép bạn xem overview về type và frequency của các statement, như trong screenshot sau, trong đó phần lớn query là type `SELECT`:

![Hình 14.3: Ví dụ về dashboard Queries](../assets/part-056-figure-14-3-000.jpg)

*Hình 14.3: Ví dụ về dashboard Queries*

Menu Top cho phép chúng ta xem “top event”, chẳng hạn các query chậm nhất và các query tốn nhiều thời gian nhất, lần lượt được thể hiện trong screenshot sau:

![Hình 14.4: Trích đoạn dashboard Top Queries](../assets/part-056-figure-14-4-000.jpg)

*Hình 14.4: Trích đoạn dashboard Top Queries*

pgBadger cũng hiển thị một phiên bản chi tiết hơn trên cùng page, như trong hình sau:

![Hình 14.5: Chi tiết về các query tốn nhiều thời gian nhất](../assets/part-056-figure-14-5-000.jpg)

*Hình 14.5: Chi tiết về các query tốn nhiều thời gian nhất*

Thảo luận về tất cả feature và dashboard của pgBadger nằm ngoài scope của cuốn sách này, nhưng bạn có thể xem tài liệu chính thức để biết thêm chi tiết và có lời giải thích rõ ràng, chính xác về từng option.

## Lập lịch pgBadger

pgBadger có thể được sử dụng theo lịch để liên tục tạo ra các report chính xác trong một khoảng thời gian xác định. Điều này khả thi vì pgBadger có feature incremental; nhờ đó report không bị overwrite mỗi lần, mà thay vào đó chương trình có thể tạo report theo từng giờ và một report summary theo từng tuần.

Điều này hữu ích vì bạn có thể lập lịch chạy pgbadger bằng, chẳng hạn, `cron(1)` rồi không phải bận tâm thêm. Trước tiên, hãy xem cách chạy pgBadger ở incremental mode:

```text
      $ pgbadger -I --outdir /data/html -f stderr            /postgres/16/data/log/
      postgresql-2023-*.log
      [========================>] Parsed 22008130 bytes of 22008130 (100.00%),
      queries: 120569, events: 1
      LOG: Ok, generating HTML daily report into /data/html/2023/07/19/...
      LOG: Ok, generating HTML weekly report into /data/html/2023/week-30/...
      LOG: Ok, generating global index to access incremental reports...
```

Argument `-I` chỉ định incremental mode, vì vậy pgBadger sẽ tạo các file riêng cho report theo giờ và theo tuần. Lưu ý rằng thay vì chỉ định output file, option `--outdir` được dùng để chỉ định directory chứa các file. Option `-f` cho pgBadger biết loại log mà nó đang quản lý; trong ví dụ này là các text file thông thường. Cuối cùng, như thường lệ, log file cần phân tích được biểu diễn dưới dạng shell glob (`postgresql-2023-*.log`).

Kết quả cuối cùng, như bạn có thể đoán từ output của chương trình, là một directory tree tương tự như sau:

```text
       $ ls -R /data/html/
      /data/html/:
      2023   LAST_PARSED   index.html


      /data/html/2023:
      07   week-30


      /data/html/2023/07:
      19


      /data/html/2023/07/19:
      2023-07-19-65.bin    index.html

      /data/html/2023/week-30:
      index.html
```

File `index.html` chính là entry point cho toàn bộ incremental report. Sau đó là một tree gồm directory cho year (2023), month (07), day (19), và một file `index.html` cho day đó.

Ngoài ra còn có một phần của tree dùng để tập hợp data cho week hiện tại; trong trường hợp này là week number 30. Vì vậy tree sẽ được mở rộng khi có thêm các day mới. File đặc biệt `LAST_PARSED` được pgBadger dùng để nhớ nó đã dừng parse ở đâu, cho phép nó bắt đầu từ vị trí đó trong lần gọi incremental tiếp theo.

Nếu trỏ web browser tới main index file, bạn sẽ thấy một calendar như screenshot sau, nơi bạn có thể chọn month và day để xem report theo từng day.

![Hình 14.6: Global dashboard của pgBadger trong một khoảng ngày](../assets/part-056-figure-14-6-000.jpg)

*Hình 14.6: Global dashboard của pgBadger trong một khoảng ngày*

Khi click vào một day cụ thể, bạn sẽ được chuyển tới daily report, nơi hiển thị đúng các dashboard đã thảo luận trước đó. Rõ ràng, bạn không thể click vào những day mà report chưa được tạo hoặc không có activity tương ứng trong PostgreSQL log.

Nhờ incremental approach, giờ bạn có thể lập lịch chạy bằng scheduler của riêng mình; ví dụ, trong `cron(1)`, bạn có thể thêm một line như sau:

```text
   59 23 * * * pgbadger -I --outdir /data/html/ -f stderr /postgres/16/data/
   log/postgresql-'date +'%Y-%m-%d''.log
```

Về cơ bản, đây là cùng command line với command trước đó, chỉ khác là current date được tự động tính. Line trước đó sẽ tạo report cho current day vào cuối mỗi day, rồi dùng report đó để populate report tree.

> Entry trong crontab trước đó chỉ là một ví dụ. Hãy cân nhắc bọc mọi thứ trong một script robust và kiểm tra tính đúng đắn của việc thực thi script.

Cuối cùng, có thể chạy pgBadger từ một remote host, nhờ đó bạn có thể dành riêng một machine để thu thập tất cả report và information tại một nơi. Thực tế, pgBadger chấp nhận một URI parameter là remote location của log directory (hoặc file), và có thể truy cập qua FTP hoặc SSH, trong đó SSH an toàn hơn và được khuyến nghị.

Ví dụ sau biểu diễn cùng command line như trước, nhưng ở đây nó pull log ở incremental mode từ một remote PostgreSQL host có tên `miguel`:

```text
   $ pgbadger -I --outdir /data/html ssh://postgres@miguel//postgres/16/
   data/log/postgresql-'date +'%Y-%m-%d''.pgbadger.log
   [========================>] Parsed 313252 bytes of 313252 (100.00%),
   queries: 841, events: 34
```

Lưu ý rằng log file được chỉ định thông qua SSH URL. Bạn được khuyến nghị mạnh mẽ sử dụng một remote user có quyền truy cập log và thực hiện SSH key exchange để tự động hóa việc login giữa các host.

Bây giờ chúng ta đã biết cách sử dụng log, hãy chuyển sang một cách khác để xem xét task: auditing.

## Triển khai auditing

Auditing là khả năng thực hiện introspection trên một application hoặc user session, nói cách khác là có thể tái tạo từng bước những gì user hoặc application yêu cầu cluster thực hiện.

Auditing hơi khác logging, vì logging cung cấp một cách đơn giản để lưu các action của user, nhưng không cung cấp cách dễ dàng để reconstruct interaction của user hoặc application với cluster. Thực tế, trong một cluster có tính concurrent cao, nhiều action do các user khác nhau thực hiện sẽ cùng tồn tại trong log dưới dạng một mớ các line trộn lẫn. Hơn nữa, logging không cung cấp logic cụ thể nào về việc nó đang lưu gì, do đó sẽ khó tìm ra user đã làm gì. Điều này càng đúng hơn khi user hoặc application thực thi các statement phức tạp, đặc biệt là các statement không cung cấp tường minh parameter và value.

Ví dụ, hãy xét section đơn giản sau:

```text
   forumdb=> PREPARE my_query( text ) AS SELECT * FROM forum.categories WHERE
   title like $1;
   PREPARE
   forumdb=>     EXECUTE my_query( 'PROGRAMMING%' );
      pk |           title             |              description
   ----+-----------------------+---------------------------------
      3 | PROGRAMMING LANGUAGES | All about programming languages
   (1 row)
```

Với verbose logging, section đó sẽ cho ra output sau:

```text
   LOG: duration: 19.011 ms statement: PREPARE my_query( text ) AS SELECT *
   FROM forum.categories WHERE title like $1;
   LOG:      duration: 6.539 ms    statement: EXECUTE my_query( 'PROGRAMMING%' );
```

Như bạn thấy, log chứa mọi thứ cần thiết để reconstruct user đã làm gì, nhưng việc đó không đơn giản. Bạn phải hiểu rằng hai line có liên quan với nhau và session thực thi các statement là cùng một session. Điều này không phải lúc nào cũng khả thi, đặc biệt nếu có các query khác được log ở giữa hai line mà bạn quan tâm.

Ngoài ra, có thể log không báo cáo toàn bộ information bạn cần, có lẽ vì bạn đã chọn không log các statement thực thi nhanh hơn một threshold.

Vì vậy, dù có thể dùng logging để thực hiện auditing, đó không phải lúc nào cũng là lựa chọn tốt nhất. Trong section này, bạn sẽ tìm hiểu extension PgAudit, được tạo ra để cung cấp một auditing infrastructure đáng tin cậy và dễ sử dụng. PgAudit tận dụng logging facility xuất sắc của PostgreSQL; vì vậy, bạn cần cấu hình logging infrastructure theo cách phù hợp, như sẽ thấy trong các subsection tiếp theo.

Trước khi đi vào configuration và cách sử dụng PgAudit, có một số detail và concept cần được giải thích. PgAudit có thể hoạt động theo hai cách khác nhau: auditing theo session hoặc theo object. Cách đầu tiên là một cách nhanh và đơn giản để audit một phần (hoặc toàn bộ) session của user hay application; cách thứ hai là cách phức tạp và fine-grained hơn để log các action liên quan tới những database object cụ thể (ví dụ, ai đã delete row từ table đó?).

Auditing theo session hoạt động bằng cách chỉ cần cấu hình các category statement cần audit trong một session. Ngược lại, auditing theo object yêu cầu bạn cấu hình từng database role; tùy theo tập permission được gán, các role đó sẽ trigger việc audit những action cụ thể. Trong các subsection tiếp theo, bạn sẽ thấy cả hai cách được dùng để audit.

## Cài đặt PgAudit

Cách nhanh nhất để cài đặt PgAudit là dùng package manager của operating system. Ví dụ, trên system GNU/Debian hoặc Ubuntu, bạn có thể nhập:

```text
   $ sudo apt install pgaudit-16-pgaudit
```

Nếu cần cài đặt PgAudit từ source, trước tiên bạn phải lấy một version tương thích với PostgreSQL cluster của mình, sau đó uncompress và cài đặt nó:

```text
   $ wget https://github.com/pgaudit/pgaudit/archive/refs/tags/1.7.0.tar.gz
   ..
   $ tar xzvf 1.7.0.tar.gz
   ...
   $ cd pgaudit-1.7.0
   $ make USE_PGXS=1
   ...

   $ sudo make USE_PGXS=1 install
```

Sau khi extension được cài đặt, bạn phải cấu hình PostgreSQL để sử dụng PgAudit.

## Cấu hình PostgreSQL để sử dụng PgAudit

PgAudit là một extension cần được load khi server startup, vì vậy bạn phải thay đổi configuration file chính, `postgresql.conf`, để thêm library `pgaudit` như sau:

```text
   shared_preload_libraries = 'pgaudit'
```

Tiếp theo, hãy restart cluster để các thay đổi có hiệu lực:

```text
   $    pg_ctl -D /postgres/16/data restart
```

Vì PgAudit là một extension, bạn phải enable nó trong database mà mình muốn audit để activate nó. Để đơn giản, hãy enable nó trong database `forumdb` của chúng ta (bạn cần connect với tư cách database superuser):

```text
   forumdb=# CREATE EXTENSION pgaudit;
   CREATE EXTENSION
```

Bây giờ là lúc quyết định khi nào và bằng cách nào áp dụng auditing.

> Nếu đang sử dụng Docker image cho chapter này, PgAudit đã được cài đặt sẵn cho bạn!

## Cấu hình PgAudit

PgAudit đi kèm một tập configuration parameter phong phú, cho phép bạn chỉ định chính xác cần log gì, khi nào log, loại trừ điều gì khỏi auditing, v.v. Tất cả configuration parameter đều nằm trong namespace `pgaudit` để không xung đột với các setting hiện có khác cùng tên.

Setting quan trọng nhất là `pgaudit.log`, xác định những statement và action mà bạn muốn audit. Parameter này có thể nhận bất kỳ value nào sau đây:

- `ALL` để audit mọi statement
- `NONE` để không audit bất kỳ thứ gì
- `READ` để chỉ audit các statement `SELECT` và `COPY`
- `WRITE` để audit mọi statement sửa đổi data (`INSERT`, `UPDATE` và `COPY`)
- `ROLE` để audit việc thay đổi hoặc tạo role
- `DDL` để audit mọi data-definition statement, và do đó mọi thay đổi đối với database structure
- `FUNCTION` để audit mọi lần thực thi code, bao gồm cả DO block
- `MISC` để audit mọi value chưa được phân loại tường minh ở trên
- `MISC_SET` để audit mọi command dạng SET

Bạn có thể chỉ định nhiều setting cùng lúc bằng cách phân tách từng name bằng dấu phẩy, ví dụ:

```text
   pgaudit.log = 'WRITE,FUNCTION';
```

Function này có thể được dùng để audit mọi thay đổi data và lần thực thi code.

Một configuration parameter quan trọng khác là `pgaudit.log_level`, chỉ định log level mà PgAudit dùng để đưa các audit message vào log. Theo mặc định, setting này nhận value `log`, nhưng bạn có thể đổi nó thành bất kỳ log threshold nào khác, ngoại trừ các threshold error (chẳng hạn `ERROR`, `FATAL` và `PANIC`).

Để thêm nhiều detail hơn vào audit information, có lẽ bạn sẽ muốn enable parameter `pgaudit.log_parameter` để dump mọi query parameter (bạn sẽ thấy một ví dụ ở phần sau).

Nếu định cấu hình PgAudit theo object, bạn cần set parameter `pgaudit.role` như sẽ thấy ở phần sau của chapter này.
