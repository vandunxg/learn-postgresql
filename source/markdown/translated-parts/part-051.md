```text
   indisvalid          | t
   pg_get_indexdef | CREATE INDEX idx_post_created_on ON posts USING hash
   (created_on)
```

Column `indisunique` được đặt thành true nếu index được tạo với clause `UNIQUE`, như trường hợp của index primary key. `indisvalid` là một giá trị boolean cho biết index có thể được sử dụng hay không (như bạn sẽ thấy sau đây, bạn có thể quyết định disable một index vì bất kỳ lý do nào).

Vì bạn có thể cluster một table theo một index, tức là sort table tùy theo một index cụ thể, `indisclustered` cho biết table có được cluster theo index cụ thể đó hay không.

Function đặc biệt `pg_get_indexdef()` cung cấp biểu diễn dạng text của statement `CREATE INDEX` được dùng để tạo từng index, và có thể rất hữu ích để giải mã cũng như tìm hiểu cách build các index phức tạp.

Do đó, bằng cách dùng command `psql \d` hoặc query `pg_index`, bạn có thể lấy thông tin chi tiết về các index hiện có và trạng thái của chúng.

### Dropping an index

Để loại bỏ một index, bạn cần dùng statement `DROP INDEX`, có dạng như sau:

```sql
   DROP INDEX [ CONCURRENTLY ] [ IF EXISTS ] name [, ...] [ CASCADE |
   RESTRICT ]
```

Statement này nhận tên của index và có thể drop nhiều index cùng lúc nếu bạn chỉ định nhiều name trong cùng một statement.

Clause `CONCURRENTLY` ngăn command lấy exclusive lock trên table underlying, nhờ đó ngăn các query khác truy cập table cho đến khi index được drop. Lưu ý rằng clause này không phải lúc nào cũng dùng được; chẳng hạn, nó không thể được dùng bên trong một explicit transaction.

Option `CASCADE` drop index và mọi object khác phụ thuộc vào index đó (ví dụ, một table constraint), còn option `RESTRICT` là đối lập của nó và ngăn index bị drop nếu vẫn còn object yêu cầu index đó. Clause `RESTRICT` là mặc định.

Cuối cùng, option `IF EXISTS` cho phép command dừng nhẹ nhàng nếu index đã bị drop.

### Invalidating an index

Có thể invalidate một index, tức là yêu cầu PostgreSQL hoàn toàn không xem xét index đó mà không drop index rồi build lại. Điều này có thể hữu ích trong những tình huống bạn đang nghiên cứu behavior của cluster và muốn buộc optimizer chọn một path khác để truy cập data, không bao gồm một index cụ thể, hoặc có thể cần thiết khi index gặp vấn đề.

Để invalidate một index, bạn phải trực tiếp thao tác trên system catalog `pg_index` để đặt attribute `indisvalid` thành false. Ví dụ, để tạm dừng việc sử dụng index `idx_author_created_on`, bạn phải thực hiện một update trên `pg_index` như sau:

```text
   forumdb=# UPDATE pg_index SET indisvalid = false
                WHERE indexrelid = ( SELECT oid FROM pg_class
                                           WHERE relkind = 'i'
                                           AND relname = 'idx_author_created_on' );
   UPDATE 1


   forumdb=# \d posts
   ...
   Indexes:
         "posts_pkey" PRIMARY KEY, btree (pk)
         "idx_author_created_on" btree (author, created_on) INVALID
         "idx_post_category" btree (category)
         "idx_post_created_on" hash (created_on)
   ...
```

> Bạn cần invalidate một index bằng administrator user, ngay cả khi bạn là user đã tạo index đó. Lý do là bạn cần thao tác trên system catalog, một hoạt động chỉ dành cho administrator user.

Như bạn có thể thấy, index sau đó được đánh dấu là `INVALID` để cho biết PostgreSQL sẽ không bao giờ thử xem xét nó trong execution plan. Dĩ nhiên, bạn có thể đưa index về trạng thái ban đầu bằng cách thực hiện update giống như trên và đặt column `indisvalid` thành giá trị true.

### Rebuilding an index

Vì index được tách khỏi data được lưu trong table, thông tin bên trong index có thể bị corrupt hoặc trở nên không còn cập nhật theo một cách nào đó. Đây không phải là điều kiện bình thường và không xảy ra trong việc sử dụng database hằng ngày, nhưng storage lỗi có thể dẫn đến tình huống như vậy. Tuy nhiên, biết cách rebuild một index là kiến thức quan trọng vì nó giúp ngăn anomaly và cho phép bạn revalidate các index đã bị out of date (vì chúng không còn valid).

Bạn luôn có thể rebuild một index bắt đầu từ data trong table underlying bằng command `REINDEX`, có dạng như sau:

```sql
   REINDEX [ ( VERBOSE ) ] { INDEX | TABLE | SCHEMA | DATABASE | SYSTEM } [
   CONCURRENTLY ] name
```

Bạn có thể rebuild một index duy nhất bằng argument `INDEX` theo sau là tên index, hoặc rebuild mọi index của một table bằng argument `TABLE` theo sau, như bạn có thể hình dung, là tên table.

Tiếp theo, bạn có thể rebuild mọi index của mọi table trong một schema cụ thể bằng argument `SCHEMA` (theo sau là tên schema), hoặc toàn bộ index của một database bằng argument `DATABASE` và tên database bạn muốn reindex. Cuối cùng, bạn cũng có thể rebuild index trên các system catalog table bằng argument `SYSTEM`.

Bạn có thể thực thi `REINDEX` bên trong một transaction block nhưng chỉ với một index hoặc table duy nhất, tức là chỉ với các option `INDEX` và `TABLE`. Mọi dạng khác của command `REINDEX` không thể được thực thi trong một transaction block.

Option `CONCURRENTLY` ngăn command lấy exclusive lock trên table underlying theo cách tương tự như khi build một index mới.

## The EXPLAIN statement

`EXPLAIN` là statement cho phép bạn xem PostgreSQL sẽ execute một query cụ thể như thế nào. Bạn truyền statement muốn analyze cho `EXPLAIN`, và execution plan sẽ được hiển thị.

Có một vài điều quan trọng cần biết trước khi dùng `EXPLAIN`:

- Nó chỉ hiển thị plan tốt nhất, tức plan có cost thấp nhất trong tất cả plan đã được đánh giá.
- Nó sẽ không execute statement mà bạn yêu cầu plan, trừ khi bạn explicitly yêu cầu execute statement đó. Vì vậy, việc thực thi `EXPLAIN` nhanh và gần như không đổi trong mỗi lần.
- Nó sẽ trình bày tất cả execution node mà executor sẽ dùng để cung cấp dataset.

Hãy xem một ví dụ về `EXPLAIN` để hiểu rõ hơn. Hãy hình dung chúng ta cần hiểu execution plan của statement `SELECT * FROM categories`. Trong trường hợp này, bạn cần đặt command `EXPLAIN` trước statement như sau:

```text
   forumdb=> EXPLAIN SELECT * FROM categories;
                                QUERY PLAN
   -----------------------------------------------------------
   Seq Scan on categories        (cost=0.00..1.05 rows=5 width=68)
   (1 row)
```

Như bạn có thể thấy, output của `EXPLAIN` báo cáo query plan. Có một execution node duy nhất, thuộc type `Seq Scan`, theo sau là table nơi node được execute (trên `categories`). Trong output của command `EXPLAIN`, bạn sẽ tìm thấy tất cả type execution node đã được thảo luận trong các section trước.

Với mỗi node, `EXPLAIN` sẽ báo cáo thêm một số thông tin trong dấu ngoặc: cost, số row và width. Cost là mức effort cần thiết để execute node, và luôn được biểu diễn dưới dạng “startup cost” và “final cost”. Startup cost là lượng công việc PostgreSQL phải thực hiện trước khi bắt đầu execute node; trong ví dụ trước, cost là 0, nghĩa là việc execute node có thể bắt đầu ngay lập tức. Final cost là lượng effort PostgreSQL phải thực hiện để cung cấp phần cuối cùng của dataset, tức hoàn tất execution của node.

Field `rows` cho biết node được kỳ vọng cung cấp bao nhiêu tuple trong dataset cuối cùng, và hoàn toàn là một ước tính. Vì là ước tính, giá trị này có thể sai, và bạn phải nhớ rằng nó sẽ không bao giờ bằng zero: khi PostgreSQL ước tính số tuple rất thấp, nó luôn cung cấp 1 làm số row.

Cuối cùng, field `width` cho biết trung bình mỗi tuple sẽ chiếm bao nhiêu bit. Về cơ bản, thông tin này được dùng để ước tính network traffic mà query sẽ tạo ra: trong ví dụ trước, có thể ước tính 68 byte cho mỗi tuple.

Bây giờ hãy xem một ví dụ khác để làm quen với output của `EXPLAIN`; query thay đổi một chút để tạo thêm một vài node, như sau:

```text
      forumdb=> EXPLAIN
                 SELECT title
                 FROM categories ORDER BY description DESC;
                                 QUERY PLAN                                           ---------
      --------------------------------------------------------
      Sort   (cost=1.11..1.12 rows=5 width=64)
        Sort Key: description DESC
        ->   Seq Scan on categories      (cost=0.00..1.05 rows=5 width=64)
```

Ở đây, chúng ta có hai node khác nhau: node đầu tiên ở trên cùng là node `Sort` (do clause `ORDER BY`), còn node thứ hai là `Seq Scan`, như trong ví dụ trước. Lưu ý rằng có ba row output, vậy làm sao xác định row nào là node và row nào không phải? Row đầu tiên trong plan luôn là một node, còn các row node khác được thụt vào bên phải và có mũi tên làm tiền tố (`->`). Các line khác trong plan cung cấp thông tin về node mà chúng trực thuộc; do đó, trong ví dụ trước, row `Sort Key` là thông tin bổ sung cho node `Sort`.

Một cách khác để phân biệt row node với thông tin bổ sung là xem xét rằng mọi line node đều có các attribute cost, rows và width trong dấu ngoặc.

Sau khi xác định được các node của query, bạn phải tìm node đầu tiên, thường là node được thụt vào nhiều nhất và cũng là node có startup cost thấp nhất; trong ví dụ trước, `Seq Scan` là node được execute đầu tiên. Node này thực hiện chính xác điều đã giải thích trong ví dụ trước: buộc executor đi tới table trên physical storage và lấy toàn bộ content của table theo thứ tự tuần tự. Tuy nhiên, có một điểm khác trong ví dụ trước: width trung bình đã giảm, vì query không yêu cầu tất cả column của mọi tuple, mà chỉ yêu cầu column `title`.

Khi node `Sequential Scan` hoàn tất, output của nó được dùng làm input cho node `Sort`, node thực hiện operation `ORDER BY` mong muốn. Như bạn có thể dễ dàng đọc, sort key của statement ban đầu được in ra để cung cấp đủ thông tin giúp bạn hiểu executor sẽ sort data theo những gì. Node `Sort` có startup cost lớn hơn (hoặc tốt nhất là gần như bằng) final cost của node trước: sequential scan có final cost là 1.05 còn sort bắt đầu với cost 1.11. Điều này một lần nữa nhấn mạnh rằng các node được execute theo pipeline, đồng thời cho biết sort không thể bắt đầu trước khi node kia hoàn tất. Node `Sort` có final cost gần bằng startup cost, nghĩa là PostgreSQL thực hiện node này khá đơn giản.

Bạn có thể thử execute `EXPLAIN` trên các statement khác nhau để xem plan thay đổi như thế nào và có thể tạo ra những node nào, từ đó dùng để nhận biết các node và thông tin resource.

Trong các subsection sau, bạn sẽ thấy những option khác nhau để explain một statement.

### EXPLAIN output formats

Mặc định, `EXPLAIN` cung cấp output dạng text, nhưng nó cũng có thể cung cấp output có cấu trúc hơn nhiều ở dạng XML, JSON và YAML. Những format khác này không chỉ hữu ích khi bạn phải làm việc với tool và application bên ngoài mà còn hữu ích vì chúng cung cấp nhiều thông tin hơn để tuning query plan.

Bạn có thể chỉ định format mong muốn bằng option `FORMAT` theo sau là tên format, có thể là `TEXT`, `XML`, `JSON` hoặc `YAML`. Hãy xem ví dụ sau:

```text
   forumdb=> EXPLAIN ( FORMAT JSON ) SELECT * FROM categories;
                       QUERY PLAN
   --------------------------------------
    [                                           +
       {                                       +
           "Plan": {                           +
               "Node Type": "Seq Scan",        +
               "Parallel Aware": false,        +
               "Async Capable": false,         +
               "Relation Name": "categories",+
               "Alias": "categories",          +
               "Startup Cost": 0.00,             +
               "Total Cost": 1.05,             +
               "Plan Rows": 5,                 +
               "Plan Width": 68                +
           }                                   +
       }                                       +
   ]


   (1 row)
```

Như bạn có thể thấy, format JSON không chỉ cung cấp cấu trúc khác cho query plan mà còn cung cấp tập thông tin khác và phong phú hơn. Ví dụ, từ ví dụ trước, chúng ta có thể thấy query đã được execute ở chế độ nonparallel (`"Parallel Aware": false,`).

Nếu cần parse output của `EXPLAIN` bằng application hoặc tool, bạn nên dùng một trong các format có cấu trúc thay vì format text mặc định.

### EXPLAIN ANALYZE

Mode `ANALYZE` của `EXPLAIN` mở rộng command bằng cách thực sự chạy query cần explain. Do đó, command thực hiện hai nhiệm vụ: in ra plan tốt nhất để execute query và chạy query, đồng thời báo cáo một số thông tin thống kê.

Để hiểu rõ hơn khái niệm này, hãy xem output của `EXPLAIN ANALYZE` so với output của command `EXPLAIN` thông thường:

```text
      forumdb=> EXPLAIN SELECT * FROM posts;
                               QUERY PLAN
      ----------------------------------------------------------
      Seq Scan on posts   (cost=0.00..31.04 rows=1004 width=71)
      (1 row)




      forumdb=> EXPLAIN ANALYZE SELECT * FROM posts;
                                                           QUERY PLAN
      --------------------------------------------------------------------------
      -----------------------------
      Seq Scan on posts (cost=0.00..31.04 rows=1004 width=71) (actual
      time=0.006..0.101 rows=1004 loops=1)
      Planning Time: 0.052 ms
      Execution Time: 0.163 ms
      (3 rows)
```

Output của command `EXPLAIN ANALYZE` được bổ sung phần “actual” của mỗi node: executor báo cáo chính xác việc execute node đã diễn ra như thế nào. Vì vậy, trong khi `EXPLAIN` chỉ có thể ước tính cost của node, `EXPLAIN ANALYZE` cung cấp thông tin về execution time (tính bằng millisecond), số row thực tế và số lần một node đã được execute (loops).

Thời gian của node được biểu diễn, tương tự cost, bằng startup time và final time, là thời gian cần để node hoàn tất việc execute. Do đó, trong ví dụ trước, PostgreSQL mất 0.006 millisecond để “warm up” và hoàn tất việc execute query trong 0.101 millisecond, nên node cần 0.107 millisecond để hoàn thành công việc.

Một phần thông tin quan trọng khác trong phần actual của output node là số row (tức node đã tạo ra bao nhiêu tuple), tương tự như phép ước tính của `EXPLAIN` thông thường. Tại sao cần báo cáo lại số row mà node thu được? Hãy nhớ rằng `EXPLAIN` đưa ra ước tính, còn `EXPLAIN ANALYZE` cung cấp số tuple thực tế thu được bởi node. Khi hai giá trị này thực sự khác nhau, chênh lệch một bậc độ lớn hoặc hơn, PostgreSQL không thể ước tính chính xác kích thước result set và do đó không thể chọn plan tốt nhất để truy cập data, nghĩa là nó có thể chọn một access method không tối ưu.

Cuối cùng, output actual có số loop, tức số lần chính node đó đã execute. Thông thường số này là 1, nghĩa là node chỉ được execute một lần, nhưng nếu node thuộc về một subquery thì giá trị có thể lớn hơn 1. Timing và số row liên quan đến một lần execute loop; do đó, để có các giá trị cuối cùng, bạn cần nhân rows và time với loops.

Ở cuối output của command, `EXPLAIN ANALYZE` cung cấp thông tin thời gian tổng thể, bao gồm planning time, là thời gian optimizer đã dùng để tạo access plan tốt nhất, và execution time, là tổng thời gian đã dùng để chạy query (không bao gồm parsing và planning time).

Do đó, ví dụ trước mất 0.163 millisecond để “fetch data” và 0.052 millisecond để quyết định cách fetch data, còn tổng thời gian query mất là 0.219 millisecond (nhỉnh hơn một chút so với 0.052 + 0.163 vì một phần thời gian được dùng để cấp phát resource).

> Khi data cần truy cập rất nhỏ, planning time sẽ dài hơn execution time.

Execution time cũng bao gồm thời gian chạy các trigger `BEFORE`, trong khi trigger `AFTER` không được tính vì function của chúng được execute sau khi plan đã hoàn tất.

Tương tự, planning time chỉ tính thời gian dùng để tạo access plan tốt nhất, không tính thời gian cần để xử lý rule và viết statement, cũng như parsing.

> `EXPLAIN ANALYZE` luôn execute query mà bạn muốn analyze; do đó, để tránh side effect, bạn nên bọc `EXPLAIN ANALYZE` trong một transaction và rollback công việc sau khi hoàn thành việc phân tích.

`EXPLAIN ANALYZE` cũng có thể được gọi bằng cách truyền `ANALYZE` như một option cho `EXPLAIN`, như sau:

```text
      forumdb=> EXPLAIN ( ANALYZE ) SELECT * FROM categories ORDER BY title
      DESC;
```

Dạng option của `EXPLAIN ANALYZE` tiện dụng khi bạn muốn thêm các option khác cho `EXPLAIN`, như được trình bày trong subsection sau.

### EXPLAIN options

`EXPLAIN` cung cấp một tập option phong phú, phần lớn trong số đó chỉ có thể được dùng ở dạng `ANALYZE`. Tất cả option của `EXPLAIN` được trình bày trong section này đều là boolean, nghĩa là chúng có thể được bật và tắt nhưng không làm gì khác.

Option `VERBOSE` cho phép mỗi node báo cáo thông tin chi tiết hơn, chẳng hạn danh sách các output column, ngay cả khi không được chỉ định. Ví dụ, ngay cả khi query không yêu cầu rõ ràng danh sách column, hãy lưu ý rằng nhờ `VERBOSE`, bạn có thể biết node sẽ cung cấp những column nào cho output dataset:

```text
      forumdb=> EXPLAIN (VERBOSE on) SELECT * FROM categories;
                                    QUERY PLAN
      -----------------------------------------------------------------
      Seq Scan on forum.categories       (cost=0.00..1.05 rows=5 width=68)
        Output: pk, title, description
      (2 rows)
```

Option `SETTINGS` được dùng để xác định query có được plan bằng một configuration khác với tập configuration chung ở cấp cluster hay không. Một số thay đổi có thể được áp dụng ở cấp session; do đó, `EXPLAIN` có thể báo cáo session có đang dùng một custom setting hay không. Ví dụ, hãy xét việc thay đổi parameter `work_mem`; dù parameter này không liên quan gì đến query được hiển thị trong ví dụ sau, `EXPLAIN` vẫn báo cáo nó là một parameter đã được thay đổi thủ công trước khi query được plan:

```text
      forumdb=> SHOW work_mem;
      work_mem
      ----------
      4MB
      (1 row)
```

```text
   forumdb=> SET work_mem TO '32MB';
   SET
   forumdb=> EXPLAIN (SETTINGS on) SELECT * FROM posts ORDER BY created_on
   DESC;
                                     QUERY PLAN
   ----------------------------------------------------------------------
   Sort      (cost=164403.31..166903.32 rows=1000004 width=75)
      Sort Key: created_on DESC
      ->     Seq Scan on posts   (cost=0.00..20309.04 rows=1000004 width=75)
   Settings: work_mem = '32MB'
   (4 rows)
```

Nhờ option `SETTINGS`, có thể hiểu query plan có được tạo ra với custom configuration của một số parameter hay không, và do đó hiểu rõ hơn liệu các parameter đó có ảnh hưởng đến query plan hay không.

Option `COSTS`, được bật theo mặc định, hiển thị phần cost của một node. Ví dụ, tắt option này sẽ loại bỏ startup cost và final cost, cũng như width trung bình và số row:

```text
   forumdb=> EXPLAIN (COSTS off) SELECT * FROM categories;
              QUERY PLAN
   ------------------------
    Seq Scan on categories
   (1 row)


   forumdb=> EXPLAIN (COSTS on) SELECT * FROM categories;
                           QUERY PLAN
   -----------------------------------------------------------
    Seq Scan on categories       (cost=0.00..1.05 rows=5 width=68)



   (1 row
```

Option `TIMING`, được bật theo mặc định, hiển thị execution time thực tế khi `EXPLAIN` được gọi với `ANALYZE`. Nói cách khác, đặt `TIMING` thành off có nghĩa là output của `EXPLAIN` sẽ không hiển thị thời gian execute node.
