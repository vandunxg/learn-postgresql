```text
   Column |      Type    | Collation | Nullable | Default


  --------+---------+-----------+----------+---------
   pk       | integer |                | not null |


   tag      | text       |             |             |


   parent | integer |                  |             |


  Indexes:
        "table_b_pk" PRIMARY KEY, btree (pk)
  Inherits: table_a
```

Ở đây, có thể thấy `table_b` là child table của `table_a`.

4. Bây giờ hãy xem hai table này hoạt động ra sao khi chúng ta insert, modify hoặc delete data. Ví dụ, hãy thực hiện một số thao tác insert như sau:

```text
  forumdb=> insert into table_a (pk,tag,parent) values (1,'Operating
  Systems',0);
  INSERT 0 1


  forumdb=> insert into table_b (pk,tag,parent) values (2,'Linux',0);
  INSERT 0 1
```

5. Hãy xem data phản ứng ra sao nếu chúng ta thực thi command `select`:

```text
  forumdb=> select * from table_b ;
   pk |    tag    | parent


  ----+-------+--------
    2 | Linux |           0
  (1 row)
```

Có thể thấy `table_b` có một record.

6. Bây giờ chúng ta thực thi command sau:

```text
  forumdb=>      select * from table_a ;
   pk |            tag          | parent


  ----+-------------------+--------
    1 | Operating Systems |            0
    2 | Linux                   |      0
  (2 rows)
```

Có vẻ như `table_a` có hai record. Điều này xảy ra vì table này kế thừa các attribute của table kia. Nếu thực thi một command `SELECT` trên parent table, chúng ta sẽ thấy tất cả record thuộc về parent table và tất cả record thuộc về child table.

7. Nếu muốn xem tất cả record chỉ thuộc về `table_a`, chúng ta phải dùng `ONLY` clause như sau:

```text
  forumdb=>    select * from only      table_a ;
   pk |           tag           | parent


  ----+-------------------+--------
    1 | Operating Systems |            0
  (1 row)
```

8. Hãy xem điều gì xảy ra nếu chúng ta `UPDATE` một số record; ví dụ, nếu thực thi câu lệnh sau:

```text
  forumdb=> update table_a set tag='BSD Unix' where pk=2;
  UPDATE 1
```

Chúng ta đã thực hiện một update operation trên `table_a`, nhưng update này về mặt physical được thực hiện trên `table_b` nhờ table inheritance, như có thể thấy ở đây:

```text
  forumdb=> select * from table_b;
   pk |     tag     | parent


  ----+----------+--------
    2 | BSD Unix |          0
  (1 row)
```

9. Điều tương tự cũng xảy ra nếu chúng ta sử dụng một `delete` statement như sau:

```text
  forumdb=> delete from table_a where pk=2;
  DELETE 1
```

Một lần nữa, delete operation được thực hiện trên `table_a` đã ảnh hưởng đến `table_b`; như có thể thấy ở đây, `table_a` sẽ có các record sau:

```text
  forumdb=> select * from table_a;
   pk |           tag           | parent


  ----+-------------------+--------
    1 | Operating Systems |             0
  (1 row)
```

Và lúc này `table_b` sẽ không có record nào:

```text
  forumdb=>    select * from table_b;
   pk | tag | parent


  ----+-----+--------
  (0 rows)
```

Trong PostgreSQL, inheritance propagate các operation được thực hiện trên parent table đến các child table.

## Dropping tables

Để kết luận về inheritance, chúng ta cần đề cập đến cách xóa table. Nếu muốn xóa một child table, chẳng hạn drop `table_b`, chúng ta phải chạy statement sau:

```text
 forumdb=>     drop table table_b;
 DROP TABLE
```

Nếu muốn drop một parent table cùng tất cả child table liên kết với nó, chúng ta phải chạy như sau:

```text
 forumdb=>     drop table table_a cascade;
```

Inheritance đã và vẫn có thể được dùng để triển khai table partitioning, nhưng kể từ version 10, declarative partitioning đã trở thành phương pháp được ưu tiên. Chúng ta sẽ trình bày declarative partitioning trong section tiếp theo.

## Exploring declarative partitioning

Trong section này, chúng ta sẽ nói về declarative partitioning. Tính năng này đã có trong PostgreSQL từ version 10, nhưng performance của nó đã tăng lên trong các version mới hơn. Bây giờ chúng ta sẽ xem một ví dụ partitioning by range và một ví dụ partitioning by list.

## List partitioning

Trong ví dụ đầu tiên về declarative partitioning, chúng ta sẽ dùng cùng ví dụ đã xem khi giới thiệu partitioning bằng inheritance. Chúng ta sẽ thấy mọi thứ trở nên đơn giản hơn nhiều khi dùng phương pháp declarative partitioning:

1. Bây giờ hãy tạo parent table:

```text
   forumdb=> CREATE TABLE part_tags (
    pk SERIAL NOT NULL ,


    level INTEGER NOT NULL DEFAULT 0,
    tag VARCHAR (255) NOT NULL,
    primary key (pk,level)
   )
   PARTITION BY LIST (level);
```

Như có thể thấy từ ví dụ trước, chúng ta phải định nghĩa loại partitioning muốn áp dụng. Trong trường hợp này, đó là `LIST PARTITIONING`. Một điểm quan trọng khác cần lưu ý là field được dùng để partition data phải là một phần của primary key.

2. Tiếp theo, hãy định nghĩa các child table:

```text
   forumdb=> CREATE TABLE part_tags_level_0 PARTITION OF part_tags FOR
   VALUES IN (0);
   CREATE TABLE part_tags_level_1 PARTITION OF part_tags FOR VALUES IN
   (1);
   CREATE TABLE part_tags_level_2 PARTITION OF part_tags FOR VALUES IN
   (2);
   CREATE TABLE part_tags_level_3 PARTITION OF part_tags FOR VALUES IN
   (3);
   CREATE TABLE
   CREATE TABLE
   CREATE TABLE
   CREATE TABLE
```

Với các SQL statement này, chúng ta đang định nghĩa rằng tất cả record có giá trị `level` bằng 0 sẽ được lưu trong table `part_tags_level_0`, tất cả record có giá trị `level` bằng 1 sẽ được lưu trong table `part_tags_level_1`, v.v.

3. Bây giờ hãy định nghĩa các index cho parent table. Các index này sẽ tự động được propagate đến child table. Chúng ta có thể thực hiện việc này bằng statement đơn giản sau:

```text
  forumdb=> CREATE INDEX on part_tags (tag);
  CREATE INDEX
```

4. Như được trình bày ở đây, quy trình partition của chúng ta đã hoàn tất.

Đối với các parent table, chúng ta có như sau:

```text
  forumdb=> \d part_tags;
                                      Partitioned table "forum.part_tags"
   Column |              Type             | Collation | Nullable |
  Default


  --------+------------------------+-----------+----------+-----------
  ----------------------------
   pk     | integer                |                   | not null |
  nextval('part_tags_pk_seq'::regclass)
   level    | integer                     |            | not null | 0
   tag      | character varying(255) |                 | not null |


  Partition key: LIST (level)
  Indexes:
       "part_tags_pkey" PRIMARY KEY, btree (pk, level)
       "part_tags_tag_idx" btree (tag)
  Number of partitions: 4 (Use \d+ to list them.)
```

Đối với các child table, chúng ta có như sau:

```text
  forumdb=>    \d part_tags_level_0;
                                                 Table "forum.part_tags_level_0"
   Column |              Type             | Collation | Nullable |
  Default


  --------+------------------------+-----------+----------+-----------
  ----------------------------
   pk     | integer                |                   | not null |
  nextval('part_tags_pk_seq'::regclass)
   level    | integer                     |            | not null | 0
   tag      | character varying(255) |                 | not null |


  Partition of: part_tags FOR VALUES IN (0)
  Indexes:
      "part_tags_level_0_pkey" PRIMARY KEY, btree (pk, level)
      "part_tags_level_0_tag_idx" btree (tag)
```

5. Bây giờ hãy thực hiện một số operation `INSERT`:

```text
  forumdb=> insert into part_tags (tag,level) values ('Operating
  System',0);
  INSERT 0 1
  forumdb=> insert into part_tags (tag,level) values ('Linux',1);
  INSERT 0 1
  forumdb=> insert into part_tags (tag,level) values ('BSD Unix',1);
  INSERT 0 1
  forumdb=> insert into part_tags (tag,level) values ('DOS',1);
  INSERT 0 1
  forumdb=> insert into part_tags (tag,level) values ('Windows',2);
  INSERT 0 1
```

6. Cuối cùng, hãy kiểm tra xem mọi thứ có ổn không:

```text
  forumdb=> select * from part_tags;
   pk | level |          tag


  ----+-------+------------------
    1 |      0 | Operating System
    2 |      1 | Linux
    3 |      1 | BSD Unix
    4 |      1 | DOS
    5 |      2 | Windows
  (5 rows)


  forumdb=> select * from part_tags_level_0;


   pk | level |          tag


  ----+-------+------------------
    1 |      0 | Operating System


  (1 row)

  forumdb=> select * from part_tags_level_1;
   pk | level |       tag


  ----+-------+----------
    2 |       1 | Linux
    3 |       1 | BSD Unix
    4 |       1 | DOS
  (3 rows)
  forumdb=> select * from part_tags_level_2;
   pk | level |       tag


  ----+-------+---------
    5 |       2 | Windows
  (1 row)
```

Như vậy, chúng ta đã tạo thành công các partition theo list.

## Range partitioning

Sau khi đã thấy có thể partition by list theo cách rất đơn giản, hãy xem cách partition by range:

1. Như trước đó, hãy `DROP` table `part_tags` hiện có cùng child table của nó:

```text
  forumdb=> DROP TABLE IF EXISTS part_tags cascade;
  DROP TABLE
```

2. Giả sử chúng ta muốn có một table giống hệt table trước đó, nhưng bây giờ muốn table `part_tags` có một field `ins_date`, nơi lưu ngày tag được thêm vào. Chúng ta muốn partition by range trên field `ins_date` để đưa tất cả record được nhập trong January 2023, February 2023, March 2023 và April 2023 vào các table khác nhau. Dưới đây là tất cả statement giúp thực hiện việc này; chúng rất giống các statement đã xem trong section trước:

```text
  forumdb=> CREATE TABLE part_tags (
        pk serial NOT NULL,
        ins_date date not null default now()::date,
        tag VARCHAR (255) NOT NULL,

        level INTEGER NOT NULL DEFAULT 0,
        primary key (pk,ins_date)
   )
   PARTITION BY RANGE (ins_date);
   CREATE TABLE


   forumdb=> CREATE TABLE part_tags_date_01_2023 PARTITION OF part_tags
   FOR VALUES FROM ('2023-01-01') TO ('2023-01-31');
   CREATE TABLE


   forumdb=> CREATE TABLE part_tags_date_02_2023 PARTITION OF part_tags
   FOR VALUES FROM ('2023-02-01') TO ('2023-02-28');
   CREATE TABLE


   forumdb=> CREATE TABLE part_tags_date_03_2023 PARTITION OF part_tags
   FOR VALUES FROM ('2023-03-01') TO ('2023-03-31');
   CREATE TABLE


   forumdb=> CREATE TABLE part_tags_date_04_2023 PARTITION OF part_tags
   FOR VALUES FROM ('2023-04-01') TO ('2023-04-30');
   CREATE TABLE


   forumdb=> CREATE INDEX on part_tags(tag);
   CREATE INDEX
```

Như có thể thấy, hai khác biệt duy nhất là `PARTITION BY RANGE` và `FOR VALUES FROM .. TO ...`

3. Trong ví dụ này, cũng như ví dụ trước về list partitioning, chúng ta đã tạo được parent table và tất cả child table một cách đơn giản, và như có thể thấy trong snippet sau, statement `CREATE INDEX` đã được tự động propagate đến các child table:

```text
   forumdb=> \d part_tags;
              Partitioned table "forum.part_tags"
    Column   |           Type             | Collation | Nullable |
   Default


  ----------+------------------------+-----------+----------+---------
  ------------------------------
   pk       | integer                |            | not null |
  nextval('part_tags_pk_seq'::regclass)
   ins_date | date                    |           | not null |
  now()::date
   tag      | character varying(255) |           | not null |


   level     | integer                |           | not null | 0
  Partition key: RANGE (ins_date)
  Indexes:
      "part_tags_pkey" PRIMARY KEY, btree (pk, ins_date)
      "part_tags_tag_idx" btree (tag)
  Number of partitions: 4 (Use \d+ to list them.)


   forumdb=> \d part_tags_date_01_2023;
                                  Table "forum.part_tags_date_01_2023"
    Column   |           Type         | Collation | Nullable |
  Default


  ----------+------------------------+-----------+----------+---------
  ------------------------------
   pk       | integer                |            | not null |
  nextval('part_tags_pk_seq'::regclass)
   ins_date | date                    |           | not null |
  now()::date
   tag      | character varying(255) |           | not null |


   level     | integer                |           | not null | 0
  Partition of: part_tags FOR VALUES FROM ('2023-01-01') TO ('2023-01-
  31')
  Indexes:
      "part_tags_date_01_2023_pkey" PRIMARY KEY, btree (pk, ins_date)
      "part_tags_date_01_2023_tag_idx" btree (tag)
```

4. Như đã làm trước đó, hãy thực hiện một số operation `INSERT`:

```text
  forumdb=> insert into part_tags (tag,ins_date,level) values
  ('Operating Systems','2023-01-01',0);
  INSERT 0 1
  forumdb=> insert into part_tags (tag,ins_date,level) values
  ('Linux','2023-02-01',1);
  INSERT 0 1
  forumdb=> insert into part_tags (tag,ins_date,level) values ('BSD
  Unix','2023-03-01',1);
  INSERT 0 1
  forumdb=> insert into part_tags (tag,ins_date,level) values ('Rocky
  Linux Distro','2023-04-01',2);
  INSERT 0 1
```

5. Và bây giờ hãy kiểm tra xem mọi thứ có ổn không:

```text
  forumdb=> select * from part_tags;
   pk |   ins_date   |          tag            | level


  ----+------------+--------------------+-------
    1 | 2023-01-01 | Operating Systems         |     0
    2 | 2023-02-01 | Linux                     |     1
    3 | 2023-03-01 | BSD Unix                  |     1
    4 | 2023-04-01 | Rocky Linux Distro |            2
  (4 rows)


  forumdb=> select * from part_tags_date_01_2023;
   pk |   ins_date   |          tag           | level


  ----+------------+-------------------+-------
    1 | 2023-01-01 | Operating Systems |            0
  (1 row)


  forumdb=> select * from part_tags_date_02_2023;


   pk |   ins_date   |   tag   | level


  ----+------------+-------+-------
```
