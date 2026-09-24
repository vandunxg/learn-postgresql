```text
   indexrelname      | idx_scan | idx_tup_read | idx_tup_fetch
------------------+----------+--------------+---------------
posts_pkey           |          5 |                5 |                 5
idx_posts_date       |          1 |          500000 |            500000
idx_posts_author |             51 |            8534 |                  0
```

Điều này cho chúng ta biết rằng `idx_posts_date` đã được sử dụng 1 lần và cung cấp 500000 tuple, trong khi `idx_posts_author` đã được sử dụng 51 lần và cũng cung cấp ít tuple hơn nhiều (chỉ 8534), nghĩa là nó rất hiệu quả.

Sau khi quan sát xu hướng này theo thời gian, nếu `idx_posts_date` hiếm khi được sử dụng, bạn có thể an toàn drop nó.

Ví dụ cuối cùng, hãy xem xét một query được viết kém và vấn đề mà nó kéo theo: giả sử chúng ta muốn lấy tất cả author đã tạo post vào một ngày nhất định và trong cùng ngày đó nhận được một số lượng like cụ thể. Một query tệ có thể là query sau:

```sql
   SELECT u.username
   FROM users u JOIN posts p ON p.author = u.pk WHERE p.created_on = CURRENT_
   DATE - 5
   AND u.pk IN ( SELECT pp.author FROM posts pp WHERE likes = 5 and
   p.created_on = created_on );
```

Rõ ràng không cần subquery trên table `posts`, nhưng đây là một ví dụ cụ thể cho thấy vì sao việc hiểu cách viết query tốt lại quan trọng.

Thoạt nhìn, query trước đó chạy đủ nhanh; nó mất 190 millisecond để thực thi, như được minh họa bởi `EXPLAIN ANALYZE`:

```text
   forumdb=> EXPLAIN ANALYZE SELECT u.username
   FROM users u JOIN posts p ON p.author = u.pk WHERE p.created_on = CURRENT_
   DATE - 5
   AND u.pk IN ( SELECT pp.author FROM posts pp WHERE likes = 5 and
   p.created_on = created_on );
                                                                               QUERY PLAN
   --------------------------------------------------------------------------
   -------------------------------------------------------------
   Hash Join (cost=33.93..92.04 rows=498 width=15) (actual
   time=1.351..189.308 rows=100 loops=1)
   Hash Cond: (p.author = u.pk)
      Join Filter: (SubPlan 1)
      Rows Removed by Join Filter: 900
     -> Index Scan using idx_posts_date on posts p (cost=0.43..55.92
   rows=996 width=12) (actual time=0.029..0.254 rows=1000 loops=1)
              Index Cond: (created_on = (CURRENT_DATE - 5))
     -> Hash (cost=21.00..21.00 rows=1000 width=19) (actual
   time=0.345..0.345 rows=1000 loops=1)
              Buckets: 1024    Batches: 1    Memory Usage: 59kB
           -> Seq Scan on users u (cost=0.00..21.00 rows=1000 width=19)
   (actual time=0.006..0.151 rows=1000 loops=1)
      SubPlan 1
       -> Index Scan using idx_posts_date on posts pp (cost=0.42..58.49
   rows=99 width=4) (actual time=0.005..0.176 rows=95 loops=1000)
                Index Cond: (created_on = p.created_on)
                Filter: (likes = 5)
                Rows Removed by Filter: 855
   Planning Time: 0.393 ms
   Execution Time: 189.439 ms
```

Tuy nhiên, khi xem output, bạn có thể thấy node **Index Scan** sử dụng `idx_posts_date` trên `pp posts` có counter `loops` được đặt là 1000: điều này nghĩa là node này được thực thi 1.000 lần trong query. Node này là subquery, và đó là cách SQL đạt được kết quả: mỗi khi tìm thấy một tuple từ outer query, inner query phải được chạy và các kết quả phải được join. Một lựa chọn có thể là rewrite query để PostgreSQL không phải looping, chẳng hạn dùng subquery với expression `GROUP BY`:

```text
   forumdb=> EXPLAIN ANALYZE
   WITH likes AS (
             SELECT pp.author, pp.created_on FROM posts pp
             WHERE likes = 5
             GROUP BY pp.author, pp.created_on
                  )
   SELECT u.username
   FROM users u JOIN posts p ON p.author = u.pk
   JOIN likes l ON l.created_on = p.created_on AND l.author = u.pk
   WHERE p.created_on = CURRENT_DATE - 5;
```

```text
  --------------------------------------------------------------------------
  -------------------------------------------------------------------------
  ---------------
  Hash Join (cost=89.47..149.68 rows=98 width=15) (actual time=0.581..0.896
  rows=100 loops=1)
      Hash Cond: (p.author = u.pk)
    -> Index Scan using idx_posts_date on posts p (cost=0.43..55.92
  rows=996 width=12) (actual time=0.012..0.167 rows=1000 loops=1)
            Index Cond: (created_on = (CURRENT_DATE - 5))
    -> Hash (cost=87.82..87.82 rows=98 width=31) (actual time=0.561..0.562
  rows=100 loops=1)
            Buckets: 1024   Batches: 1   Memory Usage: 15kB
          -> Hash Join (cost=62.09..87.82 rows=98 width=31) (actual
  time=0.305..0.540 rows=100 loops=1)
                  Hash Cond: (u.pk = l.author)
                -> Seq Scan on users u (cost=0.00..21.00 rows=1000
  width=19) (actual time=0.005..0.094 rows=1000 loops=1)
                -> Hash (cost=60.86..60.86 rows=98 width=12) (actual
  time=0.294..0.294 rows=100 loops=1)
                        Buckets: 1024   Batches: 1   Memory Usage: 13kB
                      -> Subquery Scan on l (cost=58.90..60.86 rows=98
  width=12) (actual time=0.243..0.276 rows=100 loops=1)
                            -> HashAggregate (cost=58.90..59.88 rows=98
  width=12) (actual time=0.242..0.260 rows=100 loops=1)
                                     Group Key: pp.author, pp.created_on
                                     Batches: 1   Memory Usage: 24kB
                                    -> Index Scan using idx_posts_date on
  posts pp    (cost=0.43..58.41 rows=98 width=12) (actual time=0.009..0.208
  rows=100 loops=1)
                                            Index Cond: (created_on = (CURRENT_
  DATE - 5))
                                            Filter: (likes = 5)
                                            Rows Removed by Filter: 900
  Planning Time: 0.455 ms
  Execution Time: 0.954 ms
```

Output này báo thời gian chưa đến một millisecond, và đáng chú ý nhất là không khiến PostgreSQL loop qua cùng subquery nhiều lần.

Rõ ràng, viết query hoàn toàn không có subquery là cách hiệu quả nhất để cho PostgreSQL hiểu nó phải làm gì:

```text
   forumdb=> EXPLAIN ANALYZE
   SELECT u.username
   FROM users u JOIN posts p ON p.author = u.pk
   WHERE p.created_on = CURRENT_DATE - 5
   AND p.likes = 5;
                                                                           QUERY PLAN
   --------------------------------------------------------------------------
   --------------------------------------------------------
   Hash Join (cost=33.93..92.17 rows=98 width=15) (actual time=0.413..0.638
   rows=100 loops=1)
      Hash Cond: (p.author = u.pk)
     -> Index Scan using idx_posts_date on posts p (cost=0.43..58.41
   rows=98 width=4) (actual time=0.015..0.212 rows=100 loops=1)
             Index Cond: (created_on = (CURRENT_DATE - 5))
             Filter: (likes = 5)
             Rows Removed by Filter: 900
     -> Hash (cost=21.00..21.00 rows=1000 width=19) (actual
   time=0.393..0.394 rows=1000 loops=1)
           Buckets: 1024     Batches: 1     Memory Usage: 59kB
         -> Seq Scan on users u (cost=0.00..21.00 rows=1000 width=19)
   (actual time=0.007..0.173 rows=1000 loops=1)
   Planning Time: 0.263 ms
   Execution Time: 0.666 ms
```

Ví dụ đơn giản trước đó cho thấy vì sao việc hiểu output của `EXPLAIN` và `EXPLAIN ANALYZE` lại quan trọng, để hiểu rõ hơn liệu query có đang thiếu index hay cần rewrite để PostgreSQL thực hiện công việc của nó tốt nhất hay không.

## ANALYZE và cách cập nhật statistics

PostgreSQL sử dụng cách tiếp cận dựa trên statistics để đánh giá các execution plan khác nhau. Điều này nghĩa là PostgreSQL không biết có bao nhiêu tuple trong một table, nhưng có một xấp xỉ tốt cho phép planner tính cost của execution plan.

Statistics không chỉ liên quan đến số lượng (có bao nhiêu tuple) mà còn liên quan đến chất lượng của data bên dưới, chẳng hạn có bao nhiêu value khác nhau, value nào xuất hiện thường xuyên hơn trong một column, v.v. Nhờ kết hợp toàn bộ data này, PostgreSQL có thể đưa ra quyết định hiệu năng tốt.

Tuy nhiên, có những lúc chất lượng của statistical data không đủ tốt để PostgreSQL chọn plan tốt nhất, một vấn đề thường được gọi là “out-of-date statistics”. Thực tế, statistics không được cập nhật theo thời gian thực; thay vào đó, PostgreSQL theo dõi những gì đang diễn ra trong mọi table thuộc mọi database và tổng hợp số tuple mới, tuple đã được update và tuple đã bị delete, cũng như chất lượng của data đó. Có thể xảy ra việc statistics không được cập nhật đủ thường xuyên (hoặc hoàn toàn không được cập nhật) vì những lý do khác nhau mà chúng ta sẽ giải thích sau trong chapter này, vì vậy DBA phải luôn có cách buộc PostgreSQL bắt đầu lại từ đầu và “rebuild” statistics.

Command thực hiện việc này là `ANALYZE`.

> **Lưu ý:** Command `ANALYZE` không liên quan gì đến option `ANALYZE` của command `EXPLAIN`; thay vào đó, nó tương tự option cùng tên được dùng với command `VACUUM`, như đã giải thích trong *Chapter 11*.

`ANALYZE` nhận một table (và tùy chọn, một danh sách column) rồi xây dựng toàn bộ statistics cho table được chỉ định (hoặc chỉ cho các column được chỉ định).

Dù việc giữ statistics luôn cập nhật là quan trọng, chạy `ANALYZE` thủ công không phải là một thói quen tốt, và đó là lý do daemon auto-analyze chịu trách nhiệm cập nhật statistics định kỳ khi có đủ thay đổi xảy ra trên một table.

Cú pháp của command `ANALYZE` như sau:

```sql
      ANALYZE [ ( option [, ...] ) ] [ table_and_columns [, ...] ]
```

Về cơ bản, nó có thể được chạy trên một table duy nhất như sau:

```text
      forumdb=> \timing
      forumdb=> ANALYZE posts;
      ANALYZE
      Time: 252.771 ms
```

> **Lưu ý:** Bạn có thể kiểm tra thời gian cần để thực thi command và query bằng special command `\timing` của `psql`, command này sẽ in ra tóm tắt thời gian đã trôi qua sau mỗi statement. Đây không phải là cách chắc chắn để đo performance, mà chỉ để có ý tưởng về thời gian một task đang mất.

`ANALYZE` không hỗ trợ nhiều option, chủ yếu là `VERBOSE` để hiển thị output chi tiết về việc `ANALYZE` đang làm gì, và `SKIP_LOCKED`, khiến `ANALYZE` bỏ qua một table nếu nó không thể acquire lock phù hợp vì có các operation đang chạy khác đã acquire một lock không tương thích.

PostgreSQL lưu statistics mà `ANALYZE` thu thập ở đâu? Catalog đặc biệt `pg_stats` chứa toàn bộ statistics được planner sử dụng để xác định các value và constraint cần xem xét trên các attribute. Ví dụ, hãy xem PostgreSQL biết gì về column `author` của table `posts`, và cụ thể là có bao nhiêu value khác nhau:

```text
   forumdb=> SELECT n_distinct
                FROM pg_stats
                WHERE attname = 'author' AND tablename = 'posts';
    n_distinct
   ------------
             1000
   (1 row)
```

PostgreSQL biết rằng trong database ví dụ của chúng ta có 1.000 author khác nhau đã đăng ít nhất một post, như được command `EXPLAIN ANALYZE` minh họa trong section trước.

Một phần thông tin quan trọng bạn có thể tìm thấy trong catalog `pg_stats` là các most common value, kèm theo frequency mà các value đó xuất hiện. Việc trích xuất thông tin này cần chú ý hơn một chút vì cả value lẫn frequency đều được lưu dưới dạng array, vì vậy query sau cung cấp các most common value và frequency cho column `author`:

```text
   forumdb=> select most_common_vals, most_common_freqs from pg_stats where
   tablename = 'posts' and attname = 'category';
   -[ RECORD 1 ]-----+-------------------------------------------------------
   --
   most_common_vals | {3,4,1,5,2}
   most_common_freqs | {0.20566666,0.20163333,0.19843334,0.19743334,0.1968333
   3}
```

Output của query nghĩa là category có primary key 3 xuất hiện với frequency 0.2056, category có primary key 4 xuất hiện với frequency 0.2016, v.v. Frequency chuyển thành số tuple bằng cách nhân số tuple chứa trong table (500,000) với frequency. Vì vậy, category có primary key 3 xuất hiện trong `500000 x 0.2056 = 102,800` tuple của table `posts`. Có thể dễ dàng kiểm tra điều này bằng query sau:

```text
   forumdb=> SELECT count(*), category
   FROM posts
   GROUP BY category
   ORDER BY 2;
   count    | category
   --------+----------
   100000 |            1
   100000 |            2
   100000 |            3
   100000 |            4
   100000 |            5
   (5 rows)
```

Result lấy từ `pg_stats` không giống query `SELECT count(*)` vì `pg_stats` không nhằm cung cấp một result tuyệt đối và chính xác, mà chỉ cung cấp một order of magnitude.

`pg_stats` còn có các thông tin khác, chẳng hạn số lượng value `NULL` của một column, số lượng value khác nhau, v.v.

Tóm lại, PostgreSQL theo dõi statistics của mọi column trong mọi table; statistics được cập nhật bởi `ANALYZE` hoặc daemon auto-analyze để planner luôn có thể được tin cậy trong việc đưa ra một xấp xỉ tốt về số lượng và chất lượng data được lưu trong table.

## Auto-explain

Auto-explain là một extension giúp DBA có được ý tưởng về các query chậm và execution plan của chúng. Về cơ bản, auto-explain được trigger khi một query đang chạy chậm hơn threshold được chỉ định, sau đó dump execution plan của query vào PostgreSQL logs (xem *Chapter 14, Logging and Auditing* để biết thêm chi tiết).

> **Lưu ý:** Docker image cho chapter này đã được cấu hình sẵn auto-explain và log machinery.

Bằng cách này, DBA có thể nắm được các query chậm và execution plan của chúng mà không cần chạy lại các query đó. Nhờ vậy, DBA có thể inspect execution plan và quyết định có áp dụng index hay không, áp dụng ở đâu, hoặc thực hiện phân tích sâu hơn.

Module auto-explain được cấu hình thông qua một tập option parameter `auto_explain` có thể được thêm vào PostgreSQL configuration (file `postgresql.conf`), nhưng cần nhớ rằng để activate module, bạn cần restart cluster.

Module auto-explain có thể thực hiện gần như những việc mà một command `EXPLAIN` thủ công có thể làm, bao gồm `EXPLAIN ANALYZE`, nhưng nó phải được cấu hình đúng.

Tất cả setting của auto-explain đều nằm trong namespace `auto_explain`, do đó mọi parameter đều có prefix bắt đầu bằng `auto_explain.`; các setting chính như sau:

- `auto_explain.log_min_duration` là threshold thời gian mà một statement phải mất trước khi được log. Bất kỳ statement nào cần nhiều thời gian hơn setting này sẽ xuất hiện trong cluster logs cùng output `EXPLAIN` của nó.
- `auto_explain.log_format` và `auto_explain.log_level` kiểm soát format của output, dưới dạng text, JSON, YAML, XML, và level mà output đó sẽ được log (ví dụ: INFO).
- `auto_explain.log_verbose`, nếu được bật, cung cấp thông tin chi tiết hơn trong output.
- `auto_explain.sample_rate` là một value từ 0 đến 1 cho biết sampling rate của một session. Ví dụ, 0.5 nghĩa là cứ hai statement thì một statement được log.
- `auto_explain.log_nested_statements` là một boolean value quyết định liệu các statement “inner” có phải được log riêng hay không. Ví dụ, nếu option này được bật khi log một function call, các statement cũng xảy ra bên trong function sẽ được log và explain.
- `auto_explain.log_analyze` là một boolean value cho biết statement được log có phải đồng thời report các value của `EXPLAIN ANALYZE`, chủ yếu là timing thực tế, hay không. Hãy lưu ý rằng việc lấy thông tin timing theo từng node có thể yêu cầu nhiều resource và vì vậy có thể làm chậm toàn bộ query. Khi parameter này được bật, có thể bật các setting khác để cung cấp cùng thông tin mà `EXPLAIN ANALYZE` cung cấp:
- `auto_explain.log_buffers`, khi được bật, cung cấp thông tin về việc sử dụng buffer.
- `auto_explain.log_wal`, khi được bật, cung cấp thông tin về WAL do một query tạo ra.
- `auto_explain.log_timing`, khi được bật, cung cấp thông tin timing theo từng node.
- `auto_explain.log_triggers`, khi được bật, cung cấp thông tin về các lần thực thi trigger bên trong một statement.
- `auto_explain.log_settings`, khi được bật, report các setting khác với cluster-wide configuration.

Để install và configure module, hãy bắt đầu đơn giản bằng cách thêm hai setting sau vào cluster configuration trong `postgresql.conf`:

```text
   session_preload_libraries = 'auto_explain'
   auto_explain.log_min_duration = '100ms'
```

Dòng đầu tiên bảo PostgreSQL load library liên quan đến module auto-explain, trong khi dòng thứ hai instrument module để trigger bất cứ khi nào một query mất hơn 100 millisecond mới hoàn tất. Tất nhiên, bạn có thể tăng hoặc giảm query duration, tùy nhu cầu.

Với configuration đó, giờ có thể thực thi một query khá dài như sau (giả sử bạn đã drop/disable các index được tạo trong section trước):

```text
   forumdb=> \timing
   forumdb=> SELECT count(*)
   FROM posts p
   JOIN users u ON u.pk = p.author
   WHERE u.username = 'fluca1978'
   AND      daterange( CURRENT_DATE - 20, CURRENT_DATE ) @> p.created_on::date;
       count
   -------
          20
   (1 row)

   Time: 142.629 ms
```

Query mất 142 millisecond, đủ lâu để trigger auto-explain, và thực tế trong PostgreSQL logs, bạn có thể thấy như sau:

```text
   $ tail /postgres/16/data/log/postgresql.log
   INFO:       duration: 139.933 ms    plan:
   Query Text: SELECT count(*)
   FROM forum.posts p
   JOIN forum.users u ON u.pk = p.author
   WHERE u.username = 'fluca1978'
   AND        daterange( CURRENT_DATE - 20, CURRENT_DATE ) @> p.created_on::date;
   Aggregate        (cost=13803.59..13803.60 rows=1 width=8)
    Output: count(*)
    ->       Gather   (cost=1008.30..13803.58 rows=2 width=0)
               Workers Planned: 2
               ->   Hash Join   (cost=8.30..12803.38 rows=1 width=0)
                      Inner Unique: true
                      Hash Cond: (p.author = u.pk)
                -> Parallel Seq Scan on forum.posts p                 (cost=0.00..12792.33
   rows=1042 width=4)



   ...
```

Đó chính xác là output mà một command `EXPLAIN` thông thường sẽ tạo ra cho cùng query.

Điểm hay của cách tiếp cận này là bạn không phải lo lắng hoặc nhớ thực thi `EXPLAIN` trên các query hay các query đã thu thập; bạn chỉ cần inspect logs để tìm execution plan của những query chậm. Sau khi đã sửa các query như query trước đó, chẳng hạn bằng cách tạo index, bạn có thể tăng threshold của auto-explain để bắt các query chậm hơn và lặp lại quy trình.

Để minh họa sự khác biệt trong output khi chạy query với `auto_explain.log_analyze` được bật, sau đây là output được tạo ra cho chính query đó:

```text
   INFO:       duration: 139.730 ms     plan:
   Query Text: SELECT count(*)
   FROM forum.posts p
   JOIN forum.users u ON u.pk = p.author
   WHERE u.username = 'fluca1978'
   AND        daterange( CURRENT_DATE - 20, CURRENT_DATE ) @> p.created_on::date;
   Aggregate (cost=13803.59..13803.60 rows=1 width=8) (actual
   time=138.110..139.720 rows=1 loops=1)
    Output: count(*)
    Buffers: shared hit=487 read=7264
    -> Gather (cost=1008.30..13803.58 rows=2 width=0) (actual
   time=0.397..139.703 rows=20 loops=1)
                 Workers Planned: 2
```
