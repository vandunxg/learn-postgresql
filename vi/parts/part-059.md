Bạn cũng có thể quyết định giới hạn phạm vi backup, theo schema hoặc data, ở một vài table bằng flag command-line `-t`; hoặc ngược lại, loại trừ một số table bằng parameter `-T`. Ví dụ, nếu muốn chỉ backup table `users` và sequence `users_pk_seq`, bạn có thể làm như sau:

```text
$ pg_dump -f users.sql -t forum.users -t forum.user_pk_seq forumdb
```

File `users.sql` được tạo sẽ chỉ chứa lượng data đủ để tạo lại các thành phần liên quan đến user, không hơn. Mặt khác, nếu muốn loại trừ table `users` khỏi backup, bạn có thể làm tương tự như sau:

```text
$ pg_dump -f users.sql -T forum.users -T forum.user_pk_seq forumdb
```

Dĩ nhiên, bạn có thể mix và match mọi option theo cách hợp lý với mình và, quan trọng hơn, cho phép restore chính xác những gì bạn cần. Ví dụ, nếu muốn lấy toàn bộ data chứa trong table `posts` cùng với chính table structure, bạn có thể làm như sau:

```text
$ pg_dump -f posts.sql -t forum.posts -a -v forumdb
...
pg_dump: warning: there are circular foreign-key constraints on this
table:
pg_dump:      posts
pg_dump: You might not be able to restore the dump without using
--disable-triggers or temporarily dropping the constraints.
pg_dump: Consider using a full dump instead of a --data-only dump to avoid
this problem.
```

`pg_dump` đủ thông minh để nhận ra table `posts` có các dependency và foreign key khác nhau, nên nó cảnh báo rằng dump của bạn sẽ không thể restore toàn bộ content của table `posts`. Bạn phải tự quản lý các dependency đó theo cách đúng, vì bạn đã yêu cầu `pg_dump` không thực hiện full backup (vốn luôn complete và consistent).

## Compression

`pg_dump` cung cấp một command-line option đặc biệt là `-Z`, nhận một integer từ 0 đến 9 để chỉ định compression level cho backup được tạo. Level 0 nghĩa là hoàn toàn không compression, còn 9 là mức compression cao nhất hiện có.

Để minh họa compression hoạt động như thế nào, giả sử chúng ta tạo hai backup của cùng một database, backup đầu tiên không compression và backup thứ hai có compression (hãy chú ý command-line option và filename thay đổi):

```text
$ pg_dump -f backup_forumdb_uncompressed.sql forumdb
$ pg_dump -f backup_forumdb_compressed.sql.gz -Z 9 forumdb
$ ls -1s backup_forumdb*
4 backup_forumdb_compressed.sql.gz
12 backup_forumdb_uncompressed.sql
```

Như bạn có thể thấy, file được compression chiếm một phần ba dung lượng của plain backup, nhưng lần này file không thể edit trực tiếp vì nó được lưu ở dạng binary compressed.

Compression có thể được áp dụng cho plain text (tức SQL) dump và directory format, nhưng không áp dụng được cho tar output format.

## Dump formats và pg_restore

Trong các section trước, bạn chỉ thấy plain SQL format cho backup và restore, nhưng `pg_dump` còn cung cấp các format phức tạp và thông minh hơn. Tất cả format ngoại trừ plain SQL đều phải dùng `pg_restore` để restore và vì vậy không phù hợp cho việc edit thủ công.

Backup format được chỉ định bằng command-line argument `-F` của `pg_dump`, cho phép dùng một trong các value sau:

- `c` (custom) là format đặc thù PostgreSQL trong một single-file archive.
- `d` (directory) là format đặc thù PostgreSQL có compression, trong đó mỗi object được tách ra thành các file khác nhau bên trong một directory.
- `t` (tar) là format `.tar` không compression; sau khi extract, nó tạo ra layout giống layout do directory format cung cấp.

Hãy bắt đầu với format đầu tiên: custom single-file format. Command để backup một database tương tự command dùng cho plain SQL format, trong đó bạn phải chỉ định output file, nhưng lần này file không phải plain text:

```text
$ pg_dump -Fc --create -f backup_forumdb.backup forumdb
```

Output file được tạo có size nhỏ hơn plain SQL file và không thể edit dưới dạng text vì nó là binary. Nhiều command-line argument của `pg_dump` áp dụng tương tự cho custom format, trong khi một số argument khác hoàn toàn không có ý nghĩa.

Trong mọi trường hợp, `pg_dump` đủ thông minh để biết cần xem xét điều gì và loại bỏ điều gì, vì vậy các command line sau sẽ tạo ra cùng backup như trong ví dụ trước:

```text
$ pg_dump -Fc --create --inserts -f backup_forumdb.backup forumdb
$ pg_dump -Fc --create --column-inserts -f backup_forumdb.backup forumdb
```

Rõ ràng, flag command-line `--column-inserts` và `--inserts` không có ý nghĩa trong loại backup này, vì sẽ không có text file (và do đó không có SQL statement) nào được tạo.

Khi đã có custom backup, làm thế nào để restore database content? Hãy nhớ rằng custom backup format yêu cầu dùng `pg_restore` để restore thành công. Như trước đó, hãy lại destroy database rồi restore nó bằng `pg_restore`:

```text
$ psql -c 'DROP DATABASE forumdb';
DROP DATABASE
$ pg_restore -C -d postgres backup_forumdb.backup
```

`pg_restore` chạy im lặng và restore database được chỉ định. Option `-C` cho biết `pg_restore` sẽ tạo lại database trước khi restore object vào đó. Option `-d` yêu cầu program trước tiên connect tới database `postgres`, phát hành một `CREATE DATABASE`, sau đó connect tới database mới được tạo để tiếp tục restore, tương tự như cách plain backup format đã làm. Rõ ràng, `pg_restore` yêu cầu một file bắt buộc để thao tác, tức argument cuối cùng được chỉ định trên command line.

Điều thú vị là `pg_restore` có thể tạo một danh sách SQL statement sẽ được thực thi mà không thực sự thực thi chúng. Command-line option `-f` thực hiện việc này, cho phép bạn lưu plain SQL vào một file hoặc inspect nó trước khi tiếp tục quá trình restore:

```text
$ pg_restore backup_forumdb.backup -f restore.sql
$ less restore.sql
--
-- PostgreSQL database dump
--

CREATE DATABASE forumdb WITH TEMPLATE = template0 ENCODING = 'UTF8'
LOCALE_PROVIDER = libc LOCALE = 'en_US.utf8';


ALTER DATABASE forumdb OWNER TO forum;


\connect forumdb


...
```

Như bạn có thể thấy, content của file `restore.sql` là plain SQL, tương tự output của plain dump bằng `pg_dump`. Điều này nghĩa là nếu dùng `pg_restore`, bạn luôn có thể lấy ra một danh sách SQL statement editable và human-readable từ một backup.

Một output format khác của `pg_dump` là directory format, được chỉ định bằng command-line flag `-Fd`. Ở format này, `pg_dump` tạo một tập các file compressed trong một directory trên disk; trong trường hợp này, command-line argument `-f` chỉ định tên của một directory thay vì một file duy nhất. Ví dụ, hãy backup vào một backup folder:

```text
$ pg_dump -Fd -f backup.d forumdb
$ ls -1s backup.d/
total 40
4 3368.dat.gz
4 3370.dat.gz
4 3371.dat.gz
4 3372.dat.gz
4 3373.dat.gz
4 3375.dat.gz
4 3377.dat.gz
12 toc.dat
```

Directory được tạo nếu cần, và mỗi database object được đặt trong một compressed file duy nhất. File `toc.dat` đại diện cho một ToC, một index cho `pg_restore` biết nơi tìm từng phần data bên trong directory. Ví dụ sau cho thấy cách destroy và restore database bằng backup ở directory format:

```text
$ psql -c "DROP DATABASE forumdb;"
DROP DATABASE
$ pg_restore -C -d postgres backup.d
```

Directory backup format hữu ích khi database tăng size, vì việc lưu một file khổng lồ duy nhất có thể trở thành vấn đề do vượt quá giới hạn của filesystem.

Format cuối cùng của `pg_dump` là `.tar`, có thể lấy được bằng command-line flag `-Ft`. Kết quả là tạo ra một uncompressed `tar(1)` archive chứa cùng directory structure đã tạo trong ví dụ trước, nhưng mọi file đều không compressed:

```text
$ pg_dump -Ft -f backup_forumdb.tar forumdb
$ tar -tf backup_forumdb.tar
toc.dat
3368.dat
3370.dat
3371.dat
3372.dat
3373.dat
3375.dat
3377.dat
```

Tiếp theo, chúng ta sẽ xem cách thực hiện selective restore, giúp bạn chọn những element nào của một database cần restore.

## Thực hiện selective restore

Khi thực hiện plain SQL database dump, bạn được phép edit thủ công kết quả vì đó là plain text, và chọn lọc remove những phần không muốn restore. Với custom format và `pg_restore`, bạn cũng có thể làm chính xác điều tương tự, nhưng cần thực hiện một vài bước.

Trước hết, bạn luôn có thể inspect content của binary dump bằng `pg_restore` và option `--list` của nó; option này in index (Table of Contents, gọi tắt là ToC) ra màn hình. Sau option `--list`, bạn cần chỉ định single file hoặc directory chứa backup để in TOC:

```text
$ pg_restore --list backup.d
;
; Archive created at 2023-09-29 15:35:12 UTC
;     dbname: forumdb
;     TOC Entries: 39
;     Compression: -1
;     Dump Version: 1.14-0
;     Format: DIRECTORY
;
;
; Selected TOC Entries:
;
6; 2615 16653 SCHEMA - forum forum
215; 1259 16654 TABLE forum categories forum
216; 1259 16659 SEQUENCE forum categories_pk_seq forum
217; 1259 16660 TABLE forum delete_posts forum
218; 1259 16665 TABLE forum j_posts_tags forum
219; 1259 16668 TABLE forum new_categories forum
220; 1259 16673 TABLE forum posts forum
221; 1259 16682 SEQUENCE forum posts_pk_seq forum
222; 1259 16683 TABLE forum tags forum
223; 1259 16688 SEQUENCE forum tags_pk_seq forum
224; 1259 16689 TABLE forum users forum
225; 1259 16694 SEQUENCE forum users_pk_seq forum
3368; 0 16654 TABLE DATA forum categories forum
3370; 0 16660 TABLE DATA forum delete_posts forum
3371; 0 16665 TABLE DATA forum j_posts_tags forum
3372; 0 16668 TABLE DATA forum new_categories forum
3373; 0 16673 TABLE DATA forum posts forum
3375; 0 16683 TABLE DATA forum tags forum
3377; 0 16689 TABLE DATA forum users forum
3385; 0 0 SEQUENCE SET forum categories_pk_seq forum
...
```

Các line bắt đầu bằng dấu chấm phẩy là comment, và như bạn có thể thấy, một vài line đầu tiên được in ra là banner mô tả content của backup, thời điểm backup được lấy, format (trong ví dụ này là “directory”) và số entry (object) trong backup.

Mỗi line không phải comment đại diện cho một database object hoặc một action đơn mà restore process sẽ thực hiện. Ví dụ, hãy xem line sau:

```text
222; 1259 16683 TABLE forum tags forum
```

Điều này cho biết table `tags` sẽ được user `forum` restore trong schema `forum`.

Line sau có nghĩa là cùng table đó sẽ được nạp data:

```text
3373; 0 16673 TABLE DATA forum posts forum
```

Nhờ ToC này, bạn có thể kiểm soát restoration process. Thực tế, nếu di chuyển hoặc xóa các line khỏi ToC, bạn có thể yêu cầu `pg_restore` thay đổi execution của nó. Ví dụ, trước hết hãy lưu ToC vào một text file:

```text
$ pg_restore --list backup.d > custom_toc.txt
```

Bây giờ, edit file `custom_toc.txt` bằng editor yêu thích và comment phần được đề cập như sau, bằng cách đặt dấu chấm phẩy ở character đầu tiên của line hoặc remove các line nạp table `tags` và join table liên quan:

```text
;3373; 0 16673 TABLE DATA forum posts forum
;3371; 0 16665 TABLE DATA forum j_posts_tags forum
```

Bây giờ, lưu file `custom_toc.txt`. Khi đó, có thể restore database bằng `pg_restore`, nhưng bạn phải yêu cầu program tuân theo ToC riêng của mình thay vì ToC đầy đủ và chưa sửa đổi đi kèm chính backup. Vì mục đích này, `pg_restore` cho phép chỉ định flag `-L` cùng ToC cần dùng:

```text
$ psql -c 'DROP DATABASE forumdb;'
DROP DATABASE

$ pg_restore -C -d postgres -L custom_toc.txt                backup.d
$ psql -c 'SELECT count(*) FROM forum.tags;' forumdb
count
-------
     0
(1 row)
```

Như bạn có thể thấy, table đã được tạo nhưng rỗng. Điều này minh họa cách bạn có thể điều khiển restoration của một backup để sắp xếp lại có chọn lọc các object cần restore.

Cũng có thể sắp xếp lại các line để một số object được restore trước những object khác, nhưng việc này phức tạp hơn nhiều, đặc biệt khi tồn tại cross-reference và dependency giữa các object. Dù vậy, đây là một cách cực kỳ linh hoạt để quyết định có chọn lọc những gì cần restore; hơn nữa, bạn có thể tạo một ToC khác để restore cùng format backup trong các working set khác nhau.

## Dump toàn bộ cluster

`pg_dumpall` là tool dùng để dump một full cluster. Nói ngắn gọn, `pg_dumpall` loop qua tất cả database có trong cluster và thực hiện một `pg_dump` trên từng database, sau đó dump các object cụ thể ở cluster level, chẳng hạn role.

`pg_dumpall` hoạt động tương tự `pg_dump`, vì vậy gần như mọi concept và option bạn đã thấy trong các section trước cũng áp dụng cho `pg_dumpall`. Nếu không chỉ định output format và file, `pg_dumpall` in mọi SQL statement cần thiết ra standard output. Giả sử bạn muốn lưu toàn bộ database content vào một SQL file duy nhất, command line sau cung cấp một full backup:

```text
$ pg_dumpall -f cluster.sql
```

File có thể nhanh chóng trở nên lớn, và lần này nó bắt đầu bằng việc tạo mọi role cần thiết:

```text
$ less cluster.sql
...
CREATE ROLE book_authors;
ALTER ROLE book_authors WITH NOSUPERUSER INHERIT NOCREATEROLE NOCREATEDB
NOLOGIN NOREPLICATION NOBYPASSRLS;
CREATE ROLE enrico;
ALTER ROLE enrico WITH NOSUPERUSER INHERIT NOCREATEROLE NOCREATEDB LOGIN
NOREPLICATION NOBYPASSRLS PASSWORD 'SCRAM-SHA-256$4096:PiAJvQ9sn/TcrlcfhJF
isQ==$+gEEKa0oYVLPYNS1o4zO4Jng0qAwajBe3DHirEkJT40=:gek2heWOJT+G+8dJa
zqtn4x3Wl5zYY0DyyyKed7pvXY=';
CREATE ROLE forum;

...
```

Sau đó nó tiếp tục bằng việc restore từng database, bao gồm cả `template1`. Tiếp theo, tất cả database được populate bằng các SQL statement do những lần chạy `pg_dump` riêng lẻ tạo ra.

`pg_dumpall` chỉ tạo SQL script, vì vậy bạn cần restore cluster bằng `psql` hoặc một interactive connection. Tất cả option chính có thể dùng với `pg_dump` đã trình bày ở các section trước cũng áp dụng cho `pg_dumpall`.

`pg_dumpall` cung cấp một option đặc biệt hữu ích là `--globals-only`, được dùng để chỉ dump các intra-cluster object, chẳng hạn role, tablespace và replication slot. Option này hữu ích để dump và restore các object đó giữa những cluster khác nhau:

```text
$ pg_dumpall --globals-only -f cluster.sql
```

## Parallel backups

Có thể dùng parallelization để tăng tốc backup và restore. Ý tưởng cơ bản là có nhiều process (và database connection), mỗi process được giao một task nhỏ hơn, nhờ đó thực hiện tất cả task song song sẽ cho performance tốt hơn.

Điều quan trọng cần lưu ý là thường vấn đề không phải là backup nhanh hơn, mà là có thể thực hiện restoration nhanh nhất có thể. Vì vậy, mặc dù có thể thực hiện cả backup và restoration ở parallel mode, bạn sẽ thấy restoration quan trọng hơn.

`pg_dump` cho phép chỉ định parallelism level qua command-line argument `-j`, và bạn phải gán cho nó một positive integer, tức số parallel process cần start. Sau đó `pg_dump` sẽ mở số parallel connection tới database bằng parallelism, cộng thêm một connection để điều khiển tất cả, và buộc mỗi connection dump một table riêng. Rõ ràng, không có ý nghĩa khi start nhiều process hơn số table trong database mà bạn cần backup.

Vì tất cả process sẽ dump một table duy nhất, parallel mode chỉ khả dụng cho directory (`-Fd`) format, trong đó mỗi table được lưu trong một file riêng để các process không trộn lẫn việc ghi của chúng.

Ví dụ, instruction sau sẽ dump database với ba parallel job, do đó mở bốn database connection:

```text
$ pg_dump -Fd -f backup_forumdb -v -j 3 forumdb
...
pg_dump: finished item 3373 TABLE DATA posts
pg_dump: finished item 3370 TABLE DATA delete_posts
pg_dump: finished item 3377 TABLE DATA users
pg_dump: dumping contents of table "forum.j_posts_tags"
pg_dump: dumping contents of table "forum.new_categories"
pg_dump: dumping contents of table "forum.tags"
pg_dump: finished item 3372 TABLE DATA new_categories
pg_dump: finished item 3375 TABLE DATA tags
pg_dump: finished item 3371 TABLE DATA j_posts_tags
```

Các message như `finished item` là những dumping process đơn lẻ đã hoàn tất cho một table duy nhất, và chúng sẽ không xuất hiện trong verbose output không parallel của command `pg_dump`. Điều quan trọng là phải xem xét số connection được mở bởi parallel `pg_dump`: chúng luôn được mở cho mỗi parallel job, cộng thêm một connection để synchronize và quản lý toàn bộ backup procedure. Điều này nghĩa là để thực hiện parallel backup, bạn phải bảo đảm có đủ connection khả dụng cho database; nếu không, backup sẽ fail.

Một khía cạnh quan trọng khác của parallel backup là chúng có thể fail trong hoàn cảnh concurrent. Thực tế, ngay khi `pg_dump` bắt đầu, process “master” acquire light lock (shared lock) trên mọi object mà parallel process sẽ dump; trong khi khi khởi động, mỗi parallel process acquire exclusive (heavy) lock trên object. Việc này ngăn object (một table) bị destroy trước khi parallel process hoàn tất công việc. Tuy nhiên, giữa lúc master process acquire lock đầu tiên và lúc parallel process được spawn acquire heavy lock, một connection concurrent khác có thể cố acquire lock trên table, dẫn đến khả năng xảy ra deadlock. Để ngăn việc này, master `pg_dump` process sẽ phát hiện dependency và abort toàn bộ backup.

`pg_restore` cũng hỗ trợ parallel restoration, bằng cùng mnemonic command-line argument `-j`. Command này sẽ spawn số process được chỉ định, tham gia vào việc load data, tạo index và mọi operation nặng, tốn thời gian khác.

Không giống `pg_dump`, `pg_restore` có thể hoạt động parallel cho cả directory format và custom format. Không dễ xác định số parallel job cần chỉ định cho `pg_restore`, nhưng thông thường đó là số CPU core, dù các value lớn hơn một chút đôi khi có thể tạo ra restoration nhanh hơn.

Ví dụ, command sau cho phép parallel restoration của backup đã tạo trước đó (line đầu tiên drop database để restoration thành công):

```text
$ psql -c "DROP DATABASE forumdb;"
$ pg_restore -C -d postgres -j 4 -v backup.d
...
pg_restore: finished item 3388 SEQUENCE SET users_pk_seq
pg_restore: finished item 3387 SEQUENCE SET tags_pk_seq
```
