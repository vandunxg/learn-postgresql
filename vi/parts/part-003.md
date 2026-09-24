## Chương 14: Logging và Auditing — 503

- Yêu cầu kỹ thuật — 503
- Giới thiệu về logging — 504
  - Ghi log ở đâu — 505
  - Khi nào ghi log — 508
  - Ghi log gì — 512
- Trích xuất thông tin từ log – pgBadger — 514
  - Cài đặt pgBadger — 514
  - Cấu hình logging của PostgreSQL để sử dụng pgBadger — 515
  - Sử dụng pgBadger — 516
  - Lập lịch cho pgBadger — 521
- Triển khai auditing — 524
  - Cài đặt PgAudit — 525
  - Cấu hình PostgreSQL để khai thác PgAudit — 526
  - Cấu hình PgAudit — 527
  - Auditing theo session — 528
  - Auditing theo role — 530
- Tóm tắt — 532
- Kiểm tra kiến thức — 532
- Tài liệu tham khảo — 533

## Chương 15: Backup và Restore — 535

- Yêu cầu kỹ thuật — 536
- Giới thiệu các loại backup và restore — 536
- Tìm hiểu logical backup — 537
  - Dump một database — 539
  - Restore một database — 543
  - Giới hạn lượng dữ liệu cần backup — 547
  - Compression — 548
  - Các định dạng dump và pg_restore — 549
- Thực hiện selective restore — 552
- Dump toàn bộ cluster — 555
- Backup song song — 556
- Tự động hóa backup — 558
- Lệnh COPY — 559
- Tìm hiểu physical backup — 563
  - Thực hiện physical backup thủ công — 564
    - pg_verifybackup — 566
  - Khởi động cluster đã clone — 567
  - Restore từ physical backup — 568
- Các khái niệm cơ bản phía sau PITR — 569
- Tóm tắt — 570
- Kiểm tra kiến thức — 570
- Tài liệu tham khảo — 571

## Chương 16: Configuration và Monitoring — 573

- Yêu cầu kỹ thuật — 574
- Cấu hình cluster — 574
  - Kiểm tra tất cả configuration parameter — 576
  - Tìm configuration error — 578
  - Lồng các configuration file — 579
  - Configuration context — 580
  - Main configuration setting — 581
    - WAL setting — 582
    - Setting liên quan đến memory — 584
    - Setting thông tin process — 585
    - Setting liên quan đến networking — 585
    - Setting archive và replication — 586
    - Setting liên quan đến VACUUM và autovacuum — 587
    - Setting optimizer — 587
    - Statistics collector — 587
  - Sửa configuration từ live system — 588
  - Configuration generator — 589
- Monitoring cluster — 592
  - Thông tin về query và session đang chạy — 593
  - Kiểm tra lock — 594
  - Kiểm tra database — 596
  - Kiểm tra table và index — 597
  - Các statistics khác — 599
- Statistics nâng cao với extension pg_stat_statements — 600
  - Cài đặt extension pg_stat_statements — 600
  - Sử dụng pg_stat_statements — 601
  - Reset dữ liệu được thu thập từ pg_stat_statements — 602
  - Tuning pg_stat_statements — 602
- Tóm tắt — 603
- Kiểm tra kiến thức — 603
- Tài liệu tham khảo — 604

## Chương 17: Physical Replication — 607

- Yêu cầu kỹ thuật — 608
- Tìm hiểu các khái niệm replication cơ bản — 609
  - Physical replication và WAL — 609
    - Directive wal_level — 610
  - Chuẩn bị môi trường cho streaming replication — 610
- Quản lý streaming replication — 612
  - Các khái niệm cơ bản của streaming replication — 612
  - Môi trường asynchronous replication — 614
  - Tùy chọn wal_keep_segments — 615
  - Cách dùng slot — 616
  - Lệnh pg_basebackup — 616
  - Asynchronous replication — 617
    - Monitoring replica — 619
  - Synchronous replication — 620
    - PostgreSQL setting — 621
    - Cascading replication — 623
    - Delayed replication — 626
  - Promote replica server thành primary — 626
- Tóm tắt — 627
- Kiểm tra kiến thức — 628
- Tài liệu tham khảo — 628

## Chương 18: Logical Replication — 631

- Yêu cầu kỹ thuật — 631
- Tìm hiểu các khái niệm cơ bản của logical replication — 632
- So sánh logical replication và physical replication — 635
- Tìm hiểu thiết lập logical replication và các tính năng logical replication mới trên PostgreSQL 16 — 636
  - Setting môi trường logical replication — 636
    - Replica role — 637
    - Primary server – postgresql.conf — 637
    - Replica server – postgresql.conf — 638
    - File pg_hba.conf — 639
  - Thiết lập logical replication — 639
  - Monitoring logical replication — 641
    - Read-only so với write-allowed — 643
  - DDL command — 649
  - Vô hiệu hóa logical replication — 651
  - Tạo logical replication bằng một physical replication instance — 652
- Tóm tắt — 657
- Kiểm tra kiến thức — 658
- Tài liệu tham khảo — 658

## Chương 19: Các công cụ và extension hữu ích — 661

- Yêu cầu kỹ thuật — 662
- Tìm hiểu extension pg_trgm — 662
- Sử dụng foreign data wrapper và extension postgres_fdw — 665
- Disaster recovery với pgbackrest — 667
  - Các khái niệm cơ bản — 668
  - Thiết lập môi trường — 669
    - Trao đổi public key — 669
  - Cài đặt pgbackrest — 671
  - Cấu hình pgbackrest — 672
    - Cấu hình repository — 672
    - Sử dụng pgbackrest với object store support — 675
    - Cấu hình PostgreSQL server — 675
- File postgresql.conf — 675
- File pgbackrest.conf — 676
- Tạo và quản lý continuous backup — 677
  - Tạo stanza — 677
  - Kiểm tra stanza — 677
  - Quản lý base backup — 678
  - Quản lý PITR — 681
- Di chuyển từ MySQL/MariaDB sang PostgreSQL bằng pgloader — 684
- Tóm tắt — 688
- Kiểm tra kiến thức — 688
- Tài liệu tham khảo — 689

## Các sách khác bạn có thể quan tâm — 691

## Mục lục tra cứu — 697

# Lời nói đầu

PostgreSQL là một trong những hệ quản trị database object-relational mã nguồn mở phát triển nhanh nhất thế giới (Database Management Systems, DBMS). PostgreSQL cung cấp các tính năng cấp enterprise; có khả năng mở rộng, bảo mật và hiệu năng cao; dễ sử dụng; đồng thời có một ecosystem rất phong phú, bao gồm application driver và tool. Trong cuốn sách này, bạn sẽ tìm hiểu PostgreSQL 16, bản stable release mới nhất, và học cách xây dựng các database solution an toàn, đáng tin cậy và có khả năng mở rộng bằng PostgreSQL. Với các tutorial thực hành và một bộ Docker image để bạn làm theo từng ví dụ từng bước, cuốn sách sẽ dạy bạn cách đạt được database design phù hợp cho một môi trường đáng tin cậy.

Bạn sẽ học cách cài đặt, cấu hình và quản lý PostgreSQL server; quản lý user và connection; đồng thời kiểm tra activity của server để tối ưu hiệu năng. Với các phần hỏi và đáp trong mỗi chương, bạn có thể kiểm tra kiến thức mới tiếp thu trong quá trình học.

Cuốn sách bắt đầu bằng việc giới thiệu các khái niệm chính liên quan đến PostgreSQL, cũng như cách cài đặt và kết nối đến database, sau đó chuyển sang quản lý user, permission và các object cơ bản như table. Bạn sẽ được học về Data Definition Language và các statement, command phổ biến và hữu ích nhất, cũng như tất cả khái niệm relational database thiết yếu, chẳng hạn foreign key, trigger và function. Tiếp theo, bạn sẽ tìm hiểu cách cấu hình và tuning cluster để khai thác PostgreSQL service hiệu quả nhất, cách tạo và quản lý index để truy xuất dữ liệu nhanh, cũng như cách tạo và restore bản backup dữ liệu. Cuối cùng, bạn sẽ học cách tạo solution high availability của riêng mình bằng physical hoặc logical replication, đồng thời làm quen với một số tool và extension phổ biến, hữu ích nhất mà bạn có thể áp dụng cho cluster.

Đến cuối cuốn sách, bạn sẽ nắm vững database PostgreSQL và có thể thiết lập PostgreSQL instance của riêng mình để xây dựng các solution hướng dữ liệu vững chắc cho những vấn đề thực tế.

## Cuốn sách này dành cho ai

Cuốn sách này dành cho bất kỳ ai muốn học về database PostgreSQL từ đầu, hoặc bất kỳ ai muốn xây dựng các database application vững chắc, có khả năng mở rộng và high availability. Tất cả tính năng mới nhất và thú vị nhất của PostgreSQL sẽ được trình bày, cùng với mọi khái niệm mà database administrator hoặc application developer cần để khai thác PostgreSQL instance hiệu quả nhất.

Mặc dù không yêu cầu có kiến thức trước về PostgreSQL, bạn cần quen thuộc với database và ngôn ngữ SQL.

## Cuốn sách này bao quát những gì

**Chương 1, Giới thiệu về PostgreSQL** giải thích database PostgreSQL là gì, cộng đồng và quá trình phát triển phía sau database relational cấp enterprise mạnh mẽ này, cũng như cách nhận trợ giúp và nhận biết các version PostgreSQL khác nhau cùng các dependency. Bạn cũng sẽ học cách lấy và cài đặt PostgreSQL thông qua binary package hoặc bằng cách compile từ source. Bạn sẽ thấy cách quản lý cluster bằng các tool của operating system (systemd và rc script).

**Chương 2, Tìm hiểu Cluster của bạn** trình bày cấu trúc của PostgreSQL cluster bằng cách mô tả những gì có trên file system, vị trí của các configuration file chính và cách chúng được sử dụng. Command-line utility psql được mô tả để giúp bạn kết nối đến database cluster và tương tác với cluster.

**Chương 3, Quản lý User và Connection** cung cấp mô tả đầy đủ về cách user và connection được quản lý bởi một instance đang chạy, cũng như cách ngăn hoặc giới hạn user kết nối. Khái niệm “role” được mô tả, và bạn sẽ học cách tạo các user account riêng lẻ cũng như các group gồm những user có liên quan.

**Chương 4, Các Statement cơ bản** trình bày cách tạo và hủy các database object chính, chẳng hạn database, table và schema. Chương này cũng đề cập đến các statement cơ bản như SELECT, INSERT, UPDATE và DELETE. Chương này chỉ ra cách quản lý public schema trên PostgreSQL 16.

**Chương 5, Các Statement nâng cao** giới thiệu các statement nâng cao mà PostgreSQL cung cấp, chẳng hạn common table expression, MERGE, UPSERT và query sử dụng RETURNING để trả về các row. Chương này cung cấp các ví dụ thực tế về thời điểm và cách sử dụng chúng.

**Chương 6, Window Function** giới thiệu một tập function mạnh mẽ, cho phép aggregate mà không cần gộp result thành một row duy nhất. Nói cách khác, nhờ window function, bạn có thể thực hiện aggregate trên nhiều row (window) mà vẫn trình bày tất cả tuple trong output. Window function cho phép triển khai business intelligence và giúp việc lập report trở nên dễ dàng.

**Chương 7, Lập trình Server-Side** đề cập đến thực tế rằng mặc dù SQL phù hợp với phần lớn công việc hằng ngày trên database, bạn có thể gặp một vấn đề cụ thể đòi hỏi cách tiếp cận imperative. Chương này chỉ ra cách triển khai code của riêng bạn bên trong database, cách viết function và procedure bằng các ngôn ngữ khác nhau, cũng như cách làm cho chúng tương tác với transaction boundary.

**Chương 8, Trigger và Rule** trình bày cả trigger và rule bằng các ví dụ thực tế, cho thấy ưu điểm và hạn chế của chúng. Chương kết thúc bằng các ví dụ về event trigger.

**Chương 9, Partitioning** tìm hiểu partitioning – việc chia một table thành các phần nhỏ hơn. PostgreSQL đã hỗ trợ partitioning từ lâu, nhưng ở version 10, PostgreSQL giới thiệu cái gọi là “declarative partitioning”. Chương này tập trung vào tất cả tính năng liên quan đến declarative partitioning, tuning parameter của nó và cách partition một table bằng các tablespace khác nhau.

**Chương 10, User, Role và Database Security** trước hết xem xét user management: role, group và password. Bạn sẽ học cách giới hạn user chỉ được truy cập các database cụ thể và từ các máy cụ thể, cũng như cách quản lý permission gắn với user và database object. Sau đó, bạn sẽ thấy row-level security có thể tăng cường bảo vệ nội dung table và ngăn user truy xuất hoặc sửa các tuple không thuộc về họ như thế nào.

**Chương 11, Transaction, MVCC, WAL và Checkpoint** trình bày các khái niệm nền tảng trong PostgreSQL: Write-Ahead Log (WAL) và cơ chế cho phép database chạy các transaction đồng thời rồi hợp nhất dữ liệu trong storage. Chương này cũng trình bày khái niệm transaction isolation, các quy tắc ACID và cách database có thể triển khai chúng. Sau đó, bạn sẽ khám phá cách WAL tăng tốc công việc database, đồng thời bảo vệ database khỏi crash. Bạn sẽ hiểu MVCC là gì và tại sao nó quan trọng. Cuối cùng, chương cung cấp thông tin chuyên sâu về checkpoint và các tunable liên quan.

**Chương 12, Mở rộng Database – Extension Ecosystem** giới thiệu một cách thuận tiện để cắm functionality mới vào cluster bằng cách sử dụng cái gọi là “extension”. Chương này sẽ cho bạn biết extension là gì; cách tìm kiếm, lấy và cài đặt extension bên thứ ba; cũng như cách phát triển extension của riêng bạn.

**Chương 13, Query Tuning, Index và Tối ưu Performance** đề cập đến một chủ đề quan trọng đối với mọi database administrator: performance. Index là cách nhanh để giúp database truy cập dữ liệu được sử dụng phổ biến nhất, nhưng không thể xây dựng index trên mọi thứ vì chi phí maintenance của chúng. Chương này trình bày các loại index hiện có, sau đó giải thích cách nhận biết table và query có thể hưởng lợi từ index, cũng như cách triển khai chúng. Nhờ các tool như explain và autoexplain, bạn sẽ kiểm soát được query của mình.

**Chương 14, Logging và Auditing** giải quyết các câu hỏi như “Điều gì đang xảy ra trong database cluster?” và “Hôm qua đã xảy ra chuyện gì?”. Có một ruleset logging và auditing tốt là điểm then chốt trong việc quản trị database cluster. Chương này giới thiệu các option chính cho logging, cách kiểm tra log bằng các utility bên ngoài như pgBadger và cách audit cluster (theo cách có thể giúp bạn tuân thủ các chính sách về quy định dữ liệu, ví dụ GDPR).

**Chương 15, Backup và Restore** giải thích tại sao việc có backup lại quan trọng, cách backup toàn bộ hoặc một phần cluster của bạn và cách restore từ một backup hợp lệ. Chương này trình bày những cách cơ bản và phổ biến nhất để backup một database hoặc toàn bộ cluster, cũng như cách thực hiện archiving và point-in-time recovery.

**Chương 16, Configuration và Monitoring** trình bày các tùy chọn configuration của cluster và các PostgreSQL catalog dùng để kiểm tra hệ thống từ bên trong. Nhiều cách tuning configuration khác nhau sẽ được trình bày. Nhờ các extension đặc biệt như pg_stat_activity, bạn có thể monitoring theo thời gian thực những gì user đang thực hiện trên database.

**Chương 17, Physical Replication** trình bày replication tích hợp sẵn, một cơ chế cho phép bạn giữ nhiều instance hoạt động và đồng bộ với một master node duy nhất, được PostgreSQL hỗ trợ từ version 9. Replication cho phép scalability và redundancy, cũng như nhiều kịch bản khác như test và so sánh database. Chương này trình bày cái gọi là “physical replication”, một cách replicate toàn bộ cluster sang một instance khác, instance này sẽ liên tục theo leader của nó. Cả asynchronous và synchronous replication, cũng như replication slot và delayed replication, đều sẽ được trình bày.

**Chương 18, Logical Replication** trình bày logical replication, cho phép replication rất chi tiết bằng cách chỉ định table nào phải được replicate và table nào không phải, một tính năng được PostgreSQL hỗ trợ từ version 10. Điều này dĩ nhiên tạo ra một kịch bản chia sẻ dữ liệu mới mẻ và phong phú giữa các database instance khác nhau. Chương này trình bày cách logical replication hoạt động, cách thiết lập và cách monitoring replication.

**Chương 19, Tool và Extension hữu ích** nên được xem như một phần phụ lục của cuốn sách. Trong chương này, chúng ta sẽ nói về một số tool và extension cho phép database administrator tối đa hóa khối lượng công việc hoàn thành trong khi giảm thiểu nỗ lực.

## Khai thác tối đa cuốn sách

Để cuốn sách hữu ích, bạn cần có kiến thức cơ bản về operating system Linux (hoặc một operating system tương tự Unix). Tất cả ví dụ SQL có thể chạy bằng command-line program psql hoặc bất kỳ GUI tool nào có sẵn (không được trình bày trong sách), chẳng hạn pgAdmin4 dành riêng cho PostgreSQL. Shell script sẽ được thực thi bằng ngôn ngữ GNU Bash.

| Software/hardware được đề cập trong sách | Yêu cầu OS |
| --- | --- |
| PostgreSQL 16 | Linux OS/Unix-like OS (ví dụ: FreeBSD, OpenBSD) |

Cuốn sách cung cấp một bộ Docker image để người đọc có thể làm theo và kiểm thử tất cả code example. Việc chạy Docker image không bắt buộc, nhưng khi làm vậy, bạn không cần có PostgreSQL installation tùy chỉnh của riêng mình. Để chạy Docker image, bạn cần cài đặt application Docker trên operating system của mình.

Nếu đang sử dụng phiên bản digital của cuốn sách, chúng tôi khuyên bạn nên tự gõ code hoặc truy cập code thông qua GitHub repository (link có sẵn trong section tiếp theo). Làm như vậy sẽ giúp bạn tránh các lỗi tiềm ẩn liên quan đến việc copy và paste code.

## Tải file code example

Code bundle của cuốn sách được lưu trữ trên GitHub tại https://github.com/PacktPublishing/Learn-PostgreSQL-Second-Edition. Chúng tôi cũng có các code bundle khác từ danh mục phong phú gồm sách và video tại https://github.com/PacktPublishing/. Hãy ghé xem!

## Tải ảnh màu

Chúng tôi cũng cung cấp một file PDF chứa ảnh màu của các screenshot/diagram được sử dụng trong cuốn sách. Bạn có thể tải file tại đây: https://packt.link/gbp/9781837635641.
