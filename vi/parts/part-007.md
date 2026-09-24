- Chế độ immediate sẽ abort mọi PostgreSQL process, bao gồm cả client connection, và shutdown cluster theo cách dirty; nghĩa là server sẽ cần thực hiện một số hoạt động cụ thể khi restart để dọn dẹp dữ liệu dirty đó (sẽ nói thêm về việc này trong các chapter tiếp theo).

Trong mọi trường hợp, một khi stop command được phát hành, server sẽ không chấp nhận bất kỳ incoming connection mới nào từ client, và tùy vào stop mode bạn đã chọn, các connection hiện có sẽ bị terminate. Stop mode mặc định, nếu không được chỉ định, là fast; mode này buộc client phải disconnect ngay lập tức nhưng bảo đảm data integrity.

Nếu muốn thay đổi stop mode, bạn có thể dùng flag `-m` và chỉ định tên mode như sau:

```text
$ pg_ctl stop -m smart
waiting for server to shut down........................ done
server stopped
```

Trong ví dụ trước, command `pg_ctl` sẽ chờ, in ra một dấu chấm mỗi giây cho đến khi tất cả client disconnect khỏi server. Trong lúc đó, nếu bạn thử connect tới cùng cluster từ một client khác, bạn sẽ nhận được error vì server đã bước vào quy trình stopping:

```text
$ psql
psql: error: could not connect to server: FATAL:  the database system is
shutting down
```

Có thể chỉ định chữ cái đầu tiên của stop mode thay vì viết cả từ; chẳng hạn, `s` cho smart, `i` cho immediate và `f` cho fast.


## Các PostgreSQL process

Bạn đã biết postmaster là root của mọi PostgreSQL process, nhưng như đã giải thích trong Chapter 1, *Introduction to PostgreSQL*, PostgreSQL sẽ khởi chạy nhiều process khác nhau khi startup. Các process này chịu trách nhiệm giữ cho cluster hoạt động và ở trạng thái tốt.

Phần này cung cấp một cái nhìn tổng quan về các process chính bạn có thể tìm thấy trong một cluster đang chạy, giúp bạn nhận diện từng process và mục đích tương ứng của chúng.

Nếu kiểm tra một cluster đang chạy từ góc nhìn của operating system, bạn sẽ thấy một nhóm process gắn với PostgreSQL:

```text
$ pstree -p postgres
postgres(1)─┬─postgres(34)
            ├─postgres(35)
            ├─postgres(37)
            ├─postgres(38)
            └─postgres(39)
```

```text
$ ps -C postgres -af
postgres           1         0   0 11:08 ?            00:00:00 postgres
postgres          34         1   0 11:08 ?            00:00:00 postgres: checkpointer
postgres          35         1   0 11:08 ?            00:00:00 postgres: background
writer
postgres          37         1   0 11:08 ?            00:00:00 postgres: walwriter
postgres          38         1   0 11:08 ?            00:00:00 postgres: autovacuum
launcher
postgres          39         1   0 11:08 ?            00:00:00 postgres: logical
replication launcher
```

> Các PID được báo cáo trong những ví dụ này là PID của Docker container, trong đó PostgreSQL process đầu tiên có PID bằng `1`. Trên các máy khác, bạn sẽ nhận được các PID khác.

Như bạn có thể thấy, process có PID `1` là process spawn một số child process, do đó đây là PostgreSQL process đầu tiên và chính được khởi chạy; vì vậy, nó thường được gọi là postmaster. Các process khác gồm:

- **checkpointer** là process chịu trách nhiệm thực thi các checkpoint, tức những thời điểm database bảo đảm rằng toàn bộ data thực sự được lưu bền vững trên disk.
- **background writer** chịu trách nhiệm hỗ trợ đẩy data từ memory ra permanent storage.
- **walwriter** chịu trách nhiệm ghi Write-Ahead Logs (WAL), các log cần thiết để bảo đảm data reliability ngay cả khi database crash.
- **logical replication launcher** là process chịu trách nhiệm xử lý logical replication.

Tùy vào configuration chính xác của cluster, có thể có các process khác đang hoạt động:

- **Background workers:** Đây là các process có thể được user tùy chỉnh để thực hiện các background task.
- **WAL receiver và/hoặc WAL sender:** Đây là các process tham gia nhận data từ hoặc gửi data tới một cluster khác trong các replication scenario.

Nhiều concept và mục đích của danh sách process trước sẽ trở nên rõ ràng hơn khi bạn tiếp tục đi qua các chapter của sách, nhưng hiện tại, chỉ cần biết rằng PostgreSQL còn có một vài process khác luôn active bất kể có incoming client connection hay không.

Khi một client connect tới cluster của bạn, một process mới sẽ được spawn: process này, được gọi là backend process, chịu trách nhiệm phục vụ request của client (nghĩa là execute query và trả về result). Bạn có thể xem và đếm các connection bằng cách kiểm tra process list:

```text
$ ps -C postgres -af
UID             PID       PPID   C STIME TTY                 TIME CMD
postgres          1          0   0 11:08 ?              00:00:00 postgres
postgres         34          1   0 11:08 ?              00:00:00 postgres: checkpointer
postgres         35          1   0 11:08 ?              00:00:00 postgres: background
writer
postgres         37          1   0 11:08 ?              00:00:00 postgres: walwriter
postgres         38          1   0 11:08 ?              00:00:00 postgres: autovacuum
launcher
postgres         39          1   0 11:08 ?              00:00:00 postgres: logical
replication launcher

postgres     40       1    0 04:35 ?             00:00:00 postgres: postgres postgres
[local] idle
```

Nếu so sánh danh sách trước với danh sách vừa rồi, bạn sẽ thấy có thêm một process với PID `40`: đây là một backend process. Cụ thể, process này đại diện cho một client connection tới database có tên `postgres`.

PostgreSQL dùng cách tiếp cận process cho concurrency thay vì cách tiếp cận multi-thread. Có nhiều lý do cho việc này; đáng chú ý nhất là isolation và portability mà cách tiếp cận multi-process mang lại. Hơn nữa, trên phần cứng và phần mềm hiện đại, việc fork một process không còn là một thao tác quá tốn kém.

Vì vậy, một khi PostgreSQL đang chạy, có một cây process bắt nguồn từ postmaster. Mục đích của postmaster là spawn process mới khi cần xử lý các database connection mới, đồng thời monitor toàn bộ maintenance process để bảo đảm cluster đang hoạt động tốt.

## Kết nối tới cluster

Khi PostgreSQL đang chạy, nó chờ các incoming database connection để phục vụ; ngay khi có một connection đến, PostgreSQL phục vụ connection đó bằng cách connect client tới database phù hợp. Điều này có nghĩa là để tương tác với cluster, bạn cần connect tới cluster. Tuy nhiên, bạn không connect tới toàn bộ cluster; thay vào đó, bạn yêu cầu PostgreSQL tương tác với một trong các database mà cluster đang phục vụ. Do đó, khi connect tới cluster, bạn cần connect tới một database cụ thể. Điều này cũng có nghĩa là cluster phải có ít nhất một database ngay từ đầu vòng đời của nó.

Khi khởi tạo cluster bằng command `initdb`, PostgreSQL xây dựng filesystem layout của thư mục `PGDATA` và xây dựng hai template database có tên `template0` và `template1`. Các template database được dùng làm điểm bắt đầu để clone những database mới khác, sau đó các database này có thể được user thông thường dùng để connect. Trong một PostgreSQL cluster mới cài đặt, bạn thường có một database `postgres`, được dùng để database administrator user `postgres` connect và tương tác với cluster.

Để connect tới một trong các database, dù là template database hay user-defined database, bạn cần một client để thực hiện connection. PostgreSQL đi kèm `psql`, một command-line client cho phép bạn connect, tương tác với và administer database cũng như chính cluster.

Các client khác cũng tồn tại, nhưng sẽ không được thảo luận trong sách này. Bạn có thể tự do chọn client mình thích nhất, vì mọi command, query và example được trình bày trong sách đều chạy không có ngoại lệ trên mọi client tương thích.

Trong khi việc connect tương tác tới cluster là một task quan trọng đối với database administrator, các developer thường cần application riêng của họ connect tới cluster. Để làm được điều này, application cần một thứ gọi là connection string, một URI chỉ ra mọi parameter cần thiết để connect tới database.

Phần này sẽ giải thích toàn bộ concept nói trên, bắt đầu từ template database, sau đó trình bày cách sử dụng cơ bản của `psql` và connection string.

### Các template database

Database `template1` là database đầu tiên được tạo khi system được initialize, sau đó nó được clone thành `template0`. Điều này có nghĩa là, ít nhất là ban đầu, hai database này giống hệt nhau; mục đích của `template0` là làm bản copy an toàn để rebuild trong trường hợp nó vô tình bị hỏng hoặc bị xóa.

Bạn có thể inspect các database khả dụng bằng command `psql -l`. Trên một installation mới cài đặt, bạn sẽ nhận được ba database sau:

```text
$ psql -l                                      List of databases
  Name    | Owner         | Encoding |   Collate         |     Ctype       | ICU Locale |
Locale Provider |        Access privileges
-----------+----------+----------+-------------+-------------+------------
+-----------------+-----------------------
postgres     | postgres | UTF8         | it_IT.UTF-8 | it_IT.UTF-8 |                         |
libc               |
 template0 | postgres | UTF8             | it_IT.UTF-8 | it_IT.UTF-8 |
| libc            | =c/postgres                  +
         |          |                 |                 |                 |
         | postgres=CTc/postgres
template1 | postgres | UTF8            | it_IT.UTF-8 | it_IT.UTF-8 |                         |
libc            | =c/postgres                 +
         |          |                 |                 |                 |
         | postgres=CTc/postgres
(3 rows)



                  +
```

> Trong Docker image, bạn cũng sẽ thấy database `forumdb`, database này đã được tự động tạo để bạn tương tác với các example khác.

Điều thú vị cần lưu ý là bên cạnh hai template database còn có database thứ ba được tạo trong quá trình installation: database `postgres`. Database đó thuộc về user `postgres`, theo mặc định là database administrator duy nhất được tạo trong quá trình initialization. Database này là một *common space* được dùng cho các connection thay vì các template database.

Tên **template** cho thấy mục đích thực sự của hai database này: khi bạn tạo một database mới, PostgreSQL clone một template database làm **common base**. Điều này hơi giống việc tạo user home directory trên Unix system: system clone một **skeleton directory** và gán bản copy mới cho user. PostgreSQL cũng làm tương tự: nó clone `template1` và gán database mới được tạo cho user đã yêu cầu việc đó.

Điều này cũng có nghĩa là bất kỳ object nào bạn đặt vào `template1`, bạn sẽ tìm thấy chính object đó trong các database mới được tạo. Điều này có thể rất hữu ích để cung cấp một **common base database** và tạo ra tất cả database khác với cùng một tập attribute và object.

Tuy nhiên, bạn không bị buộc phải dùng `template1` làm base template; thực tế, bạn có thể tạo các database riêng và dùng chúng làm template cho các database khác. Dù vậy, hãy nhớ rằng theo mặc định (đặc biệt là trên một system mới được initialize), database `template1` là database được clone cho những database đầu tiên bạn sẽ tạo.

Một khác biệt khác giữa `template1` và `template0`, ngoài việc database trước là mặc định cho các database mới, là bạn không thể connect tới database sau. Mục đích là ngăn việc vô tình làm hỏng `template0` (safety copy).

Điều quan trọng cần lưu ý là cluster (và mọi user-defined database) vẫn có thể hoạt động ngay cả khi không có template database; các database `template1` và `template0` không phải là thành phần nền tảng cần thiết để các database khác chạy. Tuy nhiên, nếu mất các template, bạn sẽ phải dùng một database khác làm template mỗi khi thực hiện một action cần template, chẳng hạn như tạo một database mới.

> Template database không được dành cho interactive connection, và bạn không nên connect tới các template database trừ khi cần customize chúng. PostgreSQL sẽ dùng template như một *skeleton* cho database khác nếu có connection đang active tới template đó.

### Command-line client `psql`

Command `psql` là command-line interface đi kèm mọi installation của PostgreSQL. Dù chắc chắn bạn có thể dùng graphical user interface để connect và tương tác với database, hiểu biết cơ bản về `psql` là bắt buộc để administer PostgreSQL cluster. Thực tế, một version `psql` cụ thể được đi kèm với mỗi release PostgreSQL; do đó, đây là client up-to-date nhất sử dụng cùng ngôn ngữ (tức protocol) với cluster. Hơn nữa, client này nhẹ và hữu ích ngay cả trong các tình huống khẩn cấp khi không có GUI.

`psql` chấp nhận một số option để connect tới database, chủ yếu gồm:

- `-d`: Tên database
- `-U`: Username
- `-h`: Host (một địa chỉ IPv4 hoặc IPv6, hoặc một hostname)

Nếu không chỉ định option nào, `psql` giả định user của operating system đang cố connect tới database có cùng tên, và database user có tên trùng với operating system user trên local connection. Xét connection sau:

```text
$ id
uid=999(postgres) gid=999(postgres) groups=999(postgres),101(ssl-cert)

$ psql
psql (16.0)
Type "help" for help.

postgres=#
```

Điều này có nghĩa là operating system user hiện tại (`postgres`) đã yêu cầu `psql` connect tới database có tên `postgres` thông qua PostgreSQL user có tên `postgres` trên local machine. Có thể yêu cầu connection một cách tường minh như sau:

```text
$ psql -U postgres -d postgres
psql (16.0)
Type "help" for help.

postgres=#
```

Điểm đầu tiên cần lưu ý là sau khi connection được thiết lập, command prompt thay đổi: `psql` báo database mà user đã connect tới (`postgres`) và một dấu hiệu cho biết user là superuser (`#`). Nếu user không phải database administrator, prompt sẽ kết thúc bằng dấu `>`.

Nếu cần connect tới một database có tên khác với operating system username của bạn, bạn cần chỉ định database đó:

```text
$ psql -d template1
psql (16.0)
Type "help" for help.

template1=#
```

Tương tự, nếu cần connect tới một database không tương ứng với operating system username, bằng một PostgreSQL user khác với operating system username, bạn phải truyền tường minh cả hai parameter cho `psql`:

```text
$ id
uid=999(postgres) gid=999(postgres) groups=999(postgres),101(ssl-cert)

$ psql -d template1 -U luca
psql (16.0)
Type "help" for help.

template1=>
```

Như bạn có thể thấy từ ví dụ trước, operating system user `postgres` đã connect tới database `template1` bằng PostgreSQL user `luca`. Vì user sau không phải system administrator, command prompt kết thúc bằng dấu `>`.

Để thoát khỏi `psql` và đóng connection tới database, bạn phải nhập `\q` hoặc `quit` rồi nhấn Enter (bạn cũng có thể nhấn `CTRL + D` để thoát trên mọi máy Unix và Linux):

```text
$ psql -d template1 -U luca
psql (16.0)
Type "help" for help.

template1=> \q
$
```

### Nhập SQL statement qua psql

Sau khi connect tới một database qua `psql`, bạn có thể issue bất kỳ statement nào mình muốn. Statement phải kết thúc bằng dấu chấm phẩy, cho biết lần nhấn Enter tiếp theo sẽ execute statement. Sau đây là một ví dụ trong đó phím Enter được đánh dấu:

```text
$ psql -d template1 -U luca
psql (16.0)
Type "help" for help.

template1=> SELECT current_time; <ENTER>
    current_time
--------------------
06:04:57.435155-05

(1 row)
```

SQL là ngôn ngữ case-insensitive, vì vậy bạn có thể nhập statement bằng uppercase, lowercase hoặc kết hợp cả hai. Quy tắc tương tự áp dụng cho column name, vì chúng cũng case-insensitive. Nếu cần identifier với case cụ thể, bạn phải đặt chúng trong double quote.

Một cách khác để execute statement là issue command `\g`, một lần nữa theo sau bởi `<ENTER>`. Cách này hữu ích khi connect thông qua terminal emulator có các phím đã được remap:

```text
template1=> SELECT current_time \g <ENTER>
 current_time
--------------------
06:07:03.328744-05

(1 row)
```

Cho đến khi bạn kết thúc statement bằng dấu chấm phẩy hoặc `\g`, `psql` sẽ giữ content bạn đang nhập trong query buffer, vì vậy bạn cũng có thể edit nhiều dòng text như sau:

```text
template1=> SELECT
template1-> current_time
template1-> ;
 current_time
--------------------
06:07:28.908215-05

(1 row)
```

Hãy lưu ý command prompt của `psql` đã thay đổi trên các dòng sau dòng đầu tiên: sự khác biệt này nhắc bạn rằng bạn đang edit một multi-line statement và `psql` vẫn chưa tìm thấy statement terminator (dấu chấm phẩy hoặc `\g`).

Một feature hữu ích của `psql` query buffer là khả năng edit content của query buffer trong một external editor. Nếu issue command `\e`, editor bạn yêu thích sẽ hiện ra cùng content của query được edit gần nhất. Sau đó, bạn có thể edit và refine SQL statement tùy ý; khi thoát editor, `psql` sẽ đọc nội dung bạn đã tạo và execute nó. Editor được sử dụng được chọn bằng operating system environment variable `EDITOR`.

Cũng có thể execute tất cả statement trong một file hoặc edit một file trước khi execute nó. Ví dụ, giả sử file `test.sql` có content sau:

```text
$ cat test.sql

SELECT current_database();
SELECT current_time;
SELECT current_role;
```

File có ba SQL statement rất đơn giản. Để execute toàn bộ file cùng một lúc, bạn có thể dùng special command `\i` theo sau bởi tên file:

```text
template1=> \i test.sql
 current_database
------------------
 template1

(1 row)

    current_time
--------------------
06:08:43.077305-05

(1 row)

 current_role
--------------
 luca
(1 row)
```

Như bạn có thể thấy, client đã execute lần lượt từng statement trong file. Nếu cần edit file mà không rời khỏi `psql`, bạn có thể issue `\e test.sql` để mở editor yêu thích, thực hiện thay đổi rồi quay lại `psql` connection.
