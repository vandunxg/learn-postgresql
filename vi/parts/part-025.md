Bây giờ, giả sử chúng ta muốn xóa record có field `title` bằng `A view of Data types in C++`. Table `posts` có field `pk` làm primary key, và với record `A view of Data types in C++`, giá trị của `pk` bằng `7`; vì vậy trước hết, hãy xóa các record khỏi table `j_posts_tags` mà giá trị `post_pk=7`. Lý do là có một foreign key liên kết các table `posts` và `j_posts_tags`:

```text
     forumdb=> delete from j_posts_tags where post_pk = 7;
     DELETE 1
```

Bây giờ hãy gọi function `delete_posts`, sử dụng `A view of Data types in C++` làm parameter. Đây là trạng thái sau khi chúng ta gọi function `delete_posts`:

```text
     forumdb=> select delete_posts('A view of            Data types in C++');
      delete_posts
     --------------
                   7
     (1 row)
     forumdb=> select pk,title from posts order by pk;
      pk |          title
     ----+---------------------
       5 | Indexing PostgreSQL
       6 | Indexing Mysql
     (2 rows)
```

Trong function này, chúng ta đã giới thiệu một loại data type mới - data type `setof`. Directive `setof` đơn giản định nghĩa một result set của một data type. Ví dụ, function `delete_posts` được định nghĩa để trả về một set các integer, vì vậy result của nó sẽ là một integer dataset. Chúng ta có thể sử dụng directive `setof` với bất kỳ data type nào.

## SQL functions trả về table

Trong section trước, chúng ta đã thấy cách viết một function trả về một result set của một data type duy nhất; tuy nhiên, có thể có những trường hợp chúng ta cần function trả về một result set gồm nhiều field. Ví dụ, hãy xét cùng function như trước, nhưng lần này chúng ta muốn cặp `pk`, `title` được trả về làm result, vì vậy function của chúng ta trở thành như sau:

```text
     forumdb=> create or replace function delete_posts_table (p_title text)
     returns table (ret_key integer,ret_title text) AS $$
     delete from posts where title=p_title returning pk,title;
     $$
     language SQL;
     CREATE FUNCTION
```

Điểm khác biệt duy nhất giữa function này và function trước là hiện giờ function trả về một table type; bên trong table type, chúng ta phải chỉ định tên và type của các field. Như đã thấy trước đây, đây là trạng thái trước khi gọi function:

```text
    forumdb=> select pk,title from posts order by pk;
     pk |            title
    ----+---------------------
        5 | Indexing PostgreSQL
        6 | Indexing Mysql
    (2 rows)
```

Bây giờ hãy insert một record mới:

```text
    forumdb=> insert into posts(title,author,category) values ('My new
    post',1,1);
    INSERT 0 1
```

Bây giờ hãy gọi function `delete_posts_table`. Cách gọi function đúng là:

```text
    forumdb=> select * from         delete_posts_table('My new post');
     ret_key |     ret_title
    ---------+-------------
             9 | My new post
    (1 row)
    )
```

Đây là trạng thái sau khi gọi function:

```text
    forumdb=> select pk,title from posts order by pk;
     pk |            title
    ----+---------------------
        5 | Indexing PostgreSQL
        6 | Indexing Mysql
    (2 rows)
```

Các function trả về một table có thể được xử lý như các table thực, theo nghĩa chúng ta có thể sử dụng chúng với các option `in`, `exists`, `join`, v.v.

## Polymorphic SQL functions

Trong section này, chúng ta sẽ nói ngắn gọn về polymorphic SQL functions.

Polymorphic function hữu ích cho DBA khi chúng ta cần viết một function phải làm việc với các data type khác nhau. Để hiểu rõ hơn về polymorphic function, hãy bắt đầu bằng một ví dụ. Giả sử chúng ta muốn tạo lại một thứ trông giống function Oracle `NVL` - nói cách khác, chúng ta muốn tạo một function nhận hai parameter và thay parameter đầu tiên bằng parameter thứ hai nếu parameter đầu tiên là `NULL`. Vấn đề là chúng ta muốn viết một function duy nhất hợp lệ cho mọi data type (integer, real, text, v.v.).

Function sau đây làm cho điều đó khả thi:

```text
      forumdb=> create or replace function nvl ( anyelement,anyelement) returns
      anyelement as $$
      select coalesce($1,$2);
      $$
      language SQL;
      CREATE FUNCTION
```

Đây là cách gọi function:

```text
      forumdb=> select nvl(NULL::int,1);
       nvl
      -----
           1
      (1 row)


      forumdb=> select nvl(''::text,'n'::text);
       nvl
      -----


      (1 row)

      forumdb=> select nvl('a'::text,'n'::text);
       nvl
      -----
       a
      (1 row)
```

Để biết thêm thông tin, xem documentation chính thức tại https://www.postgresql.org/docs/current/extend-type-system.html.

## PL/pgSQL functions

Trong section này, chúng ta sẽ nói về ngôn ngữ PL/pgSQL. Ngôn ngữ PL/pgSQL là procedural language built-in mặc định của PostgreSQL. Như được mô tả trong documentation chính thức, các mục tiêu thiết kế của PL/pgSQL là tạo ra một loadable procedural language có thể:

- Được sử dụng để tạo function và trigger procedure (chúng ta sẽ nói về trigger trong chapter tiếp theo).
- Thêm control structure mới.
- Thêm data type mới vào SQL language.

Nó rất giống Oracle PL/SQL và hỗ trợ những thành phần sau:

- Variable declaration
- Expression
- Control structure như conditional structure hoặc loop structure
- Cursor

### Tổng quan đầu tiên

Như đã thấy ở phần đầu của section SQL functions, prototype để viết function trong PostgreSQL như sau:

```text
   CREATE FUNCTION function_name(p1 type, p2 type,p3 type, ....., pn type)
       RETURNS type AS
   BEGIN
       -- function logic
   END;
   LANGUAGE language_name
```

Bây giờ, giả sử chúng ta muốn tạo lại function `my_sum` bằng ngôn ngữ PL/pgSQL:

```text
   forumdb=> CREATE OR REPLACE FUNCTION my_sum(x integer, y integer) RETURNS
   integer AS
   $BODY$
   DECLARE
       ret integer;
   BEGIN
       ret := x + y;
       return ret;
      END;
      $BODY$
      language 'plpgsql';
      CREATE FUNCTION
   forumdb=> select my_sum(2,3);
    my_sum
   --------
          5
   (1 row)
```

Query trước đó cung cấp cùng result như query đã thấy ở đầu chapter. Bây giờ hãy xem xét nó chi tiết hơn:

1. Sau đây là function header; ở đây, bạn định nghĩa tên function, input parameter và return value:

   ```text
       CREATE OR REPLACE FUNCTION my_sum(x integer, y integer) RETURNS
       integer AS
   ```

2. Sau đây là một label chỉ ra phần bắt đầu của code. Chúng ta có thể đặt bất kỳ string nào giữa các ký tự `$$`; điều quan trọng là label đó xuất hiện giống hệt ở cuối function:

   ```text
       $BODY$
   ```

3. Trong section sau, chúng ta có thể định nghĩa các variable; điều quan trọng là mỗi declaration hoặc statement kết thúc bằng dấu chấm phẩy:

   ```text
       DECLARE
         ret integer;
   ```

4. Với statement `BEGIN`, chúng ta báo cho PostgreSQL rằng muốn bắt đầu viết logic của mình:

   ```text
       BEGIN
         ret := x + y;
         return ret;
   ```

   > **Caution:** Không viết dấu chấm phẩy sau `BEGIN` - điều đó không đúng và sẽ tạo ra syntax error.

5. Giữa statement `BEGIN` và statement `END`, chúng ta có thể đặt code của mình:

   ```text
            END;
   ```

6. Instruction `END` chỉ ra rằng code của chúng ta đã kết thúc:

   ```text
            $BODY$
   ```

7. Label này đóng label đầu tiên; cuối cùng, statement `language` chỉ định ngôn ngữ mà function được viết bằng:

   ```text
            language 'plpgsql';
   ```

### Dropping functions

Để drop một function, chúng ta phải thực thi command `DROP FUNCTION`, theo sau là tên function và các parameter của nó. Ví dụ, để drop function `my_sum`, chúng ta phải thực thi:

```text
   forumdb=> DROP FUNCTION my_sum(integer,integer);
   DROP FUNCTION
```

### Declaring function parameters

Sau khi học cách viết một PL/pgSQL function đơn giản, hãy đi vào chi tiết hơn một chút về từng khía cạnh đã thấy trong section trước. Hãy bắt đầu với việc declaration parameter. Trong hai ví dụ tiếp theo, chúng ta sẽ thấy hai cách khác nhau để định nghĩa function `my_sum` đã thấy trước đây.

Ví dụ đầu tiên như sau:

```text
   forumdb=> CREATE OR REPLACE FUNCTION my_sum(integer, integer) RETURNS
   integer AS
   $BODY$
   DECLARE
    x alias for $1;
    y alias for $2;
   ret integer;
   BEGIN
    ret := x + y;
    return ret;
   END;
   $BODY$
   language 'plpgsql';
   CREATE FUNCTION
```

Ví dụ thứ hai như sau:

```text
      forumdb=> CREATE OR REPLACE FUNCTION my_sum(integer, integer) RETURNS
      integer AS
      $BODY$
      DECLARE
       ret integer;
      BEGIN
       ret := $1 + $2;
       return ret;
      END;
      $BODY$
      language 'plpgsql';
      CREATE FUNCTION
```

Trong ví dụ đầu tiên, chúng ta sử dụng alias; syntax của alias nói chung là như sau:

```text
      newname ALIAS FOR oldname;
```

Trong trường hợp cụ thể này, chúng ta sử dụng positional variable `$1` làm giá trị `oldname`. Trong ví dụ thứ hai, chúng ta sử dụng positional approach chính xác như đã làm với SQL functions.

### IN/OUT parameters

Trong ví dụ trước, chúng ta sử dụng clause `RETURNS` ở dòng đầu tiên của function definition; tuy nhiên, có một cách khác để đạt được cùng mục tiêu. Trong PL/pgSQL, chúng ta có thể định nghĩa tất cả parameter là input parameter, output parameter hoặc input/output parameter. Ví dụ, giả sử chúng ta viết như sau:

```text
      forumdb=> CREATE OR REPLACE FUNCTION my_sum_3_params(IN x integer,IN y
      integer, OUT z integer) AS
      $BODY$
      BEGIN
       z := x+y;
      END;
      $BODY$
      language 'plpgsql';
      CREATE FUNCTION
```

Chúng ta đã định nghĩa một function mới có tên `my_sum_3_params`, nhận hai input parameter (`x` và `y`) và có output parameter `z`. Vì có hai input parameter, function sẽ được gọi chỉ với hai parameter, chính xác như function trước:

```text
   forumdb=> select my_sum_3_params(2,3);
    my_sum_3_params
   -----------------
                     5
   (1 row)
```

Với kiểu định nghĩa parameter này, chúng ta có thể có các function với nhiều variable làm result. Ví dụ, nếu muốn một function nhận hai giá trị integer, tính tổng và tích của chúng, chúng ta có thể viết như sau:

```text
   forumdb=> CREATE OR REPLACE FUNCTION my_sum_mul(IN x integer,IN y
   integer,OUT w integer, OUT z integer) AS
   $BODY$
   BEGIN
    z := x+y;
    w := x*y;
   END;
   $BODY$
   language 'plpgsql';
   CREATE FUNCTION
```

Điều lạ là nếu invoke function như trước, chúng ta sẽ có result sau:

```text
   forumdb=> select my_sum_mul(2,3);
    my_sum_mul
   ------------
    (6,5)
   (1 row)
```

Result này có vẻ hơi lạ vì result không phải scalar value mà là một record, tức một custom type. Để output được tách thành các column, chúng ta phải sử dụng syntax sau:

```text
      forumdb=> select * from my_sum_mul(2,3);
          w | z
      ---+---
          6 | 5
      (1 row)
```

Chúng ta có thể sử dụng result của function chính xác như result của một table và viết, ví dụ, như sau:

```text
      forumdb=> select * from my_sum_mul(2,3) where w=6;
          w | z
      ---+---
          6 | 5
      (1 row)
```

Chúng ta có thể định nghĩa các parameter như sau:

- `IN`: Input parameter (nếu bỏ qua, đây là option mặc định)
- `OUT`: Output parameter
- `INOUT`: Input/output parameter

### Function volatility categories

Trong PostgreSQL, mỗi function có thể được định nghĩa là `VOLATILE`, `STABLE` hoặc `IMMUTABLE`. Nếu không chỉ định gì, giá trị mặc định là `VOLATILE`. Sự khác biệt giữa ba definition có thể này được mô tả rõ trong documentation chính thức (https://www.postgresql.org/docs/current/xfunc-volatility.html):

> Một function `VOLATILE` có thể làm mọi thứ, bao gồm sửa đổi database. Nó có thể trả về các result khác nhau trong những lần gọi liên tiếp với cùng các argument. Optimizer không đưa ra giả định nào về behavior của các function như vậy. Một query sử dụng function volatile sẽ đánh giá lại function tại mỗi row nơi cần giá trị của nó. Nếu một function được đánh dấu là `VOLATILE`, nó có thể trả về các result khác nhau nếu chúng ta gọi nó nhiều lần bằng cùng các input parameter.
>
> Một function `STABLE` không thể sửa đổi database và được đảm bảo trả về cùng result với cùng các argument cho mọi row trong một statement duy nhất. Category này cho phép optimizer tối ưu nhiều lần gọi function thành một lần gọi duy nhất. Cụ thể, việc sử dụng một expression chứa function như vậy trong index scan condition là an toàn. Nếu một function được đánh dấu là `STABLE`, function sẽ trả về cùng result với cùng các parameter trong cùng một transaction.
>
> Một function `IMMUTABLE` không thể sửa đổi database và được đảm bảo trả về cùng result với cùng các argument mãi mãi. Category này cho phép optimizer pre-evaluate function khi query gọi nó với các argument hằng số.

Trong các trang tiếp theo của chapter này, chúng ta sẽ chỉ tập trung vào các ví dụ về volatile function; tuy nhiên, ở đây chúng ta sẽ xem nhanh một ví dụ về stable function và một ví dụ về immutable function:

1. Hãy bắt đầu với một stable function - ví dụ, function `now()` là một stable function. Function `now()` trả về date và time hiện tại tại thời điểm bắt đầu transaction, như có thể thấy ở đây:

   ```text
             forumdb=> begin ;
             BEGIN


             forumdb=*> select now();
                            now
             ------------------------------
   ```
