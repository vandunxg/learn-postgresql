Có ba ứng dụng chính tham gia vào các thao tác backup và restore: `pg_dump`, `pg_dumpall` và `pg_restore`. Như có thể hình dung từ tên gọi, `pg_dump` và `pg_dumpall` liên quan đến việc trích xuất (dump) nội dung của một database, qua đó tạo ra một backup, còn `pg_restore` là đối tác tương ứng của chúng và cho phép bạn restore một backup hiện có.

> **Lưu ý:** Cần lưu ý rằng version của tool rất quan trọng, và bạn luôn nên dùng các tool khớp với cùng major version của PostgreSQL. Bạn có thể dùng tool từ version mới nhất để thực hiện backup trên các cluster cũ hơn, nhưng điều ngược lại thì không đúng.

Không giống các database engine khác, PostgreSQL không yêu cầu một permission đặc biệt có tên “backup” để dump nội dung của một database: chỉ cần user thực hiện backup có các grant cần thiết để truy cập dữ liệu mà họ muốn backup là đủ. Tương tự, để restore data, user phải có permission đủ để ghi data vào các table. Tuy nhiên, để đơn giản hóa việc quản lý permission, PostgreSQL cung cấp hai role được định nghĩa sẵn đặc biệt là `pg_read_all_data` và `pg_write_all_data`. Có thể grant các role này cho một user cần thực hiện backup và/hoặc restore; chúng sẽ tự động cung cấp cho user mọi quyền cần thiết để truy cập (read) hoặc restore (write) data.

Ứng dụng `pg_dump` được dùng để dump một database đơn lẻ bên trong một cluster, `pg_dumpall` cung cấp một cách thuận tiện để dump toàn bộ nội dung cluster, bao gồm các role và các object nội-cluster khác, còn `pg_restore` có thể xử lý output của hai ứng dụng trước để thực hiện restoration.

> **Lưu ý:** Hãy nhớ rằng một backup hợp lệ khi và chỉ khi nó có thể được restore. `pg_dump` và `pg_dumpall` sẽ không tạo ra một backup bị corrupt, nhưng storage của bạn có thể vô tình làm hỏng các file backup; vì vậy, để bảo đảm bạn có một backup hợp lệ, bạn luôn nên thử restore nó trên một machine hoặc cluster khác.

Cả ba command đều có thể hoạt động local hoặc remote trên cluster để backup hoặc restore data. Điều đó có nghĩa là bạn có thể dùng chúng từ một backup machine remote hoặc trên chính server đang chạy cluster. Các ứng dụng này tuân theo cùng quy ước về parameter và variable như `psql`; chẳng hạn, bạn có thể chỉ định username sẽ thực hiện backup (hoặc restore) bằng flag command-line `-U`, cũng như chỉ định remote host nơi cluster đang chạy bằng `-h`, v.v. Nếu không cung cấp parameter nào, ứng dụng giả định cluster đang chạy local và kết nối tới nó bằng user của operating system hiện tại, giống như `psql`.

Trong các subsection tiếp theo, bạn sẽ học cách backup và restore các database của chính mình.

## Dumping một database đơn lẻ

Để dump, tức là tạo một bản sao backup của một database, bạn cần dùng command `pg_dump`.

`pg_dump` cho phép dùng các backup format chính sau đây; chỉ format đầu tiên là phù hợp để restoration mà không cần `pg_restore`:

- **Plain text format:** Backup gồm các SQL statement có thể dùng để tái tạo database và được biểu diễn dưới dạng text SQL. Backup tạo ra có thể ở dạng plain text hoặc được compressed ngay trong quá trình tạo.
- **Directory format:** Backup được đặt trong một directory cụ thể, và mỗi table cùng large object của database được đặt vào một file compressed.
- **Custom format:** Đây là format đặc thù của PostgreSQL, phù hợp cho selective restore bằng `pg_restore`.
- **Tar format:** Phiên bản `tar(1)` của directory format nói trên.

Mặc định, `pg_dump` dùng plain text format. Format này tạo ra các SQL statement có thể dùng để dựng lại structure và content của database, đồng thời xuất backup trực tiếp ra standard output. Điều đó có nghĩa là nếu bạn backup một database mà không dùng option cụ thể nào, bạn sẽ thấy một danh sách dài các SQL statement:

```text
$ pg_dump forumdb
-- PostgreSQL database dump
...
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
...
CREATE SCHEMA forum;


ALTER SCHEMA forum OWNER TO forum;


SET default_tablespace = '';


SET default_table_access_method = heap;


--
-- Name: categories; Type: TABLE; Schema: forum; Owner: forum
--


CREATE TABLE forum.categories (
     pk integer NOT NULL,
     title text NOT NULL,
     description text



);


...
COPY forum.tags (pk, tag, parent) FROM stdin;
1         Operating Systems            \N
2         Linux     1
3         Ubuntu    2
4         Kubuntu 3
5         Database           \N
6         Operating Systems            \N
\.



...
```

Như bạn thấy, `pg_dump` đã tạo ra một tập hợp các SQL statement có thứ tự. Nếu đưa chúng vào một connection interactive, các statement này cho phép bạn dựng lại không chỉ database structure (table và function) mà cả content (data trong table), permission (grant và revoke), cùng các object cần thiết khác. Tất cả dòng bắt đầu bằng hai dấu gạch ngang là SQL comment mà `pg_dump` đã cẩn thận đặt vào để giúp bạn phân tích và hiểu content của backup database.

Có một vài điểm quan trọng cần lưu ý liên quan đến content của backup. Đầu tiên, `pg_dump` đặt một loạt `SET` statement ở ngay đầu backup; các `SET` statement này không bắt buộc đối với backup, nhưng cần thiết để restore từ content của backup này. Nói cách khác, vài dòng đầu tiên của backup không liên quan đến content của backup mà liên quan đến cách sử dụng backup đó.

Một dòng quan trọng trong số các `SET` statement này là dòng sau, được giới thiệu trong các version gần đây của PostgreSQL:

```sql
SELECT pg_catalog.set_config('search_path', '', false);
```

Các dòng như vậy loại bỏ (tức là làm rỗng) variable `search_path`, vốn là danh sách tên schema được dùng để tìm một object chưa được qualify. Tác động của dòng này là mọi object được tạo từ backup trong quá trình restore sẽ không khai thác bất kỳ malicious code nào có thể đã làm nhiễm environment và `search_path` của bạn. Side effect của việc này, như sẽ được trình bày sau, là sau khi restoration, user sẽ có một search path rỗng và sẽ không thể tìm các object chưa được fully qualify bằng tên của chúng.

Một điểm quan trọng khác về content của backup là theo mặc định, `pg_dump` dùng `COPY` để insert data vào các table đơn lẻ. `COPY` là một PostgreSQL command hoạt động giống `INSERT`, cho phép chỉ định nhiều tuple cùng lúc, và đáng chú ý nhất là được tối ưu cho bulk loading, nhờ đó recovery nhanh hơn. Tuy nhiên, điều này có thể khiến backup không portable giữa các database engine khác nhau. Vì vậy, nếu mục tiêu của bạn là dump content của database để migrate sang engine khác, bạn phải yêu cầu `pg_dump` dùng các `INSERT` statement thông thường thông qua flag command-line `--insert`:

```text
$ pg_dump --insert forumdb

...
INSERT INTO forum.tags OVERRIDING SYSTEM VALUE VALUES (1, 'Operating Systems', NULL);
INSERT INTO forum.tags OVERRIDING SYSTEM VALUE VALUES (2, 'Linux', 1);
INSERT INTO forum.tags OVERRIDING SYSTEM VALUE VALUES (3, 'Ubuntu', 2);
INSERT INTO forum.tags OVERRIDING SYSTEM VALUE VALUES (4, 'Kubuntu', 3);
INSERT INTO forum.tags OVERRIDING SYSTEM VALUE VALUES (5, 'Database', NULL);
INSERT INTO forum.tags OVERRIDING SYSTEM VALUE VALUES (6, 'Operating Systems', NULL);


...
```

Toàn bộ content của backup vẫn giống nhau, nhưng lần này các table được populate bằng những `INSERT` statement chuẩn. Như có thể hình dung, kết quả cuối cùng portable hơn nhưng cũng dài hơn (và do đó lớn hơn). Tuy nhiên, hãy lưu ý rằng trong ví dụ trước, các `INSERT` statement không chứa danh sách column mà mỗi field value ánh xạ tới; có thể tạo một tập `INSERT` statement portable hoàn toàn bằng cách thay option `--inserts` bằng `--column-inserts`:

```text
$ pg_dump --column-inserts forumdb
...
INSERT INTO forum.tags (pk, tag, parent) OVERRIDING SYSTEM VALUE VALUES
(1, 'Operating Systems', NULL);
INSERT INTO forum.tags (pk, tag, parent) OVERRIDING SYSTEM VALUE VALUES
(2, 'Linux', 1);
INSERT INTO forum.tags (pk, tag, parent) OVERRIDING SYSTEM VALUE VALUES
(3, 'Ubuntu', 2);
INSERT INTO forum.tags (pk, tag, parent) OVERRIDING SYSTEM VALUE VALUES
(4, 'Kubuntu', 3);
INSERT INTO forum.tags (pk, tag, parent) OVERRIDING SYSTEM VALUE VALUES
(5, 'Database', NULL);
INSERT INTO forum.tags (pk, tag, parent) OVERRIDING SYSTEM VALUE VALUES
(6, 'Operating Systems', NULL);


...
```

Dump content của database là việc hữu ích, nhưng lưu content đó vào một file còn hữu ích hơn nhiều và cho phép thực hiện restoration vào một thời điểm sau đó. Có hai cách chính để lưu output của `pg_dump` vào một file. Một cách là redirect output vào file, như trong ví dụ sau:

```text
$ pg_dump --column-inserts forumdb > backup_forumdb.sql
```

Cách còn lại (được khuyến nghị) là dùng option `-f` của `pg_dump`, cho phép chỉ định filename nơi content sẽ được đặt vào. Khi đó, command line trước có thể viết lại như sau:

```text
$ pg_dump --column-inserts -f backup_forumdb.sql forumdb
```

Cách này có đúng tác động như tạo file `backup_forumdb.sql`; file này chứa cùng SQL content đã được trình bày trong các ví dụ trước.

`pg_dump` cũng cho phép verbose output, tức là in ra các thao tác backup đang thực hiện. Flag command-line `-v` bật verbose output này:

```text
$ pg_dump -f backup_forumdb.sql -v forumdb
pg_dump: last built-in OID is 16383
pg_dump: reading extensions
...
pg_dump: creating SCHEMA "forum"
pg_dump: creating TABLE "forum.categories"
pg_dump: creating SEQUENCE "forum.categories_pk_seq"
pg_dump: creating TABLE "forum.delete_posts"
pg_dump: creating TABLE "forum.j_posts_tags"
pg_dump: creating TABLE "forum.new_categories"
pg_dump: creating TABLE "forum.posts"
pg_dump: creating SEQUENCE "forum.posts_pk_seq"
...
...
```

Khi đã chuẩn bị xong backup file, bạn có thể dễ dàng restore nó. Chúng ta sẽ học cách thực hiện việc này trong section tiếp theo.

## Restoring một database đơn lẻ

Nếu backup bạn tạo là plain SQL, bạn không cần gì ngoài một database connection để restore nó: bạn có thể thực thi một loạt statement theo đúng thứ tự để tạo lại content của database.

Cần lưu ý rằng theo mặc định, `pg_dump` không phát hành statement `CREATE DATABASE` trong content backup của nó. Thực tế, giả sử chúng ta tạo một backup file như sau:

```text
$ pg_dump --column-inserts -f backup_forumdb.sql forumdb
```

File `backup_forumd.sql` được tạo ra sẽ không bao gồm bất kỳ instruction nào về cách tạo một database mới. Điều này có thể tiện lợi nhưng cũng nguy hiểm: nó có nghĩa là restoration sẽ diễn ra bên trong database mà bạn đang kết nối tới.

> **Lưu ý:** `pg_dump` đủ thông minh để xác định đúng thứ tự mà các table và object khác phải được dump, bảo đảm dependency của chúng có thể được restore theo đúng thứ tự.

Giả sử chúng ta muốn restore content của database vào một database local khác, đặt tên là `forumdb_restore`. Bước đầu tiên là tạo một database như sau:

```text
$ psql -c 'CREATE DATABASE forumdb_restore WITH OWNER forum;'
CREATE DATABASE
```

Bây giờ có thể connect tới database đích và yêu cầu `psql` thực thi toàn bộ content của backup file:

```text
$ psql -U forum forumdb_restore
forumdb_restore=> \i backup_forumdb.sql
SET
SET
SET
SET
CREATE SCHEMA
ALTER SCHEMA
SET
SET
CREATE TABLE
ALTER TABLE
ALTER TABLE
CREATE TABLE
ALTER TABLE
CREATE TABLE
ALTER TABLE
CREATE TABLE
ALTER TABLE
CREATE TABLE
ALTER TABLE
ALTER TABLE
CREATE TABLE
ALTER TABLE
ALTER TABLE
CREATE TABLE
ALTER TABLE
ALTER TABLE
INSERT 0 1
INSERT 0 1
INSERT 0 1
...
```

Bạn sẽ thấy một danh sách output code của command như `INSERT 0 1`, nghĩa là đã xảy ra một `INSERT` đơn lẻ, cũng như xác nhận việc thực thi `ALTER TABLE`, `GRANT` và mọi command khác mà backup chứa. Tùy thuộc vào kích thước backup và performance của machine, restoration có thể mất từ vài giây đến vài phút.

Sau khi restore hoàn tất, có thể kiểm tra xem backup đã được restore hay chưa, chẳng hạn bằng cách query một table đơn lẻ để lấy data của nó:

```text
forumdb_test=> SELECT * FROM tags;
ERROR:    relation "tags" does not exist
LINE 1: SELECT * FROM tags;
                                ^
```

Khoan đã: điều này không có nghĩa là quy trình backup và restore đã không hoạt động đúng! Hãy nhớ rằng `pg_dump` đã chèn một instruction thích hợp để loại bỏ mọi entry khỏi `search_path`, vì vậy `psql` không biết cách tìm một table tên là `tags`, trong khi nó vẫn có thể tìm một table có fully qualified name như `forum.tags`:

```text
forumdb_restore=> SELECT * FROM forum.tags;
pk |           tag           | parent
----+-------------------+--------
 1 | Operating Systems |
 2 | Linux                   |        1
 3 | Ubuntu                  |        2
 4 | Kubuntu                 |        3
 5 | Database              |
 6 | Operating Systems |
(6 rows)
```

Bạn có thể đóng connection rồi khởi động lại để có một `search_path` được thiết lập như bình thường, hoặc tự đặt nó trong connection hiện tại bằng `set_config()`, chẳng hạn:

```text
forumdb_test=> SELECT pg_catalog.set_config('search_path', 'public,
"$user"', false);
    set_config
-----------------
   public, "$user"
(1 row)

forumdb_test=> SELECT * FROM tags;
pk |            tag          | parent
----+-------------------+--------
 1 | Operating Systems |
 2 | Linux                 |        1
 3 | Ubuntu                 |        2
 4 | Kubuntu                |        3
 5 | Database              |
 6 | Operating Systems |
(6 rows)
```

Như bạn thấy, bây giờ connection hoạt động hoàn toàn bình thường.

Cũng có thể thực hiện backup (và restore) ngay trong chính database đó. Trước hết, `pg_dump` phải bao gồm một option đặc biệt có tên `--create`, instruct application phát hành `CREATE DATABASE` như instruction đầu tiên của restoration:

```text
$ pg_dump --column-inserts --create -f backup_forumdb.sql forumdb
$ less backup_forumdb.sql
...
CREATE DATABASE forumdb WITH TEMPLATE = template0 ENCODING = 'UTF8'
LOCALE_PROVIDER = libc LOCALE = 'en_US.utf8';


ALTER DATABASE forumdb OWNER TO forum;


\connect forumdb



...
```

Như bạn thấy, output của `pg_dump` hiện bao gồm việc tạo database, cũng như command đặc biệt `\c` để connect ngay tới database đó. Nói cách khác, khi chạy file này thông qua `psql`, nó sẽ restore toàn bộ content vào đúng database khi database đó chưa tồn tại.

Để kiểm thử việc này, hãy hủy database thân yêu của chúng ta rồi restore nó bằng cách ban đầu connect tới `template1`:

```text
$ psql -c 'DROP DATABASE forumdb';
DROP DATABASE
$ psql
postgres=# \i backup_forumdb.sql
...
forumdb=#
```

Hãy chú ý rằng command prompt đã thay đổi để phản ánh việc hiện tại chúng ta đang connect tới database `forumdb` đã được restore.

Vậy nên dùng version dump và restoration nào? Nếu replicate database trong một cluster khác, chẳng hạn để migrate một staging database sang production, bạn nên bao gồm option `--create` để database engine tự tạo database cho bạn. Nếu migrate content của database vào một database đã tồn tại, tuyệt đối không được có option `--create`, vì không cần setup database; điều này có thể rủi ro vì bạn có thể restore object vào nhầm database, nên cần kiểm tra cẩn thận rằng bạn đang connect tới đúng database trước khi reload backup script.

Nếu migrate content của database sang engine khác, chẳng hạn một relational database khác, bạn nên dùng các option như `--inserts` hoặc `--column-inserts` để làm cho database backup portable hơn.

## Giới hạn lượng data cần backup

`pg_dump` cho phép dùng một tập hợp phong phú các filter và flag để giới hạn lượng data cần backup. Chẳng hạn, bạn có thể quyết định chỉ dump database schema mà không có data nào trong đó; việc này có thể thực hiện bằng flag `-s`. Mặt khác, có thể schema của database đã tồn tại và bạn chỉ cần content của database mà không cần bất kỳ DDL statement nào. Việc này có thể thực hiện bằng option `-a`. Tất nhiên, bạn có thể kết hợp các command `pg_dump` khác nhau để tạo các backup riêng biệt:

```text
$ pg_dump -s -f database_structure.sql forumdb
$ pg_dump -a -f database_content.sql forumdb
```

Bạn sẽ có một file tên `database_structure.sql` chứa tất cả các `CREATE TABLE` statement khác nhau, và một file khác chỉ chứa các statement `COPY` (hoặc `INSERT` nếu bạn đã chỉ định `--inserts`).
