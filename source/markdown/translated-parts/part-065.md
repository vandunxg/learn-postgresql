Trong chương này, khi nói về cách cài đặt một hệ thống replication, chúng ta sẽ không sử dụng Docker container; lý do là để cài đặt một replication service, cần tắt postgresql service trên replica server, và việc tắt một service trong môi trường Docker sẽ tắt toàn bộ container. Tuy nhiên, trên Docker, việc tắt postgresql và khởi động lại nó cùng lúc có thể được thực hiện khi Docker container khởi động lần đầu, vì vậy để hiểu rõ hơn cách cài đặt một replica trên production server, tốt hơn là không sử dụng Docker container (ngay cả khi trong GitLab repo có một số container mà bạn có thể sử dụng). Trong chương này, Docker chỉ được dùng để hỗ trợ người đọc không muốn cài đặt một replica server nhưng muốn tìm hiểu bằng cách xem physical replication hoạt động như thế nào; đối với mọi nội dung liên quan đến phần cài đặt, chúng ta sẽ tham chiếu đến các path của Debian server thay vì các path của Docker image.

## Yêu cầu kỹ thuật

Trong Learn PostgreSQL GitHub repository, bạn có thể tìm thấy ba Docker image:

- `chapter17_streaming`: replication bất đồng bộ Primary/replica; nếu muốn sử dụng replica container sau khi khởi động container bằng:

  ```text
  chapter_17$ bash run-pg-docker.sh chapter17_streaming
  ```

  bạn phải chạy:

  ```text
  chapter_17$ bash run-pg-docker_replica.sh chapter17_streaming
  ```

- **`chapter17_synchronous`**: replication đồng bộ Primary/replica; nếu muốn sử dụng replica container sau khi khởi động container bằng:

  ```text
  chapter_17$ bash run-pg-docker.sh chapter17_synchronous
  ```

  bạn phải chạy:

  ```text
  chapter_17$ bash run-pg-docker_replica.sh chapter17_synchronous
  ```

- **`chapter17_delayed`**: Primary/replica với replication delayed; nếu muốn sử dụng replica container sau khi khởi động container bằng:

  ```text
  chapter_17$ bash run-pg-docker.sh chapter17_delayed
  ```

  bạn phải chạy:

  ```text
  chapter_17$ bash run-pg-docker_replica.sh chapter17_delayed
  ```

Tất cả replica container đều bị dừng khi chúng ta thoát khỏi primary container.

Trong chương này, chúng ta sẽ đề cập đến các chủ đề sau:

- Khám phá các khái niệm cơ bản về replication
- Quản lý streaming replication

## Khám phá các khái niệm cơ bản về replication

Trong PostgreSQL có hai loại kỹ thuật physical replication:

- **Asynchronous replication:** Trong asynchronous replication, primary device (source) gửi một luồng data liên tục đến secondary device (target) mà không nhận bất kỳ return code nào từ target. Kiểu copying này có ưu điểm về tốc độ, nhưng đi kèm rủi ro mất data cao hơn vì data nhận được không được acknowledge.
- **Synchronous replication:** Trong synchronous replication, một source gửi data đến một target, tức server thứ hai; tại thời điểm này, server xác nhận rằng các thay đổi đã được ghi chính xác. Nếu việc kiểm tra thành công, quá trình truyền hoàn tất.

Cả hai method đều có ưu điểm và nhược điểm, và chúng ta sẽ phân tích chúng trong section Managing streaming replication của chương này.

## Physical replication và WAL

Hãy tóm tắt ngắn gọn những gì chúng ta đã đề cập về MVCC và WAL segment: chúng ta đã thấy PostgreSQL lưu data trên disk bằng WAL segment như thế nào, và như đã thấy trong Chapter 11, Transactions, MVCC, WAL, and Checkpoints, WAL segment chủ yếu được sử dụng khi xảy ra crash. Sau một crash, PostgreSQL truy lại các WAL segment và áp dụng lại chúng vào data, bắt đầu từ checkpoint gần nhất; trong thời gian recovery sau crash, server chuyển sang recovery state.

Dưới đây là phần tóm tắt những thông tin chính về WAL segment:

- WAL có size cố định là 16 MB.
- Theo mặc định, WAL file bị xóa ngay khi cũ hơn checkpoint mới nhất.
- Chúng ta có thể duy trì thêm WAL segment bằng `wal_keep_segments`.
- WAL segment được lưu trong `pg_wal` directory như sau:

  ```text
  postgres@pg2:~/16/main/pg_wal$ ls -alh
  total 17M
  drwx------    3 postgres postgres 4.0K May 22 09:52 .
  drwx------ 19 postgres postgres 4.0K May 22 10:18 ..
  -rw-------    1 postgres postgres          16M May 22 10:18
  000000010000000000000001
  drwx------    2 postgres postgres 4.0K May 22 09:52 archive_status
  ```

## Chỉ thị wal_level

Chỉ thị `wal_level` thiết lập loại thông tin sẽ được lưu trong WAL segment. Giá trị mặc định là `minimal`. Với giá trị này, mọi thông tin được lưu trong một WAL segment đều có thể hỗ trợ archiving và physical replication.

Để biết thêm thông tin, xem https://www.postgresql.org/docs/current/runtime-config-wal.html#GUC-WAL-LEVEL.

Vì vậy, trong chương này, chúng ta sẽ sử dụng giá trị `wal_level=replica`, vốn là giá trị mặc định, còn trong chapter tiếp theo, chúng ta sẽ sử dụng `wal_level=logical`. Cần nhớ rằng phải restart PostgreSQL server mỗi khi thay đổi parameter `wal_level`.

## Chuẩn bị setup môi trường cho streaming replication

Trong section này, chúng ta sẽ chuẩn bị hai server cần thiết để tiếp tục: máy thứ nhất là primary server, máy thứ hai là replica server. Vì vậy, hãy tiến hành cài đặt hai virtual machine. Trong các ví dụ sau, chúng ta sẽ sử dụng hai Debian Linux virtual machine, với 192.168.122.10 là IP của primary server và 192.168.122.11 là IP của replication server. Trong chương này, mọi path đều trỏ đến một PostgreSQL 16 instance được cài đặt trên Debian, chẳng hạn `/var/lib/postgresql/16/main`.

1. Đối với primary server, chúng ta sẽ thấy output sau:

   ```text
   root@pg1# ip addr
   1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN
   group default qlen 1000
        link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
        inet 127.0.0.1/8 scope host lo
           valid_lft forever preferred_lft forever
        inet6 ::1/128 scope host
           valid_lft forever preferred_lft forever
   2: enp1s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel
   state UP group default qlen 1000
       link/ether 52:54:00:5c:df:f4 brd ff:ff:ff:ff:ff:ff
       inet 192.168.122.10/24 brd 192.168.122.255 scope global enp1s0
          valid_lft forever preferred_lft forever
       inet6 fe80::5054:ff:fe5c:dff4/64 scope link
          valid_lft forever preferred_lft forever

   root@pg1:# su - postgres
   postgres@pg1:~$ psql
   psql (16)
   Type "help" for help.

   postgres=#
   ```

2. Tương tự, đối với replica server, chúng ta sẽ có:

   ```text
   root@pg2:~# ip addr
   1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN
   group default qlen 1000
       link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
       inet 127.0.0.1/8 scope host lo
          valid_lft forever preferred_lft forever
       inet6 ::1/128 scope host
          valid_lft forever preferred_lft forever
   2: enp1s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel
   state UP group default qlen 1000
       link/ether 52:54:00:93:47:18 brd ff:ff:ff:ff:ff:ff
       inet 192.168.122.11/24 brd 192.168.122.255 scope global enp1s0
          valid_lft forever preferred_lft forever
       inet6 fe80::5054:ff:fe93:4718/64 scope link
          valid_lft forever preferred_lft forever
   root@pg2:~# su - postgres
   postgres@pg2:~$ psql
   psql (16)
   Type "help" for help.

   postgres=#
   ```

3. Hãy kiểm tra xem có connection giữa hai server hay không.

   Sử dụng command `ping`, chúng ta sẽ thực hiện một test đơn giản để kiểm tra node pg1 có thể kết nối đến node pg2 hay không, và node pg2 có thể kết nối đến node pg1 hay không:

   ```text
   postgres@pg1:~$ ping 192.168.122.11
   PING 192.168.122.11 (192.168.122.11) 56(84) bytes of data.
   64 bytes from 192.168.122.11: icmp_seq=1 ttl=64 time=0.292 ms
   64 bytes from 192.168.122.11: icmp_seq=2 ttl=64 time=0.406 ms

   postgres@pg2:~$ ping 192.168.122.10
   PING 192.168.122.10 (192.168.122.10) 56(84) bytes of data.
   64 bytes from 192.168.122.10: icmp_seq=1 ttl=64 time=0.536 ms
   64 bytes from 192.168.122.10: icmp_seq=2 ttl=64 time=0.359 ms
   ```

Bây giờ mọi thứ đã sẵn sàng, hãy bắt đầu khám phá chi tiết của physical replication.

## Quản lý streaming replication

Trong section này, chúng ta sẽ nói về lý do cần có replica.

![Hình 17.1: Sơ đồ Primary/Replica](../assets/part-065-figure-17-1-000.jpg)

*Hình 17.1: Sơ đồ Primary/Replica*

Trong môi trường production, bạn thường cần có khả năng restore hệ thống nhanh nhất có thể sau một system crash. Để làm điều này, chúng ta phải sử dụng kỹ thuật streaming replication. Để thực hiện được điều đó, cần ít nhất hai server, một primary server và một secondary server. Primary server thực hiện mọi operation do application program yêu cầu; replica server chỉ sẵn sàng cho read operation và có data được copy theo thời gian thực.

## Các khái niệm cơ bản về streaming replication

Ý tưởng đằng sau streaming replication là copy WAL file từ primary server sang một server khác (replica server).

Replica server sẽ ở trong trạng thái continuous recovery và liên tục execute WAL được primary machine truyền đến; theo cách này, replica machine thực hiện binary replication data của primary machine thông qua WAL.

Như đã thấy trong Chapter 15, Backup and Restore, trong một tình huống PITR classic, WAL segment được primary lưu ở đâu đó, sau đó recovery machine lấy chúng bằng các script thủ công:

![Hình 17.2: Sơ đồ PITR](../assets/part-065-figure-17-2-000.jpg)

*Hình 17.2: Sơ đồ PITR*

Trong context streaming replication, một communication channel sẽ được mở giữa replica và primary, và primary sẽ gửi WAL segment qua channel đó:

![Hình 17.3: Sơ đồ WAL Primary/Replica](../assets/part-065-figure-17-3-000.jpg)

*Hình 17.3: Sơ đồ WAL Primary/Replica*

Replica server sẽ nhận các WAL segment và chạy lại chúng, duy trì permanent recovery state.

Bây giờ chúng ta sẽ xem cách thực hiện asynchronous physical replication. Kỹ thuật này rất tương tự PITR.

## Môi trường asynchronous replication

Hãy chuẩn bị môi trường. Chúng ta cần hai server: server thứ nhất có tên pg1 và IP là 192.168.122.10; server thứ hai có tên pg2 và IP là 192.168.122.11. Hãy xem các bước chuẩn bị cho physical replication.

Trên primary server, chúng ta cần thực hiện những việc sau:

1. Việc đầu tiên cần làm là sửa đổi `listen_addresses` để nó lắng nghe trên network. Nếu đặt `listen_addresses = '*'`, PostgreSQL sẽ lắng nghe trên mọi IP; nếu không, chúng ta có thể chỉ định một list IP address được phân tách bằng dấu phẩy. Thay đổi này yêu cầu restart PostgreSQL service.

2. Chúng ta cần tạo một user mới có khả năng thực hiện replication:

   ```text
   postgres=# CREATE role replicarole WITH REPLICATION ENCRYPTED
   PASSWORD 'SuperSecret' LOGIN;
   CREATE ROLE
   ```

3. Chúng ta phải sửa đổi file `pg_hba.conf` để từ replica machine, với user `replicarole`, có thể truy cập primary machine:

   ```text
   host    replication          replicarole         192.168.122.11/32
   scram-sha-256
   ```

4. Để kích hoạt configuration này, chúng ta cần reload PostgreSQL server. Ví dụ, có thể chạy như sau:

   ```text
   postgres=# select pg_reload_conf();
    pg_reload_conf
   ----------------
    t
   (1 row)
   ```

5. Trên replica server, chúng ta phải tắt PostgreSQL service, xóa PGDATA directory rồi tạo lại nó, lần này để trống và đặt đúng permission. Để làm vậy, chúng ta có thể sử dụng các statement sau:

   ```text
   root@pg1:/# systemctl stop postgresql
   root@pg1:/# cd /var/lib/postgresql/16/
   root@pg1:/# rm -rf main
   root@pg1:/# mkdir main
   root@pg1:/# chown postgres:postgres main
   root@pg1:/# chmod 0700 main
   ```

Tất cả path được sử dụng trong ví dụ này đều hợp lệ cho các distribution dựa trên Debian; đối với các distribution khác, hãy tham khảo tài liệu chính thức tương ứng.

## Option wal_keep_segments

Từ những gì đã hiểu, physical replication được thực hiện thông qua việc truyền WAL segment. Bây giờ hãy giả sử trong chốc lát rằng replica server bị dừng vì một lý do nào đó. Primary sẽ hoạt động thế nào? Khi replica server hoạt động trở lại, nó có tự realign với primary node hay không? Đây là những câu hỏi cần đặt ra nếu muốn replication system hoạt động chính xác.

Chỉ thị trong `postgresql.conf` cho PostgreSQL biết cần giữ bao nhiêu WAL segment trên disk có tên là `wal_keep_segments`; theo mặc định, `wal_keep_segments` được đặt bằng zero vì replica không được cài đặt bởi PostgreSQL installation process. Điều này có nghĩa PostgreSQL sẽ không lưu thêm WAL segment nào làm buffer. Điều này cũng có nghĩa nếu replica machine (standby) bị dừng, nó sẽ không còn có thể realign khi khởi động lại. Điều này xảy ra vì trong khoảng thời gian replica cần để hoạt động trở lại, primary machine có thể đã tạo và xóa các WAL segment mới. Cách đầu tiên để khắc phục vấn đề này là đặt directive `wal_keep_segments` thành một giá trị lớn hơn zero trong `postgresql.conf`. Ví dụ, nếu đặt `wal_keep_segments = 100`, điều đó có nghĩa là sẽ có ít nhất 100 file WAL segment trong `pg_wal` folder, với tổng disk space chiếm dụng là 100 * 16 MB = 1.6 GB.

Trong trường hợp này, primary luôn giữ các WAL segment bổ sung đó, và nếu replica bị dừng, nó chỉ có thể realign sau khi hoạt động trở lại nếu primary đã tạo ra số WAL segment nhỏ hơn `wal_keep_segments`.

Giải pháp này cung cấp một static buffer, trong đó bạn có thể lưu các WAL segment cũ, và cung cấp một save anchor ngắn hơn khoảng thời gian primary cần để tạo ra số WAL segment lớn hơn `wal_keep_segments`. Đây là một static solution; nó cũng có nhược điểm là disk space bị chiếm dụng luôn bằng `wal_keep_segments * 16 MB`, ngay cả khi không còn cần giữ WAL segment trên primary server nữa (vì replica server đã xử lý chúng). Ưu điểm của solution này là nếu network bị down, PostgreSQL sử dụng disk space tối đa bằng `wal_keep_segments * 16 MB` để tránh lấp đầy toàn bộ disk space nếu primary server bị dừng; vì vậy nếu không có nhiều disk space, có thể sử dụng solution này, nhưng cần nhớ rằng nếu vượt quá size `wal_keep_segments * 16 MB`, replica sẽ không còn synchronized và chúng ta sẽ phải rebuild nó.

## Cách dùng slot

Trong PostgreSQL, có một approach khác có thể được sử dụng để giải quyết vấn đề lưu WAL segment: kỹ thuật slot. Thông qua kỹ thuật slot, chúng ta có thể yêu cầu PostgreSQL giữ mọi WAL segment trên primary cho đến khi chúng được truyền đến replica server. Theo cách này, chúng ta có cơ chế quản lý dynamic, variable và hoàn toàn automated đối với số WAL segment mà primary server phải giữ làm buffer. Đây là cách rất dễ để quản lý physical replica, và là method chúng ta sẽ tập trung trong cuốn sách này.

Instruction cần thực hiện trên PostgreSQL để tạo slot mới như sau:

```text
postgres=# SELECT * FROM pg_create_physical_replication_slot('master');
 slot_name | lsn
-----------+-----
 master    |
(1 row)
```

Instruction cần thực hiện trên PostgreSQL để drop một slot là:

```text
postgres=# select pg_drop_replication_slot('master');
 pg_drop_replication_slot
--------------------------

(1 row)
```

Sau này trong chương này, chúng ta sẽ xem xét các instruction này chi tiết hơn.

## Command pg_basebackup

Trong Chapter 15, Backup and Restore, ở section Basic concepts behind Point In Time Recovery, chúng ta đã nói về base backup; đây là một hot backup đóng vai trò là base khởi đầu để sau đó chúng ta có thể áp dụng tất cả WAL segment. Có một command tên là `pg_basebackup` triển khai quy trình này gần như tự động.

Giá trị `max_wal_senders` cần ít nhất bằng 2. Đây là một command rất hữu ích cho DBA vì cho phép thực hiện mọi việc cần thiết chỉ bằng một instruction. Chúng ta sẽ sử dụng và giải thích command này kỹ hơn trong section tiếp theo, nơi chúng ta sẽ triển khai physical replication asynchronous đầu tiên.

Để biết thêm thông tin về command `pg_basebackup`, hãy tham khảo https://www.PostgreSQL.org/docs/current/app-pgbasebackup.html.

## Asynchronous replication

Bây giờ chúng ta đã có tất cả building block cần thiết để dễ dàng và nhanh chóng tạo physical replication asynchronous đầu tiên. Theo mặc định, trong PostgreSQL, physical replication là asynchronous. Bây giờ hãy bắt đầu với kỹ thuật replication. Bằng cách làm theo các bước trong những section trước của chương này, chúng ta đã có một primary server sẵn sàng để replica server kết nối tới, và replica đã sẵn sàng nhận thông tin từ primary. Lúc này, PostgreSQL service trên replica server đã được tắt và PGDATA data folder đã được tạo, để trống, với permission phù hợp:

1. Hãy đi vào PGDATA directory với tư cách system postgres user:

   ```text
   root@pg2:# su - postgres
   postgres@pg2:~$ cd /var/lib/PostgreSQL/16/main
   ```

2. Bây giờ hãy chạy command `pg_basebackup` với các option phù hợp. Command này sẽ thực thi command `base_backup` từ primary machine đến replica machine và chuẩn bị replica machine để nhận rồi execute các WAL segment nhận được, khiến replica server duy trì permanent recovery state:

   ```text
   postgres@pg2:~/16/main$ pg_basebackup -h 192.168.122.10 -U
   replicarole -p5432 -D /var/lib/PostgreSQL/16/main -Fp -Xs -P -R -S
   master
   Password:
   22483/22483 kB (100%), 1/1 tablespace
   ```

   Password cần nhập là password của user `replicarole`; trong trường hợp này là `SuperSecret`. Nếu `pg_basebackup` không khởi động nhanh, điều đó có nghĩa là nó đang chờ checkpoint từ primary, vì vậy để cải thiện performance của operation này, chúng ta có thể vào primary server và execute:

   ```text
   postgres=# checkpoint ;
   CHECKPOINT
   ```

   Hãy phân tích command `pg_basebackup` chi tiết hơn:

   - `-h`: Với option này, chúng ta thấy host mà replica muốn kết nối tới.
   - `-U`: Đây là user được tạo trên primary server và được sử dụng cho replication.
   - `-p`: Đây là port nơi primary server lắng nghe.
   - `-D`: Đây là giá trị PGDATA trên replica server.
