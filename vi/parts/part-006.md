3. Khi đã chắc chắn tarball đã tải xuống không bị hỏng, bạn có thể giải nén nội dung và bắt đầu compilation (hãy lưu ý rằng archive sau khi giải nén sẽ chiếm khoảng 200 MB dung lượng đĩa, còn compilation sẽ cần thêm một phần dung lượng):

```bash
$ tar xjvf postgresql-16.0.tar.bz2
$ cd postgresql-16.0
$ ./configure --prefix=/usr/local
$ make && sudo make install
```

Nếu muốn hoặc cần service file của `systemd(1)`, hãy thêm option `--with-systemd` vào dòng `configure`.

4. Sau khi database được cài đặt, bạn cần tạo một user để chạy database, thường có tên là `postgres`, và initialize database directory:

```bash
$ sudo useradd postgres
$ sudo mkdir -p /postgres/16/data
$ sudo chown -R postgres:postgres /postgres/16
$ /usr/local/bin/initdb -D /postgres/16/data
```

## Cài đặt PostgreSQL qua pgenv

`pgenv` là một tool nhỏ và tiện dụng, cho phép bạn download và quản lý nhiều instance PostgreSQL với các version khác nhau trên cùng một machine. Ý tưởng phía sau `pgenv` là giúp bạn khám phá các version PostgreSQL khác nhau, chẳng hạn để test application với các major version khác nhau. `pgenv` không nhằm trở thành một tool cấp enterprise để quản lý các instance đang chạy production; thay vào đó, đây là tool giúp developer và DBA experiment với các version PostgreSQL khác nhau và dễ dàng kiểm soát chúng.

Dĩ nhiên, vì là một tool bên ngoài, `pgenv` phải được cài đặt trước khi sử dụng. Tuy nhiên, việc cài đặt rất đơn giản vì application chỉ gồm một Bash script.

Cách nhanh nhất để cài đặt `pgenv` là clone GitHub repository và đặt biến môi trường `PATH` trỏ đến executable directory, như sau:

```bash
$ git clone https://github.com/theory/pgenv

$ export PATH=$PATH:./pgenv/bin
```

Giờ đây, command `pgenv` đã sẵn sàng để bạn sử dụng; bạn có thể chạy command này để nhận help prompt và xem các command khả dụng.

Ý tưởng phía sau `pgenv` khá đơn giản: đây là một tool tự động hóa những việc “nhàm chán”, tức là download, compile, install và start/stop một cluster. Để `pgenv` quản lý một instance cụ thể, bạn phải “use” instance đó. Khi bạn use một instance, `pgenv` sẽ phát hiện instance đã được initialized hay chưa; nếu chưa, nó sẽ tự thực hiện việc initialization cho bạn.

Để install version 16.0 và 15.1 của PostgreSQL, bạn chỉ cần chạy các command sau:

```bash
$ pgenv build 16.0

$ pgenv build 15.1
```

Các command trên sẽ download và compile hai version PostgreSQL. Thời gian cần để hoàn tất các operation phụ thuộc vào năng lực và tốc độ của machine bạn đang chạy. Sau đó, bạn có thể quyết định instance nào sẽ start bằng command `use`:

```bash
$ pgenv use 16.0
```

`pgenv` đủ thông minh để kiểm tra xem instance bạn đang start đã được initialized hay chưa; nếu chưa, nó sẽ initialize instance đó cho bạn (chỉ trong lần đầu tiên).

Nếu cần stop và thay đổi version PostgreSQL sẽ sử dụng, bạn có thể chạy command `stop`, sau đó chạy command `use` với version mục tiêu. Chẳng hạn, để stop instance 16.0 đang chạy và start instance 15.1, bạn có thể dùng:

```bash
$ pgenv stop

$ pgenv use 15.1
```

Tool `pgenv` còn cung cấp nhiều command khác để lấy thông tin về các version PostgreSQL đã được install, những gì đang execute (nếu có), v.v.

Nếu bạn đang tìm một cách nhanh để test và chạy các version PostgreSQL khác nhau trên cùng một machine, `pgenv` là một tool hữu ích.

## Tóm tắt

Chương này đã giới thiệu PostgreSQL, project và các feature chính của nó. Bạn đã tìm hiểu terminology của PostgreSQL, cũng như cách install một cluster trên các operating system Unix-like, bao gồm trong container, và cách install cluster từ nhiều source khác nhau.

Sau khi đã install PostgreSQL và tìm hiểu terminology của nó, bạn có thể chuyển sang các chương tiếp theo, nơi bạn sẽ học cách sử dụng, connect và lưu trữ data trong một database.

## Tài liệu tham khảo

- Release notes PostgreSQL: https://www.postgresql.org/docs/16/release-16.html
- Tài liệu upgrading: https://www.postgresql.org/docs/current/upgrading.html
- Chính sách version PostgreSQL: https://www.postgresql.org/support/versioning/
- Tài liệu chính thức về initdb của PostgreSQL: https://www.postgresql.org/docs/current/app-initdb.html
- Tài liệu chính thức về pg_ctl của PostgreSQL: https://www.postgresql.org/docs/current/app-pg-ctl.html
- GitHub repository và documentation của pgenv: https://github.com/theory/pgenv

## Tìm hiểu thêm trên Discord

Để tham gia Discord community dành cho cuốn sách này, nơi bạn có thể chia sẻ feedback, đặt câu hỏi cho tác giả và tìm hiểu về các bản release mới, hãy làm theo QR code bên dưới:

https://discord.gg/jYWCjF6Tku

# Làm quen với cluster của bạn

Để trở thành một user và administrator thành thạo của PostgreSQL cluster, trước hết bạn phải biết và hiểu PostgreSQL hoạt động như thế nào. Một database system là một hệ thống rất phức tạp, và PostgreSQL, với tư cách là một Database Management System (DBMS) cấp enterprise, hoàn toàn không phải là một software system đơn giản. Tuy nhiên, nhờ design và implementation rất tốt, một khi hiểu các concept và terminology cơ bản của PostgreSQL, mọi thứ sẽ nhanh chóng trở nên dễ hiểu và rõ ràng.

Chương này tiếp nối nền tảng của chương trước và giới thiệu thêm một số terminology, concept PostgreSQL, đồng thời hướng dẫn bạn cách tương tác với cluster. Bạn cũng sẽ được làm quen với `psql` client, thành phần đi kèm PostgreSQL và là cách được khuyến nghị để connect tới database. Bạn có thể tự do sử dụng bất kỳ SQL client nào có thể connect tới PostgreSQL; mọi code và example trong chương này cũng sẽ chạy ngay trong bất kỳ client nào khác. Tuy vậy, chúng tôi khuyến nghị bạn dành thời gian học `psql`. Vì được ship cùng PostgreSQL, `psql` được đảm bảo hoạt động trong mọi tình huống và là cách mặc định để connect tới cluster. `psql` là một text-only client; nếu bạn cảm thấy thoải mái hơn khi dùng graphical client, bạn có thể xem xét pgAdmin4, một trong những PostgreSQL graphical client nổi tiếng nhất.

Chương này đề cập đến các topic chính sau:

- Quản lý cluster
- Connect tới cluster
- Khám phá disk layout của PGDATA
- Khám phá các configuration file và parameter

## Yêu cầu kỹ thuật

Kiến thức cần có cho chương này như sau:

- Cách install binary package trên Unix machine
- PostgreSQL terminology cơ bản (từ chương trước)
- Sử dụng Unix command line cơ bản
- Các SQL statement cơ bản được đề cập trong chương này, chẳng hạn `SELECT`

Các example trong chương có thể chạy trên standalone Docker image, bạn có thể tìm image này trong GitHub repository của cuốn sách: https://github.com/PacktPublishing/Learn-PostgreSQL-Second-Edition. Để biết cách install và sử dụng Docker image dành cho cuốn sách, hãy tham khảo hướng dẫn trong Chapter 1, Introduction to PostgreSQL.

## Quản lý cluster

Một PostgreSQL cluster là collection gồm nhiều database, tất cả cùng chạy dưới một PostgreSQL service hoặc instance.

Quản lý một cluster nghĩa là có khả năng start, stop, take control và lấy thông tin về status của một PostgreSQL instance.

Xét từ góc nhìn operating system, PostgreSQL là một service có thể được start, stop và dĩ nhiên là monitor. Như đã thấy trong chương trước, thông thường khi install PostgreSQL, bạn cũng nhận được một tập hợp các tool và script dành riêng cho operating system để tích hợp PostgreSQL với service management của operating system. Thông thường, bạn sẽ tìm thấy system service file hoặc các tool dành riêng cho operating system khác, chẳng hạn `pg_ctl cluster`, được ship cùng Debian GNU/Linux và các derivative của nó.

PostgreSQL đi kèm một tool cụ thể tên là `pg_ctl`, giúp quản lý cluster và các process đang chạy liên quan. Section này giới thiệu cách sử dụng cơ bản của `pg_ctl` và các process bạn có thể gặp trong một cluster đang chạy. Operating system đang dùng service management system nào không quan trọng; `pg_ctl` luôn sẵn có cho PostgreSQL administrator để take control một database instance.

### pg_ctl

Command-line utility `pg_ctl` cho phép bạn thực hiện nhiều action khác nhau trên một cluster, chủ yếu là initialize, start, restart, stop, v.v. `pg_ctl` nhận command cần execute làm argument đầu tiên, sau đó là các argument cụ thể khác; các command chính như sau:

- `start`, `stop` và `restart` thực hiện action tương ứng trên cluster.
- `status` báo cáo status hiện tại (đang running hay không) của cluster.
- `initdb` (hoặc viết ngắn là `init`) thực hiện initialization của cluster, có thể xóa mọi data đã tồn tại trước đó.
- `reload` khiến PostgreSQL server reload configuration, hữu ích khi bạn muốn áp dụng các configuration change.
- `promote` được dùng khi cluster đang chạy như một replica server (cụ thể là một standby node) và từ thời điểm đó phải được tách khỏi primary ban đầu để trở nên độc lập (replication sẽ được giải thích trong các chương sau).

Nói chung, `pg_ctl` chủ yếu tương tác với postmaster (process đầu tiên được launch bên trong một cluster); đến lượt nó, postmaster “redirect” command tới các process khác đang tồn tại. Chẳng hạn, khi `pg_ctl` start một server instance, nó khiến process postmaster chạy; process này sau đó hoàn tất mọi hoạt động startup, bao gồm launch các utility process khác (như đã giải thích ngắn gọn trong chương trước). Mặt khác, khi `pg_ctl` stop một cluster, nó gửi một halt command tới postmaster; đến lượt mình, postmaster yêu cầu các process đang active khác thoát và chờ chúng hoàn tất.

`pg_ctl` cần biết vị trí của `PGDATA`, và bạn có thể chỉ định vị trí này bằng cách set một environment variable tên là `PGDATA` hoặc chỉ định trên command line thông qua flag `-D`.

> Process postmaster chỉ là process đầu tiên liên quan đến PostgreSQL được launch bên trong instance; trên một số system có một process tên là “postmaster”, trong khi trên các operating system khác chỉ có các process tên là “postgres”. Process đầu tiên được launch, bất kể tên của nó là gì, được gọi là postmaster. Tên postmaster chỉ đơn giản là một tên dùng để nhận diện một process giữa các process khác (cụ thể là process đầu tiên được launch trong cluster).

Tương tác với status của một cluster (ví dụ để stop cluster) là action không phải user nào cũng cần có khả năng thực hiện; thông thường, chỉ operating system administrator mới cần có khả năng tương tác với các service, bao gồm PostgreSQL.

Để giảm thiểu side effect của privilege escalation, PostgreSQL không cho phép chạy cluster bởi các privileged user như `root`. Vì vậy, PostgreSQL được chạy bởi một “normal” user, thường có tên là `postgres` trên mọi operating system. Unprivileged user này sở hữu directory `PGDATA` và chạy process postmaster, do đó cũng chạy tất cả process do chính postmaster launch. `pg_ctl` phải được chạy bởi chính unprivileged operating system user sẽ chạy cluster.

> Nếu bạn đang sử dụng Docker image, PostgreSQL đã chạy sẵn dưới dạng main service. Điều này có nghĩa là việc thực hiện command `stop` hoặc `restart` sẽ buộc bạn thoát khỏi container vì container bị shutdown.
>
> Ngoài ra, trong Docker container, PostgreSQL service đã chạy sẵn mà không cần can thiệp thủ công.

Command `status` chỉ query cluster để lấy thông tin, nên khá an toàn để bắt đầu tìm hiểu chuyện gì đang xảy ra:

```text
$ pg_ctl status
pg_ctl: server is running (PID: 1)
/usr/lib/postgresql/16/bin/postgres
```

Command báo cáo rằng server đang running, với Process Identifier (PID) bằng một (con số này sẽ khác trên machine của bạn). Ngoài ra, command báo cáo executable file được dùng để launch server; trong ví dụ trên là `/usr/lib/postgresql/16/bin/postgres`.

Nếu server không running vì bất kỳ lý do nào, command `pg_ctl` sẽ báo một message thích hợp cho biết nó không thể tìm thấy một instance PostgreSQL đã được start:

```text
$ pg_ctl status
pg_ctl: no server running
```

Để báo cáo status của cluster, `pg_ctl` cần biết database đang lưu data của chính nó ở đâu, tức là `PGDATA` nằm ở đâu trên disk. Có hai cách để cho `pg_ctl` biết vị trí của `PGDATA`:

- Set một environment variable tên là `PGDATA`, chứa path tới data directory.
- Dùng command-line flag `-D` để chỉ định path tới data directory.

> Hầu hết command liên quan đến PostgreSQL cluster đều tìm giá trị của `PGDATA` dưới dạng environment variable hoặc dưới dạng command-line option `-D`.

Trong các example trước, không có `PGDATA` nào được chỉ định vì giả định rằng giá trị của `PGDATA` đã được chỉ định bởi một environment variable.

Có thể dễ dàng kiểm tra điều này, chẳng hạn trong Docker container:

```text
$ echo $PGDATA
/postgres/16/data
$ pg_ctl status
pg_ctl: server is running (PID: 1)
/usr/lib/postgresql/16/bin/postgres
```

Nếu setup của bạn không có environment variable `PGDATA`, bạn luôn có thể set thủ công trước khi launch `pg_ctl` hoặc bất kỳ command nào khác liên quan đến cluster:

```bash
$ export PGDATA=/postgres/16/data
$ pg_ctl status
pg_ctl: server is running (PID: 1)
/usr/lib/postgresql/16/bin/postgres
```

Command-line argument được chỉ định bằng `-D` luôn có precedence so với mọi environment variable `PGDATA`. Vì vậy, nếu bạn không set hoặc cấu hình sai variable `PGDATA` nhưng truyền đúng value trên command line, mọi thứ vẫn hoạt động:

```text
$ export PGDATA=/postgres/data          # wrong PGDATA!
$ pg_ctl status -D /postgres/16/data
pg_ctl: server is running (PID: 1)
/usr/lib/postgresql/16/bin/postgres "-D" "/postgres/16/data"
```

Các concept về `PGDATA` và optional argument `-D` tương tự với hầu hết command “low-level” tác động lên một cluster. Điều này cho thấy rằng với cùng một tập executable, bạn có thể chạy nhiều PostgreSQL instance trên cùng một machine, miễn là giữ `PGDATA` directory của từng instance riêng biệt.

> Không sử dụng cùng một `PGDATA` directory cho nhiều version PostgreSQL. Dù trên test machine của riêng bạn, việc có một `PGDATA` directory duy nhất lần lượt được dùng bởi PostgreSQL 16 và PostgreSQL 15 có thể rất hấp dẫn, cách này sẽ không hoạt động như mong đợi và bạn có nguy cơ mất toàn bộ data. May mắn là PostgreSQL đủ thông minh để nhận ra `PGDATA` đã được tạo và sử dụng bởi một version khác, rồi từ chối operation; nhưng hãy cẩn thận, không chia sẻ cùng một `PGDATA` directory cho các instance khác nhau.

`pg_ctl` có thể được dùng để start và stop một cluster thông qua các command tương ứng. Ví dụ, bạn có thể start một instance bằng command `start` (giả sử environment variable `PGDATA` đã được set):

```text
$ pg_ctl start
waiting for server to start....
[27765] LOG:   starting PostgreSQL 16.0 on x
86_64-pc-linux-gnu, compiled by gcc (GCC) 12.1.0, 64-bit
[27765] LOG:   listening on IPv6 address "::1", port 5432
[27765] LOG: listening on IPv4 address "127.0.0.1", port 5432 [27765]
LOG: listening on Unix socket "/tmp/.s.PGSQL.5432"
[27768] LOG:   database system was shut down at 2023-07-19 07:20:24 EST
[27765] LOG:   database system is ready to accept connections
done
server started
```

> Các command `start`, `stop` và `restart` không hoạt động trên Docker image từ repository của cuốn sách này vì các container đó đang chạy PostgreSQL như main process; do đó, việc stop (hoặc restart) sẽ khiến container thoát. Tương tự, không cần start service vì service được tự động start ngay khi container start.

Command `pg_ctl` launch process postmaster; process này in ra một vài log line trước khi redirect log tới log file phù hợp. Message `server started` ở cuối xác nhận server đã start. Trong quá trình startup, PID của postmaster được báo cáo trong cặp square bracket; trong ví dụ trên, postmaster là operating system process số 27765.

Bây giờ, nếu chạy lại `pg_ctl` để kiểm tra server, bạn sẽ thấy server đã được start:

```text
$ pg_ctl status
pg_ctl: server is running (PID: 27765)
/usr/pgsql-16/bin/postgres
```

Như bạn có thể thấy, server hiện đang running và `pg_ctl` hiển thị PID của postmaster đang chạy (27765), cũng như executable command line (trong trường hợp này là `/usr/pgsql-16/bin/postgres`).

> Nhớ rằng: process postmaster là process đầu tiên được start trong cluster. Cả backend process và postmaster đều được chạy từ executable `postgres`, và postmaster chỉ là root của toàn bộ PostgreSQL process, với mục đích chính là giữ tất cả process khác dưới sự kiểm soát.

Bây giờ cluster đang running, hãy stop cluster. Như bạn có thể hình dung, `stop` là command dùng để chỉ dẫn `pg_ctl` action cần thực hiện:

```text
$ pg_ctl stop
waiting for server to shut down....
[27765] LOG:     received fast shutdown request
[27765] LOG:     aborting any active transactions
[27765] LOG: background worker "logical replication launcher" (PID 27771)
exited with exit code 1
[27766] LOG:     shutting down
[27766] LOG:     checkpoint starting: shutdown immediate
[27766] LOG: checkpoint complete: wrote 0 buffers (0.0%); 0 WAL file(s)
added, 0 removed, 0 recycled; write=0.001 s, sync=0.001 s, total=0.035
s; sync files=0, longest=0.000 s, average=0.000 s; distance=0 kB,
estimate=237 kB; lsn=0/1529DC8, redo lsn=0/1529DC8
[27765] LOG:     database system is shut down
done
server stopped
```

Trong khi shutdown, system in ra một số message để thông báo cho administrator biết chuyện gì đang diễn ra; ngay khi server stop, message `server stopped` xác nhận cluster không còn running.

Shutdown một cluster có thể khó xử lý hơn nhiều so với start cluster, và vì lý do đó, bạn có thể truyền thêm argument cho command `stop` để `pg_ctl` hành động tương ứng.

Có ba cách stop một cluster:

- **smart mode** nghĩa là PostgreSQL cluster sẽ nhẹ nhàng chờ tất cả client đã connect disconnect, rồi mới shutdown cluster.
- **fast mode** sẽ lập tức disconnect mọi client và shutdown server mà không cần chờ.
