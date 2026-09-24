SQL không phân biệt chữ hoa/chữ thường và không phân biệt khoảng trắng: bạn có thể viết SQL toàn bộ bằng chữ hoa hoặc chữ thường, với bao nhiêu khoảng trắng ngang và dọc tùy ý. Trong cuốn sách này, SQL keyword sẽ được viết bằng chữ hoa và các statement sẽ được format để dễ đọc.

## Sơ lược các command của `psql`

Mọi command dành riêng cho `psql` đều bắt đầu bằng ký tự backslash (`\`). Bạn có thể xem một phần trợ giúp về SQL statement và PostgreSQL command thông qua command đặc biệt `\h`, sau đó chỉ định statement cụ thể mà bạn muốn xem trợ giúp:

```text
     template1=> \h SELECT
     Command:        SELECT
     Description: retrieve rows from a table or view
     Syntax:
     [ WITH [ RECURSIVE ] with_query [, ...] ]
     SELECT [ ALL | DISTINCT [ ON ( expression [, ...] ) ] ]
           [ * | expression [ [ AS ] output_name ] [, ...] ]
     ...
     URL: https://www.postgresql.org/docs/16/sql-select.html
```

Nội dung help hiển thị được rút gọn vì lý do không gian. Bạn có thể tìm thấy phần mô tả chi tiết hơn nhiều và các ví dụ sử dụng trong tài liệu online. Vì lý do này, ở cuối màn hình help có một link dẫn tới tài liệu online.

Nếu cần trợ giúp về các command của `psql`, bạn có thể phát hành command `\?`:

```text
     template1=> \?
     General
       \copyright                   show PostgreSQL usage and distribution terms
       \crosstabview [COLUMNS] execute query and display results in crosstab
       \errverbose                  show most recent error message at maximum
     verbosity
       \g [FILE] or ;               execute query (and send results to file or |pipe)
       \gdesc                       describe result of query, without executing it
     ...
```

Ngoài ra còn có nhiều command introspection, chẳng hạn `\d` để liệt kê tất cả table do user định nghĩa. Về bản chất, các command đặc biệt này là cách thực thi query đối với system catalog của PostgreSQL; đến lượt mình, các catalog này là registry về tất cả object tồn tại trong một database. Các command introspection sẽ được trình bày ở phần sau của cuốn sách và hữu ích như những shortcut để nắm được các object nào đang được định nghĩa trong database hiện tại.

Nhiều tính năng của `psql` sẽ được trình bày chi tiết dần trong cuốn sách, nhưng bạn nên dành thời gian làm quen với command-line client rất hiệu quả và giàu tính năng này.

## Giới thiệu connection string

Trong phần trước, bạn đã học cách chỉ định các tùy chọn connection cơ bản, chẳng hạn `-d` và `-U`, lần lượt dành cho database và user. `psql` cũng chấp nhận một connection string của LibPQ.

LibPQ là library nền tảng mà mọi application đều có thể dùng để kết nối tới một PostgreSQL cluster; chẳng hạn, nó được các client C và C++ cũng như các connector non-native sử dụng.

Một connection string trong LibPQ là một URI gồm nhiều phần:

```text
   postgresql://username@host:port/database
```

Ở đây, ta có:

- `postgresql` là fixed string chỉ protocol mà URI tham chiếu tới.
- `username` là PostgreSQL username sẽ được dùng khi kết nối tới database.
- `host` là hostname (hoặc IP address) cần kết nối tới.
- `port` là TCP/IP port mà server đang listen (mặc định là 5432).
- `database` là tên database mà bạn muốn kết nối tới.

Các phần username, port và database có thể được bỏ qua nếu chúng được đặt theo default (username giống với username của operating system).

Các connection sau tương đương nhau:

```bash
   $ psql -d template1 -U luca -h localhost
```

```bash
   $ psql postgresql://luca@localhost/template1
```

```bash
   $ psql postgresql://luca@localhost:5432/template1
```

## Giải quyết các vấn đề connection thường gặp

Có một số vấn đề thường gặp khi làm việc với database connection; phần này giải thích chúng để giúp bạn kết nối tới cluster dễ dàng hơn.

Xin lưu ý rằng các giải pháp được cung cấp chỉ dành cho mục đích testing, không dành cho production usage. Tất cả security setting sẽ được giải thích trong các chapter sau, nên mục tiêu của subsection dưới đây chỉ là giúp bạn làm cho test environment có thể sử dụng được.

### Database “foo” không tồn tại

Điều này có nghĩa là bạn đã viết sai tên database trong connection string hoặc đang cố kết nối mà không chỉ định database name.

Chẳng hạn, connection sau sẽ thất bại khi được thực thi bởi operating system user có tên `luca`, bởi theo default nó giả định rằng user `luca` đang cố kết nối tới database có cùng tên (tức là `luca`) vì chưa có tên nào được set rõ ràng:

```text
     $ psql
     psql: error: could not connect to server: FATAL:            database "luca" does not
     exist
```

Giải pháp là cung cấp một database name đang tồn tại thông qua option `-d`, hoặc tạo một database có cùng tên với user.

### Connection refused

Điều này thường có nghĩa là có vấn đề về network connection: hoặc host mà bạn đang cố kết nối tới không thể reach được, hoặc cluster không listen trên network.

Ví dụ, hãy hình dung PostgreSQL đang chạy trên một machine có tên `venkman` và ta đang cố kết nối từ một host khác trên cùng network:

```text
     $ psql -h venkman -U luca template1
     psql: error: could not connect to server: could not connect to server:
     Connection refused
             Is the server running on host "venkman" (192.168.222.123) and
     accepting
              TCP/IP connections on port 5432?
```

Trong trường hợp này, database cluster đang chạy trên remote host nhưng không accept connection từ bên ngoài. Thông thường, bạn phải sửa server configuration hoặc kết nối tới remote machine (chẳng hạn qua SSH) rồi mở một local connection từ đó.

Để nhanh chóng giải quyết vấn đề, bạn phải edit file `postgresql.conf` (thường nằm trong directory `PGDATA`) và bảo đảm option `listen_address` có giá trị dấu hoa thị (hoặc tên external network card của bạn), để server listen trên mọi network address hiện có:

```text
   listen_addresses = '*'
```

Sau khi restart service bằng command `restart` được phát hành tới `pg_ctl`, client sẽ có thể kết nối. Xin lưu ý rằng việc cho phép server listen trên mọi network address hiện có có thể không phải là giải pháp tối ưu và có thể khiến server gặp rủi ro trong production environment. Về sau trong cuốn sách, bạn sẽ học cách cấu hình cụ thể các connection property cho server.

### No `pg_hba.conf` entry

Lỗi này có nghĩa là server đang hoạt động và có thể accept request của bạn, nhưng cơ chế kiểm soát Host-Based Access (HBA) tích hợp trong PostgreSQL không cho phép bạn truy cập.

Lỗi này không bao giờ nên xảy ra trong Docker container được dùng cho chapter này, vì configuration của container đã cho phép trusted connection. Tuy nhiên, các PostgreSQL installation khác có thể strict hơn; do đó, biết về loại error message này có thể giúp bạn nhanh chóng xác định vấn đề nằm ở đâu trong configuration.

Ví dụ, connection sau bị từ chối:

```text
   $   psql -h localhost -U luca template1
   psql: error: could not connect to server: FATAL: no pg_hba.conf entry for
   host "127.0.0.1", user "luca", database "template1", SSL off
```

Lý do là khi kiểm tra file `pg_hba.conf`, không có rule nào cho phép user `luca` truy cập qua localhost interface. Vì vậy, chẳng hạn, thêm một line như sau vào file `pg_hba.conf` có thể khắc phục vấn đề:

```text
   host all luca 127.0.0.1/32 trust
```

Bạn cần reload configuration để áp dụng thay đổi. Format của từng line trong file `pg_hba.conf` sẽ được thảo luận ở phần sau, nhưng hiện tại, hãy giả định rằng line trên chỉ dẫn cho cluster accept mọi connection đi vào từ localhost bằng user `luca`.

## Khám phá disk layout của `PGDATA`

Trong các phần trước, bạn đã thấy cách install PostgreSQL và kết nối tới nó, nhưng chúng ta chưa xem xét phần storage của một cluster. Vì mục tiêu của PostgreSQL, cũng như của mọi relational database, là lưu trữ data lâu dài, cluster cần một dạng permanent storage. Cụ thể, PostgreSQL tận dụng underlying filesystem để lưu trữ data của chính nó. Tất cả thành phần liên quan đến PostgreSQL đều nằm trong một directory có tên `PGDATA`.

Directory `PGDATA` hoạt động như disk container lưu trữ toàn bộ data của cluster, bao gồm user data và cluster configuration.

Sau đây là ví dụ về nội dung của `PGDATA` đối với một PostgreSQL 16 cluster đang chạy:

```text
     $   ls -1 /postgres/16/data
     base
     global
     pg_commit_ts
     pg_dynshmem
     pg_hba.conf
     pg_ident.conf
     pg_logical
     pg_multixact
     pg_notify
     pg_replslot
     pg_serial
     pg_snapshots
     pg_stat
     pg_stat_tmp
     pg_subtrans
     pg_tblspc
     pg_twophase
     PG_VERSION
     pg_wal
     pg_xact
     postgresql.auto.conf
     postgresql.conf
     postmaster.opts
     postmaster.pid
```

Directory `PGDATA` được cấu trúc thành nhiều file và subdirectory. Các file chính gồm:

- `postgresql.conf` là main configuration file, được sử dụng theo default khi service được start.
- `postgresql.auto.conf` là configuration file được tự động include, dùng để lưu các setting được thay đổi động thông qua SQL instruction.
- `pg_hba.conf` là HBA file cung cấp configuration liên quan đến các database connection khả dụng.
- `PG_VERSION` là text file chứa major version number (hữu ích khi kiểm tra directory để biết version nào của cluster đã quản lý directory `PGDATA`).
- `postmaster.pid` là PID của postmaster process, process đầu tiên được launch trong cluster.

Các directory chính có trong `PGDATA` gồm:

- `base` là directory chứa toàn bộ user data, bao gồm database, table và các object khác.
- `global` là directory chứa các cluster-wide object.
- `pg_wal` là directory chứa các WAL file.
- `pg_stat` và `pg_stat_tmp` lần lượt là nơi lưu trữ statistical information permanent và temporary về status và health của cluster.

Tất nhiên, mọi file và directory trong `PGDATA` đều quan trọng để cluster hoạt động đúng, nhưng cho tới lúc này, danh sách trên là danh sách “core” các object nền tảng của chính `PGDATA`. Các file và directory khác sẽ được thảo luận trong những chapter sau.

## Các object trong directory `PGDATA`

PostgreSQL không đặt tên cho các object trên disk, chẳng hạn table, theo cách mnemonic hoặc human-readable; thay vào đó, mọi file đều được đặt tên theo một numeric identifier. Bạn có thể thấy điều này bằng cách xem subdirectory `base`, chẳng hạn:

```text
   $   ls -1 /postgres/16/data/base
   1
   16386
   4
   5
```

Như bạn thấy từ code trên, directory `base` chứa bốn object có tên 1, 4, 5 và 16386. Xin lưu ý rằng các số này có thể khác trên machine của bạn. Cụ thể, mỗi object trên là một directory chứa các file khác, như sau:

```text
      $ ls -1 /postgres/16/data/base/16386 | head
      112
      113
      1247
      1247_fsm
      1247_vm
      1249
      1249_fsm
      1249_vm
      1255
      1255_fsm
```

Như bạn thấy, mỗi file được đặt tên bằng một numeric identifier. Bên trong, PostgreSQL lưu một catalog cụ thể cho phép database ánh xạ mnemonic name tới numeric identifier và ngược lại. Integer identifier được gọi là OID (hay Object Identifier); đây là một thuật ngữ lịch sử mà ngày nay tương ứng với filenode. Hai thuật ngữ này sẽ được sử dụng thay thế cho nhau trong phần này.

Có một utility cụ thể cho phép bạn kiểm tra directory `PGDATA` và trích xuất mnemonic name: `oid2name`. Ví dụ, nếu thực thi utility `oid2name`, bạn sẽ nhận được danh sách tất cả database có sẵn tương tự như sau:

```text
      $ oid2name
      All databases:
         Oid     Database Name   Tablespace
      ----------------------------------
       16390           forumdb   pg_default
             5        postgres   pg_default
             4       template0   pg_default
             1       template1   pg_default
```

Như bạn thấy, các Oid number trong output của `oid2name` phản ánh chính những directory name được liệt kê trong directory `base`; mỗi subdirectory có tên tương ứng với database.

Bạn còn có thể đi xa hơn và kiểm tra một file đơn lẻ bằng cách đi vào database directory, chỉ định database nơi bạn sẽ tìm object name bằng flag `-d`:

```text
   $ cd /postgres/16/data/base/1
   $ oid2name -d template1 -f 3395
   From database "template1":
      Filenode                       Table Name
   -------------------------------------
           3395   pg_init_privs_o_c_o_index
```

Như bạn thấy, file 3395 trong directory `/postgres/16/data/base/1` tương ứng với table có tên `pg_init_privs_o_c_o_index`. Vì vậy, khi PostgreSQL cần tương tác với một table như thế này, nó sẽ tìm tới file `/postgres/16/data/base/1/3395` trên disk.

Từ ví dụ trên, có thể thấy rõ rằng mọi SQL table đều được lưu trữ dưới dạng một file có numeric name. Tuy nhiên, PostgreSQL không cho phép một file đơn lẻ lớn hơn 1 GB, vậy điều gì xảy ra nếu một table tăng quá giới hạn đó? PostgreSQL “gắn thêm” một file khác với numeric extension cho biết chunk 1 GB tiếp theo. Nói cách khác, nếu table của bạn được lưu trong file `123`, gigabyte thứ hai sẽ được lưu trong file `123.1`, và nếu cần thêm một gigabyte storage nữa, file `123.2` sẽ được tạo. Vì vậy, filenode tham chiếu tới file đầu tiên liên quan đến một table cụ thể, nhưng trên disk có thể lưu nhiều hơn một file.

## Tablespaces

PostgreSQL giả định rằng toàn bộ data của nó nằm trong directory `PGDATA`, nhưng điều đó không có nghĩa cluster của bạn bị “nhốt” trong directory này. Thực tế, PostgreSQL cho phép “thoát” khỏi directory `PGDATA` thông qua tablespace. Tablespace là một directory có thể nằm bên ngoài directory `PGDATA` và cũng có thể thuộc về một storage khác. Tablespace được ánh xạ vào directory `PGDATA` bằng các symbolic link được lưu trong subdirectory `pg_tblspc`. Theo cách này, PostgreSQL process không phải tìm ra bên ngoài `PGDATA`, nhưng vẫn có thể truy cập “external” storage. Tablespace có thể được dùng cho nhiều mục đích, chẳng hạn mở rộng data storage hoặc cung cấp storage performance khác nhau cho các object cụ thể. Ví dụ, bạn có thể tạo một tablespace trên disk chậm để chứa các object và table ít được truy cập, đồng thời giữ fast storage trong một tablespace khác cho các object được truy cập thường xuyên.

Bạn không phải tự tạo link: PostgreSQL cung cấp tính năng `TABLESPACE` để quản lý việc này và cluster sẽ tạo cũng như quản lý các link phù hợp bên dưới subdirectory `pg_tblspc`.

Ví dụ, sau đây là một directory `PGDATA` có ba tablespace khác nhau:

```text
     $ ls -l /postgres/16/data/pg_tblspc/
     lrwxrwxrwx 1 postgres postgres 22 Jan 19 13:08 16384 -> /data/tablespaces/
     ts_a
     lrwxrwxrwx 1 postgres postgres 22 Jan 19 13:08 16385 -> /data/tablespaces/
     ts_b
     lrwxrwxrwx 1 postgres postgres 22 Jan 19 13:08 16386 -> /data/tablespaces/
     ts_c
```

Như bạn thấy từ ví dụ trên, có ba tablespace được attach vào storage `/data`. Bạn có thể kiểm tra chúng bằng `oid2name` và flag `-s`:

```text
      $ oid2name -s
      All tablespaces:
            Oid   Tablespace Name
      ------------------------
           1663        pg_default
           1664         pg_global
          16384               ts_a
          16385               ts_b
          16386               ts_c
```

Như bạn thấy, các numeric identifier của symbolic link được ánh xạ tới mnemonic name của tablespace. Từ ví dụ trên, bạn có thể thấy cũng có hai tablespace đặc biệt:

- `pg_default` là default tablespace tương ứng với “none”, tức storage default được dùng cho mọi object khi không có gì được chỉ định rõ ràng. Nói cách khác, mọi object được lưu trực tiếp bên dưới directory `PGDATA` đều được attach vào tablespace `pg_default`.
- `pg_global` là tablespace được dùng cho các system-wide object.

Theo default, cả hai tablespace trên đều tham chiếu trực tiếp tới directory `PGDATA`, nghĩa là mọi cluster không có custom tablespace đều được chứa hoàn toàn bên trong directory `PGDATA`.

## Khám phá các configuration file và parameter

Main configuration file của PostgreSQL là `postgresql.conf`, một text-based file điều khiển cluster khi cluster start.

Thông thường, khi thay đổi cluster configuration, bạn phải edit file `postgresql.conf` để ghi các setting mới và, tùy theo context của các setting đã edit, phát hành tín hiệu SIGHUP tới cluster (tức là reload configuration) hoặc restart cluster.

Mỗi configuration parameter được gắn với một context; tùy context, bạn có thể áp dụng thay đổi có hoặc không cần restart cluster. Các context khả dụng gồm:

- `internal`: một nhóm parameter được set tại compile time và vì vậy không thể thay đổi tại runtime.
- `postmaster`: tất cả parameter yêu cầu restart cluster (tức là kill postmaster process rồi start lại) để được activate.
- `sighup`: tất cả configuration parameter có thể được áp dụng bằng tín hiệu SIGHUP gửi tới postmaster process; điều này tương đương với việc phát hành một reload signal trong operating system service manager.
- `backend` và `superuser-backend`: tất cả parameter có thể được set tại runtime nhưng sẽ được áp dụng cho connection bình thường hoặc administrative connection tiếp theo.
- `user` và `superuser`: một nhóm setting có thể thay đổi tại runtime và lập tức active đối với connection bình thường và administrative connection.

Các configuration parameter sẽ được giải thích ở phần sau của cuốn sách, nhưng sau đây là ví dụ về một configuration file tối thiểu với một số setting khác nhau:

```text
   $ cat /postgres/16/data/postgresql.conf
   shared_buffers = 512MB
   maintenance_work_mem = 128MB
   checkpoint_completion_target = 0.7
   wal_buffers = 16MB
   work_mem = 32MB
   min_wal_size = 1GB
   max_wal_size = 2GB
```

File `postgresql.auto.conf` có chính xác cùng syntax như file `postgresql.conf` chính, nhưng được PostgreSQL tự động overwrite khi configuration được thay đổi tại runtime trực tiếp trong system, thông qua các administrative statement cụ thể như `ALTER SYSTEM`. File `postgresql.auto.conf` luôn được load ở thời điểm cuối cùng, do đó overwrite các setting khác. Trong một fresh installation, file này rỗng, nghĩa là nó sẽ không overwrite bất kỳ custom setting nào khác.
