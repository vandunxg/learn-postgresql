Đây là query cho clause `ROWS`. Như có thể thấy, mọi thứ hoạt động chính xác như trong ví dụ trước mà không có option `ORDER BY DESC`:

```text
      forumdb=> SELECT x,row_number() OVER w, dense_rank() OVER w,sum(x) OVER w
      FROM (select generate_series(1,8) % 4 as x) V
      WINDOW w AS (ORDER BY x desc ROWS BETWEEN 1 PRECEDING AND CURRENT ROW);
       x | row_number | dense_rank | sum
      ---+------------+------------+-----
       3 |          1 |            1 |    3
       3 |          2 |            1 |    6
       2 |          3 |            2 |    5
       2 |          4 |            2 |    4
       1 |          5 |            3 |    3
       1 |          6 |            3 |    2
       0 |          7 |            4 |    1
       0 |          8 |            4 |    0
      (8 rows)
```

Trong ví dụ này, việc sử dụng function `sum` giúp chúng ta hiểu rõ hơn sự khác biệt giữa option `RANGE` và `ROWS`. Như có thể thấy, option `RANGE` aggregate dữ liệu theo frame (`RANGE`), trong khi option `ROWS` aggregate dữ liệu theo row. Điểm khác biệt chính giữa clause `ROWS` và clause `RANGE` là `ROWS` hoạt động trên từng row, còn `RANGE` hoạt động trên các group. Như vậy, chapter về window function của chúng ta kết thúc.

## Tóm tắt

Trong chapter này, chúng ta đã tìm hiểu cách sử dụng window function. Chúng ta đã thấy rằng bằng cách sử dụng window function, chúng ta có thể tạo ra các aggregate phức tạp hơn so với những aggregate được tạo bằng statement `GROUP BY`, mà chúng ta đã tìm hiểu trong Chapter 5, Advanced Statements. Chúng ta đã học cách sử dụng các function `ROW_NUMBER()`, `FIRST_VALUE()`, `LAST_VALUE()`, `RANK`, `DENSE_RANK()`, `LAG()`, `LEAD()`, `CUME_DIST()` và `NTILE()`. Chúng ta cũng đã thấy sự khác biệt giữa việc tạo aggregate bằng clause `ROWS BETWEEN` và `RANGE BETWEEN`. Bạn có thể sử dụng những gì đã học trong chapter này cho các hoạt động data mining để công việc dễ dàng hơn nhiều.

Để biết thêm thông tin về window function, bạn có thể tham khảo tài liệu chính thức: https://www.postgresql.org/docs/current/functions-window.html.

Trong chapter tiếp theo, chúng ta sẽ nói về server-side programming. Chúng ta sẽ xem cách tạo các function để sử dụng ở phía server và, nếu cần, nơi sử dụng window function.

## Kiểm tra kiến thức

- Hãy xem xét hai query sau:

  1. `select category,count(*) from posts group by category order by category;`
  2. `select category, count(*) over (partition by category) from posts order by category;`

  Query nào trong hai query có số record lớn hơn?

  Query thứ hai có số record lớn hơn.

  Xem section Using basic statement window functions để biết thêm chi tiết.

- Hãy xem xét hai query sau:

  1. `select category,count(*) from posts group by category order by category;`
  2. `select distinct category, count(*) over (partition by category) from posts order by category;`

  Query nào trong hai query có số record lớn hơn?

  Hai query có cùng số record.

  Xem section Using basic statement window functions để biết thêm chi tiết.

- Query nào trong hai query sau đúng về semantic?

  1. `select category,row_number() over w,title from posts WINDOW w as (partition by category order by title) order by category;`
  2. `select category,row_number() over w,title from posts WINDOW w as (partition by category) order by category;`

  Query thứ nhất đúng về semantic vì function `row_number()` phụ thuộc vào `order by`.

  Xem section The row number function để biết thêm chi tiết.

- Có thể lấy value đầu tiên trong một partition không?

  Có, chúng ta có thể làm vậy bằng function `first_value()`. Xem section `FIRST_VALUE` để biết thêm chi tiết.

- Có thể tính tổng tăng dần từng row trong một table không?

  Có, chúng ta có thể làm vậy bằng clause `BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`.

  Xem section Using advanced statement window functions để biết thêm chi tiết.

## Tài liệu tham khảo

- Tài liệu chính thức về PostgreSQL window function: https://www.postgresql.org/docs/current/functions-window.html

## Tìm hiểu thêm trên Discord

Để tham gia cộng đồng Discord dành cho cuốn sách này, nơi bạn có thể chia sẻ feedback, đặt câu hỏi cho tác giả và tìm hiểu về các bản phát hành mới, hãy follow QR code bên dưới:

https://discord.gg/jYWCjF6Tku

# 7. Lập trình phía server

Trong các chapter trước, chúng ta đã học cách thực thi SQL query. Chúng ta bắt đầu bằng việc viết các query đơn giản, sau đó chuyển sang viết các query phức tạp hơn; chúng ta đã học cách sử dụng aggregate theo cách truyền thống, và trong Chapter 5, Advanced Statements, chúng ta đã nói về window function, một cách khác để viết aggregate. Trong chapter này, chúng ta sẽ bổ sung server-side programming vào danh sách các kỹ năng đó. Server-side programming có thể hữu ích trong nhiều trường hợp vì nó chuyển logic programming từ phía client sang phía database. Ví dụ, chúng ta có thể lấy một function đã được viết nhiều lần ở các vị trí khác nhau trong application program và chuyển nó vào server để chỉ viết một lần, nghĩa là khi cần sửa đổi, chúng ta chỉ phải sửa một function. Trong chapter này, chúng ta cũng sẽ xem PostgreSQL có thể quản lý các server-side programming language khác nhau như thế nào, và sẽ thấy server-side programming rất hữu ích nếu cần xử lý một lượng lớn dữ liệu đã được extract từ các table. Chúng ta sẽ đề cập đến việc mọi function chúng ta viết đều có thể được gọi trong bất kỳ SQL statement nào. Chúng ta cũng sẽ thấy rằng trong một số trường hợp, với một số loại function nhất định, có thể tạo index trên các function đó.

Một tính năng khác của server-side programming là khả năng định nghĩa data tùy chỉnh. Trong chapter này, chúng ta sẽ xem một số ví dụ về việc đó.

Nói một cách đơn giản, chapter này sẽ thảo luận các nội dung sau:

- Khám phá data type
- Khám phá function và language
- Data type NoSQL

## Yêu cầu kỹ thuật

Trước khi bắt đầu, hãy nhớ khởi động Docker container có tên `chapter_07`, như bên dưới:

```text
      $ bash run-pg-docker.sh chapter_07
      postgres@learn_postgresql:~$ psql -U forum forumdb
```

## Khám phá data types

Với tư cách người dùng, chúng ta đã có cơ hội trải nghiệm sức mạnh và tính linh hoạt của server-side function; ví dụ, trong Chapter 5, Advanced Statements, chúng ta đã sử dụng một query tương tự query sau:

```text
      forumdb=> select * from categories where upper(title) like 'A%';
       pk | title |            description
      ----+-------+------------------------------
        4 | A.I   | Machine Learning discussions
      (1 row)
```

Trong đoạn code này, function `upper` là một server-side function; function này chuyển tất cả ký tự trong một string thành chữ uppercase. Trong chapter này, chúng ta sẽ có được kiến thức để viết những function như function `upper` được gọi trong query trước đó.

Trong section này, chúng ta sẽ nói về data type. Chúng ta sẽ đề cập ngắn gọn đến các type chuẩn được PostgreSQL quản lý và cách tạo type mới.

### Khái niệm extensibility

Extensibility là gì? Extensibility là khả năng mở rộng functionality và data type của PostgreSQL. Extensibility là một tính năng PostgreSQL cực kỳ hữu ích vì cho phép chúng ta có các data type, function và functional index không có trong base system. Trong chapter này, chúng ta sẽ đề cập đến extension ở cấp data type, cũng như việc bổ sung các function mới.

### Standard data types

Trong các chapter trước, dù chưa thật sự rõ ràng, chúng ta đã sử dụng các data type chuẩn. Đó là khi chúng ta học cách sử dụng các command Data Definition Language (DDL). Tuy nhiên, bây giờ chúng ta sẽ xem xét chủ đề này sâu hơn. Sau đây là danh sách ngắn các data type được sử dụng nhiều nhất:

- Boolean type
- Numeric types
- Character types
- Date/time
- NoSQL data types: hstore, xml, json và jsonb

Với mỗi data type, chúng ta sẽ trình bày một operation mẫu, sau đó là phần giải thích ngắn. Để biết thêm thông tin về các data type chuẩn được PostgreSQL hỗ trợ, hãy tham khảo tài liệu chính thức tại https://www.postgresql.org/docs/current/extend-type-system.html.

### Boolean data type

Trước tiên, chúng ta sẽ giới thiệu Boolean data type. PostgreSQL hỗ trợ Boolean data type. Boolean type (được xác định bằng `BOOLEAN` hoặc `BOOL`), giống như tất cả data type được PostgreSQL hỗ trợ, có thể nhận value `NULL`. Vì vậy, Boolean data type có thể nhận các value `NULL`, `FALSE` và `TRUE`. Input function của Boolean type chấp nhận các biểu diễn sau cho trạng thái `TRUE`:

| State | true | yes | on | 1 |
| --- | --- | --- | --- | --- |

Đối với trạng thái `false`, chúng ta có các biểu diễn sau:

| State | false | no | off | 0 |
| --- | --- | --- | --- | --- |

Hãy xem một số ví dụ, bắt đầu với table `users`:

1. Trước tiên, hãy hiển thị nội dung của table `users`:

   ```text
   forumdb=> select * from users;
    pk |      username       | gecos |                email
   ----+----------------+-------+------------------------
     1 | luca_ferrari        |         | luca@pgtraining.com
     2 | enrico_pirozzi |              | enrico@pgtraiing.com
     3 | newuser             |         | newuser@pgtraining.com
   (3 rows)
   ```

2. Bây giờ hãy thêm một Boolean data type vào table `users`:

   ```text
   forumdb=> alter table users add user_on_line boolean;
   ALTER TABLE
   ```

3. Hãy update một số value:

   ```text
   forumdb=> update users set user_on_line = true where pk=1;
   UPDATE 1
   ```

4. Bây giờ, nếu muốn tìm tất cả record có field `user_on_line` được đặt thành `true`, chúng ta phải thực hiện như sau:

   ```text
   forumdb=> \x
   Expanded display is on.
   forumdb=> select * from users where user_on_line = true;
   -[ RECORD 1 ]+--------------------
   pk              | 1
   username        | luca_ferrari
   gecos           |
   email           | luca@pgtraining.com
   user_on_line | t
   ```

5. Nếu muốn tìm tất cả record có field `user_on_line` được đặt thành `NULL`, như chúng ta đã thấy trong Chapter 4, Basic Statements, chúng ta phải thực hiện như sau:

   ```text
   forumdb=> select * from users where user_on_line is NULL;
   -[ RECORD 1 ]+-----------------------
   pk              | 2
   username        | enrico_pirozzi
   gecos           |
   email           | enrico@pgtraiing.com
   user_on_line |
   -[ RECORD 2 ]+-----------------------
   pk              | 3
   username        | newuser
   gecos           |
   email           | newuser@pgtraining.com
   user_on_line |
   ```

Như vậy, chúng ta đã tìm hiểu Boolean data type.

### Numeric data type

PostgreSQL hỗ trợ nhiều loại numeric data type; những loại được sử dụng nhiều nhất như sau:

- `integer` hoặc `int4` (số nguyên 4 byte).
- `bigint` hoặc `int8` (số nguyên 8 byte).
- `real` (độ chính xác biến thiên 4 byte, không chính xác với độ chính xác 6 chữ số thập phân).
- `double precision` (độ chính xác biến thiên 8 byte, không chính xác với độ chính xác 15 chữ số thập phân).
- `numeric` (precision, scale), trong đó precision của một numeric là tổng số chữ số có nghĩa trong toàn bộ number, còn scale của một numeric là số chữ số thập phân trong phần fractional. Ví dụ, `5.827` có precision bằng 4 và scale bằng 3.

Bây giờ, chúng ta sẽ xem một số ví dụ ngắn về từng type trong các section tiếp theo.

#### Integer types

Như có thể thấy ở đây, nếu cast một number sang integer type như `integer` hoặc `bigint`, PostgreSQL sẽ tạo ra value bị truncate từ input number:

```text
   forumdb=> \x
   Expanded display is off.
   forumdb=> select 1.123456789::integer as my_field;
       my_field
   ----------
              1
   (1 row)


   forumdb=> select 1.123456789::int4 as my_field;
       my_field
   ----------
              1
   (1 row)
   forumdb=> select 1.123456789::bigint as my_field;
       my_field
   ----------
              1
   (1 row)


   forumdb=> select 1.123456789::int8 as my_field;
       my_field
   ----------
              1
   (1 row)
```

#### Data type number với precision cố định

Trong ví dụ sau, chúng ta sẽ xem query tương tự query đã thấy trước đó, nhưng lần này sẽ cast sang `real` và `double precision`:

```text
      forumdb=> select 1.123456789::real as my_field;
       my_field
      -----------
       1.1234568
      (1 row)


      forumdb=> select 1.123456789::double precision as my_field;
        my_field
      -------------
       1.123456789
      (1 row)
```

Như có thể thấy ở đây, trong query đầu tiên, result bị cắt đến chữ số thứ sáu; điều này xảy ra vì type `real` có độ chính xác ít nhất 6 chữ số thập phân.

Bây giờ giả sử chúng ta muốn tính tổng value `0.1` 10 lần. Result đúng phải là number `1`. Thay vào đó, nếu thực thi:

```text
      forumdb=> select sum(0.1::real) from generate_series(1,10);
          sum
      -----------
       1.0000001
      (1 row)
```

Chúng ta nhận được value `1.0000001`. Điều này xảy ra do lỗi rounding nội tại trong `real` data type, vì vậy không nên sử dụng `real` data type trong các field biểu diễn tiền. Cách đúng để thực hiện phép tính tổng này là sử dụng `numeric` data type.

#### Data type number với precision tùy ý

Trong section cuối cùng về numeric data type này, chúng ta sẽ thực hiện query giống query đã thấy trước đó, nhưng sẽ cast sang arbitrary precision:

```text
      forumdb=> select 1.123456789::numeric(10,1) as my_field;
       my_field
      ----------
             1.1
      (1 row)


   forumdb=> select 1.123456789::numeric(10,5) as my_field;
    my_field
   ----------
      1.12346
   (1 row)


   forumdb=> select 1.123456789::numeric(10,9) as my_field;
      my_field
   -------------
    1.123456789
   (1 row)
```

Như có thể thấy từ các ví dụ ở đây, chúng ta quyết định scale có bao nhiêu chữ số.

Nhưng điều gì xảy ra nếu chúng ta thực hiện query như sau?

```text
   forumdb=> select 1.123456789::numeric(10,11) as my_field;
   ERROR:      numeric field overflow
   DETAIL: A field with precision 10, scale 11 must round to an absolute
   value less than 10^-1.
```

Kết quả là một error. Điều này xảy ra vì data type được định nghĩa là numeric type với value precision bằng 10, do đó chúng ta không thể có parameter scale bằng hoặc lớn hơn value precision.

Tương tự, ví dụ tiếp theo cũng tạo ra một error:

```text
   forumdb=> select 1.123456789::numeric(10,10) as my_field;
   ERROR:      numeric field overflow
   DETAIL: A field with precision 10, scale 10 must round to an absolute
   value less than 1.
```

Trong ví dụ trước, query tạo ra một error vì scale là 10, nghĩa là chúng ta phải có 10 chữ số, nhưng tổng cộng chúng ta có 11 chữ số:

```text
 Digits         1   2   3      4       5       6        7        8       9       10       11
                1   .   1      2       3       4        5        6       7        8       9
```
