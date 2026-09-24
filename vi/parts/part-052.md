Ví dụ, hãy lưu ý trong statement `EXPLAIN` sau đây rằng actual time bị thiếu trong output:

```text
forumdb=> EXPLAIN (ANALYZE on, TIMING off) SELECT * FROM categories;
                                  QUERY PLAN
--------------------------------------------------------------------------
---------
Seq Scan on categories      (cost=0.00..1.05 rows=5 width=68) (actual rows=5
loops=1)
Planning Time: 0.113 ms
Execution Time: 0.047 ms
(3 rows)
```

Option `SUMMARY` báo cáo tổng thời gian dành cho việc planning execution và thời gian dành cho query execution, nhờ đó bạn có thể hình dung planner đã cần bao nhiêu effort để tìm ra execution plan tốt nhất.

Option `BUFFERS`, mặc định là off, cung cấp thông tin về các data buffer mà query đã sử dụng để hoàn tất. Ví dụ, hãy lưu ý thông tin liên quan đến buffer trên Execution node trong query sau:

```text
forumdb=> EXPLAIN (ANALYZE, BUFFERS on) SELECT * FROM posts;
                                                             QUERY PLAN
--------------------------------------------------------------------------
-----------------------------
Seq Scan on posts (cost=0.00..31.04 rows=1004 width=71) (actual
time=0.006..0.100 rows=1004 loops=1)
  Buffers: shared hit=21
Planning Time: 0.061 ms
Execution Time: 0.171 ms
(4 rows)
```

Thông tin về buffer không đơn giản để phân tích và có thể được chia thành hai phần: prefix và suffix.

Prefix có thể là một trong các giá trị sau:

- `shared`, nghĩa là một PostgreSQL shared buffer, tức database in-memory cache
- `temp`, nghĩa là temporary memory (được dùng cho sorting, hashing, v.v.)
- `local`, nghĩa là temporary database objects space (ví dụ, temporary tables)

Suffix có thể là một trong các giá trị sau:

- `hit`, cung cấp số lần memory access thành công
- `read`, cung cấp số buffer được đọc từ storage (vì vậy không nằm trong cache)
- `dirtied`, số buffer đã được query sửa đổi
- `written`, số buffer bị loại khỏi PostgreSQL cache và được ghi xuống disk
- `lossy`, số buffer mà PostgreSQL đã kiểm tra trong memory ở pass thứ hai

Kết hợp prefix và suffix sẽ cung cấp thông tin về các buffer. Ví dụ, trong query trước, dòng buffer chứa `shared hit=21`, có nghĩa là “21 buffer đã được tìm thấy thành công trong database cache, không cần thực hiện thêm operation nào trên buffer.”

Option `WAL` cung cấp thông tin về việc sử dụng WAL của một writing statement. Ví dụ, hãy xem query sau, query này thêm một loạt username giả vào table users:

```text
forumdb=> EXPLAIN (ANALYZE on, WAL on, FORMAT yaml)
INSERT INTO posts( title, content, author, created_on, category )
SELECT 'A random post title ' || v, md5( v::text ), v%2 + 1, current_date
- v, v%5 + 1
FROM generate_series( 1, 100000 ) v;


                             QUERY PLAN
----------------------------------------------------
- Plan:                                                      +
      Node Type: "ModifyTable"                               +
...
      Actual Loops: 1                                        +
      WAL Records: 506908                                    +
      WAL FPI: 651                                           +
      WAL Bytes: 46291062                                    +



...
```

Như bạn có thể thấy, output báo cáo thông tin về số WAL record đã được tạo ra (506908), số WAL Full Page Image (FPI) (651), và số byte được ghi vào WAL log (46291062). Vì vậy, statement trên đã tạo ra khoảng 46 MB WAL traffic.

> Kích thước WAL sẽ luôn lớn hơn kích thước thực tế của table. Ví dụ, trong ví dụ trước, data được tạo ra trong table có kích thước khoảng 13 MB, trong khi kích thước WAL lớn hơn nhiều, khoảng 46 MB. Lý do của sự khác biệt về kích thước này là PostgreSQL phải bảo đảm data an toàn trong WAL và hữu ích cho crash recovery; vì vậy, WAL không chỉ lưu content của data mà còn lưu metadata về cách restore content đó một cách chính xác.

## Ví dụ về query tuning

Trong section trước, bạn đã tìm hiểu cách `EXPLAIN` có thể hiển thị plan mà PostgreSQL sẽ dùng để truy cập underlying data; bây giờ là lúc dùng `EXPLAIN` để tune một số slow query và cải thiện performance.

Section này sẽ trình bày một số concept cơ bản trong việc sử dụng `EXPLAIN` hằng ngày như một tool mạnh để xác định PostgreSQL nên được instrument ở đâu và bằng cách nào để truy cập data nhanh hơn. Dĩ nhiên, query tuning là một chủ đề rất phức tạp và thường đòi hỏi optimization dựa trên việc thử nghiệm lặp lại, vì vậy mục tiêu của section này không phải là cung cấp cho bạn kiến thức chuyên sâu về query tuning, mà là giúp bạn có hiểu biết cơ bản về cách cải thiện database và query của chính mình.

Đôi khi, tuning một query chỉ đơn giản là viết lại query theo cách PostgreSQL thấy dễ xử lý hơn hoặc, chính xác hơn, dễ hiểu hơn; nhưng thường thì query tuning có nghĩa là sử dụng một index phù hợp để tăng tốc việc truy cập underlying data.

Một điều quan trọng cần tính đến khi query tuning là cache effect: khi PostgreSQL truy cập một phần data, nó load data đó vào memory trong shared buffers. Vùng memory này hoạt động như một cache; vì vậy, nếu PostgreSQL lại cần cùng data đó, nó sẽ lấy data từ memory thay vì đi tới disk storage. Hệ quả là query có thể chậm ở lần đầu, nhưng nếu được thực thi lần thứ hai và nói chung là thực thi lặp đi lặp lại, thời gian cần thiết có thể nhỏ hơn lần đầu. Vì vậy, khi kiểm tra một slow query, hãy thử thực thi nó nhiều lần hơn để xem caching effect có thể ảnh hưởng đến thời gian thực thi như thế nào.

Database của chúng ta được giả định là chứa một nghìn author, mỗi author publish năm trăm post, tổng cộng nửa triệu post:

```text
forumdb=> SELECT reltuples, pg_size_pretty( pg_relation_size( oid ) ),
relname FROM pg_class
WHERE relname IN ( 'posts', 'users' ) AND relkind = 'r';
reltuples | pg_size_pretty | relname
-----------+----------------+---------
    500000 | 59 MB                 | posts
      1000 | 88 kB                 | users
```

> Docker image cho chapter này đã được populate sẵn với lượng data trên. Hãy cẩn thận, vì lượng data đó sẽ yêu cầu bạn có khoảng 60 MB free disk space.

Hãy bắt đầu với một ví dụ đơn giản; chúng ta muốn lấy tất cả post theo thứ tự ngày tạo, vì vậy query là:

```sql
SELECT * FROM posts ORDER BY created_on;
```

Chúng ta có thể truyền query này cho `EXPLAIN` để có được hình dung về cách PostgreSQL sẽ thực thi nó:

```text
forumdb=> EXPLAIN SELECT * FROM posts ORDER BY created_on;
                                         QUERY PLAN
---------------------------------------------------------------------
Sort       (cost=83838.92..85088.92 rows=500000 width=81)
   Sort Key: created_on
   ->      Seq Scan on posts     (cost=0.00..12584.00 rows=500000 width=81)
```

Như bạn có thể thấy, node đầu tiên được thực thi là sequential scan (initial cost là 0), node này sẽ tạo ra 500.000 tuple làm output. Tại sao lại là sequential scan? Trước hết, không có filtering clause nào, vì chúng ta muốn lấy toàn bộ data được lưu trong table; thứ hai, table không có access method nào (không có index).

Vì chúng ta yêu cầu sort output, node tiếp theo được thực thi là một Sorting node, node này tạo ra đúng cùng số tuple trong result.

Mất bao nhiêu thời gian để hoàn tất query trước đó? `EXPLAIN ANALYZE` có thể giúp chúng ta trả lời câu hỏi đó:

```text
forumdb=> EXPLAIN ANALYZE SELECT * FROM posts ORDER BY created_on;
                                                           ------------------
--------------------------------------------------------------------------
-------------------------
Sort (cost=83838.92..85088.92 rows=500000 width=81) (actual
time=304.283..393.395 rows=500000 loops=1)
   Sort Key: created_on
   Sort Method: external merge       Disk: 51192kB
     -> Seq Scan on posts (cost=0.00..12584.00 rows=500000 width=81)
(actual time=0.045..63.449 rows=500000 loops=1)
Planning Time: 0.059 ms
Execution Time: 429.838 ms
```

Pure execution time gần nửa giây. Có thể giảm tổng thời gian bằng cách build một index riêng trên field `created_on` hay không:

```text
forumdb=> CREATE INDEX idx_posts_date ON posts( created_on );
CREATE INDEX
forumdb=> EXPLAIN ANALYZE SELECT * FROM posts ORDER BY created_on;


QUERY PLAN
--------------------------------------------------------------------------
-------------------------------------------------------------
Index Scan using idx_posts_date on posts (cost=0.42..16887.80 rows=500000
width=81) (actual time=0.079..133.305 rows=500000 loops=1)
Planning Time: 0.203 ms
Execution Time: 162.143 ms
(3 rows)
```

Query hiện chạy trong gần một phần ba thời gian cần thiết khi không có index, và trên thực tế query plan đã thay đổi từ sequential scan thành index scan với index mới được tạo.

Dĩ nhiên, index mới được tạo có penalty về storage space; như bạn có thể hình dung, tốc độ tăng lên đi kèm một space cost bổ sung, có thể kiểm tra như sau:

```text
forumdb=> SELECT pg_size_pretty( pg_relation_size( 'posts' ) ) AS table_
size,
    pg_size_pretty( pg_relation_size( 'idx_posts_date' ) ) AS index_size;
   table_size | index_size
-------------+------------
59 MB         | 3600 kB
(1 row)
```

Việc space disk bổ sung này có quá nhiều hay không phụ thuộc vào resource và mục tiêu cuối cùng của bạn; trong trường hợp trước, giả sử bạn thực thi query khá thường xuyên, tốc độ tăng lên là xứng đáng với space bổ sung.

Bây giờ hãy tập trung vào một query điển hình hơn: tìm tất cả post của một user cụ thể trong một khoảng thời gian cụ thể. Query kết quả sẽ giống như sau, với giả định khoảng thời gian là 2 ngày:

```sql
SELECT p.title, u.username
FROM posts p
JOIN users u ON u.pk = p.author
WHERE u.username = 'fluca1978'
AND       daterange( CURRENT_DATE - 20, CURRENT_DATE ) @> p.created_on::date
```

PostgreSQL thực thi query trước đó như thế nào? Một lần nữa, `EXPLAIN` có thể giúp chúng ta hiểu database cho rằng query plan tốt nhất là gì:

```text
forumdb=> EXPLAIN
      SELECT p.title, u.username
      FROM posts p
      JOIN users u ON u.pk = p.author
      WHERE u.username = 'fluca1978'
    AND   daterange( CURRENT_DATE - 20, CURRENT_DATE ) @> p.created_
on::date;


                                              QUERY PLAN
--------------------------------------------------------------------------
---------------------------
Gather      (cost=1008.30..13803.58 rows=2 width=26)
   Workers Planned: 2
   ->     Hash Join     (cost=8.30..12803.38 rows=1 width=26)
            Hash Cond: (p.author = u.pk)
        ->       Parallel Seq Scan on posts p     (cost=0.00..12792.33 rows=1042
width=15)
              Filter: (daterange((CURRENT_DATE - 2), CURRENT_DATE) @>
(created_on)::date)
            ->   Hash    (cost=8.29..8.29 rows=1 width=19)
              -> Index Scan using users_username_key on users u
(cost=0.28..8.29 rows=1 width=19)
                         Index Cond: (username = 'fluca1978'::text)
```

Planner đã chọn khởi chạy parallel query execution: node ở trên cùng là một Gather node, vì vậy nó hoạt động như một synchronization point cho các parallel worker. Cụ thể, planner quyết định sử dụng hai parallel process để hoàn tất query. Node ngoài cùng bên phải, và do đó là node đầu tiên được thực thi, là một Index Scan node trên table users. Các result được hash, đồng thời một Parallel Seq Scan được khởi chạy để lấy data từ table posts. Các result được join và Gather thu thập final result set. Tổng execution time của query này có thể dễ dàng lấy được bằng `EXPLAIN ANALYZE`, cho thấy query mất khoảng 140 millisecond để hoàn tất:

```text
forumdb=> EXPLAIN ANALYZE
     SELECT p.title, u.username
     FROM posts p
     JOIN users u ON u.pk = p.author
     WHERE u.username = 'fluca1978'
    AND   daterange( CURRENT_DATE - 20, CURRENT_DATE ) @> p.created_
on::date;




   QUERY PLAN
--------------------------------------------------------------------------
---------------------------------------------------------------------
Gather (cost=1008.30..13803.58 rows=2 width=26) (actual
time=0.856..141.434 rows=20 loops=1)
   Workers Planned: 2
   Workers Launched: 2
  -> Hash Join (cost=8.30..12803.38 rows=1 width=26) (actual
time=0.968..135.209 rows=7 loops=3)
          Hash Cond: (p.author = u.pk)
        -> Parallel Seq Scan on posts p (cost=0.00..12792.33 rows=1042
width=15) (actual time=0.076..133.975 rows=6667 loops=3)
              Filter: (daterange((CURRENT_DATE - 20), CURRENT_DATE) @>
(created_on)::date)
                 Rows Removed by Filter: 160000
        -> Hash (cost=8.29..8.29 rows=1 width=19) (actual
time=0.053..0.054 rows=1 loops=3)
                 Buckets: 1024      Batches: 1     Memory Usage: 9kB
             -> Index Scan using users_username_key on users u
(cost=0.28..8.29 rows=1 width=19) (actual time=0.047..0.048 rows=1
loops=3)
                      Index Cond: (username = 'fluca1978'::text)
Planning Time: 0.188 ms
Execution Time: 141.471 ms
```

Điều gì xảy ra nếu chúng ta thêm một index vào column `author` của table posts?

```text
forumdb=> CREATE INDEX idx_posts_author ON posts( author );
CREATE INDEX
forumdb=> EXPLAIN ANALYZE
     SELECT p.title, u.username
     FROM posts p
     JOIN users u ON u.pk = p.author
     WHERE u.username = 'fluca1978'
    AND   daterange( CURRENT_DATE - 20, CURRENT_DATE ) @> p.created_
on::date;



   QUERY PLAN
--------------------------------------------------------------------------
---------------------------------------------------------
Nested Loop (cost=8.45..1602.29 rows=2 width=26) (actual
time=0.145..0.926 rows=20 loops=1)
  -> Index Scan using users_username_key on users u (cost=0.28..8.29
rows=1 width=19) (actual time=0.011..0.012 rows=1 loops=1)
            Index Cond: (username = 'fluca1978'::text)
  -> Bitmap Heap Scan on posts p (cost=8.17..1593.98 rows=2 width=15)
(actual time=0.129..0.904 rows=20 loops=1)
            Recheck Cond: (author = u.pk)
            Filter: (daterange((CURRENT_DATE - 20), CURRENT_DATE) @> (created_
on)::date)
            Rows Removed by Filter: 480
            Heap Blocks: exact=500
         -> Bitmap Index Scan on idx_posts_author (cost=0.00..8.17
rows=500 width=0) (actual time=0.059..0.059 rows=500 loops=1)
                   Index Cond: (author = u.pk)
Planning Time: 0.401 ms
Execution Time: 0.954 ms
(12 rows)
```

Trước hết, query hiện chạy tuần tự vì không có Gather node nào: điều này có nghĩa là bây giờ PostgreSQL có thể giảm result set cần kiểm tra ngay từ trước. Ngoài ra, execution time hiện nhỏ hơn một millisecond.

Như bạn có thể thấy, node đầu tiên được thực thi là một Index Scan node trên table posts, hiện được dùng trước, không giống plan song song trước đó, sau đó result set sau khi được giảm sẽ được join bằng một Nested Loop với table authors. Việc sử dụng Nested Loop xác nhận rằng PostgreSQL đã có thể giảm result set, lấy trước chỉ những tuple cần thiết từ table posts.

Cũng cần lưu ý rằng không còn lý do để giữ index trên column `created_on`, vì query plan trước đó không còn sử dụng nó nữa.

Cần bao nhiêu space cho các index bây giờ? Một lần nữa, việc kiểm tra khá đơn giản:

```text
forumdb=> SELECT pg_size_pretty( pg_relation_size( 'posts') ) AS table_
size,
         pg_size_pretty( pg_relation_size( 'idx_posts_date' ) ) AS idx_date_
size,
        pg_size_pretty( pg_relation_size( 'idx_posts_author' ) ) AS idx_
author_size;


      table_size | idx_date_size | idx_author_size
   ------------+---------------+-----------------
   59 MB         | 3600 kB            | 3600 kB


   (1 row)
```

Cả hai index yêu cầu cùng một lượng space, nhưng như đã nói, chúng ta có thể drop date-based index vì nó không còn cần thiết. Thực tế, ngay cả với một date clause cụ thể, index cũng không còn được sử dụng:

```text
forumdb=> EXPLAIN ANALYZE
      SELECT p.title, u.username
      FROM posts p
      JOIN users u ON u.pk = p.author
      WHERE u.username = 'fluca1978'
        AND     p.created_on::date = CURRENT_DATE -2;


                                                                            QUERY PLAN
--------------------------------------------------------------------------
---------------------------------------------------------
Nested Loop (cost=8.45..1599.79 rows=2 width=26) (actual
time=0.132..0.737 rows=1 loops=1)
  -> Index Scan using users_username_key on users u (cost=0.28..8.29
rows=1 width=19) (actual time=0.009..0.010 rows=1 loops=1)
           Index Cond: (username = 'fluca1978'::text)
  -> Bitmap Heap Scan on posts p (cost=8.17..1591.48 rows=2 width=15)
(actual time=0.119..0.723 rows=1 loops=1)
           Recheck Cond: (author = u.pk)
           Filter: ((created_on)::date = (CURRENT_DATE - 2))
           Rows Removed by Filter: 499
           Heap Blocks: exact=500
        -> Bitmap Index Scan on idx_posts_author (cost=0.00..8.17
rows=500 width=0) (actual time=0.053..0.053 rows=500 loops=1)
                  Index Cond: (author = u.pk)
Planning Time: 0.237 ms
Execution Time: 0.763 ms
```

Việc xác định các index không được sử dụng rất quan trọng vì nó cho phép chúng ta thu hồi disk space và đơn giản hóa việc management cũng như data insertion: hãy nhớ rằng mỗi khi table thay đổi, index phải được update, và việc này cũng yêu cầu thêm resource như time và disk space.

Vì vậy, như bạn có thể thấy, việc phân tích các query được các application của bạn thực thi thường xuyên nhất và xác định liệu một index có thể giúp cải thiện execution speed hay không thực sự quan trọng; nhưng cũng hãy nhớ rằng index có extra cost cả về space lẫn maintenance, vì vậy đừng lạm dụng việc sử dụng index.

Nhưng làm thế nào bạn có thể xác định các index không được sử dụng mà không cần biết các query đang diễn ra?

May mắn là PostgreSQL cung cấp thông tin chi tiết về việc sử dụng mọi index: view đặc biệt `pg_stat_user_indexes` cung cấp thông tin về số lần một index đã được sử dụng và cách nó được sử dụng. Ví dụ, để lấy thông tin về các index trên table posts, bạn có thể thực thi một query như sau:

```text
forumdb=> SELECT indexrelname, idx_scan, idx_tup_read, idx_tup_fetch FROM
pg_stat_user_indexes WHERE relname = 'posts';
```
