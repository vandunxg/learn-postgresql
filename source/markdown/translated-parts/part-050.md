Các Gather node chịu trách nhiệm thu thập các kết quả trả về từ những node thực thi song song, ghép chúng lại để tạo ra kết quả cuối cùng. Điểm khác biệt là Gather Merge node yêu cầu các process song song cung cấp output đã được sort để việc ghép tập kết quả được thực hiện theo thứ tự của data.

Plain Gather node không yêu cầu sort các batch result, nên nó chỉ đơn giản ghép tất cả các phần lại để cung cấp kết quả cuối cùng.

### Parallel scans

Tất cả main node mà bạn có thể tìm thấy trong một access method tuần tự đều có thể được chạy song song. Vì vậy, bạn có thể gặp Parallel Seq scan, hoặc các index scan như Parallel Index và Parallel Index-Only scan, và dĩ nhiên là cả Parallel Bitmap Heap scan.

### Parallel joins

Khi PostgreSQL quyết định dùng một parallel join method, nó cố giữ inner table được truy cập theo cách không song song (với giả định rằng table đó đủ nhỏ) và thực hiện việc truy cập song song tới outer table bằng một trong các node được trình bày ở phần trước.

Tuy nhiên, trong trường hợp Hash Join, inner table được mỗi parallel process tính thành hash, do đó mỗi parallel process làm việc trên outer table đều phải tính cùng một result cho inner table. Vì lý do đó, còn có Parallel Hash Join, cho phép hash map của inner table được tính song song bởi mọi process đang làm việc trên outer table.

### Parallel aggregations

Khi final result set được tạo bởi việc aggregate các parallel subquery khác nhau, phải có một parallel aggregation, tức aggregation của từng phần song song.

Aggregation này diễn ra qua nhiều bước: trước tiên, mỗi parallel process thực hiện một Partial Aggregate node để tạo ra partial result set. Sau đó, một Gather node (hoặc Gather Merge) thu thập tất cả partial result và chuyển toàn bộ tập đó cho Finalize Aggregate node, node này tuần tự ghép final result.

### Khi nào optimizer chọn parallel plan?

Như đã nói, PostgreSQL thậm chí không xem xét parallel plan như một lựa chọn nếu kích thước dự kiến của result set nhỏ. Cụ thể, nếu table cần tìm data có kích thước nhỏ hơn parameter `min_parallel_table_scan_size` (mặc định là 8 MB), hoặc index cần scan nhỏ hơn `min_parallel_index_scan_size` (mặc định là 512 kB), PostgreSQL hoàn toàn không tính đến parallel plan.

Bạn có thể buộc PostgreSQL thực hiện parallel plan ngay cả khi các giá trị trước đó chưa đạt điều kiện, bằng một configuration parameter bổ sung là `debug_parallel_query`, mặc định được set là off:

```text
   forumdb=> SHOW min_parallel_table_scan_size;
   min_parallel_table_scan_size
   ------------------------------
   8MB
   (1 row)


   forumdb=> SHOW min_parallel_index_scan_size;
   min_parallel_index_scan_size
   ------------------------------
   512kB
   (1 row)


   forumdb=> SHOW debug_parallel_query ;
   debug_parallel_query
   ----------------------
    off
   (1 row)
```

Trong mọi trường hợp, khi PostgreSQL xem parallel plan là một option, nó không mặc định sử dụng plan đó; thay vào đó, nó cẩn thận đánh giá cost của sequential plan và cost của parallel plan để xem nỗ lực setup bổ sung có còn đáng hay không.

Tuy nhiên, còn có những hạn chế khác đối với việc áp dụng parallel plan: PostgreSQL phải bảo đảm không spawn quá nhiều parallel process, vì vậy nếu hệ thống đã có quá nhiều parallel process đang hoạt động thì parallel execution sẽ không được xem là một option. Ngoài ra, bất kỳ statement nào tạo ra việc ghi data, tức mọi thứ khác với một `SELECT` statement, đều không phải candidate hợp lệ cho parallel plan; tương tự là mọi statement có thể bị suspend rồi resume, chẳng hạn như việc sử dụng cursor.

Cuối cùng, bất kỳ query nào gọi một function được đánh dấu là `PARALLEL UNSAFE` sẽ không tạo ra parallel plan candidate.

### Utility nodes

Ngoài các node đã giới thiệu, được dùng để truy cập data trong một table (hoặc nhiều table trong trường hợp join), còn có một số utility node được dùng trong plan để đạt tới final result.

Khi statement của bạn yêu cầu sắp xếp result bằng một clause như `ORDER BY`, planner sẽ chèn một Sort node. Nếu query có giới hạn output, chẳng hạn một `LIMIT` clause, một Limit node sẽ được chèn vào plan để giảm final result set.

Trong trường hợp đó, node được dùng thay cho một `UNION ALL` statement là một Append node (hãy nhớ rằng `UNION ALL` cho phép các tuple bị duplicate, còn `UNION` thì không).

Nếu statement của bạn aggregate các query khác nhau, như `UNION`, một Distinct node sẽ được chèn vào. Chính node này còn có một feature khác: nó có thể phục vụ việc chọn các tuple `DISTINCT`.

Khi statement sử dụng một `GROUP BY` clause, planner chèn một GroupAggregate node chịu trách nhiệm gom các tuple. Tương tự, khi statement chứa một window function (xem Chapter 7, Server-Side Programming), planner giới thiệu một WindowAgg node để quản lý việc aggregate tuple cần thiết cho window function.

Trong trường hợp có Common Table Expression (CTE), planner giới thiệu một CTEScan node chịu trách nhiệm join giữa CTE subquery và table thật. Nếu một join yêu cầu materialize một dataset, tức cần mô phỏng một table từ một tập query result, planner giới thiệu một Materialize node.

### Node costs

PostgreSQL planner phải đánh giá execution plan có cost thấp nhất, và để tính mọi alternative có thể có, nó tính cost của tất cả access plan được đánh giá.

Mỗi node gắn với một cost, là ước tính mức độ tốn kém của việc thực thi node đó xét theo tài nguyên tính toán. Dĩ nhiên, mỗi node có một cost thay đổi tùy thuộc vào type và quantity của input, cũng như node type.

PostgreSQL cung cấp một danh sách cost, được biểu diễn bằng các unit tùy ý, cho những operation chính mà một node có thể thực hiện. Vì vậy, việc tính cost của một node là tính cost của từng operation mà node thực hiện, nhân với số lần những operation đó được lặp lại; số lần lặp phụ thuộc vào kích thước data mà node phải đánh giá.

Cost có thể được điều chỉnh trong cluster configuration, tức trong file chính `postgresql.conf` hoặc trong catalog `pg_settings`. Cụ thể, có thể query cluster về các cost chính liên quan đến việc thực thi một node:

```text
    forumdb=> SELECT name, setting
                   FROM pg_settings
                   WHERE name LIKE 'cpu%\_cost'
                        OR name LIKE '%page\_cost'
                  ORDER BY setting DESC;


                name             | setting
   ----------------------+---------
     random_page_cost            | 4
     seq_page_cost               | 1
     cpu_tuple_cost              | 0.01
     cpu_index_tuple_cost | 0.005
     cpu_operator_cost           | 0.0025
```

Các cost trước đó là cost mặc định của một PostgreSQL installation mới, và bạn không nên thay đổi bất kỳ giá trị nào trong số đó trừ khi thực sự chắc chắn về việc mình đang làm. Hãy nhớ rằng cost là thứ khiến planner lựa chọn giữa các plan khác nhau, vì vậy việc set cost không đúng sẽ dẫn đến việc optimizer chọn các execution plan sai.

Cost được biểu diễn như “expense”, nhưng các giá trị đó không liên quan đến thời gian thực thi: cost biểu thị nỗ lực PostgreSQL phải bỏ ra để lấy data; do đó, cost cao hơn phải đòi hỏi nỗ lực lớn hơn.

Như bạn có thể thấy từ danh sách cost trước đó, cơ sở cho mọi phép tính của optimizer là cost của một data page được truy cập theo sequential mode: giá trị này được đặt làm unit cost. CPU cost, tức cost liên quan đến việc phân tích một tuple đã nằm trong memory, nhỏ hơn nhiều so với một unit, trong khi việc truy cập storage theo cách random đắt hơn nhiều so với sequential access.

Cost có thể thay đổi tùy thuộc vào năng lực tính toán của system; cụ thể, việc có các disk storage SSD cấp enterprise có thể giảm `random_page_cost` xuống 1.5, gần bằng sequential page cost.

Việc thay đổi optimizer cost, dù đơn giản như thay đổi một vài setting, đòi hỏi kiến thức rất sâu về PostgreSQL internals và hardware bên dưới, và chỉ hữu ích trong những case rất cụ thể; vì vậy, việc này không được khuyến khích trong gần như mọi scenario và nằm ngoài scope của cuốn sách này. Thay vào đó, bạn sẽ tìm hiểu cách planner estimate cost của việc truy cập data.

Ở phần sau của chapter này, bạn sẽ thấy các cost trước đó được áp dụng như thế nào để tính overall cost của một query plan.

Trong section sau, bạn sẽ tìm hiểu về index, feature giúp PostgreSQL truy cập data hiệu quả hơn.

## Indexes

Index là một data structure cho phép truy cập nhanh hơn tới underlying table để có thể nhanh chóng tìm được các tuple cụ thể. Ở đây, “nhanh” có nghĩa là nhanh hơn việc scan toàn bộ underlying table và phân tích từng tuple.

PostgreSQL hỗ trợ nhiều type index khác nhau, và không phải type nào cũng tối ưu cho mọi scenario và workload. Trong các section sau, bạn sẽ khám phá những type index chính mà PostgreSQL cung cấp; trong mọi trường hợp, bạn vẫn có thể mở rộng PostgreSQL bằng index của riêng mình hoặc index do extension cung cấp.

Một index trong PostgreSQL có thể được build trên một column hoặc nhiều column cùng lúc; PostgreSQL hỗ trợ index có tối đa 32 column.

Một index có thể bao phủ toàn bộ data trong underlying table, hoặc chỉ index những value cụ thể; trong trường hợp đó, index được gọi là “partial”. Ví dụ, bạn có thể quyết định chỉ index những value của một số column mà bạn sẽ sử dụng nhiều nhất.

Một index cũng có thể là unique, nghĩa là nó được dùng để bảo đảm tính duy nhất của các value mà nó index, chẳng hạn như primary key của một table. Ngoài ra, một index có thể được build trên một user-defined function, nghĩa là index sẽ index các giá trị return của những function đó.

> Để được sử dụng trong một index, user-defined function phải được khai báo là `IMMUTABLE`, nghĩa là output của nó phải giống nhau với cùng một input.

PostgreSQL có khả năng mix và match các index với nhau; do đó, nhiều index khác nhau có thể được dùng để đáp ứng query plan. Nhờ feature quan trọng này của PostgreSQL, bạn không cần định nghĩa mọi index permutation có thể có của column, vì PostgreSQL sẽ cố gắng mix các index không liên quan trực tiếp với nhau.

Trong các subsection sau, bạn sẽ tìm hiểu tất cả type index có sẵn trong một PostgreSQL 16 cluster, cũng như cách create hoặc drop một index.

### Index types

Index mặc định PostgreSQL sử dụng là Balanced Tree (B-Tree), một implementation cụ thể của tree giữ cho depth không đổi ngay cả khi size của underlying table tăng mạnh, do đó cần cùng một nỗ lực để traverse từ root đến leaf.

Một B-Tree index có thể được dùng cho hầu hết operator và column type, kể cả so sánh string trong query dựa trên `LIKE`, nhưng nó chỉ hiệu quả nếu pattern bắt đầu bằng một string cố định. B-Tree index cũng hỗ trợ condition `UNIQUE` và vì vậy được dùng để build primary key index.

Một nhược điểm của B-Tree index là nó copy toàn bộ value của column vào tree structure; do đó, nếu bạn dùng B-Tree để index các value lớn (ví dụ, string dài), index sẽ nhanh chóng tăng về size và space.

Một type index khác PostgreSQL cung cấp là hash index: index này được build trên kết quả của một hash function áp dụng cho value của column (hoặc các column). Điều quan trọng cần lưu ý là hash index chỉ có thể được dùng cho equality operator, không dùng được cho range operator hay disequality operator. Thực tế, vì đây là index được build trên một hash function, index không thể so sánh hai hash value để hiểu thứ tự của chúng; chỉ equality (tạo ra cùng một hash value) mới có thể được đánh giá.

Block Range Index (BRIN) là một type index đặc biệt dựa trên range của các value trong data block trên storage. Ý tưởng là mỗi block có một value nhỏ nhất và một value lớn nhất, sau đó index lưu một cặp value cho mỗi data block trên storage. Khi một query tìm một value cụ thể, index biết các value có thể được tìm thấy trong data block nào, nhưng phải đánh giá tất cả tuple trong block.

Vì vậy, type index này không chính xác bằng B-Tree và được gọi là lossy (nhấn mạnh rằng nó không exact, tức có thể có loss), nhưng nó nhỏ hơn nhiều so với mọi type index khác vì chỉ lưu một cặp value cho mỗi data block.

GIN là một type index không trỏ tới một tuple duy nhất mà trỏ tới nhiều value, và ở một mức độ nào đó là một array các value. Thông thường, loại index này được dùng trong các scenario full-text search, khi bạn index một text được viết trong đó có nhiều key bị duplicate (ví dụ, cùng một word hoặc term) trỏ tới các vị trí khác nhau (ví dụ, cùng một word trong các phrase và line khác nhau).

Tiếp theo là Generalized Index Search Tree (GIST), một platform bên trên đó có thể build các type index mới. Ý tưởng là cung cấp một pluggable infrastructure nơi bạn có thể định nghĩa operator và feature có khả năng index một data structure. Một ví dụ là SP-GIST, một spatial index được dùng trong các application địa lý.

### Creating an index

Index có thể được tạo bằng `CREATE INDEX` statement, có dạng như sau:

```sql
   CREATE [ UNIQUE ] INDEX [ CONCURRENTLY ] [ [ IF NOT EXISTS ] name ] ON [
   ONLY ] table_name [ USING method ]
       ( { column_name | ( expression ) } [ COLLATE collation ] [ opclass ] [
   ASC | DESC ] [ NULLS { FIRST | LAST } ] [, ...] )
        [ INCLUDE ( column_name [, ...] ) ]
        [ WITH ( storage_parameter = value [, ... ] ) ]
        [ TABLESPACE tablespace_name ]
        [ WHERE predicate ]
```

Index được nhận diện bằng một mnemonic name, tương tự table mà chúng liên quan. Điều thú vị cần lưu ý là index name luôn unqualified, nghĩa là nó không bao gồm schema nơi index sẽ được đặt: một index luôn được tìm thấy trong chính schema của underlying table. Tuy nhiên, có thể lưu index trong một tablespace khác với tablespace của underlying table, và điều này có thể hữu ích để lưu các index quan trọng trên storage nhanh hơn. Statement hỗ trợ `IF NOT EXISTS` clause để dừng việc create theo cách nhẹ nhàng nếu một index có cùng name đã tồn tại.

`UNIQUE` clause chỉ định rằng index sẽ kiểm tra tính duy nhất của các column của nó. `WHERE` clause cho phép tạo partial index, tức một index chỉ chứa thông tin về các tuple thỏa mãn `WHERE` condition.

`INCLUDE` clause cho phép bạn chỉ định một số column bổ sung của underlying table sẽ được lưu trong index dù không được index. Ý tưởng là nếu index hữu ích cho một index-only scan, bạn vẫn có thể lấy thông tin bổ sung mà không cần quay lại underlying table. Dĩ nhiên, việc có một covering index (tên của một index dùng `INCLUDE` clause) nghĩa là index sẽ tăng size, đồng thời mỗi tuple update có thể cần thêm effort để update index.

`USING` clause cho phép chỉ định type index cần build; nếu không chỉ định, B-Tree mặc định sẽ được dùng.

`CONCURRENTLY` clause cho phép tạo index theo cách concurrent: khi index đang ở build phase, underlying table bị lock chống thay đổi để index có thể hoàn tất việc index các tuple value. Trong một concurrent index creation, table vẫn cho phép thay đổi ngay cả khi index đang được tạo, nhưng sau khi index đã được build xong, cần một pass khác trên underlying table để “điều chỉnh” những gì đã thay đổi trong thời gian đó.

Để thực tế hơn, hãy xem cách build một index đơn giản trên table `posts`. Giả sử chúng ta muốn index category mà một post thuộc về:

```text
   forumdb=> CREATE INDEX idx_post_category
                ON posts( category );
   CREATE INDEX
```

Code trước đó sẽ tạo một index tên `idx_post_category` trên table `posts`, dùng column đơn `category` và type index mặc định (B-Tree).

Ví dụ sau thực hiện điều tương tự, tạo một multi-column index:

```text
   forumdb=> CREATE INDEX idx_author_created_on
                ON posts( author, created_on );
   CREATE INDEX
```

Điều quan trọng cần lưu ý là khi tạo multi-column index, bạn luôn nên đặt các column có tính selectivity cao nhất ở trước. PostgreSQL sẽ xem xét multi-column index từ column đầu tiên trở đi, vì vậy nếu các column đầu có selectivity cao nhất, access method của index sẽ có cost thấp nhất.

Trong ví dụ trước, giả sử chúng ta muốn tìm theo một tổ hợp author và date, ta có thể kỳ vọng nhiều author publish vào một ngày cụ thể, vì vậy date (column `created_on`) sẽ không có tính selectivity cao, ít nhất không cao bằng author cụ thể; đó là lý do chúng ta đẩy column `created_on` sang bên phải trong danh sách column.

Nếu muốn tạo một hash index, chúng ta có thể làm như sau:

```text
   forumdb=> CREATE INDEX idx_post_created_on
                ON posts USING hash ( created_on );
   CREATE INDEX
```

Dĩ nhiên, index như vậy chỉ hữu ích cho equality comparison, vì vậy một query như sau sẽ không bao giờ sử dụng index trước đó:

```sql
   SELECT * FROM posts WHERE created_on < CURRENT_DATE;
```

Nhưng một query như sau có thể sử dụng hash index:

```sql
   SELECT * FROM posts WHERE created_on = CURRENT_DATE;
```

Đó là vì chúng ta đang yêu cầu một equality comparison.

### Inspecting indexes

Index được “gắn” với underlying table, vì vậy `psql` hiển thị các index đã định nghĩa bất cứ khi nào bạn yêu cầu nó mô tả một table bằng special command `\d`:

```text
   forumdb=> \d posts
                                                     Table "forum.posts"
       Column         |             Type               | Collation | Nullable |
    Default
    ----------------+--------------------------+-----------+----------+-------
    -----------------------
    pk             | integer                            |              | not null |
    generated always as identity
    title              | text                           |              |              |
    content            | text                           |              |              |
    author             | integer                        |              | not null |
    category           | integer                        |              | not null |
    reply_to           | integer                        |              |              |
    created_on     | timestamp with time zone |                        |              |
    CURRENT_TIMESTAMP
    last_edited_on | timestamp with time zone |                        |              |
    CURRENT_TIMESTAMP
    editable           | boolean                        |              |              | true
    likes              | integer                        |              |              | 0
    Indexes:
        "posts_pkey" PRIMARY KEY, btree (pk)
        "idx_author_created_on" btree (author, created_on)
        "idx_post_category" btree (category)
        "idx_post_created_on" hash (created_on)


    ...
```

Như bạn có thể thấy từ code fragment trước đó, command hiển thị tất cả index có sẵn cùng method của chúng (ví dụ `btree`) và danh sách column mà index được build trên đó.

Catalog đặc biệt `pg_index` chứa thông tin về các index và các attribute chính của chúng, vì vậy có thể query catalog này để lấy chính thông tin (và nhiều hơn) mà `psql` cung cấp. Cụ thể, vì một index được đăng ký trong `pg_class` với giá trị `relkind` đặc biệt là `i`, chúng ta có thể join `pg_class` và `pg_index` để lấy thông tin chi tiết trong một statement như sau:

```text
    forumdb=> SELECT relname, relpages, reltuples,
                i.indisunique, i.indisclustered, i.indisvalid,
                pg_catalog.pg_get_indexdef(i.indexrelid, 0, true)
                FROM pg_class c JOIN pg_index i on c.oid = i.indrelid
                WHERE c.relname = 'posts';
```

```text
    -[ RECORD 1 ]---+---------------------------------------------------------
    --------------------
    relname          | posts
    relpages         | 21
    reltuples        | 1004
    indisunique      | t
    indisclustered   | f
    indisvalid       | t
    pg_get_indexdef | CREATE UNIQUE INDEX posts_pkey ON posts USING btree (pk)
    -[ RECORD 2 ]---+---------------------------------------------------------
    --------------------
    relname          | posts
    relpages         | 21
    reltuples        | 1004
    indisunique      | f
    indisclustered   | f
    indisvalid       | t
    pg_get_indexdef | CREATE INDEX idx_post_category ON posts USING btree
    (category)
    -[ RECORD 3 ]---+---------------------------------------------------------
    --------------------
    relname          | posts
    relpages         | 21
    reltuples        | 1004
    indisunique      | f
    indisclustered   | f
    indisvalid       | t
    pg_get_indexdef | CREATE INDEX idx_author_created_on ON posts USING btree
    (author, created_on)
    -[ RECORD 4 ]---+---------------------------------------------------------
    --------------------
    relname          | posts
    relpages         | 21
    reltuples        | 1004
    indisunique      | f
    indisclustered   | f
```
