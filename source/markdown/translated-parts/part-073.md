Giờ đây, chúng ta có thể truy cập database `forumdb` của postgresql bằng user có tên `forumdb`:

```text
postgres@pg-destination:~$ psql -U forumdb forumdb

forumdb=> select * from categories;
    pk |          title             |             description
----+-----------------------+---------------------------------
     1 | Database                   | Database related discussions
     2 | Unix                       | Unix and Linux discussions
     3 | Programming Languages | All about programming languages
(3 rows)

forumdb=> select * from users;
    pk | username    |      gecos         |          email
----+-----------+----------------+---------------------
     1 | fluca1978 | Luca Ferrari         | fluca1978@gmail.com
     2 | sscotty71 | Enrico Pirozzi | sscptty71@gmail.com
(2 rows)
```

# Tóm tắt

Trong chương này, chúng ta đã tìm hiểu một số extension và tool có sẵn cho PostgreSQL. Chúng ta không trình bày tổng quan về mọi thứ có sẵn cho PostgreSQL; thay vào đó, chúng ta tập trung cụ thể vào một số tool và extension giúp DBA tiết kiệm thời gian. Chúng ta đã nói về pgbackrest, một tool rất hữu ích để quản lý recovery và PITR. Chúng ta cũng đã nói về pgloader, một tool mạnh dùng để migrate từ các DBMS khác sang PostgreSQL. Sau đó, chúng ta trình bày một ví dụ đơn giản về việc migrate từ MariaDB sang PostgreSQL.

# Kiểm tra kiến thức

- Nếu `myfield` là một field `varchar(200)` của table `mytable`, statement `create index on mytable(myfield)` có cải thiện query với điều kiện `where` dạng `like foo%` không?

  Không, statement trên sẽ không cải thiện query với điều kiện `where` dạng `like ‘foo%'`; để làm được điều đó, chúng ta phải dùng `create index on mytable using btree(my field varchar_pattern_ops);`. Xem mục *Tìm hiểu extension pg_trgm* để biết thêm chi tiết.

- Có thể dùng index với mọi loại query `like` và `ilike` không?

  Có, có thể dùng `pg_trgm`. Xem mục *Tìm hiểu extension pg_trgm* để biết thêm chi tiết.

- Point-in-time recovery (PITR) là gì?

  Trong phạm vi retention, point-in-time recovery là khả năng khôi phục về bất kỳ thời điểm nào trong quá khứ. Xem mục *Disaster recovery với pgbackrest* để biết thêm chi tiết.

- PostgreSQL có tool nào giúp chúng ta quản lý continuous backup và point-in-time recovery không?

  Có, PostgreSQL có một số tool giúp quản lý continuous backup và PITR, một trong số đó có tên là pgbackrest. Xem mục *Disaster recovery với pgbackrest* để biết thêm chi tiết.

- Có thể kết nối trực tiếp đến một PostgreSQL server khác không?

  Có, bằng extension PostgreSQL foreign data wrapper. Xem mục *Sử dụng foreign data wrapper và extension postgres_fdw* để biết thêm chi tiết.

# Tài liệu tham khảo

- Tài liệu chính thức của Pg_trgm: https://www.postgresql.org/docs/current/pgtrgm.html
- Trang wiki về foreign data wrappers: https://wiki.postgresql.org/wiki/Foreign_data_wrappers
- Tài liệu chính thức của PostgreSQL về foreign data wrappers: https://www.postgresql.org/docs/current/postgres-fdw.html
- Tài liệu chính thức của PgBackrest: https://pgbackrest.org
- Tài liệu chính thức của PgLoader: https://pgloader.readthedocs.io

# Tìm hiểu thêm trên Discord

Để tham gia cộng đồng Discord của cuốn sách này, nơi bạn có thể chia sẻ feedback, đặt câu hỏi cho tác giả và tìm hiểu về các bản phát hành mới, hãy quét mã QR bên dưới:

https://discord.gg/jYWCjF6Tku

# packt.com

Đăng ký thư viện số trực tuyến của chúng tôi để được truy cập đầy đủ hơn 7.000 sách và video, cùng các tool hàng đầu trong ngành giúp bạn lập kế hoạch phát triển cá nhân và thăng tiến sự nghiệp. Để biết thêm thông tin, vui lòng truy cập website của chúng tôi.

## Tại sao nên đăng ký?

- Dành ít thời gian hơn cho việc học và nhiều thời gian hơn cho việc coding với các eBook và video thực tiễn từ hơn 4.000 chuyên gia trong ngành.
- Cải thiện việc học với Skill Plan được xây dựng riêng cho bạn.
- Nhận miễn phí một eBook hoặc video mỗi tháng.
- Có thể tìm kiếm đầy đủ để dễ dàng truy cập thông tin quan trọng.
- Copy và paste, in và bookmark nội dung.

Tại www.packt.com, bạn cũng có thể đọc một bộ sưu tập các bài viết kỹ thuật miễn phí, đăng ký nhiều newsletter miễn phí, và nhận các ưu đãi cùng chương trình giảm giá độc quyền cho sách và eBook của Packt.

# Những cuốn sách khác bạn có thể thích

Nếu bạn thích cuốn sách này, có thể bạn sẽ quan tâm đến những cuốn sách khác của Packt sau đây:

## Mastering PostgreSQL 15 - Fifth Edition

Hans-Jürgen Schönig

ISBN: 9781803248349

- Tận dụng các tính năng indexing trong PostgreSQL và tinh chỉnh performance của query.
- Làm việc với stored procedure và quản lý backup cũng như recovery.
- Nắm được các kỹ thuật replication và failover.
- Cải thiện security của database server và xử lý encryption hiệu quả.
- Troubleshoot PostgreSQL instance để tìm giải pháp cho các vấn đề phổ biến và không phổ biến.
- Thực hiện database migration từ Oracle sang PostgreSQL một cách dễ dàng.

## SQL for Data Analytics - Third Edition

Jun Shan, Matt Goldwasser, Upom Malik , Benjamin Johnston

ISBN: 9781801812870

- Dùng SQL để làm sạch, chuẩn bị và kết hợp các dataset khác nhau.
- Aggregate các statistics cơ bản bằng các `GROUP BY` clause.
- Thực hiện các phép tính statistics nâng cao bằng một `WINDOW` function.
- Import data vào một database để kết hợp với các table khác.
- Export kết quả SQL query đến nhiều nguồn khác nhau.
- Phân tích các data type đặc biệt trong SQL, bao gồm dữ liệu địa không gian, date/time và JSON.
- Tối ưu query và tự động hóa các task.
- Suy nghĩ về các vấn đề dữ liệu và tìm câu trả lời bằng SQL.

# Packt đang tìm kiếm những tác giả như bạn

Nếu bạn quan tâm đến việc trở thành tác giả, vui lòng truy cập authors.packtpub.com và ứng tuyển ngay hôm nay. Chúng tôi đã làm việc với hàng nghìn developer và chuyên gia công nghệ, cũng như bạn, để giúp họ chia sẻ insight với cộng đồng công nghệ toàn cầu. Bạn có thể nộp một application chung, ứng tuyển cho một chủ đề cụ thể đang được tuyển, hoặc gửi ý tưởng của riêng mình.

# Chia sẻ suy nghĩ của bạn

Giờ bạn đã hoàn thành Learn PostgreSQL, chúng tôi rất muốn nghe suy nghĩ của bạn! Nếu bạn mua sách từ Amazon, vui lòng click vào đây để chuyển thẳng đến trang review Amazon của cuốn sách và chia sẻ ý kiến hoặc để lại review trên website nơi bạn đã mua sách.

Review của bạn rất quan trọng đối với chúng tôi và cộng đồng công nghệ, đồng thời sẽ giúp chúng tôi bảo đảm cung cấp nội dung chất lượng xuất sắc.

# Chỉ mục

## A

- Access Control Lists (ACLs) 307, 323-327
  - kiểm tra 345, 346
- advanced statement window functions 167
  - frame clause 167
- aggregate functions 130-133
  - `EXCEPT` operator 135
  - `INTERSECT` operator 136
  - `UNION ALL` operator 133, 134
  - `UNION` operator 133, 134
- `ALTER ROLE` statement 310
  - configuration parameter theo role 312, 313
  - `SESSION_USER`, so với `CURRENT_USER` 311, 312
  - dùng để đổi tên role hiện có 310
- `ANALYZE` command 492-494
- data type arbitrary precision 186, 188
- archive và replication settings 586, 587
- physical replication asynchronous
  - thực hiện 614, 615
- replication asynchronous 609, 617-619
  - replica, monitoring 619, 620
- Atomicity, Consistency, Isolation và Durability (ACID) 3, 360

- auditing
  - theo role 530-532
  - theo session 528-530
  - triển khai 524, 525
  - PgAudit, cấu hình 527
  - PgAudit, cài đặt 525
  - PostgreSQL, cấu hình cho PgAudit 526
- auto-explain 494-498
- VACUUM tự động 410-412
  - worker autovacuum 410

## B

- backup 536
  - ưu điểm 536
  - nhược điểm 537
- Balanced Tree (B-Tree) 462
- base backup
  - quản lý 678-681
- basic statement window functions
  - `CUME_DIST` 165
  - `DENSE_RANK` 162
  - `FIRST_VALUE` 160
  - `LAG` 163
  - `LAST_VALUE` 161
  - `LEAD` 164
