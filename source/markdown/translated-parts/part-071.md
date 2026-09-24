Có rất nhiều tool khác, và tại https://wiki.postgresql.org/wiki/Binary_Replication_Tools, bạn có thể tìm thấy một phần so sánh khá tốt về tất cả chúng.

Trong section này, chúng ta sẽ đề cập ngắn đến `pgbackrest`; đây là một trong những tool được sử dụng nhiều nhất cho disaster recovery vì nó cho phép scale trên các core theo cách rất đơn giản, đồng thời cho phép lưu data vào các bucket dưới dạng compressed và encrypted. Tool `pgbackrest` là một tool dành cho PostgreSQL disaster recovery và PITR, được thiết kế cho các server có tải lớn. URL chính thức của nó là https://pgbackrest.org/.

Sau đây là một số feature của tool này:

- Hỗ trợ parallel backup và parallel restore.
- Có thể tạo full base backup, incremental backup hoặc differential backup.
- Có thể chọn thực hiện các operation local hoặc remote.
- Có thể chọn policy retention cho backup và archive expiration.
- Hỗ trợ resume backup.
- Hỗ trợ streaming compression và checksum.
- Khi thực hiện restore, có thể sử dụng delta restore.
- Có thể sử dụng parallel WAL archiving.
- Hỗ trợ tablespace và link.
- Hỗ trợ data encryption.
- Hỗ trợ SFTP cho repository storage.
- Hỗ trợ object store storage cho S3, GCP và Azure.

## Các khái niệm cơ bản

Tool `pgbackrest` sử dụng khái niệm stanza, và có thể dùng một repository local hoặc một repository external:

- Stanza là một configuration của một remote server cho backup. Đây là một tập các target cần được backup. Một stanza configuration có thể chứa nhiều server; trong trường hợp đó, server đầu tiên (`pg1`) là master, còn các server khác được xem là standby server.
- Repository là storage local hoặc remote (SSH), nơi các backup được lưu; repository có thể được encrypted. Một repository có thể chứa nhiều definition, nhưng hiện tại chỉ definition đầu tiên (`repo1`) được hỗ trợ.
- Điều quan trọng là phải có public key exchange giữa những user sử dụng `pgbackrest`. Cách đơn giản nhất là exchange public key giữa Postgres user của PostgreSQL server và Postgres user của server nơi đặt `pgbackrest` repository.

## Thiết lập environment

Trong section này không có Docker container, vì vậy trước khi bắt đầu và test tool `pgbackrest`, hãy xem chúng ta cần gì để bắt đầu làm việc. Chúng ta sẽ cần:

- Một PostgreSQL server đang chạy.
- Một server nơi chúng ta sẽ install và configure tool `pgbackrest` cùng với một postgres user.

Trong scenario này, chúng ta sẽ tiếp tục sử dụng PostgreSQL server `pg1` với `ip= 192.168.122.170`. Chúng ta cũng cần thêm một server khác có tên `pgbackrest` với IP address `192.168.122.120`.

## Exchange public key

Bây giờ chúng ta sẽ xem cách exchange public key trước khi install `pgbackrest`:

1. Trước hết, hãy tạo một ssh key cho Postgres user trên cả hai server. Với tư cách PostgreSQL user, hãy thực thi:

   ```text
   postgres@pgbackrest:~$ ssh-keygen -t rsa -b 4096
   Generating public/private rsa key pair.
   Enter file in which to save the key (/home/postgres/.ssh/id_rsa):
   Created directory '/home/postgres/.ssh'.
   Enter passphrase (empty for no passphrase):
   Enter same passphrase again:
   Your identification has been saved in /home/postgres/.ssh/id_rsa
   Your public key has been saved in /home/postgres/.ssh/id_rsa.pub
   The key fingerprint is:
   SHA256:5BPkarhop6Z82WeWWtYM1i5gHseFHAVJEoKy8GFSHjQ postgres@
   pgbackrest
   The key's randomart image is:
   +---[RSA 4096]----+
   | oE. oo+=.         |
   |+ooo. o+o          |
   |o=..     o+.       |
   |. .    ..+o.       |
   |      .+o=S.         |
   |    .oo= =.          |
   |   o =. +.+          |
   |...= .o=.            |
    |.+o    .=            |
    +----[SHA256]-----+
    ```

    ```text
    postgres@pg1:~$ ssh-keygen -t rsa -b 4096
    Generating public/private rsa key pair.
    Enter file in which to save the key (/home/postgres/.ssh/id_rsa):
    Created directory '/home/postgres/.ssh'.
    Enter passphrase (empty for no passphrase):
    Enter same passphrase again:
    Your identification has been saved in /home/postgres/.ssh/id_rsa
    Your public key has been saved in /home/postgres/.ssh/id_rsa.pub
    The key fingerprint is:
    SHA256:g/amWaxcTGsmx2WQ91U/23UcBXmDtSsfRYhqE7dMWko postgres@pg1
    The key's randomart image is:
    +---[RSA 4096]----+
    |                 .+*=|
    |             .E =.o==|
    |            o..X ..+B|
    |         . o*.o.    O|
    |        o S.o... +.|
    |       . * =      o .|
    |        . &        . |
    |       . %           |
    |        =            |
    +----[SHA256]-----+
    ```

    Trên cả hai server, khi thực thi command `ssh-keygen`, chúng ta phải chỉ nhấn phím *Enter* khi được yêu cầu nhập passphrase.

2. Bây giờ, trên cả hai server, trong directory `~/.ssh` của postgres user sẽ có hai file:

   ```text
   postgres@pgbackrest:~/.ssh$ ls -l
   total 8
   -rw------- 1 postgres postgres 3389 Jul 10 08:34 id_rsa
   -rw-r--r-- 1 postgres postgres         745 Jul 10 08:34 id_rsa.pub
   ```

   ```text
   postgres@pg1:~/.ssh$ ls -l
   total 8
   -rw------- 1 postgres postgres 3381 Jul 10 08:34 id_rsa
   -rw-r--r-- 1 postgres postgres       738 Jul 10 08:34 id_rsa.pub
   ```

3. Cách nhanh nhất để exchange public key giữa hai server là sử dụng command `ssh-copy-id`:

   ```text
   postgres@pg1:~/.ssh$ ssh-copy-id 192.168.122.120
   [.. cutted..]
   Number of key(s) added: 1


   Now try logging into the machine, with:          "ssh '192.168.122.120'"
   and check to make sure that only the key(s) you wanted were added.

   postgres@pgbackrest:~/.ssh$ ssh-copy-id 192.168.122.170
   [.. cutted..]

   Number of key(s) added: 1

   Now try logging into the machine, with:  "ssh '192.168.122.170'"
   and check to make sure that only the key(s) you wanted were added
   ```

Bây giờ, bằng postgres user, có thể connect hai server với nhau mà không cần cung cấp password.

## Install pgbackrest

Trước khi install, chúng ta phải kiểm tra xem trong repository của mỗi host có cùng version `pgbackrest` hay không. Sau khi kiểm tra, hãy install nó trên server `pgbackrest` và server `pg1`. Trên một server kiểu Debian, với tư cách root user, hãy thực thi các command sau trên cả hai server:

```text
root@pg1:~# apt-get update
root@pgbackrest:~# apt-get update


root@pg1:~# apt-get install pgbackrest
root@pgbackrest:~# apt-get install pgbackrest
```

Nếu sử dụng RHEL server, chúng ta phải sử dụng command `yum` thay cho command `apt-get`.

## Configure pgbackrest

Bây giờ hãy xem cách configure tool `pgbackrest`. Nó cần configuration trên cả hai server; cần configuration của repository server, nơi data sẽ được lưu, và cần configuration của PostgreSQL server để server này có thể gửi toàn bộ data đến repository server. Vì vậy, chúng ta sẽ lần lượt xử lý cả hai configuration:

- Repository configuration của server `pgbackrest`.
- PostgreSQL configuration của server `pg1`.

## Repository configuration

Configuration file của server `pgbackrest` nằm ở đây:

```text
/etc/pgbackrest.conf
```

Có thể sử dụng một configuration file khác, nhưng phải chỉ định file đó nhất quán trong mỗi lần sử dụng program, vì vậy tốt hơn là để file mặc định. Mỗi parameter được chỉ định trong configuration file có thể bị override bởi parameter tương ứng được cung cấp trên command line. Mỗi parameter nằm trong một section được chỉ định bằng một key-value pair. Trong stanza configuration, các parameter của một cluster luôn bắt đầu bằng `pgN-`, trong đó N là một số tăng dần. Cluster chính (primary) luôn là số 1. Do đó, các standby cluster được đánh số tuần tự, bắt đầu từ số 2. Tương tự, trong global parameter, repository được đánh số bắt đầu từ 1 (`repo1`), nhưng hiện tại multiple repository không được hỗ trợ. `pgbackrest` có tính symmetric; nghĩa là mọi command đều có thể được thực thi trên backup machine hoặc target machine. Chúng ta sẽ có một configuration file cho repository server và một configuration file cho PostgreSQL server, và hai configuration file này khác nhau. Theo mặc định, `pgbackrest` đã bật compression cho WAL segment và base backup với compression factor bằng 6. Chúng ta có thể ép compression dùng level khác bằng directive `compress-level`; ví dụ, có thể đặt compression level bằng 9 để có compression tối đa.

Cũng có thể encrypt repository do `pgbackrest` quản lý; feature này hữu ích, chẳng hạn khi lưu backup trên một cloud có chi phí thấp.

Bây giờ hãy bắt đầu với một configuration đơn giản; trước hết là global configuration section trên server `pgbackrest`:

```text
[global]
start-fast=y
archive-async=y
process-max=2
repo-path=/var/lib/pgbackrest
repo1-retention-full=2
repo1-retention-archive=5
repo1-retention-diff=3
log-level-console=info
log-level-file=info
```

Các option ở đây có ý nghĩa như sau:

- `start-fast=y`: Ép một checkpoint trên remote server, để `pg_start_backup ()` bắt đầu sớm nhất có thể.
- `archive-async=y`: Bật việc transfer WAL bất đồng bộ cho operation push/pull.
- `process-max=2`: Đặt số process tối đa mà system có thể sử dụng cho operation transfer/compression.
- `repo-path=/var/lib/pgbackrest`: Đặt path nơi repository sẽ được lưu; user chạy command `pgbackrest` phải có quyền read/write trên directory này.
- `repo1-retention-full=2`: Số full backup cần giữ lại. Khi một full backup hết hạn, tất cả differential và/hoặc incremental backup gắn với full backup đó cũng hết hạn. Nếu option này không được định nghĩa, system sẽ phát warning. Nếu muốn retention vô thời hạn, hãy đặt option này bằng giá trị tối đa (9,999,999).
- `repo1-retention-archive=5`: Đại diện cho số WAL file của backup cần giữ lại. Các WAL segment cần thiết để tạo một backup nhất quán luôn được giữ cho đến khi backup hết hạn, bất kể configuration của option này. Nếu không đặt giá trị này, archive sắp hết hạn sẽ tự động hết hạn ở giá trị `repo-retention-full` (hoặc `repo-retention-diff`) tương ứng với loại `repo-retention archive`, nếu được đặt thành `full` (hoặc `diff`). Điều này bảo đảm WAL file chỉ được xem là hết hạn đối với những backup đã hết hạn.
- `repo1-retention-diff = 3`: Số differential backup cần giữ lại. Khi một differential backup hết hạn, tất cả incremental backup gắn với differential backup đó cũng hết hạn. Nếu không được định nghĩa, mọi differential backup sẽ được giữ cho đến khi các full backup mà chúng phụ thuộc vào hết hạn.
- `log-level-console=info/log-level-file=info log`: Các thiết lập để quản lý log; đặt log level trên terminal (`log-level-console`) và logging level trong log file (`log-level-file`).

Configuration file ở trên chỉ là một ví dụ đơn giản; nếu muốn thêm feature, chúng ta chỉ cần thêm chúng vào configuration file.

Ví dụ, nếu muốn thay đổi compression level và tăng lên level 9, có thể thêm các dòng sau:

```text
compress = y
compress-level = 9
compress-level-network = 9
```

Tương tự, nếu muốn thêm cipher feature, có thể thêm các dòng sau:

```text
repo1-cipher-type = aes-256-cbc
repo1-cipher-pass = LearnPostgreSQL
```

Sau khi configure global section, chúng ta đã sẵn sàng xem cách configure stanza. `pgbackrest` đưa vào khái niệm stanza; trên thực tế, chúng ta có thể liên kết mỗi stanza với một database cluster. Sau đây là một ví dụ về một room; việc tên của stanza, `[pg1]`, trùng với tên cluster chỉ là sự trùng hợp. Cần tạo một stanza cho mỗi remote PostgreSQL server mà chúng ta muốn quản lý backup bằng `pgbackrest`. Mỗi stanza phải có một tên khác nhau:

```text
[pg1]
pg1-host = 192.168.122.170
pg1-host-user = postgres
pg1-path = /var/lib/postgresql/16/main
pg1-port = 5432
```

Các option ở đây có ý nghĩa như sau:

- `pg1-host`: Đây là remote host của PostgreSQL master server.
- `pg1-host-user = postgres`: Khi parameter `pg-host` được đặt, đây là user mà chúng ta muốn sử dụng để truy cập remote PostgreSQL server. User này cũng sẽ là owner của remote `pgbackrest` process và process này khởi tạo connection đến PostgreSQL server. User này nên là owner của PostgreSQL database cluster. Thông thường, có thể để user mặc định là postgres, đó là lý do nó thường là user mà chúng ta đã exchange public key.
- `pg1-path = /var/lib/postgresql/16/main`: Path trên PostgreSQL cluster nơi data được lưu. Có thể tìm thấy path này trong parameter `data_directory` bên trong file `postgresql.conf`.
- `pg1-port = 5432`: Listen port của remote PostgreSQL server.

## Sử dụng pgbackrest với object store support

`pgbackrest` hỗ trợ object store cho Azure, GCP và Amazon S3; điều đó có nghĩa là `pgbackrest` có thể lưu toàn bộ data trực tiếp vào một bucket có chi phí thấp, sử dụng data encryption mà chúng ta đã thấy trước đó.

Configuration khá đơn giản; ví dụ, đối với một GCP bucket, chúng ta phải chỉ định các parameter sau:

```text
repo1-type=gcs
repo1-path=/path_on the bucket
repo1-gcs-bucket=bucket_name
repo1-gcs-key=/etc/pgbackrest-key.json
```

Khi thêm các parameter đó, `pgbackrest` sẽ có thể lưu toàn bộ data vào một Google bucket; feature này rất hữu ích cho DBA vì cho phép chúng ta lưu và encrypt data trên cloud với chi phí thấp.

Bằng cách này, chúng ta không phải lo về kích thước disk chứa repository được `pgbackrest` sử dụng; đồng thời, vì chi phí trên mỗi GB của bucket rất thấp, chúng ta có thể tăng retention đáng kể. Để biết thêm thông tin về configuration `pgbackrest` với bucket S3, Azure và GCP, bạn có thể truy cập các link dưới đây:

- https://pgbackrest.org/user-guide.html#azure-support
- https://pgbackrest.org/user-guide.html#s3-support
- https://pgbackrest.org/user-guide.html#gcs-support

## PostgreSQL server configuration

Bây giờ hãy chuyển sang PostgreSQL server configuration. Trên server `pg1`, chúng ta cần sửa file `postgresql.conf` và cũng cần thiết lập file `pgbackrest.conf`.

## File postgresql.conf

Đối với file `postgresql.conf`, chúng ta phải đặt `wal_level` thành `replica` hoặc `logical`. Điều quan trọng là WAL level không được đặt thành `minimal`, vì PITR không thể thực hiện nếu `wal_level=minimal`. Chúng ta cũng cần cho PostgreSQL biết command sẽ gửi WAL segment đến repository server của `pgbackrest`.

Hãy thêm các dòng sau vào cuối file `postgresql.conf`:

```text
#PGBACKREST
archive_mode = on
wal_level = replica #logical if we have some logical replications
archive_command = 'pgbackrest --stanza=pg1 archive-push %p'
```

Với dòng thứ hai, chúng ta nói cho PostgreSQL biết rằng các WAL segment sẽ được archive vào stanza `pg1` của repository server bằng command `pgbackrest`. Sau khi restart PostgreSQL, các dòng mới này sẽ có hiệu lực. Với tư cách root user, hãy restart PostgreSQL service:

```text
# systemctl restart postgresql
```

## File pgbackrest.conf

Bây giờ, sau khi sửa `postgresql.conf`, hãy sửa file `pgbackrest.conf` của PostgreSQL server. Hãy nhớ rằng PostgreSQL server có `ip= 192.168.122.170`, còn IP của disaster recovery server là `192.168.122.170`. Bây giờ hãy edit file `/etc/pgbackrest.conf`; xóa nội dung hiện có và thêm các dòng sau:

```text
[global]
backup-host=192.168.122.120
backup-user=postgres
backup-ssh-port=22
log-level-console=info
log-level-file=info

[pg1]
pg1-path = /var/lib/postgresql/16/main
pg1-port = 5432
```

Giống repository configuration, file này gồm các section: một global section và một section cho mỗi stanza.

Đối với global section, chúng ta có các option sau:

- `backup-host`: Repository host.
- `backup-user`: User được sử dụng cho backup.
- `backup-ssh-port`: SSH port.
- `log-level-console=info` và `log-level-file=info`: Như đã thấy trong section trước.

Đối với stanza section, chúng ta có các option sau:

- `pg1-path = /var/lib/postgresql/16/main`: Path trên PostgreSQL cluster nơi data được lưu. Có thể tìm thấy path này trong parameter `data_directory` bên trong file `postgresql.conf`.
- `pg1-port = 5432`: Listen port của remote PostgreSQL server.

## Tạo và quản lý continuous backup

Bây giờ system đã được configure tốt, hãy bắt đầu quản lý backup.

## Tạo stanza

Việc đầu tiên cần làm là tạo stanza trên repository server. Để thực hiện việc này, với tư cách postgres user, hãy chạy command sau:

```text
postgres@pgbackrest:~$ pgbackrest --stanza=pg1 stanza-create
2023-07-11 08:34:48.439 P00   INFO: stanza-create command begin 2.46:
--compress-level-network=9 --exec-id=2602-fbad976e --log-level-
console=info --log-level-file=info --pg1-host=192.168.122.170 --pg1-host-
user=postgres --pg1-path=/var/lib/postgresql/16/main --pg1-port=5432
--repo1-cipher-pass=<redacted> --repo1-cipher-type=aes-256-cbc --repo1-
path=/var/lib/pgbackrest --stanza=pg1
2023-07-11 08:34:49.558 P00           INFO: stanza-create for stanza 'pg1' on
repo1
2023-07-11 08:34:49.741 P00           INFO: stanza-create command end: completed
successfully (1305ms)
```

Bây giờ stanza đã được tạo. Nếu đi đến `/var/lib/pgbackrest`, chúng ta có thể thấy directory structure sẽ được continuous backup system sử dụng:

```text
postgres@pgbackrest:/var/lib/pgbackrest$ ls -l
total 8
drwxr-x--- 3 postgres postgres 4096 Jul 11 08:34 archive
drwxr-x--- 3 postgres postgres 4096 Jul 11 08:34 backup
```

## Kiểm tra stanza

Sau khi tạo stanza, hãy kiểm tra system đã sẵn sàng nhận continuous backup hay chưa bằng cách thực hiện:

```text
postgres@pgbackrest:~$ pgbackrest --stanza=pg1 check
