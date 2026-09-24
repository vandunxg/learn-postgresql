```text
LOG: redo done at 0/2000138 system usage: CPU: user: 0.00 s, system: 0.00
s, elapsed: 0.00 s
LOG:   database system is ready to accept connections
done
server started
```

Ở đây, server đã được khởi động trên directory `PGDATA` đã clone và TCP/IP port 5433. Nếu inspect log của database cluster, bạn sẽ thấy PostgreSQL cho biết nó đã bị gián đoạn, một redo process đã bắt đầu rồi hoàn tất. Khi redo hoàn tất, database sẵn sàng bắt đầu hoạt động bình thường. Nói ngắn gọn, đây là tình huống giống crash: physical dump đã copy một trạng thái “dirty” của database, nhưng nhờ WAL, nó có thể tự self-heal.

Bạn sẽ thấy database đã được restore từ một “forced crash”; nghĩa là cloned cluster đã tự self-heal trong lần startup đầu tiên.

## Khôi phục từ physical backup

Nếu cần restore từ một physical backup, bạn phải ghi đè directory `PGDATA` ban đầu bằng bản copy đã clone do `pg_basebackup` tạo ra. Đây là một operation rất rủi ro vì bạn sẽ mất toàn bộ content của directory `PGDATA` và thay thế nó bằng bản backup, đồng nghĩa với việc nguy cơ xảy ra lỗi rất cao.

Vì lý do đó, thay vì thực hiện online restoration, chúng tôi đề xuất bạn start một cloned cluster ở nơi khác, như đã trình bày trong section trước, để extract data cần recover rồi chỉ restore data đó trên target cluster. Chẳng hạn, bạn có thể start cloned server, extract data cần recover bằng `pg_dump`, rồi restore nó trên target cluster.

Dĩ nhiên, có những tình huống bạn cần recover toàn bộ cluster và do đó phải ghi đè `PGDATA`, nhưng ngay cả trong những trường hợp đó, chúng tôi đề xuất sử dụng các tool advanced hơn như `pgBackRest`, tool sẽ điều phối và hỗ trợ cả phần backup lẫn restore.

Physical backup và restoration là những mechanism rất mạnh, nhưng yêu cầu bạn phải hiểu sâu những gì diễn ra bên dưới. Vì vậy, hãy dành thời gian experiment với chúng một cách cẩn thận để sẵn sàng áp dụng trong production.

## Các khái niệm cơ bản đằng sau PITR

Point in Time Recovery, thường được viết là PITR, là một kỹ thuật cho phép bạn restore database về một thời điểm cụ thể trong quá khứ. Việc trình bày cách sử dụng PITR nằm ngoài scope của chapter này; section này chỉ giải thích các khái niệm cơ bản đằng sau kỹ thuật đó.

PITR chỉ có thể đạt được bằng physical backup, và thường được thực hiện thông qua các backup tool cụ thể như `pgBackRest` đã đề cập, mặc dù PostgreSQL cung cấp toàn bộ infrastructure cần thiết để thực hiện PITR.

Ý tưởng chính phía sau PITR là bắt đầu bằng một physical backup rồi liên tục lưu các WAL segment của database, một process được gọi là *WAL archiving*. Các WAL có thể được lưu local hoặc gửi tới một remote machine, thường là một backup machine chuyên dụng. Việc phải archive toàn bộ WAL là vì, như đã giải thích trong Chapter 11, PostgreSQL recycle WAL sau khi data đã sửa được lưu an toàn trên disk; do đó, để có một stream WAL liên tục, administrator cần giữ lại tất cả chúng. PostgreSQL cung cấp một configuration setting cụ thể tên là `archive_command`, có thể được điều chỉnh để execute một external command (ví dụ các command copy như `cp`, `scp`, `sftp`, v.v.); `archive_command` được execute trên từng WAL segment ngay khi PostgreSQL hoàn tất WAL file đó và chuyển sang segment mới.

Khi có physical backup và stream WAL, database cluster có thể được chỉ thị replay tất cả transaction (được chứa trong WAL) lần lượt cho đến khi đạt đến restore time mong muốn. Tại thời điểm đó, cluster có thể bỏ qua các WAL vượt quá thời điểm này và bắt đầu từ đó như một instance riêng, mới.

Vì vậy, ý tưởng của PITR là bắt đầu từ một physical backup và để cluster tiến về phía trước theo thời gian cho đến khi đạt đến instance mong muốn. Point of restoration có thể được chỉ định dưới dạng timestamp, qua đó chỉ ra một time instance cụ thể, hoặc một transaction identifier; thậm chí có thể là một label mà database administrator đã đặt vào WAL, để họ không phải bận tâm đến thời gian hay các transaction đang diễn ra.

Một nhược điểm của PITR là cần thời gian và effort để restore cluster về một thời điểm nhất định. Hơn nữa, nếu thiếu dù chỉ một WAL segment trong stream, cluster sẽ hoàn toàn không thể recover. Vì lý do đó, sử dụng các dedicated backup tool thường là lựa chọn tốt nhất để quản lý PITR.

## Tóm tắt

Trong chapter này, chúng ta đã học rằng PostgreSQL cung cấp các tool advanced để thực hiện backup và restoration. Backup rất quan trọng vì ngay cả trong một product battle-tested, chất lượng cao như PostgreSQL, mọi thứ vẫn có thể xảy ra sai: thường thì user có thể vô tình làm hỏng data, nhưng đôi khi hardware hoặc software có thể fail nghiêm trọng. Vì vậy, khả năng restore data, một phần hoặc toàn bộ, là rất quan trọng, và mọi database administrator đều nên lập kế hoạch backup strategy một cách cẩn thận.

Chúng ta cũng đã học rằng PostgreSQL đi kèm các tool cho cả logical backup và physical backup. Logical backup được thực hiện bằng cách đọc data từ chính database, sử dụng các SQL interaction thông thường; physical backup được thực hiện bằng cách clone directory `PGDATA`, bằng operating system tool hoặc PostgreSQL ad hoc solution. Restoration được thực hiện bằng các tool cụ thể trong trường hợp logical backup, và bằng database self-healing mechanism trong trường hợp physical backup.

Cuối cùng, cần nhấn mạnh rằng một backup riêng lẻ chưa có giá trị cho đến khi được restore thành công; do đó, để bảo đảm bạn có thể recover cluster, bạn cũng cần test các backup của mình.

Sau khi đã có thể backup và restore cluster, trong chapter tiếp theo, chúng ta sẽ xem xét configuration và monitoring.

## Kiểm tra kiến thức

- **Sự khác nhau giữa logical backup và physical backup là gì?**

  Logical backup, còn được gọi là “dump”, là một backup tương tác trực tiếp với database và các transaction đang chạy của nó. Physical backup, còn được gọi là “hot backup”, là một bản copy của underlying filesystem và WAL để có thể restore clear state cuối cùng đã biết của database. Xem section *Giới thiệu các loại backup và restore* để biết thêm chi tiết.

- **Sự khác nhau giữa `pg_dump` và `pg_dumpall` là gì?**

  Command `pg_dump` được dùng để dump một database đơn lẻ, trong khi `pg_dumpall` dump tất cả intra-database object (ví dụ user), sau đó thực hiện một `pg_dump` trên từng database trong cluster. Xem section *Dumping a whole cluster* để biết thêm chi tiết.

- **Command `COPY` là gì?**

  Command `COPY` là một statement đặc thù của PostgreSQL, nhằm bulk-load hoặc extract data. Nó thường được dùng như một cách để dump/restore data từ một table. Xem section *The COPY command* để biết thêm chi tiết.

- **Command `pg_basebackup` là gì?**

  Command `pg_basebackup` thực hiện physical backup của một cluster đang chạy và cũng có thể archive WAL. Xem section *Performing a manual physical backup* để biết thêm chi tiết.

- **Point in Time Recovery (PITR) là gì?**

  PITR là một kỹ thuật theo đó một physical backup được restore về một point in time cụ thể sau khi backup bắt đầu. Đây là một cách đưa cluster *back in time*. Xem section *Basic concepts behind PITR* để biết thêm chi tiết.

## Tài liệu tham khảo

- Tài liệu chính thức về tool `pg_dump` của PostgreSQL: https://www.postgresql.org/docs/current/app-pgdump.html
- Tài liệu chính thức về tool `pg_dumpall` của PostgreSQL: https://www.postgresql.org/docs/current/app-pg-dumpall.html
- Tài liệu chính thức về tool `pg_restore` của PostgreSQL: https://www.postgresql.org/docs/current/app-pgrestore.html
- FreeBSD `502.pgsql` backup script: https://www.freshports.org/databases/postgresql83-server/files/502.pgsql
- Tài liệu chính thức về tool `pg_basebackup` của PostgreSQL: https://www.postgresql.org/docs/current/app-pgbasebackup.html
- Tài liệu chính thức về tool `pg_verifybackup` của PostgreSQL: https://www.postgresql.org/docs/current/app-pgverifybackup.html
- Tài liệu chính thức về command `COPY` của PostgreSQL: https://www.postgresql.org/docs/current/sql-copy.html
- External tool `pgBackRest` cho physical backup: https://pgbackrest.org/

## Tìm hiểu thêm trên Discord

Để tham gia Discord community của cuốn sách này, nơi bạn có thể chia sẻ feedback, đặt câu hỏi cho tác giả và tìm hiểu về các bản phát hành mới, hãy theo QR code bên dưới:

https://discord.gg/jYWCjF6Tku

![Mã QR Discord](../assets/part-061-qr-discord.png)

# 16. Configuration and Monitoring

Một trong những nhiệm vụ của database administrator là configure cluster để nó hoạt động tốt với workload và context hiện tại. Configuration không static: phần lớn thời gian, bạn sẽ thấy mình đang thực hiện các thay đổi đối với configuration, vì vậy điều quan trọng là bạn cảm thấy thoải mái khi inspect và thay đổi configuration của cluster.

Một task quan trọng khác, có liên quan một phần đến configuration, là monitoring cluster để hiểu hệ thống thực sự đang hoạt động như thế nào và có bottleneck hay problem nào cần giải quyết hay không. Những problem như vậy đôi khi có thể được giải quyết bằng cách thay đổi configuration của cluster, sử dụng hardware khác (ví dụ tăng memory khả dụng), và sửa các application có thể đang gây bottleneck.

Chapter này sẽ chỉ cho bạn cách quản lý và inspect cluster configuration, generate configuration từ đầu, tìm error và mistake trong configuration hiện tại, cũng như interactively monitor activity của cluster thông qua rich statistics subsystem. Cuối cùng, bạn sẽ khám phá một extension rất mạnh và thường được sử dụng tên là `pg_stat_statements`, cho phép bạn monitor activity của cluster với mức độ chi tiết và flexibility cao.

Chapter này sẽ bao quát các chủ đề sau:

- Cluster configuration
- Monitoring cluster
- Advanced statistics với `pg_stat_statements`

Bắt đầu thôi!

## Technical requirements

Bạn cần biết những nội dung sau để hoàn thành chapter này:

- Cách tương tác với configuration file bên trong directory `PGDATA`
- Cách connect tới cluster với tư cách database administrator
- Cách execute SQL statement trên system catalog

Các example trong chapter có thể chạy trên Docker image `chapter_16`, có thể tìm thấy trong GitHub repository của cuốn sách: https://github.com/PacktPublishing/Learn-PostgreSQL-Second-Edition.

## Cấu hình cluster

PostgreSQL được configure thông qua một nhóm text file chứa directive và value được dùng để bootstrap cluster và làm cho nó hoạt động. Chúng ta đã thấy cách configuration file được xử lý xuyên suốt cuốn sách, nhưng trong chapter này, chúng ta sẽ giải thích chi tiết cách configuration được quản lý.

Có ba configuration file chính tạo thành *starting point* cho mọi configuration:

- `postgresql.conf` là main cluster configuration file, chứa toàn bộ data cần thiết để start cluster, setup process (chẳng hạn WAL sender) và logging, cũng như configure cách cluster accept connection (ví dụ trên TCP/IP address nào).
- `postgresql.auto.conf` là file được chính cluster tự động generate và edit, chứa các parameter được superuser thay đổi từ bên trong cluster. Bạn không bao giờ nên edit file này thủ công, nhưng có thể inspect nó bằng text editor để đọc content.
- `pg_hba.conf` là file được dùng để allow hoặc deny client connection tới cluster. File này đã được giải thích rộng rãi trong Chapter 3, *Managing Users and Connections*, và liên quan đến user cùng role authentication mechanism.

Thông thường, cả hai file nói trên đều nằm trong directory `PGDATA`, nơi chứa toàn bộ data của cluster, nhưng một số operating system có thể đặt chúng trong directory khác; ví dụ, Debian GNU Linux thường đặt chúng trong `/etc/postgresql`.

> Trong các Docker image của cuốn sách, các configuration file được giữ bên dưới directory `PGDATA`, tức là trong `/postgres/16/data`.

Có những configuration file khác thường được giữ trong directory `PGDATA`, nhưng chúng sẽ không được thảo luận ở đây. Section này chủ yếu dành cho `postgresql.conf`, configuration file mặc định.

File `postgresql.conf` là một text file, thường có các comment hữu ích, chứa một tập configuration parameter. Mỗi parameter được biểu diễn dưới dạng `key = value`, trong đó key là tên configuration parameter và value là configuration value của parameter đó. Chúng ta đã thấy một số configuration parameter trong các chapter trước. Ví dụ, configuration parameter `max_wal_senders = 2` đặt configuration parameter `max_wal_senders` thành value 2.

Mỗi configuration parameter phải nằm trên một dòng riêng, và mọi dòng bắt đầu bằng dấu `#` đều là comment, không được cluster tính đến. Comment hữu ích vì cho phép bạn thêm thông tin về ý định của mình đối với một configuration cụ thể. Ví dụ, hãy xem code snippet sau:

```text
# set to 2 to allow pg_basebackup to work properly
max_wal_senders = 2
```

Ví dụ trước cung cấp một gợi ý rõ ràng về lý do parameter được configure như vậy. Bạn không bắt buộc phải đặt comment trong configuration file, nhưng document việc bạn đang làm và lý do thực hiện là một thói quen rất tốt.

Một parameter có thể được định nghĩa nhiều lần; trong trường hợp đó, definition cuối cùng được tìm thấy là definition PostgreSQL sử dụng.

Nếu không muốn configure một parameter cụ thể, bạn có thể xóa dòng của parameter đó, khiến nó biến mất hoàn toàn khỏi configuration file, hoặc đặt dấu comment phía trước nó, biến dòng đó thành một comment thuần túy. Điều quan trọng cần lưu ý là nếu một parameter không được configure trong file vì nó bị thiếu hoặc đã bị comment out, thì nó sẽ nhận default value. Mọi parameter đều có default value, và bạn phải xem documentation để hiểu từng default value; tuy nhiên, một default installation configuration file chứa tất cả parameter khả dụng cùng các comment giải thích cách sử dụng và default setting của chúng.

Mỗi configuration parameter chỉ chấp nhận một tập value cụ thể, phụ thuộc vào type của chính configuration parameter đó. Chủ yếu, bạn sẽ gặp numeric value, string value và list (phân tách bằng dấu phẩy); ngoài ra còn có value được biểu diễn cùng measurement unit, chẳng hạn time như `2ms` (2 milliseconds), hoặc size như `2GB` (2 gigabytes).

## Kiểm tra tất cả configuration parameter

Bạn có thể inspect tất cả configuration parameter từ một live system bằng cách issue một query trên special catalog `pg_settings`. Catalog này chứa mọi setting mà version PostgreSQL hiện tại chấp nhận, cùng với default value, current value, mô tả mục đích của parameter và nhiều thông tin khác.

Ví dụ, với query sau, bạn có thể thu thập thông tin về mọi configuration parameter, bao gồm short description và long description, default value và current value:

```text
forumdb=> SELECT name, setting || ' ' || unit AS current_value, short_
desc, extra_desc, min_val, max_val, boot_val, reset_val FROM pg_settings;
...
name           | authentication_timeout
current_value | 360 s
short_desc    | Sets the maximum allowed time to complete client
authentication.
extra_desc     |
min_val        | 1
max_val        | 600
boot_val       | 60
reset_val      | 360
```

Trong ví dụ trên, `authentication_timeout` đã được set thành 360 giây, như cột `setting` chỉ ra, và value của nó có thể được tune trong khoảng từ 1 giây đến 600 giây; `boot_val` là default value mà parameter sẽ nhận nếu hoàn toàn không được configure, và được đặt thành 60 giây. Tương tự, column `reset_val` cho biết value parameter sẽ nhận nếu được reset sau một thay đổi.

Special catalog `pg_settings` cũng chứa các thông tin hữu ích khác, bao gồm file và line number nơi parameter được load. Thông tin này có thể được dùng để nhanh chóng tìm nơi một configuration parameter được set trong file `postgresql.conf` hoặc configuration file khác. Ví dụ, query sau sẽ cho biết từng parameter được load từ đâu:

```text
forumdb=# SELECT name, setting AS current_value, sourcefile, sourceline,
pending_restart FROM pg_settings;
...
name               | log_destination
current_value       | stderr
sourcefile          | /postgres/16/data/postgresql.auto.conf
sourceline          | 4
pending_restart | f
```

Như bạn có thể thấy trong installation example này, configuration parameter `log_destination` đã được load từ file `/postgres/16/data/postgresql.auto.conf`. Đây không phải file `postgresql.conf` chính; đó là file được PostgreSQL tự động generate để xử lý các configuration parameter được thay đổi từ bên trong cluster. Cách sử dụng `postgresql.auto.conf` sẽ trở nên rõ ràng hơn ở phần sau của chapter này; hiện tại, chỉ cần biết rằng một configuration parameter đã được load từ file khác và `pg_settings` báo cáo rõ điều đó.

> Bạn cần có database superuser rights để thu thập thông tin bổ sung, chẳng hạn file location và line number.

Còn một thông tin quan trọng khác có thể lấy được từ special catalog `pg_settings`: điều gì xảy ra nếu một parameter được thay đổi tại runtime? Tùy vào bản chất của parameter, thay đổi có thể được áp dụng ngay lập tức, hoặc bị trì hoãn trong khi chờ một event đặc biệt hay thậm chí một cluster restart. Column `pending_restart` cho biết parameter hiện tại đã thay đổi so với boot-time value hay chưa và value đó đã được áp dụng vào cluster hay chưa. Trong ví dụ trước, `pending_restart` là false, vì vậy configuration bạn đang thấy thực sự là configuration đang chạy trên cluster ngay lúc này.

Querying `pg_settings` cung cấp mọi thông tin cần thiết để hiểu status của configuration hiện tại, nhưng có một shortcut để lấy setting của parameter nhanh hơn: command `SHOW`. Special command `SHOW` chấp nhận tên của một parameter và trả về value của parameter đó dưới dạng human-understandable. Ví dụ, hãy tưởng tượng chúng ta muốn inspect memory value `shared_buffers`:

```text
forumdb=> SHOW shared_buffers ;
shared_buffers
----------------
128MB
(1 row)
```
