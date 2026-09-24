Chúng ta đã giới thiệu concept về các trigger variable:

- `NEW`
- `OLD`
- `TG_OP`

Bên cạnh các trigger dựa trên data manipulation, chúng ta cũng đã giới thiệu sơ lược các PostgreSQL event trigger, cho phép developer và database administrator kiểm soát tốt hơn việc fire và execute function.

Chúng ta đã hiểu rằng trigger là các event handler cực kỳ phức tạp. Trong chapter này, chúng ta bắt đầu cho thấy sức mạnh của các tool được cung cấp cho PostgreSQL DBA; trong chapter tiếp theo, chúng ta sẽ nói về partitioning và sẽ sử dụng các topic đã trình bày trong chapter này để thực hiện điều đó.

## Kiểm tra kiến thức

- `NEW` record là gì?

  `NEW` record là record sẽ được xử lý trước một statement `INSERT` hoặc một statement `UPDATE`, ví dụ:

  ```text
  insert into mytable(id,city_name) values (1,'New York')
  ```

  ```text
  NEW.id = 1
  NEW.city_name = 'New York'
  ```

  Xem section *Exploring rules in PostgreSQL* để biết thêm chi tiết.

- Chúng ta có thể thực thi một `INSERT` trên hai table trong một transaction bằng rules không?

  Có; chúng ta có thể làm điều đó bằng clause `ALSO`. Xem section *Exploring rules in PostgreSQL* để biết thêm chi tiết.

- Chúng ta có thể làm mọi thứ đã làm với rules bằng triggers không?

  Có; bằng triggers, chúng ta có thể làm mọi thứ đã làm với rules và nhiều hơn nữa. Xem section *Managing triggers in PostgreSQL* để biết thêm chi tiết.

- Chúng ta có thể biết một trigger đã được fire từ event `INSERT`, event `UPDATE` hay event `DELETE` không?

  Có, bằng cách sử dụng variable `TG_OP`. Xem section *Managing triggers in PostgreSQL* để biết thêm chi tiết.

- Chúng ta có thể viết một audit procedure thông báo cho chúng ta khi một DDL đã được execute không?

  Có, bằng cách sử dụng event trigger. Xem section *Event triggers* để biết thêm chi tiết.

## Tài liệu tham khảo

- Tài liệu chính thức về PostgreSQL rules trên `INSERT`, `UPDATE` và `DELETE`: https://www.PostgreSQL.org/docs/current/rules-update.html
- Tài liệu chính thức về PostgreSQL trigger function: https://www.PostgreSQL.org/docs/current/plpgsql-trigger.html
- Tài liệu chính thức về PostgreSQL `ALTER TRIGGER`: https://www.PostgreSQL.org/docs/current/sql-altertrigger.html
- Tài liệu chính thức về PostgreSQL `DROP TRIGGER`: https://www.PostgreSQL.org/docs/current/sql-droptrigger.html
- Tài liệu chính thức về PostgreSQL `EVENT TRIGGER`: https://www.postgresql.org/docs/current/functions-event-triggers.html

## Tìm hiểu thêm trên Discord

Để tham gia cộng đồng Discord của cuốn sách này, nơi bạn có thể chia sẻ feedback, đặt câu hỏi cho tác giả và tìm hiểu về các bản phát hành mới, hãy follow QR code bên dưới:

https://discord.gg/jYWCjF6Tku

# 9 Partitioning

Trong chapter trước, chúng ta đã nói về rules và triggers. Trong chapter này, chúng ta sẽ nói về partitioning. Partitioning là một kỹ thuật cho phép chia một table rất lớn thành các table nhỏ hơn để làm cho query hiệu quả hơn. Trong chapter này, chúng ta sẽ xem cách partition data và, trong một số trường hợp, cách sử dụng rules và triggers đã thấy trong chapter trước để thực hiện partitioning. Chúng ta sẽ bắt đầu bằng việc giới thiệu các concept cơ bản của partitioning, sau đó xem các khả năng PostgreSQL cung cấp để triển khai partitioning.

Chapter này sẽ bao quát các topic sau:

- Concept cơ bản
- Partitioning bằng table inheritance
- Declarative partitioning

## Yêu cầu kỹ thuật

Các example trong chapter có thể chạy trên Docker image `chapter_09`, có trong GitHub repository của cuốn sách: https://github.com/PacktPublishing/Learn-PostgreSQL-Second-Edition.

Để biết hướng dẫn cài đặt và sử dụng Docker image cho cuốn sách này, hãy xem Chapter 1, *Introduction to PostgreSQL*.

## Concept cơ bản

Trước hết, hãy thử hiểu tại sao chúng ta phải partition data. Chúng ta nên bắt đầu bằng việc nói rằng một đặc điểm chung của mọi database là kích thước của chúng luôn tăng. Do đó, một database sau vài tháng tăng trưởng có thể đạt kích thước gigabyte, terabyte hoặc thậm chí petabyte.

Một điều khác chúng ta luôn phải ghi nhớ là không phải mọi table đều tăng với cùng tốc độ hoặc đạt cùng kích thước; một số table lớn hơn các table khác và một số index cũng lớn hơn các index khác.

Chúng ta cũng cần biết rằng có một phần RAM của server, được chia sẻ giữa mọi PostgreSQL process, dùng để quản lý data hiện diện trong các table. Phần RAM này của server được gọi là `shared_buffers`.

Cách PostgreSQL hoạt động như sau:

1. Data được lấy từ hard disk.
2. Data được đặt vào shared buffers.
3. Data được xử lý trong shared buffers.
4. Data được ghi xuống disk.

Thông thường, trên một dedicated server chỉ dành cho PostgreSQL, kích thước của `shared_buffers` vào khoảng một phần ba hoặc một phần tư tổng RAM của server. Một link hữu ích để thiết lập một số PostgreSQL configuration parameter, bao gồm kích thước được khuyến nghị cho `shared_buffers`, là https://pgtune.leopard.in.ua.

Khi một table tăng quá mức so với kích thước của `shared_buffers`, performance có khả năng giảm. Trong trường hợp này, partitioning data có thể giúp chúng ta. Partitioning data nghĩa là chia một table rất lớn thành các table nhỏ hơn theo cách transparent đối với client program. Client program sẽ nghĩ rằng server vẫn chỉ có một table, nhưng việc có các table nhỏ hơn cũng có nghĩa là có các index nhỏ hơn, với khả năng ở lại trong memory cao hơn, từ đó tăng data performance; hơn nữa, việc có các table nhỏ hơn nghĩa là các vacuum process làm việc trên các table nhỏ hơn, giúp giảm thời gian execution của các vacuum process. Cuối cùng, khi chạy `vacuum full`, disk space được table sử dụng sẽ tăng gấp đôi, do đó có nhiều table nhỏ thay vì một table lớn sẽ giảm đáng kể mọi ảnh hưởng từ vấn đề này. Data partitioning có thể được thực hiện theo hai cách:

- Sử dụng table inheritance (cách duy nhất có thể dùng cho PostgreSQL < 10)
- Sử dụng declarative partitioning (cách tốt nhất bắt đầu từ version 10)

Sau khi hiểu khi nào nên partition data, hãy xem những loại table partitioning nào có thể thực hiện được. PostgreSQL hỗ trợ ba loại declarative partitioning:

- Range partitioning
- List partitioning
- Hash partitioning

Bây giờ chúng ta sẽ mô tả chi tiết ba phương pháp này.

Trước khi bắt đầu, hãy nhớ khởi động Docker container có tên `chapter9`, như dưới đây:

```text
$ bash run-pg-docker.sh chapter_09
postgres@learn_postgresql:~$ psql -U forum forumdb
```

## Range partitioning

Range partitioning là khi table được chia thành các “interval”. Các interval không được overlap và range được định nghĩa thông qua một field hoặc một tập các field. Để biết thêm thông tin, xem https://www.postgresql.org/docs/current/ddl-partitioning.html.

Hãy xem một ví dụ về định nghĩa range partitioning. Giả sử chúng ta có table này:

| field date | field_value |
| --- | --- |
| 2023-03-01 | 1 |
| 2023-03-02 | 10 |
| 2023-04-01 | 12 |
| 2023-04-15 | 1 |

*Table 9.1: Table trước khi range partitioning*

Bây giờ hãy xét việc chúng ta muốn chia table này thành hai table. Table thứ nhất (**TABLE A**) sẽ chứa mọi record có value `field_date` nằm trong khoảng từ 2023-03-01 đến 2023-03-31, còn table thứ hai (**TABLE B**) sẽ chứa mọi record có value `field_date` nằm trong khoảng từ 2023-04-01 đến 2023-04-30. Vì vậy, mục tiêu của chúng ta là có hai table như sau:

| field date | field_value |
| --- | --- |
| 2023-03-01 | 1 |
| 2023-03-02 | 10 |

*Table 9.2: Table A*

| field date | field_value |
| --- | --- |
| 2023-04-01 | 12 |
| 2023-04-15 | 1 |

*Table 9.3: Table B*

Điều chúng ta vừa thấy là một ví dụ về partitioning theo range. Cách này hữu ích khi chúng ta có các table lớn, trong đó data có thể được chia theo time range, ví dụ như turnover, audit table hoặc log table.

## List partitioning

Trong list partitioning, table sẽ được partition bằng một list các value.

Hãy xem một ví dụ về định nghĩa list partitioning. Giả sử chúng ta có table này:

| field_state | field_city |
| --- | --- |
| United States | Washington |
| United States | San Francisco |
| Italy | Rome |
| Japan | Tokyo |

*Table 9.4: Table trước khi list partitioning*

Giả sử bây giờ chúng ta muốn chia table này thành `n` table, mỗi state có một table. Table thứ nhất (**TABLE A**) sẽ chứa mọi record có value `field_state` bằng United States, table thứ hai (**TABLE B**) sẽ chứa mọi record có value `field_state` bằng Italy, còn table thứ ba (**TABLE C**) sẽ chứa các record có value `field_state` bằng Japan. Vì vậy, mục tiêu của chúng ta là có ba table như sau:

| field_state | field_city |
| --- | --- |
| United States | Washington |
| United States | San Francisco |

*Table 9.5: Table A*

| field_state | field_city |
| --- | --- |
| Italy | Rome |

*Table 9.6: Table B*

| field_state | field_city |
| --- | --- |
| Japan | Tokyo |

*Table 9.7: Table C*

Đây là một ví dụ về partitioning theo list. Cách này hữu ích khi chúng ta có các table lớn, trong đó data có thể được chia theo một field duy nhất, chẳng hạn field city hoặc state trong telephone directory hoặc customer list.

## Hash partitioning

Khi sử dụng hash partitioning, table sẽ được partition bằng các hash value để chia data vào các table khác nhau.

Hãy xem một ví dụ về hash partitioning. Giả sử chúng ta có table này:

| field date | field_value |
| --- | --- |
| 2023-03-01 | 1 |
| 2023-03-02 | 1 |
| 2023-04-01 | 2 |
| 2023-04-15 | 2 |

*Table 9.8: Table trước khi hash partitioning*

Giả sử bây giờ chúng ta có một hash function chuyển đổi date thành một hash value; ví dụ, hãy xét toán tử `del mod` (`%`):

- `hash(1) = 1`
- `hash(1) = 1`
- `hash(2) = 0`
- `hash(2) = 0`

Vì vậy, sau quá trình partitioning, chúng ta sẽ có hai table:

| field date | field_value |
| --- | --- |
| 2023-03-01 | 1 |
| 2023-03-02 | 1 |

*Table 9.9: Table A*

| field date | field_value |
| --- | --- |
| 2023-04-01 | 2 |
| 2023-04-15 | 2 |

*Table 9.10: Table B*

Đây là một ví dụ về partitioning theo hash.

Trong các section tiếp theo, chúng ta sẽ xem cách PostgreSQL triển khai list, range và hash partitioning, nhưng trước đó, hãy dành thời gian nói về table inheritance.

Để biết thêm thông tin về partitioning, xem https://www.postgresql.org/docs/current/ddl-partitioning.html.

## Table inheritance

Một topic khác chúng ta phải xem xét là inheritance của table. PostgreSQL áp dụng concept inheritance từ database cho object. Concept này rất đơn giản và có thể tóm tắt như sau: giả sử chúng ta có hai table, **TABLE A** và **TABLE B**. Nếu định nghĩa **TABLE A** là parent table và **TABLE B** là child table, điều này có nghĩa là mọi record trong **TABLE B** sẽ có thể được truy cập từ **TABLE A**.

Bây giờ hãy thử đưa ra một ví dụ về điều vừa mô tả:

1. Hãy định nghĩa hai table.

   Table thứ nhất, parent table, được định nghĩa như sau:

   ```text
   forumdb=> create table table_a (
   pk integer not null primary key,
   tag text,
   parent integer);
   CREATE TABLE
   ```

   Và table thứ hai, child table, được định nghĩa như sau:

   ```text
   forumdb=> create table table_b () inherits (table_a);
   CREATE TABLE

   forumdb=> alter table table_b add constraint table_b_pk primary
   key(pk);
   ALTER TABLE
   ```

2. Child table kế thừa tất cả field từ parent table. Parent table được hiển thị như sau:

   ```text
   forumdb=> \d table_a;
                       Table "forum.table_a"
    Column |     Type      | Collation | Nullable | Default


   --------+---------+-----------+----------+---------
    pk       | integer |                  | not null |


   tag     | text       |              |             |



   parent | integer |                  |             |



   Indexes:
         "table_a_pkey" PRIMARY KEY, btree (pk)
   Number of child tables: 1 (Use \d+ to list them.)
   ```

   Và để biết thêm chi tiết, hãy sử dụng command `\d+`:

   ```text
   forumdb=> \d+ table_a;
                      Table "forum.table_a"
    Column | Type    | Collation | Nullable | Default | Storage              |
   Compression | Stats target | Description


   --------+---------+-----------+----------+---------+----------+-----
   --------+--------------+
    pk      | integer |                 | not null |              | plain    |
   |               |


   tag      | text       |             |           |           | extended |
   |                 |



   parent | integer |                  |             |           | plain    |
   |              |



   Indexes:
         "table_a_pkey" PRIMARY KEY, btree (pk)
   Child tables: table_b
   Access method: heap
   ```

   Trong table cuối này, chúng ta có thể thấy `table_b` là child table của `table_a`.

3. Hãy làm tương tự cho table có tên `table_b`:

   ```text
   forumdb=> \d table_b;
                       Table "forum.table_b"
   ```
