## Kiểm tra kiến thức

- Tôi có phải configure file `pg_hba.conf` trước khi bắt đầu physical replication không?

  Có.

  Xem section *Managing streaming replication* để biết thêm chi tiết.

- PostgreSQL có cho phép thực hiện asynchronous replication không?

  Có, đây là configuration mặc định.

  Xem section *Managing streaming replication* để biết thêm chi tiết.

- PostgreSQL có cho phép thực hiện synchronous replication không?

  Có, bằng cách sửa `postgresql.conf` trên primary server và `postgresql.auto.conf` trên replica server.

  Xem section *Synchronous replication* để biết thêm chi tiết.

- PostgreSQL có cho phép thực hiện cascading replication không?

  Có, bằng cách sử dụng command `pg_basebackup` lấy data từ replica server.

  Xem section *Cascading replication* để biết thêm chi tiết.

- Có thể promote một replica node thành primary node không?

  Có, bằng cách sử dụng command `pg_ctl promote`.

  Xem section *Promoting a replica server to a primary* để biết thêm chi tiết.

## Tài liệu tham khảo

- Tài liệu chính thức về thiết lập Wal level: https://www.postgresql.org/docs/current/runtime-config-wal.html#GUC-WAL-LEVEL
- Tài liệu chính thức về command `pg_basebackup`: https://www.postgresql.org/docs/current/app-pgbasebackup.html
- Tài liệu chính thức về replica monitoring: https://www.postgresql.org/docs/current/monitoring-stats.html#PG-STAT-REPLICATION-VIEW
- Tài liệu chính thức về replica configuration: https://www.postgresql.org/docs/current/runtime-config-replication.html
- Tài liệu chính thức về High Availability, Load Balancing, and Replication: https://www.postgresql.org/docs/current/high-availability.html

## Tìm hiểu thêm trên Discord

Để tham gia Discord community của cuốn sách này — nơi bạn có thể chia sẻ feedback, đặt câu hỏi cho tác giả và tìm hiểu về các bản phát hành mới — hãy theo QR code bên dưới:

https://discord.gg/jYWCjF6Tku

# 18. Logical Replication

Trong chapter trước, chúng ta đã nói về WAL segments và physical replication ở các mode synchronous, asynchronous và cascading. Trong chapter này, chúng ta sẽ đề cập đến logical replication. Chúng ta sẽ xem cách thực hiện một logical replica, logical replication khác physical replication như thế nào và khi nào nên dùng logical replication thay vì physical replication. Chúng ta cũng sẽ thấy logical replication có thể được dùng để thực hiện PostgreSQL hot upgrade. Chapter này nhằm giới thiệu về logical replication; để biết thêm thông tin, hãy tham khảo các tài liệu nâng cao hơn, chẳng hạn *Mastering PostgreSQL* của Hans-Jürgen Schönig.

Chapter này bao gồm các chủ đề sau:

- Tìm hiểu các concept cơ bản của logical replication
- So sánh logical replication và physical replication
- Khám phá một logical replication setup và các feature logical replication mới trên PostgreSQL 16

## Technical requirements

Đối với chapter này, repository có ba Docker environment:

- `chapter18_logical_clear`: chứa hai PostgreSQL installation đã sẵn sàng để configure một logical replication mới.
- `chapter18_logical_ready`: chứa hai PostgreSQL installation với một logical replication mới đã active.
- `chapter18_physical_logical`: chứa ba PostgreSQL installation với một logical replication mới được tạo bằng physical replication.

Nếu muốn hiểu cách configure một logical replication mới, bạn nên sử dụng Docker environment đầu tiên; tuy nhiên, nếu muốn bỏ qua toàn bộ các chủ đề về configuration, bạn có thể sử dụng environment thứ hai. Trong Docker environment thứ hai, nằm trên publication server, bạn sẽ tìm thấy database `forumdb` mà chúng ta đã sử dụng trong suốt cuốn sách; bạn cũng sẽ tìm thấy một logical replication chỉ của table `users`. Cuối cùng, Docker environment `chapter18_physical_logical` sẽ được dùng cho section cuối của chapter này.

## Tìm hiểu các concept cơ bản của logical replication

Logical replication là một method mà chúng ta có thể dùng để replicate data dựa trên concept `identity replication`. `REPLICA IDENTITY` là một parameter có trong các table management command (chẳng hạn `CREATE TABLE` và `ALTER TABLE`); PostgreSQL sử dụng parameter này để lấy thêm thông tin bên trong WAL segments, nhằm nhận biết tuple nào đã bị xóa và tuple nào đã được update. Parameter `REPLICA IDENTITY` có thể nhận bốn value:

- `DEFAULT`
- `USING INDEX index_name`
- `FULL`
- `NOTHING`

Concept đằng sau logical replication là chuyển logic của các command được thực thi trên primary machine tới server, chứ không phải bản copy chính xác của các block cần replicate, byte theo byte. Ở trung tâm của logical replication là một reverse engineering process; bắt đầu từ các WAL segments và sử dụng logical decoding process, process này có thể suy ra các SQL command ban đầu rồi chuyển chúng tới replication machine, cũng bằng logical decoding process.

Hãy xem flow chart cho thấy PostgreSQL thực thi query nội bộ như thế nào:

![Hình 18.1: Minh họa backend process](../assets/part-067-figure-18-1-000.jpg)

*Hình 18.1: Minh họa backend process*

Như có thể thấy, trước khi được execute, một query cần trải qua một số bước nội bộ; nguyên nhân là system cố gắng execute query theo cách tốt nhất có thể, dựa trên các điều kiện đang tồn tại trong database tại thời điểm đó. Bây giờ, giả sử chúng ta muốn replicate data theo cách logical; lúc này, chúng ta có hai khả năng:

- Chúng ta có thể capture các command trước khi chúng đến parser rồi chuyển các command này tới một machine thứ hai.
- Chúng ta có thể tìm cách lấy các query đã được parse.

Method đầu tiên được triển khai bởi các system dựa trên trigger, được thiết kế trước khi có native logical replication; một ví dụ về application của method này có thể tìm thấy ở Slony (https://www.slony.info/).

Method thứ hai được sử dụng trong logical replication.

Trong logical replication, chúng ta sẽ lấy các command cần gửi tới replica server từ bên trong WAL segments. Vấn đề là trong WAL segments, data được biểu diễn theo dạng physical. Nói cách khác, trong WAL segments, data đã sẵn sàng để được gửi hoặc archive nhằm tạo ra các bản copy physical, chứ không phải logical.

Logical replication dựa trên concept rằng các WAL segments, sau khi được xử lý qua một logical decoding process đảo ngược thông tin physical thành thông tin logical, sẽ được cung cấp thông qua một publication mechanism. Sau đó, primary sẽ bắt đầu một publication process, còn replica sẽ bắt đầu một subscription process; bằng cách connect tới publication của primary, process này có thể chuyển các instruction đã decode trực tiếp tới query executor của replica machine.

![Hình 18.2: Sơ đồ logical replication](../assets/part-067-figure-18-2-000.jpg)

*Hình 18.2: Sơ đồ logical replication*

Như có thể thấy từ diagram, bằng cách sử dụng một reverse engineering process, các instruction được lấy ra từ WAL segments; các instruction này đã sẵn sàng để được executor của replica server xử lý mà không cần parsing action nào. Method thứ hai này nhanh hơn nhiều so với method đầu tiên. Method đầu tiên là method duy nhất có sẵn trong các PostgreSQL version trước 9.4; từ 9.4 trở đi, có một extension tên là `pglogical`, và kể từ version 10.0, logical replica đã trở thành native.

## So sánh logical replication và physical replication

Bây giờ hãy xem logical replica khác physical replica như thế nào:

- Một đặc điểm tích cực của physical replica là tốc độ. Tuy nhiên, một bất lợi đáng kể là chúng ta phải replicate tất cả database trong cluster. Khi sử dụng physical replica, không thể replicate một database riêng lẻ thuộc về một PostgreSQL instance, và cũng không thể chỉ replicate một số table của một database. Logical replication chậm hơn physical replication một chút, nhưng khi dùng logical replication, chúng ta có thể quyết định muốn replicate database nào trong một cluster và/hoặc muốn replicate table nào trong một database riêng lẻ.
- Physical replication chỉ khả thi nếu hai server có cùng PostgreSQL version. Với logical replication, vì logical instruction cần execute được chuyển tới replica server, cũng có thể thực hiện replication giữa các PostgreSQL version khác nhau.
- Trong physical replication, ngoại trừ các operation trên temporary và unlogged table, mọi operation đều được replicate. Trong logical replication, chỉ các operation thuộc data manipulation language (DML) được replicate; các operation thuộc data definition language (DDL), chẳng hạn operation `ALTER` và `TABLE`, thì không được replicate.
- Physical replication, theo định nghĩa, tạo ra một bản copy physical; nó replicate dưới dạng binary toàn bộ content của primary server đi qua WAL tới replica. Ngược lại, logical replication chỉ replicate các instruction, tức các statement mà chúng ta gửi cho replica server.
- Physical replication, ngoại trừ unlogged table, tạo ra trên replica server một bản copy giống hệt primary. Physical replication copy tuyệt đối mọi thứ; do bản copy là physical ở page level, chúng ta không chỉ copy data mà còn copy mọi bloat đi kèm. Đôi khi điều này hữu ích, chẳng hạn khi muốn mô phỏng behavior chính xác của production server trong test environment.
- Tuy nhiên, thông qua một reverse engineering mechanism, logical replication chuyển các query cần execute trực tiếp tới query executor của replica machine. Ví dụ, nếu muốn có một bản copy database bắt đầu với tỷ lệ bloat thấp, chúng ta có thể thực hiện logical replica trên machine thứ hai, và machine thứ hai sẽ bắt đầu từ một starting point rất sạch. Điều này xảy ra vì toàn bộ data được chuyển tới server thứ hai theo cách không physical mà là logical. Ngoài ra, theo cách này có thể replicate data giữa các PostgreSQL server khác version.

> **Lưu ý:** Vì có thể thực hiện replication giữa các version khác nhau của PostgreSQL, logical replication là một tool có thể dùng để thực hiện PostgreSQL hot upgrade.

## Khám phá một logical replication setup và các feature logical replication mới trên PostgreSQL 16

Bây giờ hãy khám phá cách thực hiện logical replication. Trong section này, chúng ta sẽ chuẩn bị environment cần thiết để có thể thực hiện logical replication.

### Thiết lập môi trường logical replication

Giả sử chúng ta có hai machine, gọi là `pg_pub` và `pg_sub`. Cần nhớ thiết lập internal DNS hoặc file `/etc hosts` để `pg_pub` có thể reach `pg_sub`; ví dụ, đối với server `pg_pub`, primary server sẽ có IP `192.168.144.3`, còn đối với server `pg_sub`, replica server sẽ có IP `192.168.144.2`. Nếu sử dụng container `chapter18`, bạn có thể execute:

```text
chapter_18$ bash run-pg-docker.sh chapter18_logical_clear
```

Sau khi vào container đầu tiên, bạn có thể mở một bash terminal khác và execute:

```text
chapter_18$ bash run-pg-docker_replica.sh chapter18_logical_clear
```

Bây giờ hãy kiểm tra xem có connection giữa hai server hay không:

```text
postgres@pg_pub:~$ ping pg_sub
PING pg_sub (192.168.144.3) 56(84) bytes of data.
64 bytes from chapter18_logical_clear_learn_postgresql_sub_1.chapter18_
logical_clear_default (192.168.144.3): icmp_seq=1 ttl=64 time=0.094 ms


postgres@pg_sub:~$ ping pg_pub
PING pg_pub (192.168.144.2) 56(84) bytes of data.
64 bytes from chapter18_logical_clear_learn_postgresql_pub_1.chapter18_
logical_clear_default (192.168.144.2): icmp_seq=1 ttl=64 time=0.070 ms
```

Như minh họa ở đây, có connection giữa hai server.

### Replica role

Để thực hiện logical replication, cũng như chúng ta đã làm trong chapter trước khi nói về physical replication, cần có một database user với replication permissions. Vì vậy, hãy tạo user sau trên publication server:

```text
postgres=# CREATE USER replicarole WITH REPLICATION ENCRYPTED PASSWORD
'LearnPostgreSQL';
CREATE ROLE
```

User này sẽ được dùng để quản lý logical replication.

### Primary server – postgresql.conf

Bây giờ chúng ta sẽ sửa file `postgresql.conf` trên cả hai server; mục đích là bảo đảm hai server listen trên port 5432 cho các network interface. Sau đó, chúng ta sẽ sửa một số value khác để cố gắng tối ưu logical replication procedure:

1. Trước tiên, thêm các line sau vào cuối file `postgresql.conf` trên publication server:

   ```text
   # Add settings for extensions here
   listen_addresses = '*'
   wal_level = logical
   max_wal_senders = 10
   ```

Bây giờ hãy xem lần lượt từng parameter:

- `listen addresses = '*'`: Theo cách này, PostgreSQL sẽ listen trên port 5432 ở tất cả network interface. Chúng ta cũng có thể chỉ cần thêm IP address của interface nơi muốn PostgreSQL service listen.
- `wal level = logical`: Chúng ta đã đổi value từ `replica` (mặc định) thành `logical`; theo cách này, ngoài toàn bộ thông tin có trong model `wal level = replica`, PostgreSQL sẽ thêm thông tin để có thể thực hiện reverse engineering process. Với `wal level = logical`, chúng ta bật khả năng logical replication.
- `max_replication_slots = 10`: Value này phải được đặt ít nhất là một cho mỗi subscriber, cộng thêm số slot cần thiết để initialize các table.
- `max_wal_senders = 10`: Value này phải được đặt thành một số ít nhất bằng một cho mỗi replication slot, cộng thêm số cần thiết cho physical replication.
