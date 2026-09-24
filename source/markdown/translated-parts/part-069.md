DROP SUBSCRIPTION
db_destination=# truncate t1;
TRUNCATE TABLE
db_destination=# CREATE SUBSCRIPTION sub_all_tables CONNECTION
'user=replicarole password=LearnPostgreSQL host=pg_pub port=5432
dbname=db_source' PUBLICATION all_tables_pub;
NOTICE:     created replication slot "sub_all_tables" on publisher
CREATE SUBSCRIPTION
```

Bây giờ, nếu kiểm tra cả hai server, primary server và replica server sẽ có toàn bộ data được đồng bộ.
Trên server `pg_pub`, ta có:

```text
db_source=# select * from t1;
   id |   name
----+---------
    1 | Linux
    2 | FreeBSD
    4 | Minix
    3 | Windows
    5 | Unix
(5 rows)
```

Trên replica `pg_sub`, ta có:

```text
db_destination=# select * from t1;
   id |   name
----+---------
    1 | Linux
    2 | FreeBSD
    4 | Minix
    3 | Windows
    5 | Unix
(5 rows)
```

Bây giờ, nếu thực thi lại query trên `pg_stat_replication`, ta sẽ thấy logical replication:

```text
db_source=# \x
Expanded display is on.
db_source=#      select * from pg_stat_replication;
-[ RECORD 1 ]----+------------------------------
pid                 | 337
usesysid            | 16477
usename             | replicarole
application_name | sub_all_tables
client_addr         | 192.168.144.2
client_hostname     |
client_port         | 57826
backend_start       | 2023-06-16 15:24:36.905319+00
backend_xmin        |
state               | streaming
sent_lsn            | 0/1DD0BC0
write_lsn           | 0/1DD0BC0
flush_lsn           | 0/1DD0BC0
replay_lsn          | 0/1DD0BC0
write_lag           |
flush_lag           |
replay_lag          |
sync_priority       | 0
sync_state          | async
reply_time          | 2023-06-16 15:27:47.24564+00
```

## Lệnh DDL

Ở section trước, chúng ta đã nói rằng logical replication không replicate các lệnh DDL, nhưng điều gì xảy ra nếu áp dụng một DDL statement trên primary server vốn đã được replicate bằng logical replication? Các lệnh DDL gồm:

- `CREATE`
- `ALTER`
- `DROP`
- `RENAME`
- `TRUNCATE`
- `COMMENT`

Giả sử bây giờ chúng ta muốn thêm một field vào table `t1` trên primary server `pg_pub`:

```text
db_source=# alter table t1 add description varchar(64);
ALTER TABLE
```

Bây giờ hãy thử thực hiện một DML command trên server `pg_pub`. Một số ví dụ về DML command:

- `INSERT`
- `DELETE`
- `UPDATE`

Ví dụ, giả sử chúng ta thử xóa một record khỏi table `t1` của server `pg_pub`:

```text
db_source=# delete from t1 where id=5;
DELETE 1
```

Trên server `pg_pub`, ta sẽ có:

```text
db_source=# select * from t1;
    id |     name   | description
----+---------+-------------
     1 | Linux     |
     2 | FreeBSD |
     4 | Minix     |
     3 | Windows |
(4 rows)
```

Tuy nhiên, trên server `pg_sub`, ta vẫn có:

```text
db_destination=#       select * from t1;
    id |     name
----+---------
     1 | Linux
     2 | FreeBSD
     4 | Minix
     3 | Windows
     5 | Unix
(5 rows)
```

Nếu kiểm tra `postgresql.log` trên server `pg_sub`, ta sẽ thấy:

```text
learn_postgresql_sub_1 | 2023-06-16 15:30:57.973 UTC [364] ERROR:
logical replication target relation "public.t1" is missing replicated
column: "description"
learn_postgresql_sub_1 | 2023-06-16 15:30:57.973 UTC [364] CONTEXT:
processing remote data for replication origin "pg_16480" during message
type "DELETE" in transaction 783, finished at 0/1DD5380
learn_postgresql_sub_1 | 2023-06-16 15:30:57.975 UTC [1] LOG: background
worker "logical replication worker" (PID 364) exited with exit code 1
^CERROR: Aborting.
```

Logical replication không còn hoạt động vì logical replication target relation `public.t1` thiếu một số replicated column, như server log đã báo cáo. Nếu muốn giải quyết vấn đề này, chúng ta phải thực thi DDL trên replica server:

```text
db_destination=# alter table t1 add description varchar(64);
ALTER TABLE
```

Bây giờ, nếu kiểm tra các record trên server `pg_sub`, ta có cùng các record đang hiện diện trên server `pg_pub`:

```text
db_destination=# select * from t1;
 id |     name   | description
----+---------+-------------
   1 | Linux     |
   2 | FreeBSD |
   4 | Minix     |
   3 | Windows |
(4 rows)
```

> Các lệnh DDL luôn phải được replicate trên các replica server.

## Vô hiệu hóa logical replication

Ở section trước, chúng ta đã dùng lệnh `DROP SUBSCRIPTION` để drop một subscription. Có thể có những trường hợp không thể trực tiếp dùng command này. Ví dụ, giả sử primary server không thể truy cập được và chúng ta cần drop subscription trên replica server. Nếu thử thực thi một lệnh `DROP SUBSCRIPTION`, ta sẽ nhận được response sau:

```text
db_destination=# drop subscription sub_all_tables ;
ERROR:     could not connect to publisher when attempting to [..]
HINT: Use ALTER SUBSCRIPTION ... SET (slot_name = NONE) to disassociate
the subscription from the slot.
```

PostgreSQL đề xuất dùng `ALTER SUBSCRIPTION ... SET (slot_name = NONE)` để disassociate subscription khỏi slot. Vấn đề là chúng ta không thể thực thi command này trước khi disable subscription. Thực tế, nếu bây giờ thử thực hiện command PostgreSQL đề xuất, ta sẽ nhận được:

```text
db_destination=#     alter subscription sub_all_tables SET (slot_name =
NONE);
ERROR:    cannot set slot_name = NONE for enabled subscription
```

Các bước đúng cần thực thi như sau:

1. Disable subscription.
2. Set `slot_name` thành `NONE`.
3. Drop subscription.

Chúng ta phải thực hiện ba statement sau:

```text
db_destination=# alter subscription sub_all_tables disable;
ALTER SUBSCRIPTION
db_destination=# alter subscription sub_all_tables SET (slot_name = NONE);
ALTER SUBSCRIPTION
db_destination=# drop subscription sub_all_tables ;
DROP SUBSCRIPTION
```

Đây là các bước đúng nếu muốn drop một subscription khi primary server không thể truy cập được. Ta cũng có thể dùng command `ALTER SUBSCRIPTION sub_name DISABLE` để detach subscription khỏi publication, và command `ALTER SUBSCRIPTION sub_name ENABLE` để re-attach subscription vào publication.

## Tạo logical replication bằng physical replication instance

Trên PostgreSQL 16, có thể tạo một logical replication bắt đầu từ một physical replication.

Các bước cần thực hiện là:

1. Set `wal_level=logical` trên Primary và Physical Replication server.

   Trên Primary server:

2. Tạo một role cho physical replication:

   ```text
   CREATE ROLE replicarole WITH REPLICATION LOGIN PASSWORD
   'LearnPostgreSQL'.
   ```

3. Tạo một role cho logical replication trên Primary server:

   ```text
   CREATE ROLE logicalreplicarole WITH REPLICATION LOGIN PASSWORD
   'LearnPostgreSQL'
   ```

4. Gán các permission phù hợp cho `logicalreplicarole` đối với các schema và table mà chúng ta muốn replicate bằng logical replication, chẳng hạn:

   ```text
   GRANT USAGE ON SCHEMA forum TO logicalreplicarole;
   GRANT SELECT ON forum.users TO logicalreplicarole
   ```

5. Tạo một physical replication slot hoặc physical replication.

6. Tạo một publication sẽ được replicate trên Physical replication server và được logical replication subscription trên Logical Replication server sử dụng.

   Trên Physical replication server:

7. Set `hot_standby_feedback = on` để ngăn các vấn đề do hoạt động vacuum trên primary server gây ra và được phản ánh trên replica server; các vấn đề này có thể tạo conflict với những query rất dài trên replica.

8. Tạo replica bằng command `pg_basebackup`, như đã mô tả trong chapter trước.

   Trên Logical replication server:

9. Tạo các table mà bạn muốn replicate data từ physical replication.

10. Tạo một subscription tham chiếu tới publication được tạo trên primary như chúng ta đã thấy.

Bây giờ, hãy thử feature này bằng Docker container; scenario chúng ta muốn thử là:

11. Một database `forumdb` trên primary server.
12. Một physical replica của toàn bộ cluster trên replica server.
13. Một logical replication của các table `forum.users` trên logical replication server.

![Hình 18.3: Cascade physical/logical replication](../assets/part-069-figure-18-3-000.jpg)

*Hình 18.3: Cascade physical/logical replication*

Hãy sử dụng các Docker container `chapter18_physical_logical` và thực hiện các bước sau:

1. Start tất cả container bằng:

   ```text
   $ bash run-pg-docker-replica-logical.sh chapter18_physical_logical
   ```

2. Sau khi thực thi statement trên Docker host, ta có ba container đang chạy:

   ```text
   chapter18_physical_logical_learn_postgresql_replica_sub_1
   chapter18_physical_logical_learn_postgresql_master_pub_1
   chapter18_physical_logical_learn_postgresql_replica_1
   ```

3. Script đã chạy đưa chúng ta trực tiếp vào container nơi primary node chạy; bây giờ, chúng ta phải mở hai cửa sổ bash terminal và thực thi statement dưới đây trong cửa sổ thứ nhất (để vào physical replication node):

   ```text
   $ bash run-pg-docker-replica1.sh chapter18_physical_logical
   ```

4. Trong cửa sổ thứ hai, chúng ta phải thực thi statement dưới đây để vào logical replication node:

   ```text
   bash run-pg-docker-replica2.sh chapter18_physical_logical
   ```

5. Như có thể thấy, trên primary node ta có:

   ```text
   postgres@pg_master_pub:~$ psql


   postgres=# select * from pg_stat_replication;
   -[ RECORD 1 ]----+------------------------------
   pid               | 108
   usesysid          | 16384
   usename           | replicarole
   application_name | walreceiver
   client_addr       | 172.29.0.4
   client_hostname   |
   client_port       | 43400
   backend_start     | 2023-06-20 16:10:30.779359+00
   backend_xmin      |
   state             | streaming
   sent_lsn          | 0/3005948
   write_lsn         | 0/3005948
   flush_lsn         | 0/3005948
   replay_lsn        | 0/3005948
   write_lag         |
   flush_lag         |
   replay_lag        |
   sync_priority     | 0
   sync_state        | async
   reply_time        | 2023-06-20 16:11:49.332655+00
   ```

   Trên physical replication server, ta có:

   ```text
   postgres@pg_replica:~$ psql forumdb


   forumdb=# select * from pg_stat_replication;
   -[ RECORD 1 ]----+------------------------------
   pid               | 101
   usesysid          | 16468
   usename           | logicalreplicarole
   application_name | users_sub
   client_addr       | 172.29.0.2
   client_hostname   |
   client_port       | 43950
   backend_start     | 2023-06-20 16:10:39.685477+00
   backend_xmin      |
   state             | streaming
   sent_lsn          | 0/3005948
   write_lsn         | 0/3005948
   flush_lsn         | 0/3005948
   replay_lsn        | 0/3005948
   write_lag         |
   flush_lag         |
   replay_lag         |
   sync_priority     | 0
   sync_state        | async
   reply_time        | 2023-06-20 16:11:39.389851+00
   ```

6. Vậy hãy thử thực hiện một số operation; trên primary server, hãy nhập:

   ```text
   forumdb=# select * from forum.users;
    pk | username | gecos |                     email
   ----+----------+-------+-----------------------------
     1 | enrico       | 1       | enrico.pirozzi@packtpub.xyz
   (1 row)
   ```

   Trên physical replication server, nhập:

   ```text
   forumdb=# select * from forum.users;
    pk | username | gecos |                     email
   ----+----------+-------+-----------------------------
     1 | enrico       | 1       | enrico.pirozzi@packtpub.xyz
   (1 row)
   ```

   Và trên logical replication server, nhập:

   ```text
   postgres@pg_replica_sub:~$ psql forumdb


   forumdb=# select * from forum.users;
    pk | username | gecos |                     email
   ----+----------+-------+-----------------------------
     1 | enrico       | 1       | enrico.pirozzi@packtpub.xyz
   (1 row)
   ```

7. Bây giờ, hãy thử xóa một record trên physical replication server:

   ```text
   forumdb=# delete from forum.users ;
   ERROR:    cannot execute DELETE in a read-only transaction
   ```

8. Và hãy thử insert một record trên logical replication server:

   ```text
   forumdb=# insert into forum.users (pk,username,gecos,email) values
   (2,'luca',1,'luca.ferrari@packtpub.xyz');
   INSERT 0 1


   forumdb=# select * from forum.users order by pk;
    pk | username | gecos |                   email
   ----+----------+-------+-----------------------------
     1 | enrico    | 1       | enrico.pirozzi@packtpub.xyz
     2 | luca      | 1       | luca.ferrari@packtpub.xyz
   (2 rows)
   ```

9. Bây giờ, hãy thử xóa một record trên primary server:

   ```text
   forumdb=# delete from forum.users where pk =1 ;
   DELETE 1
   ```

10. Và hãy xem điều gì đã xảy ra trên physical replication server:

   ```text
   forumdb=# select * from forum.users;
   (0 rows)
   ```

11. Và trên logical replication server:

   ```text
   forumdb=# select * from forum.users;
    pk | username | gecos |                 email
   ----+----------+-------+---------------------------
     2 | luca      | 1       | luca.ferrari@packtpub.xyz
   (1 row)
   ```

## Tóm tắt

Trong chapter này, chúng ta đã thảo luận về logical replication. Chúng ta đã thấy logical replication dựa trên concept reverse engineering, bắt đầu bằng việc phân tích các WAL segment để extract những logical command cần được chuyển tới replica server. Chúng ta đã thấy logical replication hữu ích khi muốn replicate một phần database và khi muốn thực hiện hot migration giữa các version PostgreSQL khác nhau. Logical replication thực hiện được điều này vì nó không replicate data ở dạng binary mà thay vào đó extract các logical DML command từ WAL file, sau đó replicate chúng trên replica server.
