```text
      temperature | numeric(8,6)                    | [...]


   Partition key: RANGE (insert_time)
   Indexes:
         "basilea_partitioned_pkey" PRIMARY KEY, btree (id, insert_time)
   Partitions: basilea_partitioned_1950 FOR VALUES FROM ('1949-12-31
   23:00:00+00') TO ('1950-12-31 23:00:00+00'),
            basilea_partitioned_1951 FOR VALUES FROM ('1950-12-31
   23:00:00+00') TO ('1951-12-31 23:00:00+00'),
   [....]
               basilea_partitioned_2023 FOR VALUES FROM ('2022-12-31
   23:00:00+00') TO ('2023-12-31 23:00:00+00'),
                  basilea_partitioned_default DEFAULT
```

Table được partition theo năm từ 1950 đến 2022, đồng thời cũng có một table mặc định (như đã giải thích trong section Default Partition).

Data được chia đều giữa tất cả các child table, và nếu thử thực thi cùng query, chúng ta sẽ nhận được kết quả sau:

```text
   world_temperatures=# explain analyze select extract (year from insert_time) as
   year, avg(temperature) avg_temp from basilea_partitioned group by 1 order by
   2 desc limit 5;



   QUERY PLAN


   ------------------------------------------------------------------------------
   ------------------------------------------------------------------------------
   -----------------------------------------
    Limit (cost=13183.59..13183.61 rows=5 width=64) (actual
   time=169.996..174.092 rows=5 loops=1)
      -> Sort (cost=13183.59..13184.09 rows=200 width=64) (actual
   time=169.995..174.090 rows=5 loops=1)
              Sort Key: (avg(basilea_partitioned.temperature)) DESC
              Sort Method: top-N heapsort       Memory: 25kB
            -> Finalize GroupAggregate (cost=13127.60..13180.27 rows=200
   width=64) (actual time=169.812..174.060 rows=73 loops=1)
                     Group Key: (EXTRACT(year FROM basilea_partitioned.insert_time))
                  -> Gather Merge (cost=13127.60..13174.27 rows=400
   width=64) (actual time=169.802..173.941 rows=132 loops=1)
                        Workers Planned: 2
                        Workers Launched: 2
                        -> Sort (cost=12127.58..12128.08 rows=200 width=64)
   (actual time=140.386..140.401 rows=44 loops=3)
                               Sort Key: (EXTRACT(year FROM basilea_
   partitioned.insert_time))
                               Sort Method: quicksort    Memory: 30kB
                               Worker 0:   Sort Method: quicksort    Memory: 29kB
                               Worker 1:   Sort Method: quicksort    Memory: 29kB
                              -> Partial HashAggregate
   (cost=12116.93..12119.93 rows=200 width=64) (actual time=140.330..140.363
   rows=44 loops=3)
                                     Group Key: (EXTRACT(year FROM basilea_
   partitioned.insert_time))
                                     Batches: 1    Memory Usage: 64kB
                                     Worker 0:    Batches: 1   Memory Usage: 48kB
                                     Worker 1:    Batches: 1   Memory Usage: 64kB
                                    -> Parallel Append (cost=0.00..10780.64
   rows=267259 width=40) (actual time=0.010..79.251 rows=213304 loops=3)
                                          -> Parallel Seq Scan on basilea_
   partitioned_1952 basilea_partitioned_3 (cost=0.00..129.59 rows=5167
   width=40) (actual time=0.010..3.176 rows=8784 loops=1)
   [....]
                                            ->Parallel Seq Scan on basilea_
   partitioned_2018 basilea_partitioned_69 (cost=0.00..128.41 rows=5153
   width=40) (actual time=0.004..2.671 rows=8760 loops=1)
                                            -> Parallel Seq Scan on basilea_
   partitioned_2021 basilea_partitioned_72 (cost=0.00..128.41 rows=5153
   width=40) (actual time=0.003..2.651 rows=8760 loops=1)
                                          -> Parallel Seq Scan on basilea_
   partitioned_default basilea_partitioned_75 (cost=0.00..21.10 rows=888
   width=40) (actual time=0.000..0.000 rows=0 loops=1)
                                          -> Parallel Seq Scan on basilea_
   partitioned_2023 basilea_partitioned_74 (cost=0.00..1.01 rows=1 width=40)
   (actual time=0.008..0.009 rows=1 loops=1)
    Planning Time: 0.698 ms

   Execution Time: 174.250 ms
   (97 rows)
```

Như chúng ta có thể thấy, trước tiên PostgreSQL thực hiện một sequential scan song song, sau đó thực hiện một parallel append để merge toàn bộ data lấy được từ các child table.

Bây giờ hãy thử thực hiện cùng operation, nhưng lọc các năm trong khoảng từ 2021 đến 2022. Trên table không partition, chúng ta sẽ có kết quả sau:

```text
   world_temperatures=# explain analyze select extract (year from insert_
   time) as year, avg(temperature) avg_temp from basilea where insert_time
   >='2021-01-01' and insert_time < '2023-01-01' group by 1 order by 2 desc
   limit 5;


   QUERY PLAN


   ------------------------------------------------------------
    Limit (cost=11498.05..11498.06 rows=5 width=64) (actual
   time=24.532..28.875 rows=2 loops=1)
      -> Sort (cost=11498.05..11544.43 rows=18554 width=64) (actual
   time=24.529..28.871 rows=2 loops=1)
              Sort Key: (avg(temperature)) DESC
              Sort Method: quicksort        Memory: 25kB
            -> Finalize HashAggregate (cost=10911.56..11189.87 rows=18554
   width=64) (actual time=24.467..28.859 rows=2 loops=1)
                     Group Key: (EXTRACT(year FROM insert_time))
                     Batches: 1     Memory Usage: 793kB
                  -> Gather (cost=9133.43..10795.60 rows=15462 width=64)
   (actual time=24.159..28.707 rows=6 loops=1)
                             Workers Planned: 2
                             Workers Launched: 2
                        -> Partial HashAggregate (cost=8133.43..8249.40
   rows=7731 width=64) (actual time=20.170..20.211 rows=2 loops=3)
                                    Group Key: EXTRACT(year FROM insert_time)
                                    Batches: 1     Memory Usage: 409kB
                                    Worker 0:     Batches: 1    Memory Usage: 409kB
                                    Worker 1:     Batches: 1    Memory Usage: 409kB
                              -> Parallel Seq Scan on basilea
   (cost=0.00..8094.78 rows=7731 width=40) (actual time=16.211..18.330
   rows=5840 loops=3)
                                    Filter: ((insert_time >= '2021-01-01
   00:00:00+00'::timestamp with time zone) AND (insert_time < '2023-01-01
   00:00:00+00'::timestamp with time zone))
                                       Rows Removed by Filter: 207464
    Planning Time: 0.248 ms
    Execution Time: 30.043 ms
   (20 rows)
```

Với table đã partition, chúng ta sẽ có kết quả sau:

```text
   world_temperatures=# explain analyze select extract (year from insert_
   time) as year, avg(temperature) avg_temp from basilea_partitioned where
   insert_time >='2021-01-01' and insert_time < '2023-01-01' group by 1 order
   by 2 desc limit 5;


   QUERY PLAN


   ---------------------------------------------------------
    Limit (cost=618.10..618.11 rows=5 width=64) (actual time=15.205..15.208
   rows=2 loops=1)
      -> Sort (cost=618.10..618.60 rows=200 width=64) (actual
   time=15.203..15.205 rows=2 loops=1)
             Sort Key: (avg(basilea_partitioned.temperature)) DESC
             Sort Method: quicksort    Memory: 25kB
            -> HashAggregate (cost=611.78..614.78 rows=200 width=64)
   (actual time=15.190..15.194 rows=2 loops=1)
                   Group Key: (EXTRACT(year FROM basilea_partitioned.insert_
   time))
                   Batches: 1    Memory Usage: 40kB
                  -> Append (cost=0.00..524.19 rows=17517 width=40) (actual
   time=0.032..8.804 rows=17520 loops=1)
                        -> Seq Scan on basilea_partitioned_2021
   basilea_partitioned_1 (cost=0.00..217.30 rows=8758 width=40) (actual
   time=0.030..4.466 rows=8759 loops=1)
                              Filter: ((insert_time >= '2021-01-01
   00:00:00+00'::timestamp with time zone) AND (insert_time < '2023-01-01
   00:00:00+00'::timestamp with time zone))
                                 Rows Removed by Filter: 1
                        -> Seq Scan on basilea_partitioned_2022
   basilea_partitioned_2 (cost=0.00..218.30 rows=8758 width=40) (actual
   time=0.003..2.930 rows=8760 loops=1)
                              Filter: ((insert_time >= '2021-01-01
   00:00:00+00'::timestamp with time zone) AND (insert_time < '2023-01-01
   00:00:00+00'::timestamp with time zone))
                        -> Seq Scan on basilea_partitioned_2023 basilea_
   partitioned_3 (cost=0.00..1.02 rows=1 width=40) (actual time=0.006..0.006
   rows=1 loops=1)
                              Filter: ((insert_time >= '2021-01-01
   00:00:00+00'::timestamp with time zone) AND (insert_time < '2023-01-01
   00:00:00+00'::timestamp with time zone))
       Planning Time: 0.439 ms
       Execution Time: 15.311 ms
   (17 rows)
```

Điều đầu tiên chúng ta thấy là PostgreSQL kiểm tra ít child table hơn khi có một `where` clause trên field được dùng để partition; parameter `constraint_exclusion` trong `postgresql.conf` làm cho điều này khả thi:

```text
   world_temperatures=# select * from pg_settings where name ='constraint_
   exclusion';
   -[ RECORD 1 ]-
   name               | constraint_exclusion
   setting            | partition
   unit               |


   category           | Query Tuning / Other Planner Options
   short_desc         | Enables the planner to use constraints to optimize
   queries.
   extra_desc      | Table scans will be skipped if their constraints
   guarantee that no rows match the query.
   context            | user
   vartype            | enum
   source             | default
   min_val            |


   max_val            |

   enumvals            | {partition,on,off}
   boot_val            | partition
   reset_val           | partition
   sourcefile          |


   sourceline          |
   pending_restart | f
```

Parameter này cho phép query optimizer loại một số child table khỏi việc tìm kiếm. Như có thể thấy trong đoạn code trước, các giá trị khả dĩ của parameter `constraint_exclusion` là:

- `on`: Khi đặt giá trị này, PostgreSQL kiểm tra tất cả table.
- `off`: Khi đặt giá trị này, PostgreSQL không kiểm tra bất kỳ constraint nào.
- `partition`: Với giá trị này, PostgreSQL kiểm tra constraint cho các subquery `UNION ALL` và chỉ kiểm tra các inheritance child table. `partition` là setting mặc định.

Để biết thêm thông tin, xem https://www.postgresql.org/docs/current/runtime-config-query.html#GUC-CONSTRAINT-EXCLUSION.

## Tóm tắt

Trong chapter này, chúng ta đã giới thiệu chủ đề table partitioning trong PostgreSQL. Partitioning table hữu ích khi table ngày càng lớn, khiến query ngày càng chậm. Chúng ta bắt đầu bằng việc giới thiệu các khái niệm cơ bản của partitioning. Chúng ta đã nói về range partitioning, list partitioning và hash partitioning. Chúng ta cũng đã xem qua một số ví dụ về list partitioning và range partitioning sử dụng tablespace.

Chúng ta sẽ quay lại chủ đề partitioning trong Chapter 13, Indexes and Performance Optimization. Trong chapter tiếp theo, chúng ta sẽ nói về cách PostgreSQL quản lý user, role và nói chung là security của database.

## Kiểm tra kiến thức

- Có thể thực hiện declarative partitioning trong PostgreSQL không?

  Có, kể từ PostgreSQL 10, có thể sử dụng declarative partitioning.

  Xem section Exploring declarative partitioning để biết thêm chi tiết.

- Nếu có một table như sau:

```sql
       CREATE TABLE mytable (
             pk serial NOT NULL,
             create_date date not null default now()::date,
             primary key (pk)
       )
```

- Có thể partition table đó theo range không? Có, có thể thực hiện bằng cách viết như sau:

```sql
       CREATE TABLE mytable (
             pk serial NOT NULL,
             create_date date not null default now()::date,
             primary key (pk,creat_edate)
       )PARTITION BY RANGE (create_date);
       CREATE TABLE


       forumdb=> CREATE TABLE part_tags_date_01 PARTITION OF part_tags FOR
       VALUES FROM (‘2023-01-01’) TO (‘2023-06-31’);
       forumdb=> CREATE TABLE part_tags_date_01 PARTITION OF part_tags FOR
       VALUES FROM (‘2023-07-01’) TO (‘2023-12-31’);
```

  Xem section Exploring declarative partitioning để biết thêm chi tiết.

- Default partition dùng để làm gì?

  Default partition bảo đảm không có data nào bị mất; nếu PostgreSQL không tìm thấy child table nào để lưu record, record sẽ được lưu trong default partition.

  Xem section The default partition để biết thêm chi tiết.

- Có thể chia data trên các disk khác nhau không?

  Có, có thể dùng tablespace.

  Xem section Partitioning and tablespaces để biết thêm chi tiết.

- PostgreSQL có quản lý index trên partitioned table không?

  Có, PostgreSQL quản lý index trên partitioned table; nếu build một index trên parent table, PostgreSQL sẽ tự build index đó trên tất cả child table.

## Tài liệu tham khảo

- Tài liệu chính thức của PostgreSQL về table partitioning: https://www.postgresql.org/docs/current/ddl-partitioning.html
- Tài liệu chính thức của PostgreSQL về inheritance: https://www.postgresql.org/docs/current/tutorial-inheritance.html
- PostgreSQL tuning: https://pgtune.leopard.in.ua
- Tài liệu chính thức của PostgreSQL về CONSTRAINT EXCLUSION: https://www.postgresql.org/docs/current/runtime-config-query.html#GUC-CONSTRAINT-EXCLUSION
- Tài liệu chính thức của PostgreSQL về trigrams: https://www.postgresql.org/docs/current/pgtrgm.html

## Tìm hiểu thêm trên Discord

Để tham gia cộng đồng Discord dành cho cuốn sách này, nơi bạn có thể chia sẻ feedback, đặt câu hỏi cho tác giả và tìm hiểu về các bản phát hành mới, hãy quét QR code bên dưới:

https://discord.gg/jYWCjF6Tku

![QR code Discord](../assets/part-034-qr-discord.png)

# 10 Người dùng, Role và Bảo mật Database

PostgreSQL là một database rất vững chắc và đặc biệt chú trọng đến security, cung cấp một infrastructure rất phong phú để xử lý permission, privilege và security policy. Chapter này xây dựng trên các khái niệm cơ bản được giới thiệu trong Chapter 3, Quản lý User và Connection, xem xét lại khái niệm role và mở rộng kiến thức với trọng tâm đặc biệt vào security và privilege được cấp cho role (một role có thể vừa là một user vừa là một group gồm nhiều user). Bạn sẽ học cách cấu hình mọi khía cạnh của một role để quản lý security cẩn thận, từ connection đến việc truy cập data bên trong database.

PostgreSQL cũng cung cấp một cơ chế mạnh có tên Row-Level Security (RLS), cho phép định nghĩa policy ở mức chi tiết để che một phần data đối với một số user nhất định.

Trong chapter này, bạn cũng sẽ tìm hiểu về Access Control List (ACL) và cách PostgreSQL xử lý permission ở bên trong, là kết quả của việc grant hoặc revoke privilege. Cuối cùng, bạn sẽ xem qua một cách ngắn gọn các thuật toán mã hóa password mà PostgreSQL cung cấp để lưu password của role một cách an toàn.

Chapter này bao gồm các chủ đề sau:

- Tìm hiểu về role
- ACL
- Grant và revoke permission
- RLS
- Mã hóa password của role
- Connection SSL
