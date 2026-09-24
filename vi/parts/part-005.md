Đây là điểm quan trọng cần ghi nhớ: PostgreSQL dựa vào filesystem bên dưới để triển khai persistence, và do đó việc tuning filesystem là một task quan trọng để PostgreSQL hoạt động tốt. Cụ thể, PostgreSQL lưu trữ toàn bộ content của nó (user data và internal status) trong một thư mục filesystem duy nhất có tên là `PGDATA`. Thư mục `PGDATA` đại diện cho tập các database mà cluster đang phục vụ, vì vậy bạn có thể có một installation PostgreSQL duy nhất và chuyển nó sang các thư mục `PGDATA` khác nhau để cung cấp các content khác nhau. Như bạn sẽ thấy trong các section tiếp theo, thư mục `PGDATA` cần được initialize trước khi có thể sử dụng; initialization là việc tạo cấu trúc thư mục bên trong chính `PGDATA` và dĩ nhiên đây là operation chỉ thực hiện một lần.

Nội dung chi tiết của `PGDATA` sẽ được giải thích trong chapter tiếp theo, nhưng hiện tại, bạn chỉ cần nhớ rằng thư mục `PGDATA` là nơi PostgreSQL mong đợi tìm thấy các file dữ liệu và configuration. Cụ thể, thư mục `PGDATA` bao gồm ít nhất Write-Ahead Logs (WALs) và data storage. Nếu thiếu một trong hai phần này, cluster không thể đảm bảo data consistency và trong một số tình huống nghiêm trọng thậm chí còn không thể start.

WALs là một technology được nhiều database system sử dụng, và ý tưởng cơ bản về cách chúng hoạt động được chia sẻ với các technology khác như transactional filesystem (chẳng hạn ZFS, UFS với Soft Updates, v.v.). Ý tưởng là trước khi áp dụng bất kỳ thay đổi nào vào một chunk dữ liệu, một intent log sẽ được ghi persistent. Trong trường hợp này, nếu cluster bị crash, nó luôn có thể dựa vào intent log đã được ghi trước đó để hiểu operation nào đã hoàn tất và operation nào phải được recover (sẽ có thêm chi tiết về việc này trong các chapter sau). Lưu ý rằng với thuật ngữ “crash”, chúng tôi đề cập đến mọi disaster có thể xảy ra với cluster của bạn, bao gồm software bug, nhưng nhiều khả năng hơn là mất điện, hỏng hard disk, v.v. PostgreSQL cam kết cung cấp mức data consistency tốt nhất có thể, vì vậy nó nỗ lực rất nhiều để đảm bảo intent log (WAL) an toàn hết mức có thể.

Ở bên trong, PostgreSQL theo dõi cấu trúc của các table, index, function và mọi thứ cần thiết để quản lý cluster trong storage chuyên dụng của nó, gọi là catalog.

SQL standard định nghĩa một information schema, tức một tập hợp các table dùng chung cho mọi standard database implementation, bao gồm PostgreSQL, mà DBA có thể dùng để kiểm tra internal status của chính database. Ví dụ, information schema định nghĩa một table tập hợp thông tin về tất cả user-defined table, nhờ đó có thể query information schema để xem một table cụ thể có tồn tại hay không. PostgreSQL catalog có thể được gọi là một “information schema on steroids”: catalog chính xác hơn nhiều và đặc thù PostgreSQL hơn information schema tổng quát, đồng thời DBA có thể trích xuất nhiều thông tin hơn về status của PostgreSQL từ catalog. Tất nhiên, PostgreSQL có hỗ trợ information schema, nhưng trong toàn bộ cuốn sách, bạn sẽ thấy các tham chiếu đến catalog vì chúng cung cấp thông tin chi tiết hơn nhiều.

Khi cluster được start, PostgreSQL khởi chạy một process duy nhất gọi là `postmaster`. Mục tiêu của `postmaster` là bootstrap instance, spawn các process cần thiết để quản lý database activity, sau đó chờ các incoming connection. Một user connection, thường được thực hiện qua TCP/IP connection, yêu cầu `postmaster` fork một process khác có tên là backend process; đến lượt nó, process này chịu trách nhiệm phục vụ đúng một connection.

Điều này có nghĩa là mỗi khi một connection mới đến cluster được mở, cluster sẽ phản ứng bằng cách khởi chạy một backend process mới để phục vụ connection đó cho đến khi connection kết thúc và process sau đó bị destroy. `postmaster` thường cũng start một số utility process chịu trách nhiệm giữ cho PostgreSQL hoạt động tốt trong khi đang chạy; các process này sẽ được thảo luận ở phần sau của chapter này và chapter tiếp theo.

Tóm lại, PostgreSQL cung cấp các executable có thể được install ở bất kỳ đâu bạn muốn trên system và có thể serve một cluster duy nhất. Đến lượt mình, cluster phục vụ dữ liệu từ một thư mục `PGDATA` duy nhất, thư mục này chứa, cùng với các thành phần khác, user data, internal status của cluster, catalog và WALs. Mỗi khi một client connect đến server, process `postmaster` fork một backend process mới, process này chịu trách nhiệm phục vụ connection.

Từ các concept đã giải thích ở trên, sau đây là phần recap nhanh về những thuật ngữ phức tạp nhất được sử dụng trong PostgreSQL:

- **Cluster:** toàn bộ PostgreSQL service.
- **Postmaster:** process đầu tiên mà cluster execute; process này chịu trách nhiệm theo dõi activity của toàn bộ cluster. `postmaster` spawn một backend process mỗi khi một connection được thiết lập.
- **Database:** một data container biệt lập mà user (hoặc application) có thể connect vào. Một cluster có thể xử lý nhiều database. Một database có thể bao gồm nhiều object khác nhau, như schema (namespace), table, trigger và các object khác mà bạn sẽ gặp trong quá trình đọc sách.
- **PGDATA:** thư mục trên persistent storage được dành riêng hoàn toàn cho PostgreSQL và dữ liệu của nó. PostgreSQL lưu trữ dữ liệu bên trong thư mục này.
- **WALs:** intent log của các thay đổi trong database, được dùng để recover dữ liệu sau một critical crash.

Sau khi đã thảo luận về terminology cơ bản liên quan đến PostgreSQL, đã đến lúc install nó trên machine của bạn.

## Cài đặt PostgreSQL

PostgreSQL có thể chạy trên nhiều operating system, đáng chú ý nhất là Unix và các Unix-like system, bao gồm Linux, cũng như Microsoft Windows 11 hoặc cao hơn. Cho đến nay, platform được support nhiều nhất vẫn là Linux vì phần lớn PostgreSQL developer làm việc trên platform này, và do đó đây là platform có nhiều use case được test nhất. Tuy nhiên, việc deploy trên các platform được support khác sẽ không gây ra vấn đề nào và không đặt data của bạn vào bất kỳ rủi ro nào.

Section này tập trung vào việc install PostgreSQL 16, vì đây là stable version mới nhất hiện có trên toàn thế giới. Tuy nhiên, bạn cũng sẽ học cách build version PostgreSQL của riêng mình, và đây có thể là cách để bạn install các version khác của PostgreSQL trong tương lai.

Trước khi install PostgreSQL, bạn cần chọn, hoặc ít nhất là đánh giá, cách install nó. Có hai cách chính để đưa PostgreSQL vào trạng thái running:

- Compile từ source
- Sử dụng binary package

Binary package được PostgreSQL community hoặc operating system cung cấp, và việc sử dụng chúng có ưu điểm là giúp bạn có một PostgreSQL installation thuận lợi.

Hơn nữa, binary package không yêu cầu compilation toolchain và do đó dễ áp dụng hơn nhiều. Cuối cùng, binary package tuân theo các convention của operating system mà nó được build cho (ví dụ, convention về vị trí đặt configuration file), và operating system cũng có thể quản lý việc upgrade. Vì binary package cần được vendor build sẵn, chúng có thể không phản ánh release version mới nhất. Ví dụ, khi PGDG cung cấp một minor update mới, operating system cần vài ngày để đưa binary package chứa các upgrade đó ra cho tất cả platform được support.

Mặt khác, việc install từ source yêu cầu compilation toolchain, cũng như tốn nhiều thời gian và CPU hơn để build các PostgreSQL executable. Bạn có toàn quyền kiểm soát những component nào sẽ có trong final product và có thể trim, optimize instance cho performance rất cao cũng như giảm resource consumption xuống mức tối thiểu. Tuy nhiên, về lâu dài, bạn sẽ chịu trách nhiệm maintenance installation và upgrade nó theo cách tương tự.

### Cài đặt gì

PostgreSQL được chia thành một số component để install:

- PostgreSQL server là phần có thể serve database cho application và user, đồng thời bắt buộc phải có để lưu trữ data.
- PostgreSQL client là library và client tool dùng để connect đến database server. Nó không bắt buộc nếu bạn không cần connect đến database trên chính machine đó, nhưng bắt buộc phải có trên client machine.
- PostgreSQL contrib package là một tập hợp các extension và utility phổ biến có thể nâng cao trải nghiệm PostgreSQL của bạn. Package bổ sung này do PGDG phát triển nên được tích hợp tốt và ổn định.
- PostgreSQL docs là documentation (ví dụ, man page) liên quan đến server và client.
- PostgreSQL PL/Perl, PL/Python và PL/Tcl là ba component cho phép sử dụng các programming language tương ứng là Perl, Python và Tcl trực tiếp bên trong PostgreSQL server.

Set component được khuyến nghị là server, client và contrib modules; các module này sẽ được sử dụng xuyên suốt cuốn sách. Bạn có thể tự quyết định có install các component khác hay không, nhưng cuốn sách này sẽ không trình bày chi tiết từng component.

### Cài đặt PostgreSQL từ binary package

Để hiểu rõ hơn các concept được giải thích trong cuốn sách này, chúng tôi khuyến nghị độc giả tự thử các code example; do đó, bạn sẽ cần? một PostgreSQL instance có sẵn. Mặc dù lựa chọn tốt nhất để có một PostgreSQL instance đầy đủ trong tầm tay là install nó trên virtual machine hoặc physical computer, chúng tôi cũng cung cấp một tập Docker image dưới dạng các PostgreSQL instance containerized để chạy và thử nghiệm. Vì vậy, bạn có thể chọn thực hiện full installation hoặc thiết lập Docker nhanh để có một PostgreSQL machine sẵn sàng. Tuy nhiên, mọi DBA đều cần có khả năng install PostgreSQL trên nhiều system, vì vậy section này nhằm chỉ cho bạn cách thực hiện một installation hoàn chỉnh từ đầu trên một số Unix-like operating system.

Trong các section sau, bạn sẽ thấy cách install PostgreSQL trên một số Linux và Unix operating system phổ biến, cụ thể là:

- Linux Docker containers
- GNU/Linux Debian, Ubuntu và derivative
- Fedora Linux (điều này cũng áp dụng cho Red Hat Enterprise Linux và các distribution tương thích, như Rocky Linux)
- FreeBSD

Không thể cung cấp instruction chi tiết cho mọi operating system hiện có, nhưng các concept được trình bày trong những section sau sẽ hữu ích bất kể platform nào.

Trước khi đi vào phần installation thực tế, cần lưu ý rằng binary package có thể thuộc một trong hai loại: loại do operating system vendor cung cấp và loại do PGDG cung cấp. Thông thường, trên các system dựa trên Linux, bạn nên sử dụng binary package do PGDG cung cấp vì đây là source có thẩm quyền nhất đối với PostgreSQL. Trên thực tế, package do operating system vendor cung cấp có xu hướng nhanh chóng trở nên out of date, nghĩa là chúng thường chậm hơn latest version hiện có trên toàn cầu vài version. Mặt khác, trên các BSD platform như FreeBSD, OpenBSD và NetBSD, các operating system porter làm rất tốt việc giữ cho package do chính operating system cung cấp luôn up to date, vì vậy bạn có thể sử dụng operating system package một cách an toàn và dễ dàng.

Một điều quan trọng cần lưu ý là các operating system khác nhau lưu file ở những vị trí khác nhau: thông thường, tất cả configuration file được đặt ngay trong `PGDATA`, nhưng package của một số operating system phân tán configuration file dưới thư mục `/etc`. Một số operating system cũng đặt executable trong các path cụ thể, tách biệt theo PostgreSQL version, trong khi các system khác đặt tất cả executable trong cùng một path.

Bạn cần tìm hiểu với package provider của operating system xem từng file hoặc directory được đặt ở đâu để có thể configure và sử dụng PostgreSQL.

#### Sử dụng Docker image của cuốn sách

Docker là một container cho phép bạn chạy một tập process biệt lập như thể chúng là một phần của một micro virtual machine. PGDG cung cấp một Docker image mà bạn có thể dùng để chạy một cluster containerized.

Giải thích về Docker technology nằm ngoài phạm vi của cuốn sách này, và để bạn có thể nhanh chóng, dễ dàng thử nghiệm với PostgreSQL, chúng tôi đã cung cấp một tập Docker image dựa trên PostgreSQL image, được customize để bạn thử nghiệm các concept được giải thích trong cuốn sách. Bạn có thể dùng các image nói trên làm điểm khởi đầu cho project của riêng mình, dù các image này không nhằm sử dụng trong production environment. Các image nằm trong directory `docker_images` của code repository của cuốn sách (https://github.com/PacktPublishing/Learn-PostgreSQL-Second-Edition/).

Chúng tôi tách từng Docker image theo chapter mà image đó phục vụ. Có một image catch-all dùng tên `standalone`, có thể được dùng làm base chung và sẽ được sử dụng trong những chapter đầu tiên. Các chapter khác, chẳng hạn chapter về replication, yêu cầu image riêng để chạy.

Để start base image `standalone`, bạn chỉ cần execute shell script `run-pg-docker.sh` như sau:

```text
$ sh run-pg-docker.sh
…
postgres@learn_postgresql:~$
```

Script sẽ yêu cầu bạn nhập password; user của bạn bắt buộc phải có sudo capability để connect Docker network và port. Tất cả container sẽ khởi chạy một GNU Bash session với operating system user `postgres`.

Lần đầu mỗi container được start, quá trình này sẽ mất một khoảng thời gian vì nó cần pull PostgreSQL image từ network, install các package cần thiết và configure image. Cuối cùng, system sẽ đưa bạn đến Bash prompt; lúc này bạn đã đăng nhập qua container với user `postgres` và có thể bắt đầu tương tác với system theo các example trong cuốn sách.

Trong mỗi container, thư mục `PGDATA` được đặt là `/postgres/16/data`.

Sau khi bạn thoát khỏi shell của container, container sẽ stop và sẽ không còn process nào liên quan đến PostgreSQL active.

Để start một image riêng cho từng chapter, bạn có thể dùng cùng script và chỉ định folder của chapter làm argument, ví dụ:

```text
$ sh run-pg-docker.sh chapter_12_extensions
```

Mỗi container sẽ start với một PostgreSQL instance được pre-populate, nhờ đó bạn có thể dễ dàng làm theo các code example trong từng chapter.

> **Note:** Có thể có một số khác biệt giữa output bạn thấy trong các code example và output nhận được khi execute cùng command trong Docker container. Ví dụ, các giá trị được generate tự động và số lượng tuple có thể khác nhau, cũng như timestamp và date. Hơn nữa, mỗi Docker container sẽ lưu data trong một disk directory riêng, do đó nếu bạn thao tác với content của PostgreSQL instance containerized, lần tiếp theo bạn start container, các thay đổi của bạn sẽ vẫn được persist.

#### Cài đặt PostgreSQL trên GNU/Linux Debian, Ubuntu và derivative

PGDG cung cấp binary package cho Debian và các derivative của nó, bao gồm họ operating system Ubuntu. Để sử dụng PGDG repository, trước tiên bạn cần install source và signature của repository:

```text
$ sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'

$ wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc |
sudo apt-key add -

$ sudo apt-get update
```

Điều này đảm bảo repository source cho operating system của bạn được up to date để bạn có thể install PostgreSQL package:

```text
$ sudo apt-get -y install postgresql
```

Debian và Ubuntu cung cấp command riêng để control cluster, `pg_ctlcluster(1)`. Lý do là trên operating system Debian/Ubuntu, mỗi PostgreSQL version được install trong directory riêng với các configuration file riêng, nhờ đó có thể chạy đồng thời các version khác nhau và quản lý chúng thông qua operating system. Ví dụ, configuration file nằm dưới directory `/etc/postgresql/16/main`, còn data directory mặc định được đặt tại `/var/lib/postgresql/16/main`.

Nếu muốn enable PostgreSQL khi boot, bạn cần chạy command sau:

```text
$ sudo update-rc.d postgresql enable
```

Để start cluster, bạn có thể sử dụng command `service(1)` như sau:

```text
$ sudo service postgresql start
```

Như vậy, bạn đã install PostgreSQL trên GNU/Linux Debian, Ubuntu và các derivative.

#### Cài đặt PostgreSQL trên Fedora Linux

PostgreSQL package cho Fedora Linux do PostgreSQL community cung cấp. Để cho phép `dnf(8)` tìm PostgreSQL package, bạn cần install PGDG repository, sau đó tiếp tục installation dưới dạng distribution package:

```text
$ sudo dnf install -y https://download.postgresql.org/pub/repos/yum/reporpms/F-38-x86_64/pgdg-fedora-repo-latest.noarch.rpm
```

Danh sách repository có sẵn có thể được lấy từ official website của PostgreSQL, tại download page (xem section References).

Package được đặt tên với postfix là version number. Bạn có thể install PostgreSQL package bằng command sau:

```text
$ sudo dnf install -y postgresql16-server postgresql16
```

Sau đó, bạn cần configure system, chỉ định directory `PGDATA` và enable option start service khi boot. Để chỉ định directory `PGDATA`, bạn cần dùng `systemd(1)` để edit overriding configuration file cho service `postgresql-16`:

```text
$ sudo systemctl edit postgresql-16
```

Command trước đó sẽ mở text editor mặc định với một file rỗng; do đó, bạn có thể set biến `PGDATA` như sau rồi save và exit editor để áp dụng thay đổi:

```text
[Service]
Environment=PGDATA=/postgres/16/data
```

Cuối cùng, đã đến lúc initialize database directory; việc này có thể thực hiện bằng một installation command cụ thể của Fedora có tên `postgresql-16-setup`, như sau:

```text
$ sudo /usr/pgsql-16/bin/postgresql-16-setup initdb
```

Để enable PostgreSQL start khi boot và launch server ngay lập tức, bạn có thể execute các command sau:

```text
$ sudo systemctl enable postgresql-16

$ sudo systemctl start postgresql-16.service
```

Nếu Fedora installation của bạn có command `service(8)`, bạn cũng có thể start service bằng command sau:

```text
$ sudo service postgresql-16 start
```

#### Cài đặt PostgreSQL trên FreeBSD

PostgreSQL có sẵn trên FreeBSD thông qua ports và package. Nhờ command `pkg(1)`, việc install PostgreSQL rất dễ dàng. Trước hết, hãy update package list và search các PostgreSQL package được đặt tên với major version làm postfix:

```text
$ pkg update
$ pkg search postgresql16
```

Sau đó bạn có thể install package bằng cách execute `pkg(1)` và chỉ định tập package cần dùng. Tất nhiên, installation phải được execute bởi user có administrative privilege, như sau:

```text
   $ sudo pkg install     postgresql16-server-16.0         \
                             postgresql16-client-16.0         \
                             postgresql16-contrib-16.0 \
                             postgresql16-docs-16.0
```

Để start cluster, bạn cần initialize directory dùng để serve database và enable server startup khi machine boot. Các parameter tối thiểu cần set là `postgresql_enable` và `postgresql_data`.

Ví dụ, để edit file `/etc/rc.conf` (với tư cách administrative user), hãy thêm các option như sau:

```text
# to enable PostgreSQL at boot time
postgresql_enable="YES"

# PGDATA to use
postgresql_data="/postgres/16/data"
```

Bây giờ bạn có thể initialize data directory bằng command sau:

```text
$ sudo /usr/local/etc/rc.d/postgresql initdb
```

Giờ mọi thứ đã sẵn sàng, bạn có thể start PostgreSQL instance bằng command sau:

```text
$ sudo service postgresql start
```

### Cài đặt PostgreSQL từ source

Việc install PostgreSQL từ source yêu cầu download một tarball, tức một compressed package chứa toàn bộ source code file, rồi bắt đầu compilation. Thông thường, quá trình này mất vài phút, tùy thuộc vào power của machine và I/O bandwidth. Để compile PostgreSQL từ source, bạn sẽ cần nhiều tool và library khác nhau, chủ yếu là một C compiler tương thích với standard C99 (hoặc cao hơn). Thông thường, bạn đã có sẵn các tool này trên Linux hoặc Unix system; nếu không, hãy tham khảo documentation của operating system để biết cách install chúng.

Sau khi đã install tất cả dependency, hãy làm theo các step dưới đây để compile và install PostgreSQL:

1. Step đầu tiên là download PostgreSQL tarball tương ứng với version bạn muốn install và xác minh rằng nó chính xác. Ví dụ, để download version 16.0, bạn có thể làm như sau:

   ```text
   $ wget https://ftp.postgresql.org/pub/source/v16.0/postgresql-16.0.tar.bz2
   ...
   $ wget https://ftp.postgresql.org/pub/source/v16.0/postgresql-16.0.tar.bz2.md5
   ```

2. Trước khi bắt đầu compilation, hãy kiểm tra rằng tarball đã download còn nguyên vẹn:

   ```text
   $ md5sum --check postgresql-16.0.tar.bz2.md5
   postgresql-16.0.tar.bz2: OK
   ```
