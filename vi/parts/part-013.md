```text
Table "pg_temp_3.temp_users_transaction"
Column   |   Type    | Collation | Nullable |                 Default
----------+---------+-----------+----------+-----------------------
-------
pk        | integer |               | not null | generated always as
identity
username | text       |             | not null |
gecos     | text       |             |            |
email     | text       |             | not null |
Indexes:
"temp_users_transaction_pkey" PRIMARY KEY, btree (pk)
"temp_users_transaction_username_key" UNIQUE CONSTRAINT, btree
(username)
```

3. Bạn có thể thấy cấu trúc của table `temp_users_transaction`, vậy bây giờ hãy commit transaction:

```text
forumdb=*> commit work;
COMMIT
```

Nếu bạn thực thi lại command DESCRIBE `\d temp_users_transaction`, PostgreSQL sẽ phản hồi như sau:

```text
forumdb=> \d temp_users_transaction
Did not find any relation named "temp_users_transaction".
```

Điều này xảy ra vì option `on commit drop` sẽ drop table ngay khi transaction hoàn tất.

## Quản lý unlogged table

Bây giờ chúng ta sẽ nói về chủ đề unlogged table. Hiện tại, chúng ta chỉ cần lưu ý rằng unlogged table nhanh hơn nhiều so với table classic (còn được gọi là logged table), nhưng không crash-safe. Điều này có nghĩa là tính nhất quán của data không được bảo đảm trong trường hợp xảy ra crash.

Đoạn mã sau cho thấy cách tạo một unlogged table:

```text
forumdb=> create unlogged table if not exists unlogged_users (
      pk int GENERATED ALWAYS AS IDENTITY
     ,username text NOT NULL
     ,gecos text
     ,email text NOT NULL
     ,PRIMARY KEY( pk )
     ,UNIQUE ( username )
);
CREATE TABLE
```

Unlogged table là một lựa chọn thay thế nhanh cho permanent table và temporary table. Đổi lại việc tăng performance này là data sẽ bị mất khi server crash. Nếu server crash sau khi reboot, table sẽ rỗng. Trong một số trường hợp, bạn có thể chấp nhận điều này.

## Tạo table

Bây giờ chúng ta sẽ tìm hiểu điều gì xảy ra bên trong khi một table mới được tạo. Ngoài ra, đối với table, PostgreSQL gán một object identifier gọi là OID. Chúng ta đã thấy `oid2name` trong Chapter 2, Getting to know your cluster. Bây giờ chúng ta sẽ xem một thứ tương tự. OID đơn giản là một số nhận diện một object bên trong PostgreSQL cluster. Hãy xem mối quan hệ giữa các table được tạo ở SQL level và những gì xảy ra phía sau trong filesystem:

1. Để làm việc này, chúng ta sẽ sử dụng OID và một system table có tên `pg_class`, nơi tập hợp thông tin về tất cả table hiện có trong database. Hãy chạy query sau:

```text
forumdb=> select oid,relname from pg_class where relname='users';
  oid   | relname
-------+---------
 16389 | users
(1 row)
```

Ở đây, field `oid` là field object identifier, còn `relname` đại diện cho relation name của object. Như đã thấy ở đây, database `forumdb` được lưu trong directory `16389`.

2. Bây giờ hãy xem table `users` được lưu ở đâu. Để làm việc này, hãy đi đến directory `16386` bằng code sau:

```text
postgres@learn_postgresql:~$ cd /var/lib/postgresql/16/main/
base/16386
```

Hoặc nếu bạn đang sử dụng Docker image, hãy thực thi:

```text
postgres@learn_postgresql:~$ cd /postgres/16/data/base/16386
```

3. Khi đã ở đây, hãy thực thi command sau:

```text
postgres@learn_postgresql:~/data/base/16386$ ls -l | grep 16389
-rw------- 1 postgres postgres               0 Jan    3 09:13 16389
```

Như bạn có thể thấy, trong directory `16386` có một file tên `16389`. Trong PostgreSQL, mỗi table được lưu trong một hoặc nhiều file. Nếu kích thước table nhỏ hơn 1 GB, table sẽ được lưu trong một file duy nhất. Nếu kích thước table lớn hơn 1 GB, table sẽ được lưu trong hai file và file thứ hai sẽ có tên `16389.1`. Nếu table `users` có kích thước lớn hơn 2 GB, table sẽ được lưu trong ba file có tên `16389`, `16389.1` và `16389.2`; điều tương tự cũng xảy ra với index `users_username_key`.

> Trong PostgreSQL, mỗi table hoặc index được lưu trong một hoặc nhiều file. Khi một table hoặc index vượt quá 1 GB, nó được chia thành các segment có kích thước một gigabyte.

Trong section này, chúng ta đã học cách quản lý table và đã thấy điều gì xảy ra bên trong. Trong section tiếp theo, chúng ta sẽ học cách thao tác data bên trong table.

## Tìm hiểu các statement thao tác table cơ bản

Bây giờ bạn đã học cách tạo table, bạn cần hiểu cách insert, xem, sửa đổi và delete data trong table. Điều này sẽ giúp bạn cập nhật những entry không chính xác hoặc cập nhật các entry hiện có khi cần. Có nhiều command có thể dùng cho việc này, và bây giờ chúng ta sẽ xem xét chúng.

## Insert và select data

Trong section này, chúng ta sẽ học cách insert data vào table. Để insert data vào table, bạn cần sử dụng command `INSERT`. Command `INSERT` sẽ insert các row mới vào table.

Có thể insert một hoặc nhiều row được chỉ định bằng value expression, hoặc không row nào hay nhiều row được tạo ra từ một query. Bây giờ chúng ta sẽ lần lượt xem một số use case như sau:

1. Để insert một user mới vào table `users`, hãy thực thi command sau:

```text
forumdb=> insert into users (username,gecos,email) values
('myusername','mygecos','myemail');
INSERT 0 1
```

Kết quả này cho thấy PostgreSQL đã insert một record vào table `users`. Số đầu tiên là OID của row đã được insert; trong các phiên bản PostgreSQL mới hơn, theo mặc định table được tạo mà không có OID trên các row, vì vậy bạn chỉ nhận được giá trị 0 trả về.

2. Bây giờ, nếu muốn xem record vừa nhập vào table `users`, chúng ta phải thực thi command select:

```text
forumdb=> select * from users;
 pk | username       | gecos     | email
----+------------+---------+---------
  1 | myusername | mygecos | myemail
(1 row)
```

Command select được thực thi để lấy các row từ một table. Với SQL statement này, PostgreSQL trả về toàn bộ data có trong tất cả field của table. Giá trị `*` chỉ định tất cả field hiện có. Điều này cũng có thể được viết như sau:

```text
forumdb=> select pk,username,gecos,email from users;
 pk | username       | gecos     | email
----+------------+---------+---------
 1   | myusername | mygecos | myemail
(1 row)
```

3. Bây giờ hãy insert một user khác vào table `users`; chẳng hạn, insert user `'scotty'` với tất cả field của user đó:

```text
forumdb=> insert into users (username,gecos,email) values
('scotty','scotty_gecos','scotty_email');
INSERT 0 1
```

4. Nếu muốn thực hiện cùng search như trước, sắp xếp data theo field `username`, chúng ta phải thực thi như sau:

```text
forumdb=> select pk,username,gecos,email from users order by
username;
 pk | username       | gecos            | email
----+------------+--------------+--------------
 1 | myusername | mygecos             | myemail
 2 | scotty        | scotty_gecos | scotty_email
(2 rows)
```

> Ngôn ngữ SQL, nếu không có option `ORDER BY`, không trả về data theo thứ tự.

Trong PostgreSQL, điều này cũng có thể được viết như sau:

```text
forumdb=> select pk,username,gecos,email from users order by 2;
 pk | username      | gecos             | email
----+------------+--------------+--------------
  1 | myusername | mygecos              | myemail
  2 | scotty        | scotty_gecos | scotty_email
(2 rows)
```

> PostgreSQL cũng chấp nhận vị trí field trong query làm option sắp xếp.

5. Bây giờ hãy xem cách insert nhiều record bằng một single-row statement. Ví dụ, statement sau sẽ insert ba record vào table `categories`:

```text
forumdb=> insert into categories (title,description) values ('C
Language', 'Languages'), ('Python Language','Languages');
INSERT 0 2
```

Đây là một biến thể nhỏ của command `INSERT`. Table `categories` của chúng ta bây giờ sẽ chứa các giá trị sau:

```text
forumdb=> select * from categories;
 pk |            title            |               description
----+-----------------------+---------------------------------
  1 | Database                    | Database related discussions
  2 | Unix                        | Unix and Linux discussions
  3 | Programming Languages | All about programming languages
  4 | C Language                  | Languages
  5 | Python Language             | Languages
(5 rows)
```

6. Bây giờ, nếu muốn chỉ select những tuple có description bằng `Database related discussions`, hãy sử dụng where condition:

```text
forumdb=> select * from categories where description ='Database
related discussions';
 pk |   title     |          description
----+----------+------------------------------
  1 | Database | Database related discussions
(1 row)
```

7. Where condition filter trên một hoặc nhiều field của table. Ví dụ, nếu muốn search tất cả topic có title là orange và description là fruits, chúng ta sẽ phải viết như sau:

```text
forumdb=> select * from categories where description = 'Languages'
and title='C Language';
 pk |     title       | description
----+------------+-------------
  4 | C Language | Languages
(1 row)
```

8. Bây giờ, ví dụ nếu muốn select tất cả tuple vừa có field description bằng `Languages` vừa được sort theo title theo thứ tự ngược, hãy thực thi như sau:

```text
forumdb=> select * from categories where description ='Languages'
order by title desc;
 pk |        title         | description
----+-----------------+-------------
  5 | Python Language | Languages
  4 | C Language           | Languages
(2 rows)
```

Hoặc chúng ta cũng có thể viết như sau:

```text
forumdb=> select * from categories where description ='Languages'
order by 2 desc;
 pk |        title         | description
----+-----------------+-------------
  5 | Python Language | Languages
  4 | C Language           | Languages
(2 rows)
```

Option `ASC` và `DESC` sort query theo thứ tự tăng dần hoặc giảm dần; nếu không chỉ định gì, `ASC` là mặc định.

## Giá trị NULL

Trong section này, chúng ta sẽ nói về các giá trị `NULL`. Trong ngôn ngữ SQL, giá trị `NULL` được định nghĩa như sau:

> Null (hoặc NULL) là một marker đặc biệt được sử dụng trong Structured Query Language để chỉ ra rằng một data value không tồn tại trong database. Được giới thiệu bởi người tạo ra relational database model, E. F. Codd, SQL NULL đáp ứng yêu cầu rằng mọi Relational Database Management System (RDBMS) thực sự đều hỗ trợ biểu diễn thông tin bị thiếu.

Bây giờ hãy xem `NULL` được sử dụng trong PostgreSQL như thế nào:

1. Hãy bắt đầu bằng cách insert một tuple như sau:

```text
forumdb=> insert into categories (title) values ('A new
discussion');
INSERT 0 1
```

2. Bây giờ hãy xem những tuple nào đang có trong table `categories`:

```text
forumdb=> select * from categories;
 pk |             title             |               description
----+-----------------------+---------------------------------
  1 | Database                      | Database related discussions
  2 | Unix                          | Unix and Linux discussions
  3 | Programming Languages | All about programming languages
  4 | C Language                    | Languages
  5 | Python Language               | Languages
  6 | A new discussion              |
(6 rows)
```

3. Vậy bây giờ, nếu muốn select tất cả tuple mà description không hiện diện, hãy sử dụng như sau:

```text
forumdb=> select * from categories where description ='';
 pk | title | description
----+-------+-------------
(0 rows)
```

Như bạn có thể thấy, PostgreSQL không trả về tuple nào. Đó là vì lần insert cuối đã đưa một giá trị `NULL` vào field description.

4. Để xem các giá trị `NULL` hiện có trong table, hãy thực thi command sau:

```text
forumdb=> \pset null NULL
Null display is "NULL".
```

5. Điều này bảo `psql` hiển thị các giá trị `NULL` đang có trong table dưới dạng `NULL`, như sau:

```text
forumdb=> select * from categories;
 pk |           title             |              description
----+-----------------------+----------------------------
  1 | Database                    | Database related discussions
  2 | Unix                        | Unix and Linux discussions
  3 | Programming Languages | All about programming languages
  4 | C Language                  | Languages
  5 | Python Language             | Languages
  6 | A new discussion            | NULL
(6 rows)
```

Như bạn có thể thấy, giá trị description gắn với title `A new discussion` không phải là empty string; đó là giá trị `NULL`.

6. Bây giờ, nếu muốn xem tất cả record có giá trị `NULL` trong field description, chúng ta phải sử dụng operator `IS NULL`:

```text
forumdb=> select title,description from categories where description
is null;
       title        | description
------------------+-------------
 A new discussion | NULL
(1 row)
```

Query trước đó tìm tất cả tuple không có giá trị trong field description.

7. Bây giờ chúng ta sẽ search tất cả tuple có giá trị trong field description bằng query sau:

```text
forumdb=> select title,description from categories where description
is not null;
           title             |               description
-----------------------+---------------------------------
 Database                    | Database related discussions
 Unix                          | Unix and Linux discussions
 Programming Languages | All about programming languages
 C Language                  | Languages
 Python Language             | Languages
(5 rows)
```

Để thực hiện search trên các field `NULL`, chúng ta phải sử dụng các operator `IS NULL` / `IS NOT NULL`. Empty string khác với giá trị `NULL`.

## Sort với giá trị NULL

Bây giờ hãy xem điều gì xảy ra khi order một table có các giá trị `NULL`:

1. Hãy lặp lại query sort mà chúng ta đã thực hiện trước đó:

```text
forumdb=> select * from categories order by description ;
 pk |             title             |              description
----+-----------------------+----------------------------
  3 | Programming Languages | All about programming languages
  1 | Database                      | Database related discussions
  4 | C Language                   | Languages
  5 | Python Language               | Languages
  2 | Unix                          | Unix and Linux discussions
  6 | A new discussion              | NULL
(6 rows)
```

Như bạn có thể thấy, tất cả giá trị description được sort và giá trị `NULL` được đặt ở cuối result set. Có thể đạt được điều tương tự bằng cách chạy như sau:

```text
forumdb=> select * from categories order by description NULLS last;
 pk |           title              |              description
----+----------------------------+----------------------------
  3 | Programming Languages | All about programming languages
  1 | Database                     | Database related discussions
  4 | C Language                   | Languages
  5 | Python Language              | Languages
  2 | Unix                         | Unix and Linux discussions
  6 | A new discussion             | NULL
(6 rows)
```

2. Nếu muốn đặt giá trị `NULL` ở đầu, chúng ta phải thực hiện như sau:

```text
forumdb=> select * from categories order by description NULLS first;
 pk |           title         |              description
----+-----------------+---------------------------------
  6 | A new discussion             | NULL
  3 | Programming Languages | All about programming languages
  1 | Database                     | Database related discussions
  4 | C Language                   | Languages
  5 | Python Language              | Languages
  2 | Unix                         | Unix and Linux discussions
(6 rows)
```

Nếu không chỉ định, các hành vi sau là mặc định cho các query kiểu `ORDER BY`:

`ORDER BY NULLS LAST` là mặc định cho `ASC` (cũng là mặc định), còn `NULLS FIRST` là mặc định cho `DESC`.

## Tạo table bắt đầu từ một table khác

Bây giờ chúng ta sẽ xem xét cách tạo một table mới bằng data từ một table khác. Để làm việc này, bạn cần tạo một temporary table với data hiện có trong table `categories` như sau:

```text
forumdb=> create temp table temp_categories as select * from categories;
SELECT 6
```
