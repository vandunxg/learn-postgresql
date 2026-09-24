Chúng ta đã thấy cách tạo một logical replica trong thực tế và đã đề cập đến một số vấn đề có thể xảy ra khi làm việc với logical replication.

Trong chapter tiếp theo, chúng ta sẽ nói về những tool và extension hữu ích. Chúng ta sẽ xem tool nào phù hợp nhất để giúp công việc của một PostgreSQL DBA trở nên dễ dàng hơn.

## Kiểm tra kiến thức

- Có thể viết query trên một subscription của logical replication server không?

  Có. Xem section Exploring logical replication setup để biết thêm chi tiết.

- Có thể có các field khác nhau trên một subscription của logical replication server không?

  Có thể có nhiều field hơn số field có trên publication server.

  Xem section Exploring logical replication setup để biết thêm chi tiết.

- Có phải configure file `pg_hba.conf` trước khi bắt đầu logical replication không?

  Có. Xem section Exploring logical replication setup để biết thêm chi tiết.

- Nếu sau một DDL statement trên publication server, subscription server không replicate data nào, tôi phải làm gì?

  Bạn phải replicate DDL statement trên subscription server. Xem section DDL commands để biết thêm chi tiết.

- Có thể bắt đầu logical replication từ một physical replication không?

  Có, trên PostgreSQL 16 thì có thể.

## Tài liệu tham khảo

- Website của Slony: https://www.slony.info
- Logical replication: https://www.postgresql.org/docs/current/logical-replication.html

## Tìm hiểu thêm trên Discord

Để tham gia cộng đồng Discord của cuốn sách này, nơi bạn có thể chia sẻ feedback, đặt câu hỏi cho tác giả và tìm hiểu về các bản phát hành mới, hãy quét QR code bên dưới:

https://discord.gg/jYWCjF6Tku

# 19. Các công cụ và extension hữu ích

Chapter này được xem là một appendix của cuốn sách. Trong chapter này, chúng ta sẽ nói về một số tool và extension giúp Database Administrator (DBA) tối đa hóa hiệu quả công việc bằng cách giảm thiểu effort cần thiết để hoàn thành công việc.

Chúng ta sẽ nói về các extension sau:

- `pg_trgm`
- Foreign data wrappers và extension `postgres_fdw`

Đây là hai extension chính thức của PostgreSQL. Một website có thể rất hữu ích để tìm các extension hiện có cho PostgreSQL là https://pgxn.org/.

Ngoài extension, chúng ta cũng sẽ nói về các tool hữu ích khác dành cho PostgreSQL DBA. Có hàng chục tool dành cho PostgreSQL, nhưng trong chapter này, chúng ta sẽ nói về:

- `pgbackrest`: một tool mạnh dùng để quản lý disaster recovery và point-in-time recovery (PITR);
- `pgloader`: một tool hữu ích để dễ dàng migrate từ MySQL, SQLite và MS SQL sang PostgreSQL; trong section này, chúng ta sẽ trình bày một ví dụ migrate từ MySQL sang PostgreSQL theo cách rất đơn giản.

Chapter này nhằm cung cấp một overview nhanh về một số PostgreSQL extension và tool hữu ích nhất.

Các chủ đề sau sẽ được đề cập:

- Khám phá extension `pg_trgm`
- Sử dụng foreign data wrappers và extension `postgres_fdw`
- Quản lý tool `pgbackrest`
- Khám phá tool `pgloader`

Trong chapter này, Docker container chỉ được sử dụng ở một số section.

## Yêu cầu kỹ thuật

Section này có một Docker container, bạn có thể tìm thấy container đó tại `learn_postgresql_16/docker-images/chapter19`; sau khi đi đến đúng path, hãy chạy:

```text
chapter19$ bash run-pg-docker-pg_trgm.sh chapter19-pg_trgm


postgres@learn_postgresql:~$ psql -U forum forumdb
forumdb=>
```

## Khám phá extension `pg_trgm`

Bây giờ chúng ta hãy quay lại Chapter 13, Indexes and Performance Optimization, trong section Indexes. Khi nói về indexing, chúng ta đã học cách làm cho query nhanh hơn thông qua việc sử dụng index. Tuy nhiên, B-tree index không index mọi loại operation. Bây giờ hãy xem xét các textual data type (`char`, `varchar` hoặc `text`). Chúng ta sẽ thấy rằng B-tree, khi sử dụng operator class `varchar_pattern_ops`, có thể index các text query cho những sentence bắt đầu bằng `search%`, nhưng không thể index các text query cho những sentence kết thúc bằng `%search` hoặc chứa `%search%`:

1. Trước khi đi sâu vào ví dụ, hãy đặt `enable_seqscan` thành `off` để buộc PostgreSQL sử dụng index nếu có. Chúng ta cần làm vậy vì trong trường hợp ví dụ này, PostgreSQL luôn sử dụng sequential scanning theo mặc định: table chỉ có một vài record và toàn bộ data hiện có trong table được lưu trên một page duy nhất:

   ```text
   forumdb=> set enable_seqscan to 'off';
   SET
   ```

2. Bây giờ, trong database của mình, chúng ta có thể thực thi query này trên table `categories`:

   ```text
   forumdb=> select pk,title from categories;
    pk |             title
   ----+-----------------------
       1 | Database
       2 | Unix
       3 | Programming Languages
   ```

3. Hãy tạo một B-tree index với varchar opclass để kiểm tra xem PostgreSQL có sử dụng index access tới table khi chúng ta thực hiện query với operator `like` hay không:

   ```text
   forumdb=> create index on categories using btree(title varchar_
   pattern_ops);
   CREATE INDEX
   ```

   Bây giờ hãy thực hiện một số query `like`:

4. Trong ví dụ đầu tiên, hãy thực hiện một query `like` sử dụng predicate `‘search%'`:

   ```text
   forumdb=> explain analyze select * from categories where title like
   'Da%';
                                                                                   QUERY PL
   AN
   ---------------------------------------------------------
    Index Scan using categories_title_idx on categories
   (cost=0.13..8.15 rows=1 width=68)
   (actual time=0.033..0.037 rows=1 loops=1)
        Index Cond: ((title ~>=~ 'Da'::text) AND (title ~<~ 'Db'::text))
        Filter: (title ~~ 'Da%'::text)
    Planning Time: 0.172 ms
    Execution Time: 0.075 ms
   (5 rows)
   ```

5. Trong ví dụ thứ hai, hãy thực hiện một query `like` sử dụng predicate `‘%search'`:

   ```text
   forumdb=> explain analyze select * from categories where title like
   '%Da%';
                                                                              QUERY PLAN
   ---------------------------------------------------------
    Seq Scan on categories (cost=10000000000.00..10000000001.04 rows=1
   width=68) (actual time=17.278..17.283 rows=1 loops=1)
        Filter: (title ~~ '%Da%'::text)
        Rows Removed by Filter: 2
   Planning Time: 0.101 ms
   JIT:
     Functions: 2
     Options: Inlining true, Optimization true, Expressions true,
   Deforming true
       Timing: Generation 0.477 ms, Inlining 5.469 ms, Optimization
   7.027 ms, Emission 4.750 ms, Total 17.722 ms
    Execution Time: 17.834 ms
   (9 rows)
   ```

Như có thể thấy, chỉ trong trường hợp đầu tiên PostgreSQL mới sử dụng index approach. Trong trường hợp thứ hai, PostgreSQL sử dụng sequential scan (vì không có index nào có thể sử dụng được). Để cải thiện kiểu search này, chúng ta có thể sử dụng extension `pg_trgm`, đây là một extension chính thức và nằm trong official PostgreSQL contribs package. Khi sử dụng extension này, PostgreSQL tách mỗi word thành một tập trigram và tạo một GIST hoặc GIN index trên đó. Ví dụ, nếu xét word `dog`, tập trigram của nó gồm `d`, `do`, `og` và `dog`. Hãy xem cách hoạt động này trong thực tế:

1. Trước hết, hãy cài đặt extension:

   ```text
   forumdb=> create extension pg_trgm;
   CREATE EXTENSION
   ```

2. Bây giờ chúng ta có thể tạo GIN hoặc GIST index bằng opclass trigram. Ví dụ, hãy tạo một GIN index bằng opclass `gin_trgm_ops`:

   ```text
   forumdb=> create index           on categories using gin (title gin_trgm_
   ops);
   CREATE INDEX
   ```

3. Bây giờ hãy thực hiện query `like`:

   ```text
   forumdb=> explain analyze select * from categories where title like
   'Da%';
                                                                                       QUERY PL
   AN
   ---------------------------------------------------------- Index
   Scan using categories_title_idx on categories (cost=0.13..8.15
   rows=1 width=68) (actual time=0.029..0.032 rows=1 loops=1)
        Index Cond: ((title ~>=~ 'Da'::text) AND (title ~<~ 'Db'::text))
        Filter: (title ~~ 'Da%'::text)
    Planning Time: 0.217 ms
    Execution Time: 0.069 ms
   (5 rows)
   ```

Như có thể thấy ở đây, PostgreSQL hiện có thể tạo index access bằng một query `like`. Điều tương tự xảy ra với mọi loại query `like` và `ilike`; extension `pg_trgm` giải quyết access index cho các table của loại query này. Để biết thêm thông tin về extension `pg_trgm`, xem https://www.postgresql.org/docs/current/pgtrgm.html.

Extension `pg_trgm` giúp công việc của DBA dễ dàng hơn trong mọi trường hợp cần optimize query `like` và `ilike`. Bây giờ chúng ta sẽ chuyển sang extension tiếp theo, `postgres_fdw`.

## Sử dụng foreign data wrappers và extension `postgres_fdw`

Foreign data wrapper cho phép chúng ta truy cập data được host trên một external database như thể data đó được lưu trong một local table thông thường. Chúng ta có thể connect PostgreSQL tới nhiều data source khác nhau; có thể connect PostgreSQL tới một PostgreSQL server khác, hoặc connect PostgreSQL tới một data source khác, dù data source đó là relational hay non-relational. Khi foreign data wrapper đã được connect, PostgreSQL có thể đọc remote table như thể đó là local table. Có foreign data wrapper dành cho những database phổ biến như Oracle và MySQL, cũng như foreign data wrapper dành cho những system ít phổ biến hơn. Danh sách đầy đủ các foreign data wrapper hiện có cho PostgreSQL được cung cấp tại https://wiki.postgresql.org/wiki/Foreign_data_wrappers.

Trong section này, chúng ta sẽ xét một ví dụ sử dụng foreign data wrapper `postgresql_fdw`, được dùng để connect một PostgreSQL server tới một PostgreSQL server khác.

Nếu muốn sử dụng Docker image, chúng ta phải mở hai Bash terminal; trong terminal đầu tiên, thực thi:

```text
chapter19$ bash run-pg-docker.sh chapter19-postgresql_fdw
postgres@pg_fdw1:~$ psql -U forum forumdb
forumdb=> select * from categories;
 pk | title | description
----+-------+-------------
(0 rows)
```

Sau đó, trong Bash terminal thứ hai, thực thi:

```text
chapter19$ bash run-pg-docker-pg_fdw2.sh chapter19-postgresql_fdw
postgres@pg_fdw2:~$ psql -U forum forumdb
forumdb=> select * from categories;
   pk |           title            |             description
----+----------------------------+----------------------------
     1 | Database                  | Database related discussions
     2 | Unix                      | Unix and Linux discussions
     3 | Programming Languages | All about programming languages
(3 rows)
```

Tình huống ban đầu của chúng ta gồm hai server. Một server có tên `pg_fdw1` với IP address `192.168.16.2`, và server thứ hai có tên `pg_fdw2` với IP address `192.168.16.3`. Mục tiêu là connect server `pg_fdw2` tới server `pg_fdw1` và cho phép query category table của server `pg_fdw2` từ server `pg_fdw1` như thể đó là local table:

1. Hãy bắt đầu bằng việc cài đặt extension `postgres_fdw` trên server `pg_fdw1`. Với tư cách superuser `postgresql`, hãy thực thi:

   ```text
   postgres@pg_fdw1:~$ psql -U postgres forumdb


   forumdb=# create extension postgres_fdw ;
   CREATE EXTENSION
   ```

   Giả sử trên server `pg_fdw2`, `pg_hba.conf` được configure như sau:

   ```text
   host    all                  all               192.168.16.0/24
   scram-sha-256
   ```

2. Bây giờ chúng ta phải tạo connection giữa hai server bằng statement dưới đây trên server `pg_fdw1`:

   ```text
   forumdb=# CREATE SERVER remote_pg_fdw2 FOREIGN DATA WRAPPER
   postgres_fdw OPTIONS (host 'pg_fdw2', dbname 'forumdb');
   CREATE SERVER
   ```

3. Bây giờ chúng ta phải viết một user map giữa hai server:

   ```text
   forumdb=# CREATE USER MAPPING FOR forum SERVER remote_pg_fdw2
   OPTIONS (user 'forum', password 'LearnPostgreSQL');
   CREATE USER MAPPING
   ```

4. Bây giờ chúng ta phải tạo một foreign table với SELECT permission cho user `forum`:

   ```text
   forumdb=# create foreign table forum.f_categories (
             pk integer,
             title text,
             description text
   )
   SERVER remote_pg_fdw2 OPTIONS (schema_name 'forum', table_name
   'categories');
   grant SELECT ON forum.f_categories to forum;
   CREATE FOREIGN TABLE
   GRANT
   ```

   Bây giờ chúng ta có thể query table `forum.f_categories` như thể đó là một local table:

   ```text
   postgres@pg_fdw1:~$      psql -U forum forumdb
   forumdb=> select * from f_categories ;
       pk |         title            |              description
   ----+-----------------------+----------------------------
        1 | Database                 | Database related discussions
        2 | Unix                     | Unix and Linux discussions
        3 | Programming Languages | All about programming languages
   (3 rows)
   ```

Như có thể thấy trong ví dụ trước, chúng ta có thể query một foreign table như thể table đó nằm trên local server.

Foreign data wrapper là những tool rất mạnh, hỗ trợ công việc của DBA mỗi khi cần đọc data từ external source. Những external source này có thể là PostgreSQL server, nhưng cũng có thể là các loại server khác, chẳng hạn MySQL, Oracle hoặc SQL server.

Để biết thêm thông tin, xem https://www.postgresql.org/docs/current/postgres-fdw.html.

## Disaster recovery với `pgbackrest`

Trong Chapter 18, Logical Replication, chúng ta đã nói về disaster recovery và PITR, đồng thời đã thấy cách thực hiện chúng bằng program. Trong thực tế, DBA phải quản lý nhiều PostgreSQL server và sẽ hữu ích nếu có một số tool giúp công việc dễ dàng hơn. Thế giới open source cung cấp nhiều solution để giải quyết disaster recovery một cách dễ dàng. Một số tool được liệt kê ở đây:

- WAL-E
- pgbarman
- OmniPITR
