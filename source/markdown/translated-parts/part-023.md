Tuy nhiên, nếu trong số của chúng ta không có chữ số đầu tiên, query sẽ hoạt động:

```text
      forumdb=> select 0.123456789::numeric(10,10) as my_field;
           my_field
      --------------
       0.1234567890
      (1 row)
```

Bây giờ hãy quay lại ví dụ trong paragraph trước, vốn cho ra một sum không chính xác, và lặp lại ví dụ bằng data type `numeric`:

```text
      forumdb=> select sum(0.1::numeric(2,2)) from generate_series(1,10);
       sum
      ------
       1.00
      (1 row)
```

Như có thể thấy, giá trị của sum hiện đã chính xác; vì vậy, cách đúng để biểu diễn tiền là sử dụng data type `numeric`.

Như vậy, chúng ta đã tìm hiểu toàn bộ các data type numeric khác nhau.

## Data type ký tự

Các data type ký tự được sử dụng nhiều nhất trong PostgreSQL là:

- `character(n)/char(n)` (độ dài cố định, được đệm bằng khoảng trắng)
- `character varying(n)/varchar(n)` (độ dài thay đổi với giới hạn)
- `varchar/text` (độ dài thay đổi không giới hạn)

Bây giờ, chúng ta sẽ xem một số ví dụ để thấy PostgreSQL quản lý các loại data type này như thế nào.

### Data type ký tự với độ dài cố định

Chúng ta sẽ kiểm tra cách chúng hoạt động bằng ví dụ sau:

1. Hãy bắt đầu bằng cách tạo một test table mới:

```text
         forumdb=> create table new_tags (
         pk integer not null primary key,
         tag char(10)
         );
         CREATE TABLE
```

Trong code trước, chúng ta đã tạo một table mới tên là `new_tags` với field `tag` có data type `char(10)`.

2. Bây giờ hãy thêm một số record và xem PostgreSQL hoạt động như thế nào:

```text
      forumdb=> insert into new_tags values (1,'first tag');
      INSERT 0 1
      forumdb=> insert into new_tags values (2,'tag');
      INSERT 0 1
```

Để tiếp tục phân tích, chúng ta phải giới thiệu hai function mới:

- `length(p)`: đếm số ký tự, trong đó `p` là một input parameter và là một string
- `octet_length(p)`: đếm số byte, trong đó `p` là một input parameter và là một string

3. Hãy thực thi query sau:

```text
      forumdb=> \x
      Expanded display is on.
      forumdb=> select pk,tag,length(tag),octet_length(tag),char_
      length(tag) from new_tags;
      -[ RECORD 1 ]+-----------
      pk               | 1
      tag              | first tag
      length           | 9
      octet_length | 10
      char_length      | 9
      -[ RECORD 2 ]+-----------
      pk               | 2
      tag              | tag
      length           | 3
      octet_length | 10
      char_length      | 3
```

Như có thể thấy, tổng độ dài của vùng space được field chiếm bên trong luôn là 10; điều này đúng ngay cả khi số ký tự được nhập khác nhau. Điều này xảy ra vì chúng ta đã định nghĩa field là `char(10)`, với độ dài cố định là 10, nên ngay cả khi chèn một string ngắn hơn, phần chênh lệch giữa 10 và số ký tự thực của string sẽ được lấp đầy bằng các ký tự khoảng trắng.

### Data type ký tự với độ dài thay đổi có giới hạn

Trong section này, chúng ta sẽ lặp lại chính ví dụ đã dùng ở section trước, nhưng lần này sẽ sử dụng data type `varchar(10)` cho field `tag`:

1. Hãy tạo lại table `new_tags`:

```text
              forumdb=> drop table if exists new_tags;
              DROP TABLE


              forumdb=> create table new_tags (
              pk integer not null primary key,
              tag varchar(10)
              );
              CREATE TABLE
```

2. Sau đó, hãy insert một số data:

```text
              forumdb=> insert into new_tags values (1,'first tag');
              INSERT 0 1


              forumdb=> insert into new_tags values (2,'tag');
              INSERT 0 1
```

3. Bây giờ, nếu lặp lại query như trước, chúng ta nhận được kết quả sau:

```text
              forumdb=> \x
              Expanded display is off.
              forumdb=> select pk,tag,length(tag),octet_length(tag) from new_tags
              ;
               pk |      tag      | length | octet_length
              ----+-----------+--------+--------------
                1 | first tag |            9 |               9
                2 | tag           |        3 |               3
              (2 rows)
```

Như có thể thấy, lần này, kích thước thực bên trong và số ký tự trong string là giống nhau.

4. Bây giờ hãy thử insert một string dài hơn 10 ký tự và xem điều gì xảy ra:

```text
             forumdb=> insert into new_tags values (3,'this sentence has more
             than 10 characters');
             ERROR:   value too long for type character varying(10)
```

PostgreSQL trả lời chính xác bằng một error vì input string vượt quá kích thước của field.

### Data type ký tự với độ dài thay đổi không giới hạn

Trong section này, chúng ta lại sử dụng cùng ví dụ như trước, nhưng lần này sẽ dùng data type `text` cho field `tag`.

Hãy tạo lại table `new_tags` và insert lại cùng data đã insert trước đó:

```text
   forumdb=>      drop table if exists new_tags;
   DROP TABLE


   forumdb=> create table new_tags (
   pk integer not null primary key,
   tag text
   );
   CREATE TABLE


   forumdb=> insert into new_tags values (1,'first tag'), (2,'tag'),(3,'this
   sentence has more than 10 characters');
   INSERT 0 3
```

Lần này, PostgreSQL insert chính xác cả ba record. Đó là vì data type `text` là một data type ký tự có độ dài không giới hạn, như có thể thấy trong query sau:

```text
   forumdb=> select pk,substring(tag from 0 for 20),length(tag),octet_
   length(tag) from new_tags ;
    pk |          substring         | length | octet_length
   ----+---------------------+--------+--------------
        1 | first tag               |       9 |               9
        2 | tag                     |       3 |               3
        3 | this sentence has m |          41 |              41
   (3 rows)
```

Trong ví dụ trước, chúng ta có thể thấy data type `text` hoạt động chính xác như data type `varchar(n)` đã thấy trước đó. Điểm khác biệt duy nhất giữa `text` và `varchar(n)` là type `text` không có giới hạn kích thước. Điều quan trọng cần lưu ý là trong query trước, chúng ta đã sử dụng function `substring`. Function `substring` lấy một phần của string, bắt đầu từ vị trí do parameter `from` chỉ định và kéo dài `n` ký tự; ví dụ, nếu viết `substring(tag from 0 for 20)`, nghĩa là chúng ta muốn lấy 20 ký tự đầu tiên của string `tag` làm output.

Như vậy, chúng ta đã trình bày xong tất cả data type ký tự.

## Data type date/timestamp

Trong section này, chúng ta sẽ nói về cách lưu trữ date và time trong PostgreSQL. PostgreSQL hỗ trợ cả date và time, cũng như sự kết hợp giữa date và time (`timestamp`). PostgreSQL quản lý thời gian với cả thiết lập có time zone và không có time zone, như được mô tả trong documentation chính thức (https://www.postgresql.org/docs/current/datatype-datetime.html).

> PostgreSQL hỗ trợ đầy đủ các SQL date và time type. Date được tính theo lịch Gregorian.

### Data type date

Việc quản lý date thường trở thành một bài toán khó đối với developer. Đó là vì date được biểu diễn khác nhau tùy theo quốc gia nơi chúng ta phải lưu data – ví dụ, cách của Mỹ là month/day/year, còn format của châu Âu là day/month/year. PostgreSQL giúp chúng ta bằng cách cung cấp các công cụ cần thiết để giải quyết vấn đề này tốt nhất, như sau:

1. Điều đầu tiên chúng ta phải làm là xem PostgreSQL lưu trữ date bên trong như thế nào. Để làm vậy, chúng ta phải thực hiện query sau:

```text
               forumdb=> \x
               Expanded display is on.
               forumdb=> select * from pg_settings where name ='DateStyle';
               -[ RECORD 1 ]---+--------------------------------------------------
               --
               name                | DateStyle
               setting             | ISO, MDY
               [..]
               sourcefile          |
               sourceline          |
               pending_restart | f
```

Trước hết, hãy xem view `pg_settings`. Bằng cách sử dụng view `pg_settings`, chúng ta có thể xem các parameter được thiết lập trong file configuration `postgresql.conf`. Trong result trước, chúng ta thấy configuration để hiển thị date là MDY (month/day/year). Nếu muốn thay đổi parameter này trên toàn cục, chúng ta phải chỉnh sửa file `postgresql.conf`.

2. Trên một server Debian hoặc dựa trên Debian, chúng ta có thể chỉnh sửa file như sau:

```text
            root@pgdev:/# vim /etc/postgresql/16/main/postgresql.conf
```

3. Sau đó, chúng ta phải sửa section sau:

```text
            #Locale and Formatting


            datestyle = 'iso, mdy'
```

4. Sau khi thay đổi parameter này, trong query trên `pg_settings`, parameter `context` là `'user'`; chúng ta chỉ cần reload server. Trong trường hợp này, không cần restart:

```text
            root@pgdev:/# service postgresql reload
            [ ok ] Reloading postgresql configuration (via systemctl):
            postgresql.service.
```

Để biết thêm thông tin về view `pg_settings`, chúng tôi đề nghị truy cập https://www.postgresql.org/docs/current/view-pg-settings.html.

5. Chúng ta đã biết các parameter bên trong để hiển thị date, vì vậy bây giờ hãy xem cách insert, update và hiển thị date. Nếu biết giá trị của parameter date-style, cách PostgreSQL chuyển một string thành date là như sau:

```text
             forumdb=> \x
             Expanded display is off.
             forumdb=> select '12-31-2020'::date;
                  date
             ------------
              2020-12-31
             (1 row)
```

Cách này đơn giản nhưng không đặc biệt thân thiện với người dùng. Cách tốt nhất để quản lý date là sử dụng một số function PostgreSQL cung cấp cho chúng ta.

6. Function đầu tiên chúng ta sẽ nói đến là function `to_date()`. Function `to_date()` chuyển một string cho trước thành date. Syntax của function `to_date()` như sau:

```text
              forumdb=> select to_date('31/12/2020','dd/mm/yyyy') ;
                to_date
             ------------
              2020-12-31
             (1 row)
```

Function `to_date()` nhận hai string parameter. Parameter thứ nhất chứa value mà chúng ta muốn chuyển thành date. Parameter thứ hai chứa pattern của date. Function `to_date()` trả về một date value.

7. Bây giờ hãy quay lại table `posts` và thực thi query sau:

```text
              forumdb=> \x
              Expanded display is on.
              forumdb=> select pk,title,created_on from posts;
              -[ RECORD 1 ]-----------------------------
              pk           | 5
              title        | Indexing PostgreSQL
              created_on | 2023-01-23 15:21:55.747463+00
              -[ RECORD 2 ]-----------------------------
              pk           | 6
              title        | Indexing Mysql
              created_on | 2023-01-23 15:22:02.38953+00
              -[ RECORD 3 ]-----------------------------
              pk           | 7
              title        | A view of      Data types in C++
              created_on | 2023-01-23 15:26:21.367814+00
```

Làm thế nào chúng ta có các combination date/time (timestamp) nếu chưa từng có ai nhập những value này vào table? Điều này có thể xảy ra vì table `posts` đã được tạo như sau:

```text
              forumdb=> \d posts;
               Table "public.posts"
                Column             | Type                          |[...]| Default
               ----------------+-------------------------+[...]+--------
              pk               | integer                       |       | [..]
              title            | text                          |       |
              [......]
              created_on       | timestamp with time zone|             | CURRENT_TIMESTAMP
```

Như có thể thấy, field `created_on` có `CURRENT_TIMESTAMP` làm giá trị mặc định, nghĩa là nếu không có value nào được insert, current timestamp của server sẽ được insert. Bây giờ giả sử chúng ta muốn hiển thị date theo format khác – ví dụ format châu Âu, `created_on: 03-01-2020`.

8. Để đạt được mục tiêu này, chúng ta phải sử dụng một built-in function khác, function `to_char`:

```text
             forumdb=> select pk,title,to_char(created_on,'dd-mm-yyyy') as
             created_on
             from posts;
             -[ RECORD 1 ]----------------------------
             pk          | 5
             title       | Indexing PostgreSQL
             created_on | 23-01-2023
             -[ RECORD 2 ]----------------------------
             pk          | 6
             title       | Indexing Mysql
             created_on | 23-01-2023
             -[ RECORD 3 ]----------------------------
             pk          | 7
             title       | A view of     Data types in C++
             created_on | 23-01-2023
```

Như được minh họa ở đây, `to_char()` là inverse của function `to_date()`.

## Data type timestamp

PostgreSQL có thể quản lý date và time có time zone và không có time zone. Chúng ta có thể lưu cả date và time bằng data type `timestamp`. Trong PostgreSQL có data type `timestamp with time zone` để hiển thị date và time với time zone, và data type `timestamp without time zone` để lưu date và time không có time zone.

Bây giờ hãy đi qua một số ví dụ. Trước hết, hãy tạo một table mới:

```text
   forumdb=> create table new_posts as select pk,title,created_on::timestamp
   with time zone as created_on_t, created_on::timestamp without time zone as
   create_on_nt from posts;
   SELECT 3
```

Chúng ta vừa tạo một table mới tên là `new_posts` với structure sau:

```text
      forumdb=# \d new_posts;
       Table "public.new_posts"
       Column       | Type                           | [...]
      --------------+----------------------------+----------
       pk           | integer                         |
       title        | text                            |
       created_on_t | timestamp with time zone        |
       create_on_nt | timestamp without time zone |
```

Table này hiện có cùng value cho field `create_on_t` (`timestamp with time zone`) và field `created_on_nt` (`timestamp without time zone`), như có thể thấy ở đây:

```text
      forumdb=> select * from new_posts ;
      -[ RECORD 1 ]+------------------------------
      pk           | 5
      title        | Indexing PostgreSQL
      created_on_t | 2023-01-23 15:21:55.747463+00
      create_on_nt | 2023-01-23 15:21:55.747463
      -[ RECORD 2 ]+------------------------------
      pk           | 6
      title        | Indexing Mysql
      created_on_t | 2023-01-23 15:22:02.38953+00
      create_on_nt | 2023-01-23 15:22:02.38953
      -[ RECORD 3 ]+------------------------------
      pk           | 7
      title        | A view of    Data types in C++
      created_on_t | 2023-01-23 15:26:21.367814+00
      create_on_nt | 2023-01-23 15:26:21.367814
```

Bây giờ hãy giới thiệu một PostgreSQL environment variable có tên là biến `timezone`. Biến này cho biết value hiện tại của time zone:

```text
      forumdb=> show timezone;
      -[ RECORD 1 ]-----
      TimeZone | Etc/UTC
```

Trên server này, time zone được đặt là UTC; nếu muốn chỉ thay đổi value này trong session hiện tại, chúng ta phải thực hiện query sau:

```text
   forumdb=> set timezone='CET';
   SET
```

Bây giờ, time zone được đặt là CET:

```text
   forumdb=> show timezone;
   -[ RECORD 1 ]-
   TimeZone | CET
```

Bây giờ, nếu thực thi lại query đã thực hiện trước đó, chúng ta sẽ thấy field có time zone đã thay đổi value:

```text
   forumdb=> select * from new_posts ;
   -[ RECORD 1 ]+------------------------------
   pk              | 5
   title           | Indexing PostgreSQL
   created_on_t | 2023-01-23 16:21:55.747463+01
   create_on_nt | 2023-01-23 15:21:55.747463
   -[ RECORD 2 ]+------------------------------
   pk              | 6
   title           | Indexing Mysql
   created_on_t | 2023-01-23 16:22:02.38953+01
   create_on_nt | 2023-01-23 15:22:02.38953
   -[ RECORD 3 ]+------------------------------
   pk              | 7
   title           | A view of      Data types in C++
   created_on_t | 2023-01-23 16:26:21.367814+01
   create_on_nt | 2023-01-23 15:26:21.367814
```

Điều này cho thấy sự khác biệt giữa `timestamp with a time zone` và `timestamp without a time zone`. Để biết thêm thông tin về chủ đề date và time, hãy tham khảo documentation chính thức tại https://www.postgresql.org/docs/current/datatype-datetime.html.

## Data type NoSQL

Trong section này, chúng ta sẽ tiếp cận các data type NoSQL hiện có trong PostgreSQL. Vì cuốn sách này không tập trung cụ thể vào NoSQL, chúng ta sẽ chỉ xem xét nhanh.
