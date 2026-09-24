```text
2 | 2023-02-01 | Linux |            1
(1 row)


forumdb=> select * from part_tags_date_03_2023;
 pk |   ins_date     |    tag     | level


----+------------+----------+-------
  3 | 2023-03-01 | BSD Unix |             1
(1 row)
forumdb=> select * from part_tags_date_04_2023;
 pk |   ins_date     |          tag            | level


----+------------+--------------------+-------
  4 | 2023-04-01 | Rocky Linux Distro |               2
(1 row)
```

Như chúng ta có thể thấy, toàn bộ data đã được partition chính xác.

## Bảo trì partition

Trong hai section trước, chúng ta đã xem declarative partitioning là gì và cách tạo các table được partition khi bắt đầu công việc từ đầu. Trong section này, chúng ta sẽ xem xét cách attach hoặc detach partition khi partitioned table đã tồn tại. Chúng ta sẽ xem cách thực hiện những việc sau:

- Attach một partition mới
- Detach một partition hiện có
- Attach một table hiện có vào parent table

### Attach một partition mới

Nếu muốn attach một partition mới vào parent table, chúng ta phải thực thi như sau:

```text
   forumdb=> CREATE TABLE part_tags_date_05_2023 PARTITION OF part_tags FOR
   VALUES FROM ('2023-05-01') TO ('2023-05-30');
   CREATE TABLE
```

Như chúng ta có thể thấy ở đây, một partition mới có tên `part_tags_date_05_2023` đã được thêm vào parent table `part_tags`:

```text
   forumdb=> \d+ part_tags;
                     Partitioned table "forum.part_tags"
     Column    |             Type             | [...] | Description


   ----------+------------------------+-------+-------------
    pk         | integer                      | [...] |


    ins_date | date                           | [...] |


    tag        | character varying(255) | [...] |


    level      | integer                      | [...] |


   Partition key: RANGE (ins_date)
   Indexes:
       "part_tags_pkey" PRIMARY KEY, btree (pk, ins_date)
       "part_tags_tag_idx" btree (tag)
   Partitions: part_tags_date_01_2023 FOR VALUES FROM ('2023-01-01') TO
   ('2023-01-31'),
             part_tags_date_02_2023 FOR VALUES FROM ('2023-02-01') TO
   ('2023-02-28'),
             part_tags_date_03_2023 FOR VALUES FROM ('2023-03-01') TO
   ('2023-03-31'),
             part_tags_date_04_2023 FOR VALUES FROM ('2023-04-01') TO
   ('2023-04-30'),
             part_tags_date_05_2023 FOR VALUES FROM ('2023-05-01') TO
   ('2023-05-30')
```

### Detach một partition hiện có

Nếu muốn detach một partition hiện có khỏi parent table, chúng ta phải thực thi như sau:

```text
   forumdb=> ALTER TABLE part_tags DETACH PARTITION part_tags_date_05_2023 ;
   ALTER TABLE
```

Như chúng ta có thể thấy ở đây, partition có tên `part_tags_date_05_2023` đã được detach khỏi parent table `part_tags`:

```text
   forumdb=> \d+ part_tags;
                     Partitioned table "forum.part_tags"
     Column    |             Type             | [...] | Description


   ----------+------------------------+-------+-------------
    pk         | integer                    | [...] |


    ins_date | date                         | [...] |


    tag        | character varying(255) | [...] |


    level      | integer                    | [...] |


   Partition key: RANGE (ins_date)
   Indexes:
         "part_tags_pkey" PRIMARY KEY, btree (pk, ins_date)
         "part_tags_tag_idx" btree (tag)
   Partitions: part_tags_date_01_2023 FOR VALUES FROM ('2023-01-01') TO
   ('2023-01-31'),
             part_tags_date_02_2023 FOR VALUES FROM ('2023-02-01') TO
   ('2023-02-28'),
             part_tags_date_03_2023 FOR VALUES FROM ('2023-03-01') TO
   ('2023-03-31'),
             part_tags_date_04_2023 FOR VALUES FROM ('2023-04-01') TO
   ('2023-04-30')
```

### Attach một table hiện có vào parent table

Để thực hành việc này, chúng ta cần một table có tên `part_tags_already_exists` hiện diện trong database và chứa tất cả tag có ngày nhập trước `2022-12-31`. Nếu đang sử dụng Docker image, bạn có thể tìm table này trong database `forumdb`. Nếu không, hãy đảm bảo tạo table với structure sau:

```text
   forumdb=> \d part_tags_already_exists
                      Table "forum.part_tags_already_exists"
       Column    |           Type             | Collation | Nullable | Default


   ----------+------------------------+-----------+---------
    pk         | integer                |             | not null


    ins_date | date                         |             | not null


    tag        | character varying(255) |                   | not null


    level      | integer                      |             | not null


   Indexes:
        "part_tags_already_exists_pkey" PRIMARY KEY, btree (pk, ins_date)
        "part_tags_already_exists_tag_idx" btree (tag)
```

Nếu muốn attach table này, vốn chứa tất cả tag có ngày nhập trước `2022-12-31`, vào parent table, chúng ta phải chạy statement sau:

```text
   forumdb=> ALTER TABLE part_tags ATTACH PARTITION part_tags_already_exists
   FOR VALUES FROM ('1970-01-01') TO ('2022-12-31');
   ALTER TABLE
```

Bằng cách này, table `part_tags_already_exists` trở thành child table của parent table `part_tags`.

## Default partition

Trong section này, chúng ta sẽ xem điều gì xảy ra nếu insert data vào partitioned table khi child partition chưa tồn tại, và cách giải quyết bất tiện do việc này gây ra. Để mô phỏng vấn đề này, giả sử chúng ta muốn insert một date tương ứng với `2023-05-01` vào table có tên `part_tags`. Chúng ta sẽ nhận được kết quả sau:

```text
   forumdb=> insert into part_tags (tag,ins_date,level) values ('Ubuntu
   Linux','2023-05-01',2);
   ERROR:    no partition of relation "part_tags" found for row
   DETAIL:    Partition key of the failing row contains (ins_date) = (2023-05-
   01).
```

Điều này xảy ra vì PostgreSQL không tìm thấy giá trị date `2023-05-01` trong mapping của các child table.

Để loại bỏ nhược điểm này, cần sử dụng một default partition, nơi mọi value không được ánh xạ tới child table sẽ được insert.

Để làm vậy, hãy thực thi statement sau:

```text
   forumdb=> CREATE TABLE part_tags_default PARTITION OF part_tags default;
   CREATE TABLE
```

Bây giờ hãy thử lặp lại entry trước đó:

```text
   forumdb=> insert into part_tags (tag,ins_date,level) values ('Ubuntu
   Linux','2023-05-01',2);
   INSERT 0 1
```

Tại thời điểm này, data đã được insert vào default partition và có thể nhìn thấy từ parent table `part_tags`, như chúng ta thấy ở đây:

```text
   forumdb=> select * from part_tags;
      pk |   ins_date   |       tag           | level
   ----+------------+--------------------+-------
       1 | 2023-01-01 | Operating Systems     |     0
       2 | 2023-02-01 | Linux                 |     1
       3 | 2023-03-01 | BSD Unix              |     1
       4 | 2023-04-01 | Rocky Linux Distro |        2
       6 | 2023-05-01 | Ubuntu Linux          |     2
   (5 rows)


   forumdb=> select * from part_tags_default ;
      pk |   ins_date   |    tag       | level


   ----+------------+--------------+-------
       6 | 2023-05-01 | Ubuntu Linux |        2
   (1 row)
```

## Partitioning và tablespace

Bây giờ giả sử chúng ta muốn sử dụng các tablespace đã xem trong Chapter 2 cùng với cách partitioning vừa thực hiện. Bằng kỹ thuật này, chúng ta có thể đặt các child table trên những tablespace khác nhau, và do đó trên những directory khác nhau có thể được mount trên các volume khác nhau.

Cách làm này có thể tăng read/write performance. Trong ví dụ sau, chúng ta sẽ chỉ tạo hai tablespace trên các local directory. Tuy nhiên, không khó để sử dụng command `mount` nhằm map hai directory này vào các volume khác nhau. Nếu đang sử dụng Docker image được cung cấp cùng chapter này, hai directory chúng ta sẽ dùng đã có sẵn.

Nếu không sử dụng Docker image, trước tiên bạn cần tạo hai directory, `/data/tablespaces/ts_b` và `/data/tablespaces/ts_b`, nơi system user `postgres` có thể read và write data.

Bây giờ hãy connect tới database `forumdb` với tư cách user `postgres` và tạo hai tablespace có tên `ts_a` và `ts_b`:

```text
   postgres@learn_postgresql:~$ psql -U postgres forumdb


   forumdb=# create tablespace ts_a location '/data/tablespaces/ts_a';
   CREATE TABLESPACE
   forumdb=# create tablespace ts_b location '/data/tablespaces/ts_b';
   CREATE TABLESPACE
```

Hãy gán ownership cho user `postgres`:

```text
   forumdb=# alter tablespace ts_a owner to forum ;
   ALTER TABLESPACE
   forumdb=#      alter tablespace ts_b owner to forum ;
   ALTER TABLESPACE
```

Bây giờ hãy connect lại tới database `forumdb` với tư cách user `forum`:

```text
   forumdb=# \q
   postgres@learn_postgresql:~$ psql -U forum forumdb
```

Như trong trường hợp trước, hãy tạo lại parent table:

```text
   forumdb=> CREATE TABLE tablespace_part_tags (
            pk serial NOT NULL,
            ins_date date not null default now()::date,
            tag VARCHAR (255) NOT NULL,
            level INTEGER NOT NULL DEFAULT 0,

          primary key (pk,ins_date)
   )
   PARTITION BY RANGE (ins_date);
   CREATE TABLE
```

Bây giờ hãy tạo hai child table và một default table. Child table đầu tiên sẽ được tạo trên tablespace `ts_a` và child table thứ hai trên tablespace `ts_b`:

```text
   forumdb=> CREATE TABLE tablespace_part_tags_date_2022 PARTITION OF
   tablespace_part_tags FOR VALUES FROM ('2021-01-01') TO ('2022-12-31')
   TABLESPACE ts_a;
   CREATE TABLE
   forumdb=> CREATE TABLE tablespace_part_tags_date_2023 PARTITION OF
   tablespace_part_tags FOR VALUES FROM ('2023-01-01') TO ('2023-12-31')
   TABLESPACE ts_b;
   CREATE TABLE
   forumdb=> CREATE TABLE tablespace_part_tags_date_default PARTITION OF
   tablespace_part_tags default;
   CREATE TABLE
```

Bây giờ, hãy insert một số data:

```text
   forumdb=> insert into tablespace_part_tags (tag,ins_date,level) values
   ('Operating Systems','2022-01-01',0), ('Linux','2022-02-01',1),('BSD
   Unix','2023-03-01',1),('Rocky Linux Distro','2018-04-01',2);
   INSERT 0 4
```

Sau đó, hãy xem các record đã được lưu ở đâu:

```text
   forumdb=> select * from tablespace_part_tags;
      pk |   ins_date   |         tag            | level


   ----+------------+--------------------+-------
       1 | 2022-01-01 | Operating Systems        |      0
       2 | 2022-02-01 | Linux                    |      1
       3 | 2023-03-01 | BSD Unix                 |      1
       4 | 2018-04-01 | Rocky Linux Distro |            2
   (4 rows)


   forumdb=> select * from tablespace_part_tags_date_2022 ;
      pk |   ins_date   |         tag           | level


   ----+------------+-------------------+-------
      1 | 2022-01-01 | Operating Systems |               0
      2 | 2022-02-01 | Linux                      |      1
   (2 rows)


   forumdb=> select * from tablespace_part_tags_date_2023 ;
    pk |    ins_date    |     tag     | level


   ----+------------+----------+-------
      3 | 2023-03-01 | BSD Unix |             1
   (1 row)


   forumdb=>select * from tablespace_part_tags_date_default;
    pk |    ins_date    |           tag            | level


   ----+------------+--------------------+-------
      4 | 2018-04-01 | Rocky Linux Distro |                2
   (1 row)
```

Như chúng ta đã thấy trong exercise này, data đã được chia vào các tablespace khác nhau, và kết quả là tốc độ đã tăng gấp đôi. Đây là một kỹ thuật rất hiệu quả.

## Một case study đơn giản

Trong section cuối cùng này, chúng ta sẽ không sử dụng database `forumdb`. Thay vào đó, database chúng ta sẽ sử dụng có tên `world_temperatures`, trong đó public data đã được import từ public CSV tại https://www.meteoblue.com/it/tempo/archive/export.

Database backup `db-world-temperatures` có thể tìm thấy trên GitHub của Packtpub, trong directory `chapter 9`, với tên file `backup-db-world-temperatures.sql.gz`. Nếu đang sử dụng Docker image, bạn đã có mọi thứ cần thiết; nếu không, để import database, hãy chạy PostgreSQL trên server của bạn:

```text
   $ gunzip < backup-db-world-temperatures.sql.gz | psql
```

Nếu đang sử dụng Docker image, chỉ cần thực thi lệnh sau:

```text
   postgres@learn_postgresql:~$ psql -U postgres world_temperatures
```

Bây giờ bạn sẽ có database `db-world-temperatures` sẵn sàng để sử dụng. Bên trong database, bạn sẽ tìm thấy một table chưa được partition có tên `basilea` và một partitioned table có tên `basilea_partitioned`; cả hai table đều chứa thông tin nhiệt độ của thành phố Basel từ năm 1950 đến năm 2022, được lấy mẫu ở các khoảng thời gian đều đặn theo giờ. Bây giờ, hãy xem sự khác biệt về cách hoạt động khi truy vấn một partitioned table và một non-partitioned table. Trước khi tiếp tục exercise, nếu chưa quen với cách hoạt động của statement `EXPLAIN`, hãy xem Chapter 13, The EXPLAIN Statement.

Hãy bắt đầu bằng cách sử dụng non-partitioned table và viết một query trả về average temperature của 5 năm lạnh nhất trong giai đoạn bắt đầu từ năm 1950:

```text
   world_temperatures=# select extract (year from insert_time) as year,
   avg(temperature) avg_temp from basilea group by 1 order by 2 limit 5;
      year |       avg_temp


   ------+--------------------
      1956 | 8.8073832344034608
      1963 | 8.9077977708904110
      1980 | 9.3459840948315118
      1969 | 9.3705488990867580
      1972 | 9.3749401615437158
   (5 rows)
```

Tương tự, hãy lấy 5 năm nóng nhất:

```text
   world_temperatures=# select extract (year from insert_time) as year,
   avg(temperature) avg_temp from basilea group by 1 order by 2 desc limit
   5;
      year |       avg_temp


   ------+---------------------
      2022 | 12.7320820592465753
      2018 | 12.5638742964611872
      2020 | 12.3662106902322404
      2014 | 12.0601722329908676
      2015 | 11.9246379973744292
   (5 rows)
```

Hãy lấy kết quả cuối cùng làm ví dụ và xem nội bộ nó được thực hiện như thế nào:

```text
   world_temperatures=# explain analyze select extract (year from insert_
   time) as year, avg(temperature) avg_temp from basilea group by 1 order by
   2 desc limit 5;
                                                                            QUERY PLAN


   --------------------------------------------------------------------------
   ----------------------------------------------------------
    Limit (cost=98293.21..98293.23 rows=5 width=64) (actual
   time=380.284..380.286 rows=5 loops=1)
      -> Sort (cost=98293.21..99892.99 rows=639912 width=64) (actual
   time=380.282..380.283 rows=5 loops=1)
              Sort Key: (avg(temperature)) DESC
              Sort Method: top-N heapsort        Memory: 25kB
            -> HashAggregate (cost=68067.20..87664.51 rows=639912 width=64)
   (actual time=380.121..380.253 rows=73 loops=1)
                       Group Key: EXTRACT(year FROM insert_time)
                       Planned Partitions: 32     Batches: 1     Memory Usage: 817kB
                  -> Seq Scan on basilea (cost=0.00..12074.90 rows=639912
   width=40) (actual time=0.030..189.680 rows=639912 loops=1)
    Planning Time: 0.170 ms
    Execution Time: 380.480 ms
   (10 rows)
```

Như chúng ta có thể thấy, PostgreSQL thực hiện sequential scan trên toàn bộ table. Bây giờ hãy xét partitioned table `basilea_partitioned`:

```text
   world_temperatures=# \d+ basilea_partitioned
                                                                          Partitioned
   table "public.basilea_partitioned"
       Column      |             Type               | [...]


   -------------+--------------------------+
    id             | integer                        | [...]


    insert_time | timestamp with time zone | [...]
```
