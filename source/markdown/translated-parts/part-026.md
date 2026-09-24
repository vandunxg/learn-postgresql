```text
2023-03-17 13:25:25.37224+00
(1 row)


forumdb=*> select now();
               now
------------------------------
 2023-03-17 13:25:25.37224+00
(1 row)



forumdb=*> commit;
COMMIT



forumdb=> begin ;
BEGIN


forumdb=*> select now();
                 now
-------------------------------
 2023-03-17 13:27:02.012632+00
(1 row)


forumdb=*> commit ;
COMMIT
```

> **Note:** Trong PostgreSQL 16, khi `psql` hiển thị prompt như `*>`, điều đó có nghĩa là chúng ta đang ở bên trong một transaction block.

2. Bây giờ, hãy xem một function immutable, chẳng hạn function `lower(string_expression)`. Function `lower` nhận một string và chuyển nó sang dạng chữ thường. Như chúng ta có thể thấy, nếu các input parameter giống nhau, function `lower` luôn trả về cùng một result, ngay cả khi được thực thi trong các transaction khác nhau:

```text
forumdb=> begin;
BEGIN


forumdb=*> select now();
                 now
-------------------------------
 2023-03-17 13:33:39.586388+00
(1 row)


forumdb=*> select lower('MICKY MOUSE');
    lower
-------------
 micky mouse
(1 row)


forumdb=*> commit;
COMMIT


forumdb=> begin;
BEGIN


forumdb=*> select now();
                now
-------------------------------
 2023-03-17 13:34:56.491773+00
(1 row)



forumdb=*> select lower('MICKY MOUSE');
    lower
-------------
 micky mouse
(1 row)


forumdb=*> commit;
COMMIT
```

## Cấu trúc điều khiển

PL/pgSQL có khả năng quản lý các control structure như sau:

- Conditional statements
- Loop statements
- Exception handler statements

## Conditional statements

Ngôn ngữ PL/pgSQL có thể quản lý các conditional statement dạng IF và các conditional statement dạng CASE.

### IF statements

Trong PL/pgSQL, syntax của một IF statement như sau:

```text
   IF boolean-expression THEN
       statements
   [ ELSIF boolean-expression THEN
       statements
   [ ELSIF boolean-expression THEN
       statements
       ...
   ]
   ]
   [ ELSE
       statements ]
   END IF;
```

Ví dụ, giả sử chúng ta muốn viết một function khi được cung cấp hai input value `x` và `y` sẽ trả về các kết quả sau:

- parameter thứ nhất lớn hơn parameter thứ hai nếu `x > y`
- parameter thứ hai lớn hơn parameter thứ nhất nếu `x < y`
- 2 parameter bằng nhau nếu `x = y`

Chúng ta phải viết function như sau:

```text
   forumdb=> CREATE OR REPLACE FUNCTION my_check(x integer default 0, y
   integer default 0) RETURNS text AS
   $BODY$
   BEGIN
       IF x > y THEN
       return 'first parameter is greater than second parameter';
   ELSIF x < y THEN
       return 'second parameter is greater than first parameter';
       ELSE
       return 'the 2 parameters are equals';
       END IF;
   END;
   $BODY$
   language 'plpgsql';
   CREATE FUNCTION
```

Ở ví dụ này, chúng ta đã thấy construct IF ở dạng đầy đủ: `IF [...] THEN[...] ELSIF [...] ELSE[...] ENDIF;`

Tuy nhiên, cũng có các dạng ngắn hơn như sau:

- `IF [...] THEN[...] ELSE[...] ENDIF;`
- `IF [...] THEN[...] ENDIF;`

Một số ví dụ về result do function đã định nghĩa trước đó cung cấp như sau:

```text
   forumdb=> select my_check(1,2);
                            my_check
   -------------------------------------------------
       second parameter is higher than first parameter
   (1 row)



   forumdb=> select my_check(2,1);
                            my_check
   -------------------------------------------------
       first parameter is higher than second parameter
   (1 row)



   forumdb=>      select my_check(1,1);
                 my_check
   -----------------------------
       the 2 parameters are equals
   (1 row)
```

### CASE statements

Trong PL/pgSQL, cũng có thể sử dụng CASE statement. CASE statement có thể có hai syntax sau.

Sau đây là một simple CASE statement:

```text
   CASE search-expression
       WHEN expression [, expression [ ... ]] THEN
       statements
       [ WHEN expression [, expression [ ... ]] THEN
       statements
       ... ]
       [ ELSE
       statements ]
   END CASE;
```

Sau đây là một searched CASE statement:

```text
   CASE
       WHEN boolean-expression THEN
       statements
       [ WHEN boolean-expression THEN
       statements
       ... ]
       [ ELSE
       statements ]
   END CASE;
```

Bây giờ, chúng ta sẽ thực hiện các thao tác sau:

- Chúng ta sẽ dùng syntax simple CASE đầu tiên khi phải lựa chọn từ một danh sách value.
- Chúng ta sẽ dùng syntax thứ hai khi phải lựa chọn từ một range value.

Hãy bắt đầu với syntax đầu tiên:

```text
   forumdb=> CREATE OR REPLACE FUNCTION my_check_value(x integer default 0)
   RETURNS text AS
   $BODY$
   BEGIN
       CASE x
       WHEN 1 THEN return 'value = 1';
       WHEN 2 THEN return 'value = 2';
       ELSE return 'value >= 3 ';
       END CASE;
   END;
   $BODY$
   language 'plpgsql';
   CREATE FUNCTION
```

Function `my_check_value` ở trên trả về:

- `value = 1` nếu `x = 1`
- `value = 2` nếu `x = 2`
- `value >= 3` nếu `x >= 3`

Chúng ta có thể thấy điều này ở đây:

```text
   forumdb=> select my_check_value(1);
       my_check_value
   ----------------
       value = 1
   (1 row)


   forumdb=> select my_check_value(2);
       my_check_value
   ----------------
       value = 2
   (1 row)


   forumdb=> select my_check_value(3);
       my_check_value
   ----------------
       value >= 3
   (1 row)
```

Bây giờ, hãy xem một ví dụ về searched CASE syntax:

```text
   forumdb=> CREATE OR REPLACE FUNCTION my_check_case(x integer default 0, y
   integer default 0) RETURNS text AS
   $BODY$
   BEGIN
     CASE
    WHEN x > y THEN return 'first parameter is higher than second
parameter';
    WHEN x < y THEN return 'second parameter is higher than first
parameter';
   ELSE return 'the 2 parameters are equals';
   END CASE;
   END;
   $BODY$
   language 'plpgsql';
   CREATE FUNCTION
```

Function `my_check_case` trả về cùng data với function `my_check` mà chúng ta đã viết trước đó:

```text
   forumdb=> select my_check_case(2,1);
                         my_check_case
   -------------------------------------------------
      first parameter is higher than second parameter
   (1 row)


   forumdb=> select my_check_case(1,2);
                         my_check_case
   -------------------------------------------------
      second parameter is higher than first parameter
   (1 row)


   forumdb=> select my_check_case(1,1);
               my_check_case
   -----------------------------
      the 2 parameters are equals
   (1 row)


   forumdb=> select my_check_case();
               my_check_case
   -----------------------------
   the 2 parameters are equals
   (1 row)
```

## Loop statements

PL/pgSQL có thể xử lý loop theo nhiều cách. Tiếp theo, chúng ta sẽ xem một số ví dụ về cách tạo loop. Để biết thêm chi tiết, chúng tôi khuyến nghị tham khảo official documentation tại https://www.postgresql.org/docs/current/plpgsql.html. Điều làm PL/pgSQL đặc biệt hữu ích là nó cho phép chúng ta xử lý data từ các query thông qua procedural language. Bây giờ chúng ta sẽ xem điều này có thể thực hiện như thế nào.

Giả sử chúng ta muốn xây dựng một PL/pgSQL function khi được cung cấp một integer làm parameter sẽ trả về một result set thuộc một composite data type. Composite data type mà chúng ta muốn trả về như sau:

|  |  |  |
| --- | --- | --- |
| ID | pk field | Integer data type |
| TITLE | Title field | text data type |
| RECORD_DATA | Title field + content field | hstore data type |

Cách đúng để xây dựng một composite data type như sau:

```text
   forumdb=> create type my_ret_type as (
    id integer,
    title text,
    record_data hstore
   );
   CREATE TYPE
```

Statement ở trên tạo một data type mới, một composite data type, được cấu thành từ một integer data type + một text data type + một hstore data type. Bây giờ, nếu muốn viết một function trả về một result set thuộc data type `my_ret_type`, lần thử đầu tiên của chúng ta có thể như sau:

```text
   forumdb=> CREATE OR REPLACE FUNCTION my_first_fun (p_id integer) returns
   setof my_ret_type as
   $$
   DECLARE
    rw posts%ROWTYPE; -- declare a rowtype;
    ret my_ret_type;
   BEGIN
         for rw in select * from posts where pk=p_id loop
           ret.id := rw.pk;
           ret.title := rw.title;
           ret.record_data := hstore(ARRAY['title',rw.title,'Title and Content'
                                   ,format('%s %s',rw.title,rw.content)]);
          return next ret;
          end loop;
      return;
   END;
   $$
   language 'plpgsql';
   CREATE FUNCTION
```

Như chúng ta có thể thấy, nhiều điều được tập trung trong một vài dòng code PL/pgSQL này:

1. `rw posts%ROWTYPE`: Với statement này, biến `rw` được định nghĩa là một container chứa một row duy nhất của table `posts`.
2. `for rw in select * from posts where pk=p_id loop`: Với statement này, chúng ta cycle trong result của selection, mỗi lần gán value do select command trả về cho biến `rw`. Ba bước tiếp theo gán các value cho biến `ret`.
3. `return next ret;`: Statement này trả về value của biến `ret` và chuyển đến record tiếp theo của for cycle.
4. `end loop;`: Statement này cho PostgreSQL biết rằng for cycle kết thúc tại đây.
5. `return;`: Đây là return instruction của function.

> Điều quan trọng cần nhớ là ngôn ngữ PL/pgSQL nằm bên trong PostgreSQL transaction system. Điều này có nghĩa là các function được thực thi atomically và function trả về các result không phải tại thời điểm thực thi command `RETURN NEXT`, mà tại thời điểm thực thi command `RETURN` được đặt ở cuối function. Điều này có thể có nghĩa là với các dataset rất lớn, PL/pgSQL function có thể mất nhiều thời gian trước khi trả về result.

## Record type

Trong một ví dụ trước đó, chúng ta đã giới thiệu data type `%ROWTYPE`. Trong ngôn ngữ PL/pgSQL, có thể khái quát hóa concept này. Có một data type tên là `record` khái quát hóa concept của `%ROWTYPE`.

Ví dụ, chúng ta có thể viết lại `my_first_fun` như sau:

```text
   forumdb=> CREATE OR REPLACE FUNCTION my_second_fun (p_id integer) returns
   setof my_ret_type as
   $$
   DECLARE
        rw record; -- declare a record variable
        ret my_ret_type;
   BEGIN
        for rw in select * from posts where pk=p_id loop
        ret.id := rw.pk;
        ret.title := rw.title;
        ret.record_data := hstore(ARRAY['title',rw.title
                           ,'Title and Content',format('%s %s',rw.title,rw.
   content)]);
        return next ret;
    end loop;
    return;
   END;
   $$
   language 'plpgsql';
   CREATE FUNCTION
```

Điểm khác biệt duy nhất giữa `my_first_fun` và `my_second_fun` nằm trong definition này:

```text
   rw record; -- declare a record variable
```

Lần này, biến `rw` được định nghĩa là một record data type. Điều này có nghĩa là biến `rw` là một object có thể được gắn với bất kỳ record nào của bất kỳ table nào. Result của hai function `my_first_fun` và `my_second_fun` là giống nhau:

```text
forumdb=> \x
Expanded display is on.
forumdb=> select * from my_first_fun(5);
-[ RECORD 1 ]-----------------------
id            | 5
title         | Indexing PostgreSQL
record_data | "title"=>"Indexing PostgreSQL", "Title and
Content"=>"Indexing PostgreSQL Btree in PostgreSQL is...."
```
