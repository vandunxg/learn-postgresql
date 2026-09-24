> Function `get_max()` là một function PL/PgSQL đơn giản được cài đặt trong Docker container của chapter này và chỉ được dùng để minh họa rằng PostgreSQL đủ thông minh để xóa mọi object phụ thuộc khi drop một extension.

Tóm lại, bạn đã học cách quản lý một extension theo cách thủ công, từ cài đặt đến upgrade hoặc xóa nó; trong section tiếp theo, bạn sẽ học cách thực hiện các bước tương tự theo cách tự động hơn.

## Khám phá PGXN client

PGXN client là một application bên ngoài, được viết bằng Python, hoạt động như một command-line interface cho PGXN. Application này có tên `pgxnclient`, hoạt động thông qua các command, là những action như install, download, uninstall, v.v., cho phép database administrator tương tác với PGXN và các extension.

> Ở một mức độ nào đó, `pgxnclient` hoạt động giống command `cpan` (hoặc `cpanm`) dành cho Perl, `zef` dành cho Raku, `pip` dành cho Python, v.v.
>
> Vì là một application bên ngoài, `pgxnclient` không được phân phối cùng PostgreSQL, do đó bạn cần cài đặt nó trên machine trước khi có thể sử dụng. Việc cài đặt `pgxnclient` không bắt buộc để sử dụng các PostgreSQL extension, nhưng có thể giúp công việc của bạn dễ dàng hơn nhiều.

Trong các subsection tiếp theo, bạn sẽ thấy cách cài đặt `pgxnclient` trên các operating system Unix và Unix-like chính, nhưng trước hết, điều quan trọng là bạn cần biết rằng sau khi được cài đặt, bạn sẽ tìm thấy hai executable trên system: `pgxn` và `pgxnclient`. Bạn có thể xem chúng như alias của nhau, dù điều này không hoàn toàn đúng (một cái bọc cái kia); tuy nhiên, bạn có thể dùng bất kỳ executable nào mình muốn và nhận được cùng một kết quả. Trong chapter này, chúng ta sẽ dùng `pgxn` làm executable chính.

> Trong các Docker image của repository cuốn sách, program `pgxnclient` đã được cài đặt sẵn, nên bạn không cần cài đặt nó.
>
> Hướng dẫn chi tiết về cách cài đặt `pgxnclient` nằm ngoài phạm vi của cuốn sách này; vì vậy nếu bạn không thể làm cho application hoạt động đúng, hãy kiểm tra lại documentation của project và hướng dẫn cài đặt.

## Cài đặt pgxnclient trên Debian GNU/Linux và các derivative

`pgxnclient` được đóng gói cho Debian GNU/Linux và các derivative, nghĩa là bạn chỉ cần yêu cầu `apt` cài đặt nó:

```text
$ sudo apt install pgxnclient
```

Sau khi program được cài đặt, bạn có thể test nó bằng option `--version`, option này sẽ in ra version number mà bạn đã cài đặt:

```text
$ pgxn --version
pgxnclient 1.3.2
```

## Cài đặt pgxnclient trên Fedora Linux và các distribution dựa trên Red Hat

`pgxnclient` cũng được đóng gói cho Fedora, vì vậy bạn có thể cài đặt nó bằng package manager của operating system:

```text
$ sudo dnf install -y pgxnclient
```

Sau khi process hoàn tất, bạn có thể query application để xác minh rằng nó thực sự hoạt động:

```text
$ pgxn --version
pgxnclient 1.3.2
```

## Cài đặt pgxnclient trên FreeBSD

`pgxnclient` được đóng gói cho FreeBSD, vì vậy bạn có thể cài đặt nó thông qua tool `pkg` hoặc software port. Cách nhanh nhất là dùng `pkg`; tất cả những gì bạn cần làm là yêu cầu cài đặt program:

```text
$ sudo pkg install --yes pgxnclient
```

## Cài đặt pgxnclient từ source

Bạn luôn có thể cài đặt `pgxnclient` từ source, dù cách này chỉ được đề xuất khi bạn đang dùng một operating system không cung cấp version được đóng gói, hoặc version hiện tại đã quá cũ so với nhu cầu của bạn. Bạn có thể download version nén của release mới nhất từ repository GitHub chính thức của project, chẳng hạn:

```text
$ wget https://github.com/pgxn/pgxnclient/archive/refs/tags/v1.3.2.zip
```

Sau khi có compressed archive, bạn cần decompress nó và đi vào directory sẽ được tạo ra, directory này được đặt tên theo version của PXGN mà bạn đã download, trong trường hợp của chúng ta là `pgxnclient-3.1.2`. Khi đã ở trong directory, việc thực thi Python script `setup.py` sẽ cho phép bạn cài đặt application:

```text
$ unzip v1.3.2.zip
$ cd pgxnclient-1.3.2
$ sudo python setup.py install
...
Finished processing dependencies for pgxnclient==1.3.2
```

Sau khi hoàn tất việc cài đặt, bạn có thể query application để xác minh rằng nó đang hoạt động:

```text
$ pgxn --version
pgxnclient 1.3.2
```

## Command-line interface của pgxnclient

PGXN client application cung cấp một command-line interface tương tự các application dựa trên command khác, chẳng hạn như `cpanm` và `git`. Bạn có thể lấy danh sách các command chính bằng cách yêu cầu trợ giúp:

```text
$ pgxn help
usage: pgxn [--version] [--help] COMMAND ...


Interact with the PostgreSQL Extension Network (PGXN).


optional arguments:
   --version     print the version number and exit
   --help        show this help message and exit


available commands:
   COMMAND       the command to execute. The complete list is available using
                 'pgxn help --all'. Builtin commands are:
      check      run a distribution's test
      download
                 download a distribution from the network
      help       display help and other program information
      info       print information about a distribution
      install    download, build and install a distribution
      load       load a distribution's extensions into a database
      mirror      return information about the available mirrors
      search      search in the available extensions
      uninstall
                 remove a distribution from the system
      unload      unload a distribution's extensions from a database
```

Thông thường, bạn sẽ dùng tập con command sau:

- `search` để search distribution bằng keyword
- `info` để xem xét kỹ hơn một extension
- `download` để download (nhưng không install) một extension
- `install` để download và install một extension vào cluster
- `load` để thực thi `CREATE EXTENSION` trên một database cụ thể
- `unload` để thực thi `DROP EXTENSION` trên một database cụ thể
- `uninstall` để xóa một extension khỏi cluster

Tập command nhỏ nhất mà có lẽ bạn sẽ dùng là `search`, `install` và `uninstall`.

Với mỗi command, bạn có thể nhận được help chi tiết hơn nếu chỉ định command đó làm argument cho command `help`. Ví dụ, để biết thêm thông tin về command `search`, bạn có thể làm như sau:

```text
$ pgxn help search
usage: pgxn search [--help] [--mirror URL] [--verbose] [--yes]
                       [--docs | --dist | --ext]
                       TERM [TERM ...]


search in the available extensions


positional arguments:
    TERM            a string to search


optional arguments:
    --help          show this help message and exit
    --docs          search in documentation [default]
    --dist          search in distributions
    --ext           search in extensions
```

```text
global options:
  --mirror URL    the mirror to interact with [default: https://api.pgxn.
org/]
  --verbose       print more information
  --yes           assume affirmative answer to all questions
```

Trong các section tiếp theo, bạn sẽ thấy cách sử dụng PXGN hiệu quả để cài đặt một extension.

## Cài đặt extension

Thông thường, workflow để đưa một extension vào trạng thái hoạt động gồm một vài bước. Trước hết, bạn cần tìm hiểu nên dùng extension nào, version nào và mức độ tương thích với cluster của bạn. Sau khi tìm được extension cần dùng, bạn phải cài đặt nó vào cluster.

Cài đặt nó vào cluster thực sự có nghĩa là deploy nó vào các directory của PostgreSQL, tức là di chuyển mọi file và library liên quan đến extension vào shared directory của cluster để PostgreSQL có thể tìm thấy code cần thiết để chạy extension.

Cuối cùng, bạn cần tạo extension trong từng database cần nó. Việc tạo một extension giống như enable việc sử dụng extension đó trong một database cụ thể.

Để minh họa việc sử dụng một extension, chúng ta sẽ cài đặt `orafce`, extension cung cấp các function tương thích với Oracle. Mô tả toàn bộ extension không phải mục tiêu của section này, nên chỉ cần nói rằng extension này cung cấp một tập function, data type và những thứ khác khiến PostgreSQL trông giống một Oracle database, qua đó giúp việc migrate một application dựa trên Oracle dễ dàng hơn.

Các subsection sau đây mô tả từng bước cần thiết để đưa extension vào trạng thái hoạt động.

## Cài đặt extension thông qua pgxnclient

Thông thường, bước đầu tiên khi cài đặt một extension là tìm hiểu thông tin về nó, nghĩa là search một extension. Trong trường hợp cụ thể này, chúng ta đã biết extension mình đang tìm là gì, nhưng hãy search nó thông qua `pgxn`:

> Lưu ý, version của `oraface` thường xuyên thay đổi. 4.5.0 là version mới nhất tại thời điểm viết sách, nhưng bạn có thể thấy một version number mới hơn.

```text
$ pgxn search --ext orafce
orafce 4.5.0
    Oracle's compatibility functions and packages
```

Command `search` khám phá ecosystem để tìm mọi extension liên quan đến tiêu chí search của chúng ta, trong trường hợp này là tên extension (`--ext`). Nhờ `pgxn`, giờ chúng ta biết cần cài đặt version 4.2.1 của `orafce`, là stable version mới nhất có sẵn tại thời điểm viết sách.

Sau khi quyết định extension cần dùng, bạn có thể chạy command `install` của `pgxn` để tiến hành cài đặt. Workflow cài đặt bao gồm download, compile (nếu cần) source tree, package nó và đặt nó vào shared directory của PostgreSQL cluster.

Bạn có thể inspect process đang diễn ra với mức độ chi tiết rất cao nhờ option `--verbose`; và nếu bạn đang dùng `pgxn` với user khác user chạy cluster, bạn có thể dùng option `--sudo` để yêu cầu `pgxn` chuyển sang một user có privilege khi cần:

```text
$ pgxn install orafce --verbose --sudo
```

> Docker image được dùng cho chapter này có operating system user được phép sử dụng `sudo` mà không cần nhập password. Đây không phải là lựa chọn tốt trong production environment, nhưng đã được dùng để đơn giản hóa việc thử nghiệm các example trong chapter.

## Cài đặt extension thủ công

`pgxnclient` là một tool tốt để tự động hóa việc cài đặt extension, nhưng điều đó không có nghĩa là bạn không còn lựa chọn nào khác để cải thiện các tính năng PostgreSQL. Một cách khác để cài đặt extension là download chúng thủ công và thực hiện mọi bước cần thiết để cluster nhận biết các facility mới.

Điểm bắt đầu là website PGXN, có tại https://pgxn.org. Website cho phép bạn search một extension cụ thể theo tên hoặc keyword. Sau khi mở website PGXN, bạn có một textbox để nhập keyword cần search; và vì chúng ta đã biết tên extension, chúng ta có thể chọn Extensions từ pull-down menu.

Giao diện web được hiển thị trong screenshot sau:

![Hình 12.1: Trang chính của website PGXN](../assets/part-047-figure-12-1-000.jpg)

*Hình 12.1: Trang chính của website PGXN*

Kết quả search sẽ được hiển thị như trong screenshot sau, vì vậy chúng ta có thể đi vào trang extension với toàn bộ thông tin và documentation cho process cài đặt:

![Hình 12.2: Trang kết quả search của PGXN](../assets/part-047-figure-12-2-000.jpg)

*Hình 12.2: Trang kết quả search của PGXN*

Sau khi tìm thấy extension cần dùng, chúng ta có thể download nó bằng cách click vào icon download trên trang, giống icon được hiển thị ở góc trên bên phải trong screenshot sau. Kết quả là chúng ta sẽ download một file zip nén chứa tất cả những thứ liên quan đến extension:

![Hình 12.3: Trang download extension](../assets/part-047-figure-12-3-000.jpg)

*Hình 12.3: Trang download extension*

Để tiếp tục, trước hết bạn phải decompress archive đã download:

```text
$ unzip orafce-4.5.0.zip
```

Bây giờ bạn có thể đi vào directory được tạo cho extension này và compile nó (system cần có compiler và toàn bộ source build tool được cài đặt):

```text
$ cd orafce-4.5.0
$ make
```

> Bạn sẽ cần các PGXS Makefile để compile một extension từ đầu. Thông thường, các Makefile này được cài đặt cùng development tool của PostgreSQL. Ví dụ, trên các Linux distribution dựa trên Red Hat, bạn phải cài đặt package `postgresql16-dev`. Trong Docker image của chapter này, tất cả tool cần thiết để compile và install extension đã được chuẩn bị sẵn.

Nếu compilation thành công, extension sẽ được tạo và sẵn sàng để thêm vào shared library directory của PostgreSQL. Để di chuyển các file extension vào cluster, bạn cần quyền truy cập vào các database directory, chẳng hạn thông qua `sudo`:

```text
$ sudo make install
```

Từ đây, bạn có thể tiếp tục với statement `CREATE EXTENSION` trong mọi database yêu cầu extension.

## Sử dụng extension đã cài đặt

Sau khi extension đã được cài đặt, nghĩa là đã được deploy vào PostgreSQL cluster thủ công hoặc thông qua `pgxn`, bạn có thể tạo extension trong từng database cần nó.

Extension `orafce` phải được tạo bởi superuser, vì vậy bạn cần connect tới database với tư cách administrator để thực thi statement `CREATE EXTENSION`:

```text
$ psql -U postgres forumdb
psql (16.0)
Type "help" for help.


forumdb=# CREATE EXTENSION orafce;
CREATE EXTENSION
```

Nếu bây giờ inspect các extension được cài đặt trong database, bạn sẽ thấy `orafce` vừa được tạo ở version 4.5.0, giống version chúng ta tìm thấy khi search extension bằng `pgxn` hoặc trên website:

```text
forumdb=# \x \dx
Expanded display is on.
List of installed extensions
-[ RECORD 1 ]-------------------------------------------------------------
--------------------------
-------
Name        | orafce
Version     | 4.5
Schema      | public
Description | Functions and operators that emulate a subset of functions
and packages from the Oracl
e RDBMS
-[ RECORD 2 ]-------------------------------------------------------------
--------------------------
-------
Name        | pg_stat_statements
Version     | 1.10
Schema      | public
-------
Description | track planning and execution statistics of all SQL
statements executed
-[ RECORD 3 ]-------------------------------------------------------------
--------------------------
-------
Name        | plpgsql
Version     | 1.0
Schema      | pg_catalog
Description | PL/pgSQL procedural language
```

Sau khi extension đã được cài đặt trong database, mọi user đều có thể sử dụng nó. Là một test đơn giản, bạn có thể query table `DUAL` mà Oracle có và `orafce` đã tạo để các legacy query của bạn tiếp tục chạy:

```text
$ psql -U luca forumdb
psql (16.0)
Type "help" for help.


forumdb=> SELECT * FROM oracle.dual;
dummy
-------
X
(1 row)
```

Lưu ý rằng các table được extension tạo ra nằm trong namespace `oracle`. Bạn có thể dễ dàng tránh phải gõ `oracle` trước mọi object name bằng cách dùng `search_path` thay thế:

```text
forumdb=> SET search_path TO "$user", public, oracle;
SET
forumdb=> SELECT * FROM dual;
dummy
-------
X
(1 row)
```

## Xóa extension đã cài đặt

Có thể xảy ra trường hợp bạn không còn cần một extension và do đó muốn xóa nó khỏi cluster. Xóa các extension không dùng là một thói quen tốt vì nó giữ cho cluster sạch và không phụ thuộc vào những object mà bạn thực sự không cần.
