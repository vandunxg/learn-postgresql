```text
          100 | host     | {all}              | {all}         | all           | scram-
sha-256
(7 rows)
```

Như bạn có thể thấy, `pg_hba_file_rules` báo cáo tất cả thông tin giống như thông tin bạn có thể tìm thấy trong `pg_hba.conf`, cùng với indicator số dòng cho biết một rule cụ thể được load từ dòng nào.

## Include các file khác trong pg_hba.conf

Có thể include các HBA configuration file khác vào file `pg_hba.conf` chính. PostgreSQL cung cấp ba directive chính:

* `include_file` include một file cụ thể trong `pg_hba.conf`
* `include_if_exist` include một file cụ thể nhưng chỉ khi file đó tồn tại; nếu file không tồn tại (hoặc đã bị xóa), sẽ không xảy ra error
* `include_dir` include tất cả file được chỉ định trong directory đã cho

Nhờ directive này, có thể định nghĩa một tập hợp các configuration file nhỏ được include literal vào HBA configuration, như thể administrator đã chỉnh sửa trực tiếp file `pg_hba.conf`.

Để hiểu một rule cụ thể đến từ đâu, catalog `pg_hba_file_rules` có một column `file_name` báo cáo rule đó được parse từ file nào (và ở dòng nào, nhờ `line_number`).

## Tóm tắt

PostgreSQL cho phép bạn định nghĩa từng user riêng lẻ và các group user, cả hai đều được biểu diễn bằng concept role của SQL. Khi có một lần thử connection đến database, PostgreSQL xử lý thông tin connection thông qua host-based access control để có thể ngay lập tức establish hoặc reject connection, tùy theo các rule giống firewall. Nếu connection có thể được establish, credential của role được kiểm tra, và cuối cùng user được cấp quyền truy cập.

User và group có thể được fine-tune về permission được cấp và giới hạn connection, nhờ đó bạn có thể quyết định mỗi role được phép consume bao nhiêu resource.

Trong chapter này, bạn đã thấy cách tạo và quản lý role, cũng như cách cho phép từng role connect đến cluster và các database cụ thể. Trong *Chapter 10, Users, Roles, and Database Security*, bạn sẽ tìm hiểu cách xử lý security property của user và group, nhưng trước khi đi tiếp, bạn cần biết cách object của PostgreSQL được tạo và quản lý.

Trong chapter tiếp theo, bạn sẽ học cách tương tác với PostgreSQL database bằng SQL statement.

## Kiểm tra kiến thức

* **Mục đích của file `pg_hba.conf` là gì?**

  File `pg_hba.conf` cấu hình Host-Based-Access (HBA), một tập hợp các rule định nghĩa cách một role cụ thể (user hoặc group) có thể establish connection đến một database cụ thể từ một host hoặc source cụ thể, thông qua một protocol đã định nghĩa. Xem phần *Managing incoming connections at the role level* để biết thêm chi tiết.

* **Bạn có thể inspect các HBA rule hiện đang được load như thế nào?**

  Catalog đặc biệt `pg_hba_file_rules` cung cấp chi tiết về các rule đã load. Xem phần *Inspecting pg_hba.conf rules* để biết thêm chi tiết.

* **Thứ tự của các rule bên trong `pg_hba.conf` có quan trọng không?**

  Có, các rule được evaluate từ trên xuống dưới, và rule đầu tiên match sẽ khiến quá trình evaluate kết thúc. Xem phần *Order of rules in pg_hba.conf* để biết thêm chi tiết.

* **Bạn có thể tìm thông tin về role ở đâu?**

  Các catalog đặc biệt `pg_roles` và `pg_authid` cung cấp thông tin về role. Xem phần *Inspecting existing roles* để biết thêm chi tiết.

* **Bạn có thể thêm một role vào group hoặc remove role đó khỏi một group (tức một role khác) như thế nào?**

  Statement `GRANT` có thể thêm một role vào role khác, trong khi statement `REVOKE` có thể remove association đó. Xem phần *Using a role as a group* để biết thêm chi tiết.

## Tài liệu tham khảo

* Tài liệu chính thức về statement `CREATE ROLE`: https://www.postgresql.org/docs/current/sql-createrole.html
* Tài liệu chính thức về statement `DROP ROLE`: https://www.postgresql.org/docs/current/sql-droprole.html
* Chi tiết về catalog `pg_roles` của PostgreSQL: https://www.postgresql.org/docs/current/view-pg-roles.html
* Chi tiết về catalog `pg_authid` của PostgreSQL: https://www.postgresql.org/docs/current/catalog-pg-authid.html
* Chi tiết về host-based access rule của PostgreSQL: https://www.postgresql.org/docs/current/auth-pg-hba-conf.html

## Tìm hiểu thêm trên Discord

Để tham gia Discord community của cuốn sách này, nơi bạn có thể chia sẻ feedback, đặt câu hỏi cho tác giả và tìm hiểu về các bản phát hành mới, hãy làm theo mã QR bên dưới:

https://discord.gg/jYWCjF6Tku

# 4. Basic Statements

Trong chapter này, chúng ta sẽ thảo luận về các PostgreSQL basic SQL command; đây là các Data Definition Language (DDL) command và Data Manipulation Language (DML) command. Nói một cách cơ bản, DDL command được dùng để quản lý database và table, còn DML command được dùng để insert, delete, update và select data bên trong database. Trong chapter này, chúng ta cũng sẽ đi sâu vào môi trường `psql`. Như đã học trong Chapter 2, *Getting to know your cluster*, `psql` có thể được mô tả là shell environment của PostgreSQL; đây là cánh cổng chúng ta phải đi qua để bắt đầu viết command native trong PostgreSQL. Chúng ta cần nhớ rằng `psql` luôn có mặt trong mọi PostgreSQL installation mà chúng ta làm việc cùng, và đáng để học vì đây là một environment mạnh để quản lý data và database.

Basic statement và `psql` do đó là nền tảng để chúng ta xây dựng kiến thức về PostgreSQL. Vì vậy, đọc và hiểu chapter này là điều thiết yếu để hiểu một số chủ đề phức tạp hơn được đề cập về sau.

Hãy bắt đầu bằng danh sách những gì chúng ta sẽ học trong chapter này:

* Thiết lập development environment
* Tạo và quản lý database
* Quản lý table
* Tìm hiểu các basic table manipulation statement

## Technical requirements

Đến thời điểm này trong sách, chúng ta đã học cách install PostgreSQL và configure user, nhưng nếu bạn chưa đọc các chapter trước, bạn vẫn có thể dễ dàng làm theo các bước tiếp theo bằng Docker image được mô tả dưới đây.

## Dùng Docker image

Nếu muốn làm theo các bước tiếp theo mà không install và configure PostgreSQL, bạn có thể dễ dàng thực hiện bằng Docker image trong GitHub repository (chi tiết về cách setup được trình bày trong Chapter 1, *Introduction to PostgreSQL*). Vì vậy, hãy start standalone container như được mô tả trong Chapter 1, *Introduction to PostgreSQL*, sau đó execute lệnh sau:

```text
$ sudo docker exec -it standalone_learn_postgresql_1 /bin/bash
```

Sau khi execute instruction này, chúng ta sẽ ở bên trong container `standalone_learn_postgresql_1` trong một root shell:

```text
root@learn_postgresql:/#
```

## Connect đến database

Ngay cả khi không dùng Docker container mà dùng native PostgreSQL installation như được mô tả trong Chapter 1, *Introduction to PostgreSQL*, chúng ta cũng sẽ đạt được kết quả giống như trên, bằng statement tương tự được execute với tư cách postgres user:

```text
root@learn_postgresql:/# su - postgres
postgres@learn_postgresql:~$ psql
postgres=#
```

Bây giờ hãy bật expanded mode bằng command `\x`:

```text
postgres=# \x
Expanded display is on.
```

Sau đó hãy list tất cả database hiện có trong cluster:

```text
postgres=# \l
List of databases
-[ RECORD 1 ]-----+--------------
Name                 | forumdb
Owner                  | forum
Encoding               | UTF8
Collate                | en_US.utf8
Ctype                  | en_US.utf8
ICU Locale             |
Locale Provider        | libc
Access privileges |
```

Vì lý do không gian, chúng ta chỉ báo cáo database `forumdb` được import từ Docker script, nhưng cũng có các database `template0`, `template1` và `postgres` như đã thấy trong Chapter 2, *Getting to know your cluster*. Cuối cùng, hãy connect đến database `forumdb`:

```text
postgres=# \c forumdb
You are now connected to database "forumdb" as user "postgres".
```

Bây giờ chúng ta đã hoàn thành việc setup development environment, có thể chuyển sang tạo database trong đó.

## Tạo và quản lý database

Trong section này, trước hết chúng ta sẽ tạo database đầu tiên, sau đó học cách xóa một database và cuối cùng là cách tạo database mới từ một database hiện có. Chúng ta cũng sẽ phân tích góc nhìn của DBA. Chúng ta sẽ xem điều gì xảy ra phía sau khi tạo database mới và tìm hiểu một số function cơ bản hữu ích cho DBA để hình dung kích thước thực của database.

Hãy xem cách tạo database từ đầu và điều gì xảy ra phía sau khi database được tạo.

### Tạo database

Để tạo một database có tên `databasename` từ đầu, bạn cần execute statement đơn giản sau:

```sql
CREATE DATABASE databasename;
```

> SQL là một case-insensitive language, vì vậy chúng ta có thể viết tất cả command bằng chữ hoa hoặc chữ thường.

Bây giờ hãy xem điều gì xảy ra phía sau khi tạo database mới. PostgreSQL thực hiện các bước sau:

1. Tạo một bản copy vật lý của template database `template1`
2. Gán database name cho database vừa được copy

Database `template1` là một database được tạo bởi process `initdb` trong quá trình initialize PostgreSQL cluster.

## Quản lý database

Chúng ta vừa xem cách tạo database. Trong section này, chúng ta sẽ xem cách quản lý database, cách list tất cả database hiện có trong một cluster, cách tạo database bắt đầu từ một database hiện có, cách drop database, và điều gì xảy ra bên trong khi tạo và drop database.

## Giới thiệu schema

Như đã nêu trong Chapter 1, *Introduction to PostgreSQL*: “một database có thể được tổ chức thành các namespace, được gọi là schema. Schema là một mnemonic name mà user có thể gán để tổ chức database object, chẳng hạn table, thành một collection có cấu trúc hơn. Schema không thể được lồng nhau, vì vậy chúng biểu diễn một flat namespace.”

Nhắc lại Chapter 1, *Introduction to PostgreSQL*, chúng ta đã học rằng có hai loại user: normal user và superuser:

* Superuser có thể làm mọi thứ trên các database và schema.
* Normal user có thể thực hiện các operation tùy theo privilege set của mình.

## PostgreSQL và public schema

Bắt đầu từ PostgreSQL 15, PostgreSQL đã thay đổi cách quản lý public schema. Trong section này, chúng ta sẽ xem nó hoạt động như thế nào. Trước PostgreSQL 15, bất kỳ user nào cũng có thể thực hiện bất kỳ DDL operation nào trên public schema. PostgreSQL 15 giới thiệu concept remove global privilege khỏi public schema.

Bắt đầu từ PostgreSQL 15:

* Normal user sẽ không thể execute DDL trên public schema.
* Normal user sẽ không thể thực hiện DML trên public schema trừ khi nhận được permission từ superuser.

Hãy dùng một ví dụ để giải thích rõ hơn feature mới này. Chúng ta sẽ làm việc như thể đang ở trên PostgreSQL version <=14.x.

Các bước chúng ta sẽ execute như sau (một số instruction sẽ được giải thích sau trong sách):

1. Chúng ta sẽ tạo một normal user tên `myuser`.
2. Chúng ta sẽ connect đến database bằng user `myuser`.
3. Với tư cách `myuser`, chúng ta sẽ thử tạo một table mới tên `mytable`.

Dưới đây là execution của những gì vừa nêu:

```text
forumdb=# create user myuser with password 'SuperSecret' login;
CREATE ROLE
forumdb=# set role to myuser;
SET
forumdb=> create table mytable(id integer);
ERROR:     permission denied for schema public
LINE 1: create table mytable(id integer);
```

Như có thể thấy, normal user không thể tạo table (DDL) trên public schema.

## Variable search_path

PostgreSQL có nhiều system variable. Một trong số đó có tên `search_path`. Variable `search_path` chứa sequence schema mà PostgreSQL dùng để tìm table; giá trị mặc định của `search_path` là `$user,public`. Điều này có nghĩa là trước tiên nó sẽ tìm các table trong schema có tên trùng với user hiện tại, sau đó sẽ tìm trong public schema.

Ví dụ, nếu có một user tên `forum` và muốn hiển thị tất cả record có trong một table tên `cities`, trước tiên PostgreSQL sẽ tìm table `cities` trong schema `forum`, và nếu không tìm thấy table `cities` trong schema `forum`, PostgreSQL sẽ tìm table `cities` trong public schema.

## Cách đúng để bắt đầu làm việc

Hãy bắt đầu từ đầu và execute các bước sau:

1. Với tư cách superuser, hãy tạo database mới tên `myforumdb` và connect đến đó.
2. Với tư cách superuser, hãy tạo user mới tên `myforum`.
3. Với tư cách superuser, hãy tạo schema mới tên `myforum` với authorization cho user `myforum`.
4. Hãy connect đến database bằng user `myforum`:

```text
postgres=# create database myforumdb;
CREATE DATABASE
postgres=# \c myforumdb
You are now connected to database "myforumdb" as user "postgres".
myforumdb=# create user myforum with password 'SuperSecret' login;
CREATE ROLE
myforumdb=# create schema myforum authorization myforum;
CREATE SCHEMA
```

Bây giờ hãy thử connect đến database `myforumdb` bằng user `myforum`:

```text
postgres@learn_postgresql:/$ psql -U myforum myforumdb
myforumdb=>
```

Hãy thử tạo một table mới tên `mytable` như đã làm trước đó:

```text
myforumdb=> create table mytable(id integer);
CREATE TABLE
```

Bây giờ đã hoạt động! Nó hoạt động vì table `mytable` được tạo bên trong schema `myforum` như đã giải thích ở trên.

> Database `forumdb` được cung cấp cùng container đã được setup sẵn để sử dụng với user `forum`, tham chiếu đến schema `forum`.

## List tất cả table

Bây giờ hãy connect đến database `forumdb` bằng user `forum`:

```text
postgres@learn_postgresql:/$ psql -U forum forumdb
forumdb=>
```

Để list tất cả table có trong database `forumdb`, chúng ta phải dùng command `psql` `\dt`. Command `\dt` tạo một list tất cả table hiện có trong database `forumdb`:

```text
forumdb=> \dt
              List of relations
 Schema |          Name      | Type   | Owner
--------+--------------+-------+-------
 forum    | categories       | table | forum
 forum    | j_posts_tags | table | forum
 forum    | posts            | table | forum
 forum    | tags             | table | forum
 forum    | users            | table | forum
(5 rows)
```

## Tạo database mới từ một modified template

Bây giờ chúng ta đã học cách list tất cả table trong một database, hãy bảo đảm rằng mọi thay đổi được thực hiện trên database `template1` sẽ xuất hiện trong tất cả database được tạo sau đó. Chúng ta sẽ thực hiện các bước sau:

1. Connect đến database `template1`.
2. Tạo một table tên `dummytable` bên trong database `template1`.
3. Tạo một database mới tên `dummydb`.

Hãy bắt đầu tạo database bằng các bước sau:

1. Connect đến database `template1`:

   ```text
   postgres@learn_postgresql:/$ psql template1
   template1=#
   ```

2. Với tư cách **superuser**, tạo một table tên `dummytable`. Hiện tại, chúng ta chưa cần lo về syntax chính xác để tạo table; nội dung này sẽ được giải thích chi tiết hơn sau:

   ```text
   template1=# create table dummytable (dummyfield integer not null
   primary key);
   CREATE TABLE
   ```

3. Dùng command `\dt` để hiển thị list các table hiện có trong database `template1`:

   ```text
   template1=# \dt
                List of relations
    Schema |        Name   | Type   |     Owner
   --------+------------+-------+----------
    public | dummytable | table | postgres
   (1 row)
   ```
