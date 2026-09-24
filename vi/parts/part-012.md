4. Vì vậy, chúng ta đã thêm thành công một table mới vào database `template1`. Bây giờ hãy thử tạo một database mới có tên `dummydb` và liệt kê tất cả table trong database `dummydb`:

```text
template1=# create database dummydb;
CREATE DATABASE
template1=# \c dummydb
You are now connected to database "dummydb" as user "postgres".
```

Database `dummydb` chứa các table sau:

```text
dummydb=# \dt
             List of relations
 Schema |       Name      | Type    |   Owner
--------+------------+-------+----------
 public | dummytable | table | postgres
(1 row)
```

Đúng như dự kiến, trong database `dummydb`, chúng ta có thể thấy table được tạo trước đó trong database `template1`.

> Điều quan trọng cần nhớ là mọi thay đổi được thực hiện trên database `template1` sẽ có mặt trong tất cả database được tạo sau thay đổi đó.

Bây giờ chúng ta sẽ xóa database `dummydb` và dummy table trong database `template1`.

## Xóa table và database
Trong phần tiếp theo, bạn sẽ học cách xóa table và database. Các command chúng ta sẽ học là:

- `DROP TABLE`: Dùng để xóa một table trong database.
- `DROP DATABASE`: Dùng để xóa một database trong cluster.

## Xóa table
Trong PostgreSQL, command cần dùng để xóa một table đơn giản là `DROP TABLE tablename`. Để làm việc này, chúng ta phải connect đến database chứa table đó, sau đó chạy command `DROP TABLE tablename`.

Ví dụ, nếu muốn xóa table `dummytable` khỏi database `template1`, chúng ta phải thực hiện các bước sau.

Chúng ta connect đến database `template1` bằng command sau:

```text
dummydb=# \c template1
You are now connected to database "template1" as user "postgres".
```

Và chúng ta có thể xóa table bằng command sau:

```text
template1=# drop table dummytable;
DROP TABLE
```

## Xóa database
Trong PostgreSQL, command cần dùng để xóa một table đơn giản là `DROP DATABASE databasename`; ví dụ, nếu muốn xóa database `dummydb`, chúng ta phải thực thi command sau:

```text
template1=# drop database dummydb ;
DROP DATABASE
```

Sau đó, mọi thứ đã trở về trạng thái ban đầu của chapter.

## Tạo bản sao database
Các bước sau đây cho bạn biết cách tạo một database mới từ một template database:

1. Tạo một bản sao của database `forumdb` trên cùng PostgreSQL cluster bằng cách thực hiện command sau:

   ```text
   template1=# create database forumdb2 template forumdb;
   CREATE DATABASE
   ```

   Khi sử dụng command này, bạn chỉ đang yêu cầu PostgreSQL tạo một database mới có tên `forumdb2`, sử dụng database `forumdb` làm template.

2. Connect đến database `forumdb2` với tư cách forum user:

   ```text
   postgres@learn_postgresql:/$ psql -U forum forumdb2
   forumdb2=>
   ```

3. Liệt kê tất cả table trong database `forumdb2`:

   ```text
   forumdb2=> \dt
                List of relations
    Schema |       Name       | Type    | Owner
   --------+--------------+-------+-------
    forum    | categories     | table | forum
    forum    | j_posts_tags | table | forum
    forum    | posts          | table | forum
    forum    | tags           | table | forum
    forum    | users          | table | forum
   (5 rows)
   ```

Bạn có thể thấy các table có trong database `forumdb` hiện cũng có trong database này.

## Xác nhận kích thước database
Bây giờ chúng ta sẽ giải quyết câu hỏi làm thế nào để xác định kích thước thực của một database. Có hai phương thức bạn có thể sử dụng để làm việc này: `psql` và SQL. Hãy so sánh hai phương thức trong các phần sau.

## Phương thức psql
Chúng ta có thể kiểm tra kích thước database bằng phương thức `psql`, theo các bước sau:

1. Đầu tiên, hãy connect đến `forumdb` và chuyển về expanded mode:

   ```text
   postgres@learn_postgresql:/$ psql -U forum forumdb
   forumdb=> \x
   Expanded display is on.
   ```

2. Sau đó, thực thi command sau:

   ```text
   forumdb=# \l+ forumdb
   List of databases
   -[ RECORD 1 ]-----+-----------
   Name                 | forumdb
   Owner                | forum
   Encoding             | UTF8
   Collate              | en_US.utf8
   Ctype                | en_US.utf8
   ICU Locale           |
   Locale Provider      | libc
   Access privileges    |
   Size                 | 7685 kB
   Tablespace           | pg_default
   Description          |
   ```

Trong field `Size`, giờ đây bạn có thể thấy kích thước thực của database tại thời điểm đó.

## Phương thức SQL
Khi sử dụng phương thức được mô tả ở trên, bạn có thể thấy mình không thể connect đến database thông qua command `psql`. Điều này xảy ra khi chúng ta chỉ có web access đến database; ví dụ, nếu chúng ta chỉ có quyền truy cập vào server-side installation của pgadmin4. Nếu điều này xảy ra, phương thức SQL là một cách tiếp cận thay thế cho phép bạn tìm cùng thông tin. Để sử dụng phương thức này, hãy hoàn thành các bước sau:

1. Thực thi command sau:

   ```text
   forumdb=> select pg_database_size('forumdb');
   -[ RECORD 1 ]----+--------
   pg_database_size | 7869231
   ```

   Function `pg_database_size(name)` trả về disk space được database có tên `forumdb` sử dụng. Điều này có nghĩa result là số byte được database sử dụng.

2. Nếu muốn result dễ đọc hơn theo dạng “human”, bạn có thể sử dụng function `pg_size_pretty` và viết như sau:

   ```text
   forumdb=> select pg_size_pretty(pg_database_size('forumdb'));
   -[ RECORD 1 ]--+--------
   pg_size_pretty | 7685 kB
   ```

Như bạn có thể thấy, cả hai phương thức đều cho cùng một result.

## Những gì xảy ra phía sau khi tạo database
Chúng ta vừa học các command dùng để tạo một database mới, nhưng điều gì xảy ra phía sau khi một database được tạo?

Trong phần này, chúng ta sẽ xem xét các mối quan hệ tồn tại giữa những gì chúng ta thực hiện ở SQL level và những gì xảy ra về mặt vật lý trong filesystem; lưu ý rằng các số OID chúng ta thấy dưới đây liên quan đến Docker image đã tạo. Các giá trị số trong Docker image của bạn có thể khác.

Để hiểu điều này, chúng ta cần giới thiệu system table `pg_database`:

1. Quay lại expanded mode và thực thi như sau:

   ```text
   forumdb=> select * from pg_database where datname='forumdb';
   -[ RECORD 1 ]--+-----------
   oid               | 16386
   datname           | forumdb
   datdba            | 16385
   encoding          | 6
   datlocprovider | c
   datistemplate     | f
   datallowconn      | t
   datconnlimit      | -1
   datfrozenxid      | 717
   datminmxid        | 1
   dattablespace     | 1663
   datcollate        | en_US.utf8
   datctype          | en_US.utf8
   daticulocale      |
   datcollversion | 2.31
   datacl            |
   ```

   Query này cung cấp cho chúng ta mọi thông tin về database `forumdb`. Field đầu tiên là một Object Identifier (OID), một số nhận diện duy nhất database có tên `forumdb`.

2. Thoát môi trường `psql` và đi đến directory `$PGDATA` (như đã trình bày trong các chapter trước). Trong môi trường Linux Debian, chúng ta phải thực thi:

   ```text
   cd /var/lib/postgresql/16/main/
   ```

   Với Docker image, path như sau:

   ```text
   cd /postgres/16/data
   ```

   Nếu không biết giá trị của `$PGDATA` là gì, chúng ta có thể thực thi command sau với tư cách superuser:

   ```text
   forumdb=# show data_directory;
     data_directory
   -------------------
   /postgres/16/data
   (1 row)
   ```

3. Sử dụng command `ls` để xem bên trong directory `main` hoặc `data` (Docker image):

   ```text
   postgres@learn_postgresql:~/data$ ls -l
   total 128
   drwx------ 8 postgres postgres           4096 Jan   3 09:49 base
   drwx------ 2 postgres postgres           4096 Jan   3 09:49 global
   [...]
   ```

   Như bạn có thể thấy, directory đầu tiên có tên `base`. Nó chứa tất cả database nằm trong cluster.

4. Đi vào directory `base` để xem nội dung:

   ```text
   postgres@learn_postgresql:~/data$ cd base
   postgres@learn_postgresql:~/data/base$
   ```

5. Liệt kê tất cả file hiện có trong directory:

   ```text
   postgres@learn_postgresql:~/data/base$ ls -l
   total 40
   drwx------ 2 postgres postgres           4096 Jan   3 09:45 1
   drwx------ 2 postgres postgres 12288 Jan            3 09:14 16386
   [....]
   ```

Như bạn có thể thấy, có một directory tên `16386`; tên của nó chính xác giống OID trong `pg_database` catalog.

> Khi PostgreSQL tạo một database mới, nó copy directory tương ứng với database `template1`, sau đó đặt cho nó một tên mới. Trong PostgreSQL, database là các directory.

Trong phần này, chúng ta đã học cách quản lý database. Trong phần tiếp theo, chúng ta sẽ học cách quản lý table.

## Quản lý table
Trong phần này, chúng ta sẽ học cách quản lý table trong một database.

PostgreSQL có ba loại table:

- **Temporary tables**: Các table rất nhanh, chỉ hiển thị với user đã tạo chúng.
- **Unlogged tables**: Các table rất nhanh, được dùng làm support table chung cho tất cả user.
- **Logged tables**: Các table thông thường.

Bây giờ chúng ta sẽ thực hiện các bước sau để tạo một user table từ đầu:

1. Hãy connect đến `forumdb` với tư cách forum user:

   ```text
   postgres@learn_postgresql:~$ psql -U forum forumdb
   forumdb=>
   ```

2. Thực thi command sau:

   ```text
   forumdb=> CREATE TABLE myusers (
    pk int GENERATED ALWAYS AS IDENTITY
    , username text NOT NULL
    , gecos text
    , email text NOT NULL
    , PRIMARY KEY( pk )
    , UNIQUE ( username )
   );
   CREATE TABLE
   ```

   Command `CREATE TABLE` tạo một table mới. Command `GENERATED AS IDENTITY` tự động gán một giá trị duy nhất cho một column.

3. Quan sát những gì đã được tạo trong database bằng command `\d`:

   ```text
   forumdb=> \d myusers
                                  Table "forum.myusers"
     Column    |   Type    | Collation | Nullable |                 Default
    ----------+---------+-----------+----------+-----------------------
    -------
    pk         | integer |               | not null | generated always as
    identity
    username | text        |             | not null |
       gecos     | text     |              |             |
       email     | text     |              | not null |
   Indexes:
         "myusers_pkey" PRIMARY KEY, btree (pk)
         "myusers_username_key" UNIQUE CONSTRAINT, btree (username)
   ```

   Một điểm cần lưu ý là PostgreSQL đã tạo một unique index. Sau này trong sách, chúng ta sẽ phân tích index chi tiết hơn và tìm hiểu index là gì, có những loại index nào, và cách sử dụng chúng. Hiện tại, chúng ta chỉ cần nói rằng unique index là một index không cho phép chèn các giá trị trùng lặp cho field nơi index được tạo.

> Trong PostgreSQL, primary key được triển khai bằng unique index.

4. Sử dụng command sau để xóa một table:

   ```text
   forumdb=>      drop table myusers ;
   DROP TABLE
   ```

   Command trước đó đơn giản là xóa table `users`. Như chúng ta đã thấy, command `CREATE TABLE` có một số option hữu ích:

   - `IF NOT EXISTS`
   - `TEMP`
   - `UNLOGGED`

Chúng ta sẽ trình bày từng option trong các subsection sau.

## Option EXISTS
Option `EXISTS` có thể được dùng cùng các command tạo hoặc xóa entity để kiểm tra object đã tồn tại hay chưa. Một ví dụ sử dụng option này có thể kết hợp với command `CREATE TABLE` hoặc `CREATE DATABASE`. Chúng ta cũng có thể sử dụng option này khi tạo hoặc xóa sequence, index, role và schema.

Trường hợp sử dụng rất đơn giản – command tạo hoặc xóa được thực thi nếu clause `EXISTS` là true; ví dụ, nếu muốn tạo một table có tên `users`, nếu table tồn tại, chúng ta phải thực thi SQL statement sau:

```text
forumdb=> create table if not exists users (
     pk int GENERATED ALWAYS AS IDENTITY
    ,username text NOT NULL
    ,gecos text
    ,email text NOT NULL
    ,PRIMARY KEY( pk )
    ,UNIQUE ( username )
);
NOTICE:    relation "users" already exists, skipping
CREATE TABLE
```

Command được mô tả ở trên sẽ chỉ tạo table `users` nếu table đó chưa tồn tại; nếu không, command sẽ bị bỏ qua. Command `DROP` hoạt động tương tự; command `DROP TABLE` được dùng để xóa table. Option `if exists` cũng tồn tại cho command `DROP TABLE`; ví dụ, nếu muốn xóa table `myusers` nếu nó tồn tại, chúng ta phải thực thi như sau:

```text
forumdb=> drop table if exists myusers;
NOTICE:    table "myusers" does not exist, skipping
DROP TABLE
```

Bạn có thể thấy command bị bỏ qua vì table không tồn tại. Option này có thể hữu ích vì nếu table không tồn tại, PostgreSQL không chặn bất kỳ instruction nào tiếp theo.

## Quản lý temporary table
Sau này trong sách, chúng ta sẽ tìm hiểu session, transaction và concurrency sâu hơn. Hiện tại, bạn chỉ cần biết rằng một session là một tập hợp các transaction, mỗi session được cô lập, và một transaction được cô lập khỏi mọi thứ khác. Nói cách khác, bất kỳ điều gì xảy ra bên trong transaction đều không thể được nhìn thấy từ bên ngoài transaction cho đến khi transaction kết thúc. Vì vậy, chúng ta có thể cần tạo một data structure chỉ hiển thị bên trong transaction đang chạy. Để làm điều này, chúng ta phải sử dụng option `temp`.

Bây giờ chúng ta sẽ tìm hiểu hai khả năng. Khả năng thứ nhất là chúng ta có thể có một table chỉ hiển thị trong session nơi nó được tạo. Khả năng thứ hai là chúng ta có thể có một table chỉ hiển thị trong cùng transaction nơi nó được tạo.

Sau đây là ví dụ về khả năng thứ nhất, trong đó một table hiển thị bên trong session:

```text
forumdb=> create temp table if not exists temp_users                (
     pk int GENERATED ALWAYS AS IDENTITY
    ,username text NOT NULL
    ,gecos text
    ,email text NOT NULL
    ,PRIMARY KEY( pk )
    ,UNIQUE ( username )
);
CREATE TABLE
```

Command trước đó sẽ tạo table `temp_users`, table này chỉ hiển thị bên trong session nơi table được tạo.

Nếu thay vào đó muốn có một table chỉ hiển thị bên trong transaction, chúng ta phải thêm option `on commit drop`. Để làm điều này, chúng ta phải thực hiện như sau:

1. Bắt đầu một transaction mới.
2. Tạo table `temp_users`.
3. Commit hoặc rollback transaction đã bắt đầu ở Step 1.

Hãy bắt đầu với Step 1:

1. Bắt đầu transaction bằng code sau:

   ```text
   forumdb=>      begin work;
   BEGIN
   forumdb=*>
   ```

   Ký hiệu `*` có nghĩa là chúng ta đang ở bên trong một transaction block.

2. Tạo một table chỉ hiển thị bên trong transaction:

   ```text
   forumdb=*>      create temp table if not exists temp_users_transaction (
     pk int GENERATED ALWAYS AS IDENTITY
     ,username text NOT NULL
     ,gecos text
     ,email text NOT NULL
     ,PRIMARY KEY( pk )
     ,UNIQUE ( username )
    ) on commit drop;
   CREATE TABLE
   ```

   Bây giờ hãy kiểm tra table hiện diện bên trong transaction nhưng không hiện diện bên ngoài transaction:

   ```text
   forumdb=*> \d temp_users_transaction
   ```
