```text
pg_restore: finished item 3220 FK CONSTRAINT j_posts_tags j_posts_tags_
post_pk_fkey
pg_restore: finished main parallel loop
```

Nhờ verbose flag, có thể thấy rõ `pg_restore` đã thực hiện việc restore song song data trong database như thế nào. Những message như `launching item` và `finished item` cho biết thời điểm và object mà một parallel worker đã tham gia xử lý.

## Tự động hóa backup

Bằng cách kết hợp `pg_dump` và `pg_dumpall`, việc tạo automated backup khá dễ dàng, chẳng hạn chạy mỗi đêm hoặc mỗi ngày khi database system không được sử dụng nhiều. Tùy vào operating system bạn sử dụng, có thể schedule các backup như vậy để chúng được thực thi và tự động rotate.

Ví dụ, nếu sử dụng Unix, bạn có thể schedule `pg_dump` thông qua `cron(1)` như sau:

```text
$ crontab -e
```

Sau đó, bạn sẽ thêm dòng sau:

```text
30 23 * * * pg_dump -Fc -f /backup/forumdb.backup -U forum forumdb
```

Dòng này khởi tạo một full backup ở custom format mỗi ngày lúc 23:30. Tuy nhiên, cách tiếp cận trước đó có một vài nhược điểm, chẳng hạn quản lý các backup đã tồn tại, xử lý các database mới được thêm vào và cần thêm một dòng khác vào `crontab`, v.v.

Nhờ tính linh hoạt của PostgreSQL và catalog của nó, việc phát triển một wrapper script có thể dễ dàng xử lý backup cho tất cả database cũng không phức tạp. Là điểm bắt đầu, script sau thực hiện full backup cho mọi database ngoại trừ `template0`:

```sh
#!/bin/sh

BACKUP_ROOT=/backup

for database in $( psql -U postgres -A -t -c "SELECT datname FROM pg_database WHERE datname <> 'template0'" postgres )
do
     backup_dir=$BACKUP_ROOT/$database/$(date +'%Y-%m-%d')
     if [ -d $backup_dir ]; then
          echo "Skipping backup $database, already done today!"
          continue
     fi

     mkdir -p $backup_dir
     pg_dump -U postgres -Fd -f $backup_dir $database
     echo "Backup $database into $backup_dir done!"
done
```

Ý tưởng khá đơn giản: system query PostgreSQL catalog, `pg_database`, cho mỗi database mà cluster phục vụ; với mỗi database, nó tìm một dedicated directory có tên theo database và chứa một directory có tên theo ngày hiện tại. Nếu directory tồn tại, backup đã được thực hiện, nên không còn việc gì phải làm ngoài việc chuyển sang database tiếp theo. Nếu không, backup có thể được thực hiện. Vì vậy, một ngày system sẽ backup database `forumdb` vào directory `/backup/forumdb/2023-07-19`, ngày tiếp theo vào `/backup/forumdb/2023-07-20`, và tiếp tục như vậy. Nhờ đó, bạn có thể thêm script trước đó vào `crontab` rồi không cần bận tâm đến việc thêm các dòng mới cho database mới, cũng như xóa các dòng tương ứng với database đã bị xóa:

```text
30 23 * * * my_backup_script.sh
```

Dĩ nhiên, script trước đó không đại diện cho một backup system phức tạp mà chỉ là điểm bắt đầu nếu bạn cần một giải pháp nhanh và linh hoạt để thực hiện automated logical backup, sử dụng các tool mà PostgreSQL cluster và operating system của bạn cung cấp. Như đã nói, nhiều operating system đã tính đến việc backup một PostgreSQL cluster và cung cấp sẵn các script được viết để giúp bạn giải quyết vấn đề này. Một ví dụ rất tốt về loại script này là script `502.pgsql`, được cung cấp trong package PostgreSQL của FreeBSD.

## Lệnh COPY

Lệnh `COPY` về mặt thiết kế không phải là một backup facility, nhưng nó rất hiệu quả trong việc bulk loading data và vì vậy cũng hiệu quả trong restore backup như đã đề cập. Tuy nhiên, bản thân command này có thể được dùng để load data theo hai chiều: nhờ `COPY`, bạn có thể extract data từ một table (tức là thực hiện dump) hoặc load data vào một table (tức là thực hiện restore). Ngoài ra, `COPY` có thể tương tác với external program; nghĩa là nó có thể gửi (hoặc nhận) data trực tiếp từ một process khác.

`COPY` có hai operating mode chính:

- `COPY TO` lấy data ra khỏi một table và gửi nó tới một file trên filesystem hoặc tới một external application hay process khác.
- `COPY FROM` load data từ một file trên filesystem hoặc một external application và insert data vào table được chỉ định.

> Khi làm việc với external file hoặc program, command `COPY` yêu cầu superuser privilege (hoặc ít nhất user phải thuộc group `pg_write_server_files`). Vì lý do này, các ví dụ trong section này sẽ được chạy dưới user `postgres` superuser.

Ví dụ đơn giản, hãy giả sử chúng ta cần extract toàn bộ data từ table `categories`; đây là loại command `COPY TO`, như được chỉ ra dưới đây:

```text
forumdb=# COPY forum.categories TO '/tmp/categories.backup.txt';
COPY 5
```

Trong ví dụ trên, nội dung của table được ghi vào local file `/tmp/categories.backup.txt`, và nội dung file chỉ gồm các tuple, không có SQL instruction cụ thể nào:

```text
$ cat /tmp/categories.backup.txt
5         Software engineering           Software engineering discussions
1         Database               Database related discussions
2         Unix      Unix and Linux discussions
3         Programming Languages          All about programming languages
4         A.I       Machine Learning discussions
```

Command `COPY` hỗ trợ rất nhiều option cho phép user định nghĩa field delimiter, việc có table header (tức column name), quoting character, v.v. Nhờ vậy, việc tự xây dựng một tập data comma separated values (CSV) trở nên rất đơn giản:

```text
forumdb=# COPY forum.categories TO '/tmp/categories.csv'
WITH ( HEADER on, DELIMITER ';' );
COPY 5

$ cat /tmp/categories.csv
pk;title;description
5;Software engineering;Software engineering discussions
1;Database;Database related discussions
2;Unix;Unix and Linux discussions
3;Programming Languages;All about programming languages
4;A.I;Machine Learning discussions
```

Như bạn có thể thấy từ ví dụ trên, hiện mọi field đều được phân tách bằng dấu chấm phẩy, và row đầu tiên trong file là danh sách column của table. Cần lưu ý rằng `COPY` đã có sẵn một CSV format được định nghĩa, có thể chỉ định bằng option `FORMAT csv`:

```text
forumdb=# COPY forum.categories TO '/tmp/categories.csv'
WITH ( FORMAT csv );
COPY 5
```

Có một CSV file chứa data nghĩa là `COPY FROM` có thể load data vào một table. Nói cách khác, `COPY` không chỉ là một bulk loader hiệu quả; nó còn là một tool hữu ích để load data vào database từ các external resource như spreadsheet.

Hãy giả sử chúng ta cần load data trong file `categories.csv` vào một table khác có tên `categories_reloaded`:

```text
forumdb=# CREATE TABLE forum.categories_reloaded( LIKE forum.categories );
CREATE TABLE
forumdb=# COPY forum.categories_reloaded
               FROM '/tmp/categories.csv'
               WITH (FORMAT csv);
COPY 5
```

Bạn cũng có thể chỉ định một `WHERE` clause để filter những gì sẽ được load; ví dụ, hãy giả sử chúng ta chỉ muốn load các row lẻ:

```text
forumdb=# COPY forum.categories_reloaded
               FROM '/tmp/categories.csv'
          WITH (FORMAT csv)
          WHERE pk % 2 = 1;
```

`COPY TO` không cho phép `WHERE` clause, nhưng có thể copy từ một query để thực hiện việc filter tuple:

```text
forumdb=# COPY
    ( SELECT * FROM forum.categories
          WHERE pk % 2 = 1 )
    TO '/tmp/categories.odd.csv'
    WITH (FORMAT csv);
```

Bạn cũng có thể pull tuple từ một external application, như ví dụ đơn giản sau đây minh họa:

```text
forumdb=# COPY forum.categories_reloaded
FROM PROGRAM $CODE$
/bin/bash -c 'for i in {1..10}; do echo "$i,Title$i,A generated row";
done' $CODE$
WITH (FORMAT csv);
```

Trong ví dụ trên, một shell process được khởi chạy; process đó tạo ra 10 tuple ở CSV format. Command `COPY` pull các tuple từ standard output của command rồi insert chúng vào table. Điều này hoạt động như một operating system pipe giữa các PostgreSQL table và external process.

Tương tự, bạn cũng có thể gửi data tới một external program, như ví dụ đơn giản sau đây:

```text
forumdb=# COPY forum.categories
           TO PROGRAM $CODE$ awk '{print $2;}' > /tmp/titles.txt $CODE$;
COPY 5

$ cat /tmp/titles.txt
Software
Database
Unix
Programming
A.I
```

Trong ví dụ trên, toàn bộ data trong table được gửi tới `awk(1)`, tool này extract chỉ column thứ hai (tức column `title`) và redirect output của chính nó vào một file. Kết quả cuối cùng là một dạng pseudo filtering đối với nội dung của table.

> Cần lưu ý rằng `COPY` hỗ trợ single-column list, nghĩa là bạn đã có thể chỉ định những column nào mình đang extract hoặc insert vào.

Khi sử dụng `COPY` để làm việc với external file hoặc program, user chạy command phải là superuser hoặc phải thuộc group `pg_write_server_files`.

Nói cách khác, user không có privilege không thể sử dụng `COPY`. Để xử lý việc này, `psql` cung cấp command thay thế cho `COPY` của riêng nó, có tên là `\copy`, command này stream content (theo cả hai chiều) liên quan đến các file mà `psql` client có thể truy cập. Nhờ vậy, user có thể khai thác `COPY` mà không cần server privilege đặc biệt nào như `pg_write_server`.

Vì vậy, để extract data từ một query và đưa nó vào file, user không có privilege nên thực hiện tương tự như sau:

```text
forumdb=> \COPY
( SELECT * FROM forum.categories
 WHERE pk % 2 = 1 )
TO '/tmp/categories.odd.csv'
WITH (FORMAT csv);
COPY 3
```

Lưu ý việc sử dụng `\copy` thay vì `COPY`.

Nhờ có `COPY` và psql wrapper `\copy` của nó, user có thể dễ dàng bulk-load data và extract data từ database.

Sau khi đã tìm hiểu logical backup, hãy chuyển sang physical backup.

## Khám phá physical backup

Physical backup là một low-level backup được thực hiện trong khi database cluster đang hoạt động bình thường. Ở đây, low-level nghĩa là backup được thực hiện theo cách nào đó “bên ngoài” backup cluster, tức ở filesystem level.

Như bạn đã biết từ Chapter 10, Users, Roles, and Database Security, database cluster cần cả các data file nằm trong `PGDATA/base` và WAL nằm trong `PGDATA/wal`, cùng với một vài file khác, để cluster hoạt động đúng. Tuy nhiên, concept chính là data file và WAL có thể khiến cluster tự self-heal và recover sau crash. Vì vậy, physical backup thực hiện copy toàn bộ cluster file; sau đó, khi cần restore, nó mô phỏng một database crash và để cluster self-heal với WAL đang có sẵn.

Lý do physical backup quan trọng là nó cho phép chúng ta clone một cluster một cách hiệu quả, bắt đầu từ các file tạo nên cluster đó. Điều này có nghĩa là, một mặt, bạn không thể restore một cluster đã được physical backup trên một PostgreSQL version khác; mặt khác, trong backup phase, về cơ bản bạn không cần tương tác với cluster.

Điểm sau đặc biệt quan trọng: physical backup có thể được thực hiện hầu như bất kỳ lúc nào mà không tác động đến database bằng một transaction lớn như trong logical backup, và không can thiệp vào các database activity đang diễn ra, chẳng hạn client connection và query. Đúng là storage system, đặc biệt là filesystem, sẽ chịu áp lực trong kiểu backup này, nhưng đối với cluster, backup gần như transparent.

Có thể nói rằng cluster phải được thông báo khi backup bắt đầu, cho phép cluster đánh dấu rõ ràng rằng backup đang diễn ra bên trong WAL; nhưng ngoài hành động “đơn giản” này, backup hoàn toàn nằm ngoài phạm vi của database cluster.

Hơn nữa, physical backup cho phép bạn chọn tool phù hợp nhất với việc low-level file copy. Bạn được tự do sử dụng bất kỳ filesystem-specific command nào, chẳng hạn `cp(1)`, `rsync(1)`, `tar(1)`, v.v.; bạn có thể backup qua network bằng bất kỳ file-copying mechanism nào mà operating system cung cấp, và thậm chí có thể tự phát triển tool của mình. Cũng có rất nhiều backup solution cho PostgreSQL, bao gồm tool mà các tác giả yêu thích là `pgBackRest`, vì vậy bạn có thể tùy chỉnh backup strategy theo các tool phù hợp nhất với environment và requirement của mình.

Trong các subsection sau, bạn sẽ học cách thực hiện physical backup bằng tool đi kèm PostgreSQL, `pg_basebackup`. Tool này được phát triển như tool chính để clone một cluster, chẳng hạn làm điểm bắt đầu cho một replicated system (replication sẽ được trình bày trong các chapter sau).

Cần lưu ý rằng trong mọi trường hợp, việc `pg_basebackup` thực hiện thực chất là một tập các bước mà bất kỳ system administrator nào cũng có thể thực hiện thủ công; vì thế, tool này là một cách thuận tiện và đã được kiểm chứng kỹ để thực hiện physical backup.

## Thực hiện physical backup thủ công

Tool `pg_basebackup` thực hiện một thao tác clone database cluster local hoặc remote có thể được dùng làm backup. Để hoạt động đúng, cluster cần clone phải được setup phù hợp. Vì `pg_basebackup` “yêu cầu” PostgreSQL cung cấp WAL, điều quan trọng là target cluster có ít nhất hai WAL Sender process đang active (WAL Sender process chịu trách nhiệm phục vụ WAL qua một client connection).

Vì vậy, bước đầu tiên cần thực hiện trên database mà bạn muốn backup là kiểm tra configuration parameter `max_wal_senders` (trong file `postgresql.conf`) có giá trị từ 2 trở lên:

```text
max_wal_senders = 2
```

Một setting quan trọng khác là cho phép `pg_basebackup` tạo connection tới cluster: tool này sẽ connect không phải với tư cách client thông thường mà với tư cách một “replication” client, do đó file `pg_hba.conf` phải cho phép một rule cho phép administrative user connect tới database đặc biệt “replication”. Một cấu hình tương tự sau đây sẽ hoạt động cho local backup:

```text
host      replication         postgres     127.0.0.1/32       trust
```

Ở đây, user `postgres` được phép connect từ chính host đó tới database replication đặc biệt mà không cần cung cấp authentication credential.

> **WARNING:** Một replication connection có thể copy mọi phần data từ database và vì vậy phải được bảo vệ ở mức tối đa có thể. Trong production environment, luôn giới hạn incoming host cho replication connection, đồng thời thiết lập credential mạnh để validate connection!

Hãy giả sử chúng ta muốn thực hiện physical backup và lưu kết quả, tức bản thân backup, trong directory `/backup/data`. Để thực hiện backup, target directory phải tồn tại; nếu database có tablespace, từng directory của tablespace phải được remap tới một directory khác. Điều sau là bắt buộc vì chúng ta backup trên cùng host, nên PostgreSQL ngăn việc các directory clash với nhau.

Backup cũng cần một label, tức một mnemonic description về mục đích của backup, chỉ nhằm phục vụ khả năng đọc hiểu của con người.

> Trong Docker image của chapter này, các directory cần thiết để thực hiện backup và tablespace remapping đã được cấu hình sẵn.

Command sau sẽ thực hiện backup:

```text
$ pg_basebackup -D /backup/data -l 'My Physical Backup' -v -h localhost -p
5432 -U postgres -T /data/tablespaces/ts_b=/backup/tablespaces/ts_b -T /
data/tablespaces/ts_a=/backup/tablespaces/ts_a -T /data/tablespaces/ts_c=/
backup/tablespaces/ts_c
pg_basebackup: initiating base backup, waiting for checkpoint to complete
pg_basebackup: checkpoint completed
pg_basebackup: write-ahead log start point: 0/2000028 on timeline 1
pg_basebackup: starting background WAL receiver
pg_basebackup: created temporary replication slot "pg_basebackup_117"
pg_basebackup: write-ahead log end point: 0/2000100
pg_basebackup: waiting for background process to finish streaming ...
pg_basebackup: syncing data to disk ...
pg_basebackup: renaming backup_manifest.tmp to backup_manifest
pg_basebackup: base backup completed
```

Flag `-D` chỉ directory nơi bạn muốn lưu backup, trong ví dụ này là `/backup/data`. Flag tùy chọn `-l` cho phép cung cấp một textual label cho backup, có thể dùng để inspect backup và lấy thêm thông tin. Flag `-v` bật verbose mode, tạo ra output chi tiết về những gì command thực hiện ở từng bước. Flag `-T` được lặp lại cho PostgreSQL biết cách remap từng directory được dùng làm tablespace: directory bên trái dấu bằng là directory hiện tại nơi backup được lấy, còn directory bên phải là remapped path.

Các argument khác là những PostgreSQL libpq client flag điển hình, chỉ định cách connect tới database để có thể clone nó, trong trường hợp này là thông qua user `postgres` trên `localhost`, port `5432`.

> `pg_basebackup` hỗ trợ một số option khác có thể dùng để, chẳng hạn, giới hạn network bandwidth usage, hiển thị tiến trình của các backup đang diễn ra, và nhiều việc khác. Hãy tham khảo command documentation và online help để biết thêm chi tiết.

Nếu inspect directory nơi backup được lưu, bạn sẽ thấy nó thực sự là một clone của directory `PGDATA` của server mà bạn đã backup, bao gồm cả configuration file.

## `pg_verifybackup`

Từ PostgreSQL 13, có thể dùng tool tên `pg_verifybackup` để verify integrity của backup được thực hiện thông qua `pg_basebackup`. Nhìn tổng quan, nó hoạt động như sau:

```text
$ pg_verifybackup /backup/data/
backup successfully verified
```

Khi chỉ định directory chứa backup, tool có thể thực hiện check và báo cáo mọi corruption. Tool thực hiện bốn bước chính:

1. Đánh giá backup manifest để kiểm tra xem nó có thể đọc được và chứa thông tin backup hợp lệ hay không.
2. Scan backup content để tìm data file bị thiếu hoặc bị sửa đổi (một số configuration file được bỏ qua ở bước này vì user có thể đã thay đổi chúng).
3. So sánh toàn bộ data file checksum với các giá trị trong manifest để bảo đảm file không bị corrupt.
4. Bằng cách sử dụng một utility khác là `pg_waldump`, verify rằng các WAL record cần thiết để restore backup đang có sẵn và có thể đọc được.

Nhờ `pg_verifybackup`, bạn có thể chắc chắn rằng backup không bị hỏng do filesystem problem, disk failure hoặc nguyên nhân nào khác, và vì vậy có thể tiếp tục từ backup đó.

## Khởi động cluster đã clone

`pg_basebackup` thực hiện complete clone của target cluster, bao gồm các configuration file. Điều này có nghĩa là configuration của cluster chưa được “adapt” theo vị trí của clone, bao gồm data directory và listening option (ví dụ TCP/IP port). Vì vậy, bạn phải cẩn thận khi khởi động cloned cluster, vì nó có thể clash với cluster gốc, đặc biệt nếu backup được thực hiện local (trên cùng machine).

Ở đây, bạn có thể edit configuration trước khi thử start backup cluster, thay đổi main setting trên command line, hoặc chuyển backup tới một remote host.

Nếu muốn start cloned cluster, với giả định nó được giữ local như trong section trước, bạn có thể restart nó, chẳng hạn bằng các command-line setting sau:

```text
$ pg_ctl -D /backup/data/ -o '-p 5433' start
waiting for server to start....
LOG: database system was interrupted; last known up at 2023-07-19
16:43:39 UTC
LOG:      redo starts at 0/2000028
LOG:      consistent recovery state reached at 0/2000138
```
