Nếu một database không còn cần extension và các thành phần liên quan của nó nữa, bạn có thể phát hành statement `DROP EXTENSION` và extension sẽ biến mất khỏi database. Tất nhiên, nếu extension được cài đặt bởi một database superuser, bạn cũng cần phát hành statement này với tư cách superuser. Với ví dụ `orafce`, superuser có thể thực hiện như sau:

```text
   $ psql -U postgres forumdb
   psql (16.0)
   Type "help" for help.


   forumdb=# DROP EXTENSION orafce;
   DROP EXTENSION
```

Như bạn có thể hình dung, việc inspect danh sách extension không còn hiển thị entry `orafce` nữa, và tất cả feature, bao gồm table `DUAL`, đã biến mất:

```text
   forumdb=# \dx
   ù                     List of installed extensions
       Name    | Version |     Schema     |           Description
    ---------+---------+------------+------------------------------
   pg_stat_statements | 1.10          | public        | track planning and execution
   statistics of all SQL stat
   ements executed
   plpgsql                | 1.0       | pg_catalog | PL/pgSQL procedural language
   (2 rows)


   forumdb=# SELECT * FROM oracle.dual;
   ERROR:     relation "oracle.dual" does not exist
   LINE 1: SELECT * FROM oracle.dual;
```

Việc remove một extension khỏi một database duy nhất không remove nó khỏi các database khác, nơi bạn đã thực thi một statement `CREATE EXTENSION` tường minh. Nó cũng không remove các file và library của extension khỏi thư mục share của cluster.

Cách remove (un-deploy) extension khỏi cluster phụ thuộc vào cách bạn đã cài đặt nó vào cluster ngay từ đầu.

## Remove extension qua pgxnclient

Command `uninstall` của pgxn thực hiện hành động ngược lại chính xác với command `install`: nó remove tất cả file liên quan đến một extension. Các command-line option cũng giống nhau, vì vậy chúng ta có thể thực thi một command đơn giản như sau:

```text
   $ pgxn uninstall orafce --sudo --verbose
```

Tất cả file liên quan đến extension sẽ được remove khỏi các thư mục shared library của cluster. Vì vậy extension đã biến mất vĩnh viễn, và nếu cần cài đặt lại, bạn sẽ phải bắt đầu lại từ bước đầu tiên.

## Remove extension được compile thủ công

Để remove một extension mà bạn đã compile thủ công từ source, bạn lại cần dùng `make`, lần này với command `uninstall`, trong thư mục nơi bạn đã giải nén archive đã download:

```text
   $ cd orafce-4.2.1
   $ sudo make uninstall
```

> Tránh trộn lẫn việc quản lý extension bằng các tool khác nhau. Nếu bạn cài đặt extension qua pgxnclient, tốt hơn hết là remove nó bằng chính client đó; ngược lại, nếu bạn cài đặt nó từ source, hãy dùng cùng cách tiếp cận để remove nó.

Tóm lại, bạn đã thấy cách xử lý một extension bằng PGXN client hoặc thủ công thông qua PGXN infrastructure. Trong section tiếp theo, bạn sẽ học cách build extension của riêng mình.

## Tạo extension của riêng bạn

Trong section này, chúng ta sẽ build một extension từ đầu để bạn hiểu rõ hơn chúng được cấu thành như thế nào. Mục tiêu là giúp bạn biết cách chuyển ngay cả các SQL script của riêng mình thành một extension, cùng tất cả lợi ích về khả năng quản lý mà extension có thể cung cấp.

## Định nghĩa một extension ví dụ

Để minh họa cách build extension của riêng bạn, chúng ta sẽ tạo một tập capability đơn giản áp dụng cho database `forum`, cung cấp thêm một số feature. Cụ thể, chúng ta sẽ định nghĩa một extension có tên `tagext`, cung cấp một utility function mà với một tag cụ thể trong table `tag`, sẽ trả về full path tới tag đó cùng tất cả ancestor.

Ví dụ, tag `Linux` là con của tag `Operating Systems`, vì vậy path tới tag `Linux` là `Operating System > Linux`.

Cụ thể, chúng ta muốn extension cung cấp một function tên `tag_path`; với một tag, function này cung cấp tag path như trong ví dụ sau:

```text
   forumdb=> SELECT tag_path( 'Kubuntu' );
                           tag_path
   ----------------------------------------------
      Operating Systems > Linux > Ubuntu > Kubuntu
   (1 row)
```

Trong các section tiếp theo, bạn sẽ thấy cách đạt được kết quả trên bằng cách triển khai extension ví dụ. Tất cả file cần thiết đều có trong code repository của cuốn sách.

## Tạo các file của extension

Trước tiên, hãy bắt đầu với control file, nơi chúng ta chèn một số thông tin cơ bản về extension. Tạo một file tên `tagext.control` và đặt nó vào một folder, chẳng hạn `/src/tagext`. File này có nội dung như sau:

```text
   comment = 'Tag Programming Example Extension'
   default_version = '1.0'
   superuser           = false
   relocatable         = true
```

> Trong Docker image được dùng cho các example của chapter này, bạn sẽ tìm thấy các file extension trong folder `/src/tagext` và có thể cài đặt extension bằng cách vào folder đó.

Control file trên chứa một comment mô tả extension cho các administrator khác, chỉ định `default_version`, tức version sẽ được cài đặt nếu user không chỉ định version nào, đồng thời quy định rằng extension này có thể được cài đặt bởi bất kỳ user nào (`superuser = false`) và được chuyển tới bất kỳ schema nào mà user muốn (`relocatable = true`).

Tiếp theo là Makefile, tức file sẽ build và cài đặt extension:

```text
   EXTENSION = tagext
   DATA = tagext--1.0.sql


   PG_CONFIG = pg_config
```

```text
   PGXS := $(shell $(PG_CONFIG) --pgxs)
   include $(PGXS)
```

Makefile này rất đơn giản và có thể được dùng làm skeleton cho các Makefile extension khác. Cụ thể, chúng ta định nghĩa tên của extension sẽ được quản lý thông qua Makefile này, cũng như file dùng để tạo nội dung extension. Điều này được chỉ định trong biến `DATA`, vì vậy chúng ta đang thiết lập system để dùng file `tagext--1.0.sql` nhằm tạo các object mà extension này cung cấp.

Các dòng cuối định nghĩa việc sử dụng PGXS build infrastructure và cụ thể được dùng để include PGXS base Makefile, được tính toán từ output của command `pg_config`.

Khi đã có toàn bộ infrastructure, chúng ta có thể định nghĩa nội dung của extension. Do đó, file `tagext--1.0.sql` chứa định nghĩa một function (xem *Chapter 7, Server Side Programming*) mà với một tag cụ thể sẽ trả về biểu diễn text của tag path cùng tất cả ancestor:

```sql
   CREATE OR REPLACE FUNCTION tag_path( tag_to_search text )
   RETURNS TEXT
   AS $CODE$
   DECLARE
      tag_path text;
      current_parent_pk int;
   BEGIN


      tag_path = tag_to_search;


      SELECT parent
      INTO      current_parent_pk
      FROM      tags
      WHERE     tag = tag_to_search;


      -- here we must loop
      WHILE current_parent_pk IS NOT NULL LOOP
             SELECT parent, tag || ' > ' || tag_path
             INTO    current_parent_pk, tag_path
             FROM    tags
             WHERE   pk = current_parent_pk;
      END LOOP;


      RETURN tag_path;
   END
   $CODE$
   LANGUAGE plpgsql;
```

Function này nhận một tag làm argument, sau đó query table `tags` để lấy parent primary key, rồi loop qua từng parent tag. Trong mỗi loop, string text `tag_path` được bổ sung tên parent tag, để kết quả là một string có dạng `parent 1 > parent 2 > child`.

Khi tất cả file đã sẵn sàng, chúng ta sẽ có tình huống như sau, với Makefile, control file và file chứa nội dung extension:

```text
   $ ls -1 /src/tagext
   Makefile
   tagext--1.0.sql
   tagext.control
```

## Cài đặt extension

Khi đã có đủ các thành phần, bạn có thể dùng Makefile để cài đặt (deploy) extension vào cluster. Vì extension sẽ được cài đặt trong các thư mục PostgreSQL, bạn có thể cần dùng một user có privilege để cài đặt extension:

```text
   $ sudo make install
```

Bây giờ có thể cài đặt extension trong database `forumdb` bằng `CREATE EXTENSION`, sau đó thử thực thi function mà extension định nghĩa:

```text
   forumdb=> CREATE EXTENSION tagext;
   CREATE EXTENSION


                                                         List of installed extensions
          Name             | Version |      Schema     |
   Description


   --------------------+---------+------------+------------------------------
   --------------------------
   ----------------
   pg_stat_statements | 1.10           | public         | track planning and execution
   statistics of all SQL stat
   ements executed
   plpgsql                 | 1.0       | pg_catalog | PL/pgSQL procedural language
   tagext                  | 1.0       | forum          | Tag Programming Example
   Extension


   forumdb=> SELECT tag_path( 'Kubuntu' );
                           tag_path
   ----------------------------------------------
    Operating Systems > Linux > Ubuntu > Kubuntu
   (1 row)
```

Function này hoạt động và có thể xây dựng một tag tree hoặc path cho tag được chỉ định cùng tất cả ancestor của nó, đồng thời PostgreSQL báo rằng extension đang ở version 1.0.

## Tạo bản upgrade cho extension

Hãy tưởng tượng chúng ta muốn mở rộng function của extension để user có thể chỉ định tag separator trong path output. Chúng ta có thể tạo một version mới của function, drop version cũ và cho phép user upgrade extension bằng nội dung mới.

Trước tiên, hãy tạo bản upgrade cho nội dung của extension, tức function mới mà extension cung cấp. Tạo một file tên `tagext--1.0--1.1.sql` và đặt nội dung sau vào file:

```sql
   DROP FUNCTION IF EXISTS tag_path( text );


   CREATE OR REPLACE FUNCTION tag_path( tag_to_search text,
                                                 delimiter text DEFAULT ' > ' )
   RETURNS TEXT
   AS $CODE$
   DECLARE
      tag_path text;
      current_parent_pk int;
   BEGIN


      tag_path = tag_to_search;


      SELECT parent
      INTO    current_parent_pk
      FROM    tags
      WHERE   tag = tag_to_search;


      -- here we must loop
      WHILE current_parent_pk IS NOT NULL LOOP
           SELECT parent, tag || delimiter || tag_path
           INTO     current_parent_pk, tag_path
           FROM     tags
           WHERE    pk = current_parent_pk;
      END LOOP;


      RETURN tag_path;
   END
   $CODE$
   LANGUAGE plpgsql;
```

File này trước tiên drop version cũ của function (nếu version đó tồn tại và đã được cài đặt bởi version trước của extension). Sau đó, một function mới với thêm một parameter tùy chọn được tạo. Function thực hiện chính xác cùng công việc như version trước, nhưng lần này sử dụng biến `delimiter` để phân tách nhiều tag.

Vì chúng ta đã thêm một file mới vào extension, cần thông báo cho Makefile về file đó. Do vậy, chúng ta phải thêm file mới vào biến `DATA` để nội dung Makefile có dạng như sau:

```text
   EXTENSION = tagext
   DATA = tagext--1.0.sql tagext--1.0--1.1.sql


   PG_CONFIG = pg_config
   PGXS := $(shell $(PG_CONFIG) --pgxs)
   include $(PGXS)
```

## Thực hiện upgrade extension

Với Makefile mới và các file `tagext--1.0--1.1.sql`, tình trạng trên disk như sau:

```text
   $ ls -1 /src/tagext
   Makefile
   tagext--1.0--1.1.sql
   tagext--1.0.sql
   tagext.control
```

Do đó, bây giờ có thể cài đặt (deploy) extension vào cluster bằng cách chạy lại một command install:

```text
   $ make install
   /bin/mkdir -p '/usr/local/share/postgresql/extension'
   /bin/mkdir -p '/usr/local/share/postgresql/extension'
   /usr/bin/install -c -m 644 .//tagext.control '/usr/local/share/postgresql/
   extension/'
   /usr/bin/install -c -m 644 .//tagext--1.0.sql .//tagext--1.0--1.1.sql                   '/
   usr/local/share/postgresql/extension/'
```

Trong database, có thể upgrade extension bằng `ALTER EXTENSION`:

```text
   forumdb=> ALTER EXTENSION tagext UPDATE TO '1.1';
   ALTER EXTENSION


   forumdb=> \dx tagext
                        List of installed extensions
      Name   | Version | Schema |                   Description
    --------+---------+--------+-----------------------------------
     tagext | 1.1         | public | Tag Programming Example Extension
   (1 row)
```

Như bạn thấy, version của extension hiện là 1.1, vì vậy có thể gọi function `tag_path` có hoặc không có argument mới:

```text
   forumdb=> SELECT tag_path( 'Kubuntu' );
                          tag_path
   ----------------------------------------------
       Operating Systems > Linux > Ubuntu > Kubuntu
   (1 row)


   forumdb=> SELECT tag_path( 'Kubuntu', ' --> ' );
                               tag_path
   ----------------------------------------------------
       Operating Systems --> Linux --> Ubuntu --> Kubuntu
   (1 row)
```

Bây giờ bạn đã biết cách quản lý toàn bộ life cycle của extension.

## Tóm tắt

Chapter này đã giới thiệu extension ecosystem, một system rất phong phú và mạnh mẽ để package các object liên quan và quản lý chúng như một unit duy nhất. Extension cung cấp cách thêm feature mới vào cluster và database, và đáng chú ý nhất là cung cấp một cách rõ ràng, súc tích để xây dựng update và các installation có thể lặp lại, nhờ đó việc phân phối feature tới các cluster và database khác trở nên dễ dàng hơn.

PostgreSQL đi kèm các extension hữu ích được cung cấp trong contrib package; các extension này được chính các PostgreSQL developer phát triển nên tích hợp rất tốt với version PostgreSQL hiện tại. Mặt khác, PGXN network cung cấp các extension bên thứ ba có thể bổ sung functionality mới cho cluster của bạn.

Nhờ PGXS build infrastructure, việc tạo extension từ đầu khá toàn diện và tương đối dễ, còn nhờ các tool như pgxnclient, việc quản lý nhiều extension có thể được tự động hóa.

Trong chapter tiếp theo, bạn sẽ học cách quản lý status và performance của cluster, còn *Chapter 19* sẽ giới thiệu một số extension hữu ích khác.

## Kiểm tra kiến thức

- **Extension là gì?**

  Extension là một collection gồm các database object liên quan, có thể được cài đặt, upgrade hoặc remove như một unit duy nhất. Xem section *Introducing extensions* để biết thêm chi tiết.

- **Command pgxnclient là gì?**

  pgxnclient là một command giúp sử dụng PGXN dễ dàng hơn bằng cách download, cài đặt và remove extension. Xem section *Exploring the PGXN client* để biết thêm chi tiết.

- **Extension control file là gì?**

  Control file là một text file định nghĩa các property chính của extension, chẳng hạn name, version và các dependency khác. Xem section *Extension components* để biết thêm chi tiết.

- **Làm thế nào để inspect những extension nào đã được tạo trong một database?**

  Catalog đặc biệt `pg_extension` cung cấp thông tin về các extension đã cài đặt; trong `psql`, command đặc biệt `\dx` hiển thị phần tóm tắt các extension đã cài đặt. Xem section *Viewing installed extensions* để biết thêm chi tiết.

- **Làm thế nào để thay đổi version của một extension (update)?**

  Statement `ALTER EXTENSION UPDATE TO` có thể được dùng để chỉ định extension phải được upgrade lên version nào. Xem section *Altering an existing extension* để biết thêm chi tiết.

## Tài liệu tham khảo

- Tài liệu chính thức của PostgreSQL về extension: https://www.postgresql.org/docs/current/extend-extensions.html
- Tài liệu chính thức của PostgreSQL về extension build system (PGXS): https://www.postgresql.org/docs/current/extend-pgxs.html
- Repository chính thức của pgxnclient: https://pypi.org/project/pgxnclient/
- Tài liệu chính thức của pgxnclient: https://pgxn.github.io/pgxnclient/
- *PostgreSQL 11 Server Side Programming – Quick Start Guide*, Packt Publishing

## Tìm hiểu thêm trên Discord

Để tham gia cộng đồng Discord của cuốn sách, nơi bạn có thể chia sẻ feedback, đặt câu hỏi cho tác giả và tìm hiểu về các bản phát hành mới, hãy quét QR code bên dưới:

https://discord.gg/jYWCjF6Tku
