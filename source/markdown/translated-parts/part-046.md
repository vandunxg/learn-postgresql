Mặc dù bạn có thể tìm thấy các PostgreSQL extension ở khắp nơi trên internet, nhiều khả năng bạn sẽ làm việc với PGXN gần như mỗi khi cần một extension mới. PGXN không chỉ là một website hoặc một code repository đơn giản, mà là một platform chi tiết gồm bốn phần: search engine, extension manager, application programming interface (API) và client.

Search engine cho phép user tìm kiếm một extension cụ thể trong nội dung PGXN. Manager chịu trách nhiệm tiếp nhận các extension mới (hoặc version mới của extension) và cho phép user lấy chúng (tức là phân phối các extension). API định nghĩa cách các application có thể tương tác với manager và search engine, từ đó định nghĩa cách xây dựng một client. Có hai client chính: PGXN website và application command-line `pgxnclient`. Application `pgxnclient` có lẽ là cách hiệu quả nhất để lấy và cài đặt một extension, nội dung này sẽ được trình bày chi tiết trong các subsection tiếp theo; tuy nhiên, bạn cũng có thể tương tác trực tiếp với PGXN website để tìm kiếm và download extension. Sau này trong chapter, bạn sẽ thấy một ví dụ sử dụng PGXN website.

Extension được xây dựng trên PostgreSQL eXtension System (PGXS), một tập hợp rule cơ bản mà extension phải tuân thủ để cung cấp một interface quản lý thống nhất. Cụ thể, PostgreSQL cung cấp một Makefile thống nhất mà mọi extension nên sử dụng để cung cấp các chức năng chung nhằm cài đặt, upgrade và remove một extension. Bạn có thể inspect Makefile cơ sở của PGXS bằng cách tìm vị trí của nó với `pg_config`:

```text
$ pg_config --pgxs
/usr/lib/postgresql/16/lib/pgxs/src/makefiles/pgxs.mk
```

`pgxs.mk` là Makefile cơ sở cung cấp các chức năng chung cho mọi extension; cách sử dụng file này sẽ rõ ràng hơn khi chúng ta trình bày cách tạo một extension từ đầu.

## Thành phần của extension

Một extension gồm hai thành phần chính: control file và script file:

- **Control file** cung cấp thông tin về extension và cách quản lý nó, chẳng hạn cài đặt ở đâu và như thế nào, upgrade ra sao, v.v. Control file phần nào chính là metadata của extension.
- **Script file** là một SQL file chứa các statement để tạo các database object thuộc extension. Ở một mức độ nào đó, đây là content của extension. Đến lượt mình, script file có thể load các file khác hoàn thiện extension, chẳng hạn shared library và những thứ tương tự.

Khi bạn yêu cầu PostgreSQL cài đặt một extension, system inspect control file để lấy thông tin về extension, bảo đảm extension chưa được cài đặt trước đó, rồi thực thi script file bên trong một transaction. Kết quả là extension sẵn sàng trong database của bạn.

Mỗi extension có một version để bạn có thể quyết định chính xác version nào cần cài đặt. Nếu không chỉ định version, PostgreSQL sẽ giả định rằng bạn muốn version mới nhất hiện có.

Extension được cài đặt trong share directory của cluster, thường có thể tìm thấy bằng cách thực thi command `pg_config` với option `--sharedir`. Đây là một ví dụ:

```text
$ pg_config --sharedir
/usr/share/postgresql/16
```

Tất cả file tạo nên extension sẽ được đặt trong shared directory, và cluster yêu cầu các file này có sẵn ở đó cho user chạy cluster (thường là operating-system user `postgres`). Khi các file đã có sẵn cho cluster, extension phải được cài đặt riêng trong từng database cần nó; hãy nhớ rằng PostgreSQL cung cấp isolation rất mạnh giữa các database, vì vậy một extension được load vào database này sẽ không tự động có sẵn trong database khác. Tuy nhiên, hãy nhớ rằng template database (xem Chapter 2) có thể được dùng làm skeleton cho các database mới tạo, vì vậy sau khi bạn cài đặt một extension trong template database, extension đó sẽ có sẵn trong tất cả database khác được tạo ra.

## Control file

Một extension control file phải có tên liên quan đến extension và có suffix `.control`. Ví dụ, `learnpg.control` là một tên hợp lệ.

Control file là một text file nơi bạn có thể chỉ định các directive, tức instruction và metadata để PostgreSQL xử lý việc cài đặt extension. Mỗi directive có một name và một value. Các directive phổ biến nhất như sau:

- `directory` chỉ định path tới nơi chứa script của extension.
- `default_version` chỉ định version của extension cần cài đặt khi user không chỉ định version nào.
- `comment` là mô tả về extension và mục đích của nó.
- `requires` là danh sách tùy chọn các extension khác cần thiết để cài đặt và sử dụng extension này, do đó đại diện cho một dependency list.
- `schema` là một SQL schema nơi các extension object sẽ được cài đặt.
- `relocatable` cho biết extension có thể được chuyển sang một schema do user chọn hay không.
- `superuser` cho biết extension có thể được cài đặt bởi các account không phải superuser hay không (mặc định là yes, nghĩa là chỉ superuser mới có thể cài đặt extension).

Mỗi extension phải có ít nhất một control file, và file đó được gọi là main control file. Tuy nhiên, một extension có thể có thêm các control file (gọi là secondary control file).

Mỗi secondary control file phải nhắm tới một version cụ thể và phải có cùng tên với main control file, với version number được đặt trước bằng double dash; ví dụ, nếu main control file là `learnpg.control`, các file thứ cấp có thể là `learnpg--1.1.control`, `learnpg--1.2.control`, v.v.

## Script file

Script file chứa plain SQL dùng để tạo các extension object. Một extension object có thể là một table, một trigger, một function hoặc một binding cho external language.

Mỗi script file phải được đặt tên theo tên extension và có suffix `.sql`; version của extension được chỉ định bằng một number đứng trước double dash. Ví dụ, file `learnpg--1.0.sql` tạo các object cho version 1.0 của extension.

Mỗi extension phải có ít nhất một script file, nhưng có thể chỉ định nhiều hơn một file. Trong trường hợp đó, mỗi file bổ sung phải bao gồm version cần upgrade từ và version đích cuối cùng. Ví dụ, file `learnpg--1.0-1.1.sql` cung cấp việc upgrade từ version 1.0 lên version 1.1.

> Mỗi extension có một version number. Version number cao hơn nghĩa là upgrade extension, còn number thấp hơn nghĩa là downgrade extension. Ví dụ, version 1.2 là upgrade của 1.1, còn 1.0 là downgrade.

Như đã nêu, script file được thực thi trong một transaction và do đó không thể tương tác với transaction boundary (nghĩa là nó không thể phát hành `COMMIT` hoặc `ROLLBACK`). Tương tự, khi thực thi trong một transaction, script file bị ngăn không cho thực hiện bất kỳ thứ gì không thể chạy trong transaction block (ví dụ các utility command như `VACUUM`).

## Quản lý extension

Mỗi extension được quản lý ở database level, nghĩa là mọi database cần extension đều phải quản lý lifecycle của extension đó. Nói cách khác, không có cách quản lý extension ở per-cluster level rồi áp dụng extension cho mọi database bên trong cluster.

Extension chủ yếu được quản lý bằng ba SQL statement: `CREATE EXTENSION`, `DROP EXTENSION` và `ALTER EXTENSION`, lần lượt dùng để cài đặt extension vào database, remove extension khỏi database và sửa đổi attribute hoặc upgrade extension.

Mỗi extension được xác định bằng một mnemonic và một version; nếu không chỉ định version, PostgreSQL giả định rằng bạn muốn làm việc với version mới nhất hiện có hoặc version đã được cài đặt.

Trong các subsection tiếp theo, từng management statement trong ba statement trên sẽ được giải thích.

### Tạo extension

Statement `CREATE EXTENSION` cho phép bạn cài đặt một extension hiện có vào database hiện tại.

Synopsis của statement như sau:

```sql
CREATE EXTENSION [ IF NOT EXISTS ] extension_name
     [ WITH ] [ SCHEMA schema_name ]
                [ VERSION version ]
                [ CASCADE ]
```

Tên extension là mnemonic của extension; như bạn thấy, bạn có thể chỉ định version number của extension cần cài đặt. Nếu extension phụ thuộc vào extension khác, option `CASCADE` cho phép system tự động thực thi một `CREATE EXTENSION` đệ quy cho dependency đó. Bạn có thể quyết định schema nơi các extension object phải được đặt vào; tất nhiên, điều này chỉ có ý nghĩa đối với những extension có thể relocate.

Như bạn có thể hình dung, `IF NOT EXISTS` cho phép command xử lý êm thấm nếu extension đã được cài đặt. Chính xác hơn, nó không làm gì nếu extension đã được cài đặt trong database.

Để thấy rõ hơn cách `CREATE EXTENSION` hoạt động, hãy giả sử chúng ta muốn cài đặt procedural language PL/Perl trong database `forumdb`; vì extension PL/Perl có sẵn dưới dạng PostgreSQL contrib module, extension này đáng lẽ đã có sẵn bên trong cluster.

Vì vậy, để cài đặt nó, bạn phải thực hiện như sau:

```text
forumdb=# CREATE EXTENSION plperl;
CREATE EXTENSION
```

Lưu ý rằng extension PL/Perl (mnemonic `plperl`) yêu cầu được cài đặt bởi database administrator. Nếu bạn thử cài đặt lại extension đó, command sẽ fail trừ khi bạn sử dụng clause `IF NOT EXISTS`:

```text
forumdb=# CREATE EXTENSION plperl;
ERROR:    extension "plperl" already exists

forumdb=# CREATE EXTENSION IF NOT EXISTS plperl;
NOTICE:    extension "plperl" already exists, skipping
CREATE EXTENSION
```

Một ví dụ đơn giản khác là cài đặt một version cụ thể của extension `pg_stat_statements`:

```text
forumdb=# CREATE EXTENSION pg_stat_statements VERSION '1.10';
CREATE EXTENSION
```

> Lưu ý rằng `pg_stat_statements` yêu cầu thay đổi configuration parameter `shared_preload_libraries`, và thay đổi đó lại yêu cầu cluster phải được restart. Trong Docker image của chapter này, setting `shared_preload_libraries` đã được cấu hình phù hợp để bạn sử dụng extension `pg_stat_statements`. Nếu muốn thay đổi PostgreSQL configuration thủ công để sử dụng `pg_stat_statements`, bạn cần sửa configuration file `postgresql.conf` hoặc thực thi:
>
> ```sql
> ALTER SYSTEM SET shared_preload_libraries TO 'pg_stat_statements';
> ```
>
> Sau đó restart cluster.

### Xem các extension đã cài đặt

Trong `psql` terminal, bạn có thể lấy danh sách các extension đã cài đặt bằng special command `\dx`:

```text
forumdb=# \dx
                                      List of installed extensions
       Name             | Version |      Schema      |
Description
--------------------+---------+------------+------------------------------
-----------------------------
 pg_stat_statements | 1.10     | public               | track execution statistics
of all SQL statements executed
 plperl                 | 1.0       | pg_catalog | PL/Perl procedural language
 plpgsql                | 1.0       | pg_catalog | PL/pgSQL procedural language
(3 rows)
```

Có thể lấy chính thông tin này từ catalog đặc biệt `pg_extension`, bằng cách join với `pg_namespace` để trích xuất thông tin dễ đọc về schema nơi extension đang tồn tại:

```text
forumdb=# SELECT x.extname, x.extversion, n.nspname
              FROM pg_extension x JOIN pg_namespace n
              ON n.oid = x.extnamespace;

            extname       | extversion | nspname
--------------------+------------+------------
 plpgsql                | 1.0           | pg_catalog
 plperl                 | 1.0           | pg_catalog
 pg_stat_statements | 1.10               | public
(3 rows)
```

### Tìm các version extension hiện có

Bạn có thể inspect cluster để lấy thông tin về các version extension hiện có, tức các version mà bạn thực sự có thể cài đặt trong một database. Catalog đặc biệt `pg_available_extension_versions` cho phép lấy tất cả version hiện có của mọi extension khả dụng. Ví dụ, extension `pg_stat_statements` có các value sau trong cluster:

```text
forumdb=# SELECT name, version
              FROM pg_available_extension_versions
              WHERE name = 'pg_stat_statements';

            name        | version
--------------------+---------
            name        | version
--------------------+---------
pg_stat_statements | 1.4
pg_stat_statements | 1.5
pg_stat_statements | 1.6
pg_stat_statements | 1.8
pg_stat_statements | 1.9
pg_stat_statements | 1.7
pg_stat_statements | 1.10
```

Điều hữu ích cần biết là extension `pg_stat_statements` có thể được cài đặt ở một version trong khoảng từ 1.4 đến 1.10, tùy nhu cầu của bạn.

> Bạn nên luôn cài đặt version mới nhất của một extension, tức version có number cao nhất, trừ khi bị buộc phải cài một version cụ thể vì backward compatibility.

### Sửa đổi extension hiện có

Statement `ALTER EXTENSION` rất phong phú và phức tạp, cho phép bạn sửa đổi hoàn toàn một extension hiện có. Statement này cho phép thực hiện bốn thay đổi chính đối với một extension hiện có:

- Upgrade extension lên version mới.
- Set schema của một relocatable extension.
- Add một database object vào extension.
- Remove một database object khỏi extension.

Để upgrade một extension đã cài đặt, bạn phải chỉ định clause `UPDATE`, đồng thời chỉ định target version number. Ví dụ, hãy xét extension `pg_stat_statements` đã trình bày trước đó và giả sử chúng ta cài version 1.6 của nó để upgrade. Để update extension lên version 1.10, có thể phát hành một statement `ALTER EXTENSION` như ví dụ sau:

```text
forumdb=# CREATE EXTENSION
            pg_stat_statements WITH VERSION '1.6';
CREATE EXTENSION

forumdb=# ALTER EXTENSION pg_stat_statements
            UPDATE TO '1.10';
ALTER EXTENSION
```

```text
forumdb=# \dx pg_stat_statements
                                      List of installed extensions
       Name             | Version | Schema |
Description
--------------------+---------+--------+----------------------------------
-------------------------
 pg_stat_statements | 1.10            | public | track execution statistics of
all SQL statements executed
(1 row)
```

Di chuyển một relocatable extension từ schema này sang schema khác được thực hiện bằng cách chỉ định clause `SET SCHEMA`, ví dụ:

```text
forumdb=# ALTER EXTENSION pg_stat_statements SET SCHEMA my_schema;
ALTER EXTENSION

forumdb=# \dx pg_stat_statements
                                      List of installed extensions
       Name             | Version |     Schema     |
Description
--------------------+---------+-----------+-------------------------------
----------------------------
 pg_stat_statements | 1.10            | my_schema | track execution statistics of
all SQL statements executed
(1 row)
```

Command đó sẽ chuyển tất cả extension object vào schema `my_schema`, schema này phải tồn tại trước khi extension được relocate.

Nếu muốn remove một database object hiện có khỏi một extension, chẳng hạn một table, bạn có thể sử dụng clause `DROP`, theo sau là type của object và tất nhiên là tên của nó. Điều quan trọng là phải hiểu rằng việc remove một object khỏi extension sẽ không remove object khỏi database; thay vào đó, nó unlink object lifecycle khỏi lifecycle của extension. Nói cách khác, một object bị loại khỏi extension sẽ trở thành một database object thông thường. Ví dụ, nếu remove view `pg_stat_statements` khỏi extension cùng tên, bạn có thể chỉ định object type (`VIEW`) sau clause `DROP`, như sau:

```text
forumdb=# ALTER EXTENSION pg_stat_statements
            DROP VIEW pg_stat_statements;
ALTER EXTENSION
```

Nếu extension đã được relocate, cần chỉ định qualified name cho mọi object, tức đặt schema hiện tại của extension trước tên object. Ví dụ, sau khi relocate extension vào namespace `my_schema`, command trên trở thành:

```text
forumdb=# ALTER EXTENSION pg_stat_statements
            DROP VIEW my_schema.pg_stat_statements;
ALTER EXTENSION
```

Kết quả của command `DROP VIEW` trên là view vốn được tạo tại thời điểm deployment extension vẫn còn trong database và có thể được query như bình thường; nhưng view này hiện là một object có lifecycle độc lập với chính extension.

Có thể dễ dàng thấy view vẫn khả dụng bằng cách query nó:

```text
forumdb=# SELECT count(*) FROM pg_stat_statements;
 count
-------
     2
(1 row)
```

Tất nhiên, có thể add một object mới vào extension bằng clause `ADD`, hoạt động như điều ngược lại với `DROP` và yêu cầu type cùng tên của object. Ví dụ, để add view `pg_stat_statements` trở lại extension, có thể thực hiện như sau:

```text
forumdb=# ALTER EXTENSION pg_stat_statements
            ADD VIEW pg_stat_statements;
ALTER EXTENSION
```

Bạn cũng có thể add các object của riêng mình vào extension. Chẳng hạn, việc add một table mới vào extension có nghĩa là table đó sẽ trải qua lifecycle của extension:

```text
forumdb=# CREATE TABLE t_ext( i int, t text );
forumdb=# ALTER EXTENSION pg_stat_statements
            ADD TABLE t_ext;
ALTER EXTENSION
```

Table `t_ext` hiện là một phần của extension, do đó nó không thể tiếp tục được thao tác bằng các statement không tính đến extension.

Ví dụ, nếu bạn cố delete table, PostgreSQL sẽ ngăn bạn làm hỏng extension:

```text
forumdb=# DROP TABLE t_ext;
ERROR: cannot drop table t_ext because extension pg_stat_statements
requires it
HINT: You can drop extension pg_stat_statements instead.
```

Ví dụ cuối này cho thấy rõ sức mạnh của extension: mọi object thuộc một extension được quản lý như một thể thống nhất, vì vậy không thể vô tình quản lý hoặc remove chúng, do chúng phụ thuộc lẫn nhau. Điều này có nghĩa là để delete table nói trên, bạn phải remove table khỏi extension trước khi tự drop table, hoặc delete toàn bộ extension.

### Remove extension hiện có

`DROP EXTENSION` delete một extension khỏi database hiện tại. Synopsis của statement như sau:

```sql
DROP EXTENSION [ IF EXISTS ] name [, ...] [ CASCADE | RESTRICT ]
```

Command hỗ trợ clause `IF EXISTS`, giống như nhiều statement khác. Ngoài ra, có thể chỉ định nhiều hơn một extension cần remove khỏi database.

Option `CASCADE` cũng remove các database object phụ thuộc vào object của extension, trong khi option đối lập là `RESTRICT` khiến command fail nếu vẫn còn các object khác phụ thuộc vào extension này. Ngoài ra, có thể drop nhiều extension cùng lúc.

Ví dụ, statement sau remove hai extension trong một lần, đồng thời remove tất cả object phụ thuộc vào các extension đó:

```text
forumdb=# DROP EXTENSION plperl, plpgsql CASCADE;
NOTICE: drop cascades to function get_max(integer,integer)
DROP EXTENSION
```

Như bạn thấy, vì user-defined function `get_max()` phụ thuộc vào một trong hai extension, option `CASCADE` đã khiến process drop cả function đó.
