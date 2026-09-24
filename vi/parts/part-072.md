[....]

completed successfully (2868ms)
```

Nếu mọi thứ ổn, chúng ta sẽ nhận được thông báo completed successfully (như ở trên); bây giờ chúng ta đã sẵn sàng quản lý continuous backup.

## Quản lý base backup

Như đã đề cập trước đó, pgbackrest có khả năng xử lý full backup, differential backup và incremental backup bằng một command-line statement đơn giản.

Để tạo một full base backup, chúng ta có thể làm như sau:

```text
postgres@pgbackrest:~$ pgbackrest --stanza=pg1 --type=full backup
```

Khi nhấn phím Enter trên bàn phím, nếu mọi thứ ổn, chúng ta sẽ nhận được thông báo sau:

```text
2023-07-11 08:42:58.125 P00          INFO: expire command end: completed
successfully (46ms)
```

Bây giờ, nếu muốn xem thông tin về repository, chúng ta có thể dùng info command như sau:

```text
postgres@pgbackrest:~$ pgbackrest --stanza=pg1 info
stanza: pg1
     status: ok
     cipher: aes-256-cbc


     db (current)
        wal archive min/max (15): 000000010000000000000001/000000010000000
000000004


          full backup: 20230711-084245F
               timestamp start/stop: 2023-07-11 08:42:45 / 2023-07-11
08:42:57
            wal start/stop: 000000010000000000000004 /
000000010000000000000004
               database size: 22.0MB, database backup size: 22.0MB
               repo1: backup set size: 2.9MB, backup size: 2.9MB
```

info command cho chúng ta biết về các WAL segment, thời điểm bắt đầu của full backup, kích thước database ban đầu và kích thước backup trong repository.

Tương tự, bắt đầu từ full backup này, chúng ta có thể tạo một incremental backup:

```text
postgres@pgbackrest:~$ pgbackrest --stanza=pg1 --type=incr backup


2023-07-11 08:44:35.816 P00        INFO: expire command end: completed
successfully (15ms)
```

Chúng ta cũng có thể tạo một differential backup:

```text
postgres@pgbackrest:~$ pgbackrest --stanza=pg1 --type=diff backup


2023-07-11 08:45:40.020 P00        INFO: expire command end: completed
successfully (32ms)
```

Bây giờ, một info command sẽ theo dõi cả ba backup:

```text
postgres@pgbackrest:~$ pgbackrest --stanza=pg1 info
stanza: pg1
     status: ok
     cipher: aes-256-cbc


     db (current)
        wal archive min/max (15): 000000010000000000000001/000000010000000
000000008


          full backup: 20230711-084245F
              timestamp start/stop: 2023-07-11 08:42:45 / 2023-07-11
08:42:57
            wal start/stop: 000000010000000000000004 /
000000010000000000000004
              database size: 22.0MB, database backup size: 22.0MB
              repo1: backup set size: 2.9MB, backup size: 2.9MB


          incr backup: 20230711-084245F_20230711-084431I
              timestamp start/stop: 2023-07-11 08:44:31 / 2023-07-11
08:44:35
            wal start/stop: 000000010000000000000006 /
000000010000000000000006
              database size: 22.0MB, database backup size: 8.3KB
              repo1: backup set size: 2.9MB, backup size: 496B
```

```text
           backup reference list: 20230711-084245F


          diff backup: 20230711-084245F_20230711-084536D
              timestamp start/stop: 2023-07-11 08:45:36 / 2023-07-11
08:45:39
            wal start/stop: 000000010000000000000008 /
000000010000000000000008
              database size: 22.0MB, database backup size: 8.3KB
              repo1: backup set size: 2.9MB, backup size: 496B
              backup reference list: 20230711-084245F
```

Vì chúng ta đã đặt `repo1-retention-full=2` trong file `pgbackrest.conf`, pgbackrest (sau hai backup) sẽ xóa full backup đầu tiên cùng với các differential hoặc incremental backup liên kết với nó. Ví dụ, sau đây là việc thực thi hai full backup:

```text
postgres@pgbackrest:~$ pgbackrest --stanza=pg1 --type=full backup


2023-07-11 08:48:39.866 P00          INFO: expire command end: completed
successfully (22ms)


postgres@pgbackrest:~$ pgbackrest --stanza=pg1 --type=full backup


2023-07-11 08:49:37.101 P00          INFO: expire command end: completed
successfully (34ms)
```

Sau đó, chúng ta sẽ có kết quả sau:

```text
postgres@pgbackrest:~$ pgbackrest --stanza=pg1 info
stanza: pg1
     status: ok
     cipher: aes-256-cbc


     db (current)
        wal archive min/max (15): 000000010000000000000001/000000010000000
00000000C


          full backup: 20230711-084830F
               timestamp start/stop: 2023-07-11 08:48:30 / 2023-07-11
08:48:39
            wal start/stop: 00000001000000000000000A /
00000001000000000000000A
               database size: 22.0MB, database backup size: 22.0MB
               repo1: backup set size: 2.9MB, backup size: 2.9MB


          full backup: 20230711-084928F
               timestamp start/stop: 2023-07-11 08:49:28 / 2023-07-11
08:49:36
            wal start/stop: 00000001000000000000000C /
00000001000000000000000C
               database size: 22.0MB, database backup size: 22.0MB
               repo1: backup set size: 2.9MB, backup size: 2.9MB
```

Như có thể thấy, system đã tự động xóa full backup đầu tiên cùng với các incremental và differential backup liên quan.

## Quản lý PITR

Trong section này, chúng ta sẽ xem cách restore một PostgreSQL cluster sau một disaster.

Để xây dựng ví dụ, hãy tạo một table trên PostgreSQL server:

```text
postgres=# create table users (id integer, user_name text);
CREATE TABLE
```

Và hãy populate table đó bằng một số data:

```text
postgres=# insert into users select generate_
series(1,10000),'user_'||generate_series(1,10000)::text;
INSERT 0 10000
```

Bây giờ hãy xem thời gian trên PostgreSQL server:

```text
postgres=# select now();
                now
------------------------------
 2023-07-11 08:55:08.22447+00
(1 row)
```

Giả sử một disaster đã xảy ra sau thời điểm này; chẳng hạn, giả sử chúng ta đã drop một table sau thời điểm này:

```text
postgres=#     drop table users;
DROP TABLE
```

Bây giờ hãy thử recovery tại thời điểm `2023-07-11 08:55:08`, tức là thời điểm trước khi disaster xảy ra. Trên server pg1, chúng ta cần stop postgresql server:

```text
# systemctl stop postgresql
```

Sau đó, chúng ta thực hiện pgbackrest restore command:

```text
root@pg1:# su - postgres
postgres@pg1:$ pgbackrest --stanza=pg1 --delta --log-level-console=info
--type=time "--target=2023-07-11 08:55:08" restore


2023-07-11 08:57:39.803 P00         INFO: restore command end: completed
successfully (1905ms)
```

Bây giờ hãy start postgresql server với tư cách root user:

```text
# systemctl start postgresql
```

Sau đó, chúng ta kiểm tra postgresql log:

```text
2023-07-11 08:59:06.844 P00         INFO: archive-get command end: completed
successfully (532ms)
2023-07-11 08:59:06.849 UTC [8786] LOG:           restored log file
"00000001000000000000000D" from archive
2023-07-11 08:59:06.898 UTC [8786] LOG:           consistent recovery state reached
at 0/C000138
2023-07-11 08:59:06.898 UTC [8783] LOG:           database system is ready to
accept read-only connections
2023-07-11 08:59:06.938 P00   INFO: archive-get command begin 2.46:
[00000001000000000000000E, pg_wal/RECOVERYXLOG] --exec-id=8797-9e31ebc7
--log-level-console=info --log-level-file=info --pg1-path=/var/lib/
postgresql/15/main --repo1-host=192.168.122.120 --repo1-host-port=22
--repo1-host-user=postgres --stanza=pg1
2023-07-11 08:59:07.274 P00   INFO: unable to find
00000001000000000000000E in the archive
2023-07-11 08:59:07.375 P00         INFO: archive-get command end: completed
successfully (440ms)
```

```text
2023-07-11 08:59:07.379 UTC [8786] LOG: recovery stopping before commit
of transaction 737, time 2023-07-11 08:55:13.072211+00
2023-07-11 08:59:07.379 UTC [8786] LOG:         pausing at the end of recovery


2023-07-11 08:59:07.379 UTC [8786] HINT:          Execute pg_wal_replay_resume()
to promote.
```

Như có thể thấy, để kết thúc quy trình PITR, PostgreSQL đề xuất chúng ta thực thi `pg_wal_replay_resume()`. Vì vậy, hãy vào PostgreSQL environment và thực hiện như sau:

```text
postgres=# select pg_wal_replay_resume();
 pg_wal_replay_resume
----------------------


(1 row)
```

Bây giờ, nếu kiểm tra database db1, table users đã xuất hiện và database hiện ở trạng thái giống như tại `2020-05-30 16:23:38`:

```text
postgres=# \d
           List of relations
 Schema | Name      | Type   |   Owner
--------+-------+-------+----------
 public | users | table | postgres
(1 row)
```

Cuối cùng, chúng ta có thể thực thi:

```text
postgres=# select count(*) from users ;
 count
-------
 10000
(1 row)
```

Bây giờ chúng ta đã khôi phục được trạng thái tồn tại trước disaster.

Như đã thấy, quản lý continuous backup và PITR bằng pgbackrest thực sự đơn giản. Continuous backup và PITR không bao giờ nên bị thiếu trong setup của một production environment phức tạp. Điều này bảo vệ chúng ta khỏi việc data bị xóa ngoài ý muốn và cung cấp một “last resort” để sử dụng khi cả primary và replica server đều không còn khả dụng.

## Migrate từ MySQL/MariaDB sang PostgreSQL bằng pgloader

Trong section này, chúng ta sẽ xem cách migrate một database từ thế giới MySQL/MariaDB sang thế giới PostgreSQL theo một cách rất đơn giản. Tool chúng ta sẽ sử dụng có tên là pgloader. Có thể tìm thấy tài liệu tham khảo để biết thêm thông tin về section này tại https://pgloader.io.

Có hai Docker container dành cho section này, một container chứa MariaDB server và một container chứa PostgreSQL server. MariaDB server có tên mariadb-source chứa một bản sao của database forumdb được sử dụng trong Chapter 4; PostgreSQL server có tên pg-destination chứa một database forumdb trống. Mục tiêu của chúng ta là migrate toàn bộ nội dung của database forumdb từ mariadb-source server sang postgresql-destination server bằng pgloader tool.

Hãy mở hai Bash terminal và thực thi lệnh sau trong terminal thứ nhất:

```text
chapter19$ bash run-pg-docker-mariadb.sh
```

Sau khi container đã khởi động, hãy thực thi statement dưới đây bằng LearnPostgreSQL làm password:

```text
root@mariadb-source:~# mysql -D forumdb -p
[...]
Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.


Type 'help;' or '\h' for help. Type '\c' to clear the current input
statement.


MariaDB [forumdb]>
```

Bây giờ chúng ta đang ở bên trong database forumdb và có thể thực hiện query trên đó:

```text
MariaDB [forumdb]> show tables;
+-------------------+
| Tables_in_forumdb |
+-------------------+
| categories             |
| j_posts_tags           |
| posts                  |
| tags                   |
| users                  |
+-------------------+
5 rows in set (0.000 sec)
```

```text
MariaDB [forumdb]> select * from categories;
+----+-----------------------+---------------------------------+
| pk | title                        | description                            |
+----+-----------------------+---------------------------------+
|   1 | Database                    | Database related discussions           |
|   2 | Unix                        | Unix and Linux discussions             |
|   3 | Programming Languages | All about programming languages |
+----+-----------------------+---------------------------------+
3 rows in set (0.002 sec)
```

```text
MariaDB [forumdb]> select * from users;
+----+-----------+----------------+---------------------+
| pk | username      | gecos             | email                    |
+----+-----------+----------------+---------------------+
|   1 | fluca1978 | Luca Ferrari         | fluca1978@gmail.com |
|   2 | sscotty71 | Enrico Pirozzi | sscptty71@gmail.com |
+----+-----------+----------------+---------------------+
2 rows in set (0.001 sec)
```

Như có thể thấy, database này giống database chúng ta đã sử dụng trong Chapter 4, Basic Statements.

Bây giờ hãy chuyển sang Bash terminal thứ hai và thực thi:

```text
chapter19$ bash run-pg-docker-postgresql.sh
```

Sau khi container khởi động, hãy thực thi:

```text
postgres@pg-destination:~$ psql forumdb
```

Như thấy dưới đây, PostgreSQL database của chúng ta đang trống:

```text
postgres@pg-destination:~$ psql forumdb
forumdb=# \d
Did not find any relations.
```

Bây giờ hãy thoát khỏi psql client và thực thi pgloader command:

```text
forumdb=# \q
ppostgres@pg-destination:~$ pgloader mysql://root:LearnPostgreSQL@mariadb-
source/forumdb pgsql://postgres@127.0.0.1/forumdb


              table name       errors         rows        bytes        total time
-----------------------      ---------    ---------    ---------    --------------
          fetch meta data             0           22                          0.104s
           Create Schemas             0            0                          0.000s
         Create SQL Types             0            0                          0.004s
            Create tables             0           10                          0.056s
           Set Table OIDs             0            5                          0.020s
-----------------------      ---------    ---------    ---------    --------------
       forumdb.categories             0            3      0.1 kB              0.020s
            forumdb.users             0            2      0.1 kB              0.016s
     forumdb.j_posts_tags             0            0                          0.012s
             forumdb.tags             0            0                          0.016s
            forumdb.posts             0            0                          0.012s
-----------------------      ---------    ---------    ---------    --------------
COPY Threads Completion               0            4                          0.024s
   Index Build Completion             0           11                          0.048s
           Create Indexes             0           11                          0.092s
          Reset Sequences             0            4                          0.012s
             Primary Keys             0            4                          0.004s
      Create Foreign Keys             0            6                          0.004s
          Create Triggers             0            0                          0.000s
          Set Search Path             0            1                          0.000s
         Install Comments             0            0                          0.000s
-----------------------      ---------    ---------    ---------    --------------
        Total import time             ✓            5      0.2 kB              0.184s
```

Bằng command đơn giản trên, chúng ta đã migrate MariaDB database forumdb vào PostgreSQL database forumdb. Bây giờ hãy kiểm tra xem mọi thứ đã được migrate chưa; hãy kết nối lại với forumdb trên PostgreSQL server:

```text
postgres@pg-destination:~$ psql forumdb
```

```text
forumdb=# \dn
          List of schemas
   Name     |       Owner
---------+-------------------
 forumdb | postgres
 public     | pg_database_owner
(2 rows)


forumdb=# \dt forumdb.*
                    List of relations
     Schema     |     Name       | Type    |   Owner
    ---------+--------------+-------+----------
     forumdb | categories        | table | postgres
     forumdb | j_posts_tags | table | postgres
     forumdb | posts             | table | postgres
     forumdb | tags              | table | postgres
     forumdb | users             | table | postgres
(5 rows)
```

Như có thể thấy ở trên, MariaDB database có tên forumdb đã được migrate sang PostgreSQL database có tên forumdb. pgloader tự động tạo một schema có tên forumdb, nơi chúng ta có thể tìm thấy tất cả table và data đến từ MariaDB database forumdb ban đầu; bây giờ điều duy nhất chúng ta cần là tạo một user có tên forumdb, user này có đủ permission để sử dụng toàn bộ data vừa import:

```text
forumdb=# create role forumdb with password 'LearnPostgreSQL' login;
CREATE ROLE


forumdb=# grant usage on schema forumdb to forumdb ;
GRANT
forumdb=# grant all on all tables in schema forumdb to forumdb ;
GRANT


forumdb=# \q
```
