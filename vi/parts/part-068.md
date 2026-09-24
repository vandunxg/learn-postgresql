2. Sau khi đặt các giá trị này, hãy restart primary PostgreSQL server trên physical server; chúng ta cần execute:

```text
# systemctl restart postgresql
```

Với container đi kèm sách, chúng ta chỉ cần thoát khỏi container bằng `Ctrl + D`, sau đó restart nó.

3. Sau khi hoàn tất, chúng ta sẽ chạy command này từ shell:

```text
# netstat -an | grep 5432
tcp 0 0 0.0.0.0:5432 0.0.0.0:* LISTEN
tcp6 0 0 :::5432 :::* LISTEN
unix 2 [ ACC ] STREAM LISTENING 19910 /var/run/
postgresql/.s.PGSQL.5432
```

Như chúng ta có thể thấy, PostgreSQL hiện lắng nghe trên tất cả network interface có trên server.

## Replica server – postgresql.conf

Đối với replica server, các thay đổi đối với `postgresql.conf` như sau:

```text
# Add settings for extensions here
max_logical_replication_workers = 4
max_worker_processes = 10
```

Như chúng ta có thể thấy, các giá trị của `listen_addresses` và `wal_level` giống hệt primary; ở đây chúng ta không có các giá trị cho `max_replication_slots` và `max_wal_senders`, nhưng có các giá trị sau:

- `max_logical_replication_workers`: Parameter này phải được đặt thành một cho mỗi subscription, cộng thêm một số giá trị cần tính đến cho việc đồng bộ table.
- `max_worker_processes`: Giá trị này phải được đặt ít nhất là một cho mỗi replication worker, cộng thêm một.

Ở đây, cũng như đã làm với primary, hãy restart PostgreSQL server:

```text
# systemctl restart postgresql
```

Sau khi restart, hãy chạy command này từ shell:

```text
# netstat -an | grep 5432
tcp 0 0 0.0.0.0:5432 0.0.0.0:* LISTEN
tcp6 0 0 :::5432 :::* LISTEN
unix 2 [ ACC ] STREAM LISTENING 19910 /var/run/postgresql/.s.PGSQL.5432
```

Như chúng ta có thể thấy, PostgreSQL hiện lắng nghe trên tất cả network interface có trên server.

## File pg_hba.conf

Bây giờ hãy configure file này trên primary server để có thể kết nối replica machine với primary machine. Trên primary machine, chúng ta đặt như sau:

```text
# IPv4 local connections:
host all all 127.0.0.1/32 md5
host all replicarole 192.168.144.2/32 md5
```

Điều này cho phép user thực hiện replication tới replica machine để query primary server. Để activate thay đổi, cần reload primary server:

```text
# systemctl reload postgresql
```

## Thiết lập logical replication

Tại thời điểm này, chúng ta đã sẵn sàng để bắt đầu chuẩn bị logical replica:

1. Hãy đi tới primary machine và tạo database của chúng ta:

   ```text
   postgres=# create database db_source;
   CREATE DATABASE
   dostgres=# \c db_source
   You are now connected to database "db_source" as user "postgres"
   ```

2. Bây giờ hãy tạo một table tên là `t1`, bảo đảm rằng table có primary key:

   ```text
   db_source=# create table t1 (id integer not null primary key, name
   varchar(64));
   CREATE TABLE
   ```

3. Hãy cấp quyền SELECT cho user `REPLICAROLE`:

   ```text
   db_source=# GRANT SELECT ON ALL TABLES IN SCHEMA public TO
   replicarole;
   GRANT
   ```

4. Bây giờ hãy tạo publication trên primary machine, trong đó chúng ta sẽ chỉ ra danh sách các table muốn replicate trên replica machine.

   Chúng ta cũng có thể chỉ ra tất cả table, như trong ví dụ sau:

   ```text
   db_source=# CREATE PUBLICATION all_tables_pub FOR ALL TABLES;
   CREATE PUBLICATION
   ```

5. Tại thời điểm này, chúng ta đi tới replica machine và tạo một database mới:

   ```text
   postgres=# create database db_destination;
   CREATE DATABASE
   postgres=# \c db_destination
   You are now connected to database "db_destination" as user
   "postgres"
   ```

6. Chúng ta tạo lại chính xác structure của table đã tạo trên primary machine:

   ```text
   db_destination=# create table t1 (id integer not null primary key,
   name varchar(64));
   CREATE TABLE
   ```

7. Sau đó, chúng ta phải thiết lập subscription để data từ publication được replicate trên replica machine:

   ```text
   db_destination=# CREATE SUBSCRIPTION sub_all_tables CONNECTION
   'user=replicarole password=LearnPostgreSQL host=pg_pub port=5432
   dbname=db_source' PUBLICATION all_tables_pub;
   NOTICE:    created replication slot "sub_all_tables" on publisher
   CREATE SUBSCRIPTION
   ```

   Bây giờ thiết lập logical replication của chúng ta đã hoàn tất.

8. Chúng ta có thể thử insert một số data vào primary server:

   ```text
   db_source=#     insert into t1 values(1,'Linux'),(2,'FreeBSD');
   INSERT 0 2
   ```

9. Như có thể thấy ở đây, cùng data đó đã được replicate trên replica server:

   ```text
   db_destination=# select * from t1;
   id |   name
   ----+---------
     1 | Linux
     2 | FreeBSD
   (2 rows)
   ```

Như vậy, chúng ta đã chuẩn bị thành công logical replica. Tiếp theo chúng ta sẽ học cách monitor nó trong section kế tiếp.

## Monitoring logical replication

Cũng giống như physical replication, PostgreSQL cung cấp các tool cần thiết để monitor logical replication.

Đối với logical replication, chúng ta phải query table `pg_stat_replication`, cũng là table được dùng để monitor physical replication, như có thể thấy ở đây:

```text
db_source=# \x
Expanded display is on.
db_source=# select * from pg_stat_replication ;
-[ RECORD 1 ]----+------------------------------
pid                  | 144
usesysid             | 16477
usename              | replicarole
application_name | sub_all_tables
client_addr          | 192.168.144.2
client_hostname      |
client_port          | 43162
backend_start        | 2023-06-16 15:04:09.074749+00
backend_xmin         |
state                | streaming
sent_lsn             | 0/1DD0398
write_lsn            | 0/1DD0398
flush_lsn            | 0/1DD0398
replay_lsn           | 0/1DD0398
write_lag            |
flush_lag            |
replay_lag           |
sync_priority        | 0
sync_state           | async
reply_time           | 2023-06-16 15:05:23.524003+00
```

Thông tin được hiển thị bởi query này giống với những gì chúng ta đã thấy trong trường hợp physical replication, nhưng chúng ta biết thông tin này tham chiếu tới một logical replica vì có slot name `sub_all_tables`, được tạo trước đó, trong `application_name`.

Query này phải được thực hiện trên primary server (`pg_pub`). Nếu chạy cùng query trên replica machine (`pg_sub`), chúng ta không nhận được kết quả nào, như có thể thấy ở đây:

```text
db_destination=# select * from pg_stat_replication ;
(0 rows)
```

Ngoài ra còn có hai catalog table khác mà chúng ta có thể query để lấy thêm thông tin về publication và subscription. Giả sử trên primary server, chúng ta thực hiện:

```text
db_source=# select * from pg_publication;
-[ RECORD 1 ]+---------------
oid             | 16479
pubname         | all_tables_pub
pubowner        | 10
puballtables | t
pubinsert       | t
pubupdate       | t
pubdelete       | t
pubtruncate     | t
pubviaroot      | f
```

Nếu làm vậy, chúng ta nhận được thông tin về tất cả publication được tạo trong database. Để biết thêm thông tin, hãy tham khảo documentation chính thức: https://www.postgresql.org/docs/current/catalog-pg-publication.html.

Tương tự, giả sử chúng ta chạy query này trên replica server:

```text
db_destination=# select * from pg_subscription;
-[ RECORD 1 ]----+-------------------------------------
oid                   | 16477
subdbid               | 16471
subskiplsn            | 0/0
subname               | sub_all_tables
subowner              | 10
subenabled            | t
subbinary             | f
substream             | f
subtwophasestate | d
subdisableonerr       | f
subconninfo      | user=replicarole password=LearnPostgreSQL host=pg_pub
port=5432 dbname=db_source
subslotname          | sub_all_tables
subsynccommit        | off
subpublications      | {all_tables_pub}
```

Khi đó chúng ta có thông tin về tất cả subscription được tạo trong database. Để biết thêm thông tin, hãy tham khảo documentation chính thức: https://www.postgresql.org/docs/current/catalog-pg-subscription.html.

## Read-only so với write-allowed

Trong chapter trước, chúng ta đã thấy rằng chỉ có thể access physical replication server bằng các read operation và không cho phép write operation. Chúng ta cũng đã thấy physical replication replicate mọi loại operation, cả DML operation lẫn DDL operation. Với logical replication, chúng ta cũng có thể thực hiện write operation trên replica server, nhưng trong logical replica, chỉ DML operation được replicate tới replica server; DDL operation không được replicate. Hãy thực hiện một số test và xem điều gì xảy ra. Trong các ví dụ sau, primary server sẽ luôn được gọi là `pg_pub`, còn server có logical replication sẽ luôn được gọi là `pg_sub`.

Đây là tình trạng ban đầu trên server `pg_pub`:

```text
db_source=#      select * from t1;
 id |     name
----+---------
   1 | Linux
   2 | FreeBSD
(2 rows)
```

Đây là tình trạng ban đầu trên server `pg_sub`:

```text
db_destination=# select * from t1;
 id |     name
----+---------
   1 | Linux
   2 | FreeBSD
(2 rows)
```

Hãy insert một record trên server `pg_sub`:

```text
db_destination=# insert into t1 values (3,'OpenBSD');
INSERT 0 1
```

Đây là tình trạng hiện tại trên server `pg_sub`:

```text
db_destination=# select * from t1;
   id |   name
----+---------
    1 | Linux
    2 | FreeBSD
    3 | OpenBSD
(3 rows)
```

Trên server `pg_pub`, chúng ta vẫn có như sau:

```text
db_source=# select * from t1;
   id |   name
----+---------
    1 | Linux
    2 | FreeBSD
(2 rows)
```

> **Lưu ý:** Logical replica cho phép write operation trên replica server.

Hãy xem điều gì xảy ra nếu chúng ta thêm một record vào server `pg_pub`:

```text
db_source=# insert into t1 values(4,'Minix');
INSERT 0 1
```

Tình trạng trên server `pg_pub` như sau:

```text
db_source=# select * from t1;
   id |   name
----+---------
    1 | Linux
    2 | FreeBSD
    4 | Minix
(3 rows)
```

Tình trạng trên server `pg_sub` như sau:

```text
db_destination=# select * from t1;
 id | name
----+--------
 1   | Linux
 2   | FreeBSD
 3   | OpenBSD
 4   | Minix
(4 rows)
```

Như có thể thấy, các value đã được insert vào table của primary server `pg_pub` và replicate qua logical replica tới server `pg_sub`. Bây giờ hãy xem điều gì xảy ra nếu chúng ta thử insert một record có key value đã được insert trên server `pg_sub`. Chẳng hạn, hãy thử insert record này:

```text
db_source=# insert into t1 values(3,'Windows');
INSERT 0 1
```

Tình trạng trên server `pg_pub` lúc này là:

```text
db_source=# select * from t1;
   id |     name
----+---------
    1 | Linux
    2 | FreeBSD
    4 | Minix
    3 | Windows
(4 rows)
```

Tuy nhiên, tình trạng trên server `pg_sub` lúc này là:

```text
db_destination=# select * from t1;
   id |     name
----+---------
    1 | Linux
    2 | FreeBSD
    3 | OpenBSD
    4 | Minix
(4 rows)
```

Không có record nào được insert trên server `pg_sub`. Nếu không ở trong container environment, chúng ta có thể kiểm tra file `postgresql.log` của replica server `pg_sub`; nếu dùng Docker environment `chapter18_logical_clear`, chúng ta có thể mở một cửa sổ bash terminal khác và execute hai statement sau để xem log:

```text
$ cd chapter18_logical_clear
$ chapter18_logical_clear$ sudo docker-compose logs -f


learn_postgresql_sub_1 | 2023-06-16 15:17:23.774 UTC [213] ERROR:
duplicate key value violates unique constraint "t1_pkey"
learn_postgresql_sub_1 | 2023-06-16 15:17:23.774 UTC [213] DETAIL:                   Key
(id)=(3) already exists.
learn_postgresql_sub_1 | 2023-06-16 15:17:23.774 UTC [213] CONTEXT:
processing remote data for replication origin "pg_16477" during message
type "INSERT" for replication target relation "public.t1" in transaction
780, finished at 0/1DD0918
learn_postgresql_sub_1 | 2023-06-16 15:17:23.776 UTC [1] LOG: background
worker "logical replication worker" (PID 213) exited with exit code 1
```

Nếu kiểm tra log của primary server `pg_pub`, chúng ta sẽ thấy các message sau:

```text
learn_postgresql_pub_1 | 2023-06-16 15:17:23.774 UTC [221] LOG:                  logical
decoding found consistent point at 0/1DD0720
learn_postgresql_pub_1 | 2023-06-16 15:17:23.774 UTC [221] DETAIL:                   There
are no running transactions.
learn_postgresql_pub_1 | 2023-06-16 15:17:23.774 UTC [221] STATEMENT:
START_REPLICATION SLOT "sub_all_tables" LOGICAL 0/1DD0638 (proto_version
'3', publication_names '"all_tables_pub"')
```

Lỗi duplicate key trên replica server khiến primary server ghi lại message được minh họa ở đây.

Vì vậy, nếu bây giờ thử thêm một record khác trên primary server, record này sẽ không được insert trên replica server. Giả sử chúng ta đã thử thực hiện statement này trên server `pg_pub`:

```text
db_source=# insert into t1 values(5,'Unix');
INSERT 0 1
```

Khi đó trên server `pg_pub` sẽ có:

```text
db_source=#      select * from t1;
 id |     name
----+---------
   1 | Linux
   2 | FreeBSD
   4 | Minix
   3 | Windows
   5 | Unix
(5 rows)
```

Tuy nhiên, trên replica server `pg_sub`, chúng ta vẫn sẽ có:

```text
db_destination=# select * from t1;
 id |     name
----+---------
   1 | Linux
   2 | FreeBSD
   3 | OpenBSD
   4 | Minix
(4 rows)
```

Từ thời điểm này, logical replication không còn replicate data nữa, và nếu chúng ta execute query này trên server `pg_pub`:

```text
db_source=# select * from pg_stat_replication;
(0 rows)
```

Sẽ không còn replication nào được tìm thấy; đó là vì logical replication của chúng ta không còn hoạt động.

> **Lưu ý:** Nếu muốn write record trên replica server, chúng ta phải bảo đảm các record đó không conflict với các record trên primary server.

Một cách đơn giản để đưa replica server về cùng trạng thái là drop subscription, truncate table rồi tạo lại subscription:

```text
db_destination=# drop subscription sub_all_tables ;
NOTICE:     dropped replication slot "sub_all_tables" on publisher
