### Auditing theo session

Cách đầu tiên để sử dụng PgAudit (và cũng là cách dễ hiểu, dễ thử nhất) là audit theo session.

Cũng như các configuration setting khác, bạn có thể thiết lập configuration của PgAudit thông qua `SET` SQL statement. Cách này hữu ích để test configuration trước khi áp dụng cho toàn bộ cluster. Hãy thử thiết lập `pgaudit.log` trực tiếp trong interactive session và thực hiện một vài action để xem điều gì xảy ra. Ví dụ, giả sử chúng ta muốn audit mọi thay đổi đối với data:

```text
   forumdb=# SET pgaudit.log TO 'write, ddl';
   SET
   forumdb=# SELECT count(*) FROM forum.categories;
      count
   -------
          3
   (1 row)


   forumdb=# INSERT INTO forum.categories( description, title ) VALUES(
   'Fake', 'A Malicious Category' );
   INSERT 0 1


   forumdb=# SELECT count(*) FROM forum.categories;
      count
   -------
          4
   (1 row)


   forumdb=# INSERT INTO forum.categories( description, title ) VALUES(
   'Fake2', 'Another Malicious Category' );
   INSERT 0 1
```

`pgaudit.log` chỉ có thể được set bởi superuser, vì vậy nếu muốn thử dynamic setting này trong một interactive session, bạn cần connect với tư cách database administrator. Tất nhiên, bạn có thể set nó cho tất cả user ở cluster-wide level bằng cách set parameter trong configuration file `postgresql.conf`.

Trong log, PostgreSQL sẽ ghi nội dung tương tự như sau:

```text
   LOG: AUDIT: SESSION,1,1,WRITE,INSERT,,,"INSERT INTO forum.categories(
   description, title ) VALUES( 'Fake', 'A Malicious Category' );",<not
   logged>
   LOG: AUDIT: SESSION,2,1,WRITE,INSERT,,,"INSERT INTO forum.categories(
   description, title ) VALUES( 'Fake2', 'Another Malicious Category'
   );",<not logged>
```

Một dòng log như vậy có nhiều chi tiết, nhưng trước khi xem xét các field, hãy lưu ý rằng không có gì được ghi về hai câu lệnh `SELECT`: vì chúng ta yêu cầu PgAudit không audit các query `READ`, các câu lệnh `SELECT` đã bị loại khỏi quá trình audit.

Hãy lưu ý rằng mọi audit line đều có prefix rất dễ hiểu là `AUDIT`, nhờ đó có thể dễ dàng biết log line được tạo bởi PgAudit hay bởi một event nội bộ khác của PostgreSQL.

Mỗi line cho biết audit type (trong ví dụ trước là `SESSION`) và một counter tăng dần để biểu thị thứ tự theo thời gian mà các statement được audit. Tiếp theo là category của statement mà PgAudit nhận diện (trong ví dụ trước, cả hai đều là `WRITE` event), rồi đến các statement hoàn chỉnh đã được thực thi. Vẫn còn chỗ cho những detail khác, sẽ được thảo luận trong các ví dụ tiếp theo.

Hãy chuyển sang một ví dụ khác — xét việc thực thi một query được build dynamic như sau:

```text
   forumdb=# DO $$ BEGIN
   EXECUTE 'TRUNCATE TABLE ' || 'forum.tags CASCADE';
   END $$;
   NOTICE:    truncate cascades to table "forum.j_posts_tags"
   DO
```

Thay vì thực thi một statement `TRUNCATE TABLE tags`, statement đã được tạo bằng cách nối hai string. Trong log, PgAudit chèn một line như sau:

```text
   LOG: AUDIT: SESSION,3,1,WRITE,TRUNCATE TABLE,,,TRUNCATE TABLE forum.tags
   CASCADE,<not logged>
```

Một lần nữa, line này báo cáo auditing mode (`SESSION`), auditing statement number (`3`), category (`WRITE`), và statement (`TRUNCATE TABLE`), cũng như statement đã thực thi đầy đủ. Chi tiết cuối cùng này rất quan trọng: nếu bạn thực thi cùng statement mà không audit, PostgreSQL log sẽ chứa một line như sau:

```text
   LOG:    duration: 12.616 ms        statement: DO $$ BEGIN
             EXECUTE 'TRUNCATE TABLE ' || 'forum.tags CASCADE';
             END $$;
```

Ở đây, bạn có thể thấy log đã sao chép nguyên xi source statement, bao gồm string concatenation và newline, khiến statement khó đọc và khó search hơn.

### Audit theo role

Cơ chế audit theo role của PgAudit cho phép bạn định nghĩa rất fine-grained những event nào mình quan tâm.

Ý tưởng là bạn định nghĩa một database role và grant cho role đó các permission liên quan đến action muốn audit. Sau khi role và các permission của nó được thiết lập, bạn thông báo cho PgAudit biết phải audit theo role đó. Khi ấy, PgAudit sẽ báo cáo trong log mọi action khớp với action đã grant cho auditing role, bất kể role nào đã thực hiện action đó.

Vì vậy, bước đầu tiên là tạo một role chỉ được dùng để chỉ định những action cần audit, và sẽ không được dùng như một role thông thường cho các interactive session:

```text
   forumdb=# CREATE ROLE auditor WITH NOLOGIN;
   CREATE ROLE
```

Để chỉ định những action mà role phải audit, chúng ta chỉ cần `GRANT` các permission tương ứng cho role. Ví dụ, giả sử chúng ta muốn audit mọi action `DELETE` trên mọi table và chỉ audit action `INSERT` trên `posts` và `categories`, chúng ta phải grant cho role tập permission sau:

```text
   forumdb=# GRANT DELETE ON ALL TABLES IN SCHEMA forum TO auditor;
   GRANT
   forumdb=# GRANT INSERT ON forum.posts TO auditor;
   GRANT
   forumdb=# GRANT INSERT ON forum.categories TO auditor;
   GRANT
```

Mọi thứ đã sẵn sàng để PgAudit thực hiện công việc, nhưng điều quan trọng là auditing system phải biết role `auditor` cần được sử dụng. Vì vậy, chúng ta cần configure `pgaudit.role` ở cluster configuration hoặc trong current session. Cách thứ nhất dĩ nhiên là cách phù hợp để dùng trong production environment, còn set configuration parameter trong một session riêng lẻ hữu ích cho mục đích test. Hãy set parameter trong session với tư cách database administrator để thử hoạt động của nó:

```text
   forumdb=# SET pgaudit.role TO auditor;
   SET
```

Bây giờ là lúc thực thi một vài statement và xem PgAudit lưu gì trong cluster log:

```text
   forumdb=# INSERT INTO forum.categories( title, description ) VALUES(
   'PgAudit', 'Topics related to auditing in PostgreSQL' );
   INSERT 0 1


   -- this will not be logged
   forumdb=# INSERT INTO forum.tags( tag ) VALUES( 'pgaudit' );
   INSERT 0 1


   forumdb=# DELETE FROM forum.posts WHERE author NOT IN ( SELECT pk FROM
   forum.users WHERE username NOT IN ( 'fluca1978', 'sscotty71' ) );
   DELETE
```

Như bạn có thể hình dung, PgAudit sẽ log statement đầu tiên và cuối cùng trong session ví dụ trên: thực tế, chỉ những statement đó liên quan đến các table và action mà auditing role đã được grant permission.

Trong PostgreSQL log, bạn sẽ tìm thấy các line tương tự như sau:

```text
   LOG: AUDIT: OBJECT,1,1,WRITE,INSERT,TABLE,forum.categories,"INSERT INTO
   forum.categories( title, description ) VALUES( 'PgAudit', 'Topics related
   to auditing in PostgreSQL' );",<not logged>
   LOG: AUDIT: OBJECT,2,1,WRITE,DELETE,TABLE,forum.posts,"DELETE FROM forum.
   posts WHERE author NOT IN ( SELECT pk FROM forum.users WHERE username NOT
   IN ( 'fluca1978', 'sscotty71' ) );",<not logged>
```

Hãy lưu ý rằng tuple insertion vào table `tags` bị thiếu: nó không được audit và log vì auditing role không bao gồm một permission `GRANT` cụ thể cho table đó.

Sau khi auditing role đã được configure đúng, chúng ta có thể lưu configuration sau khi sửa configuration file `postgresql.conf` và set `pgaudit.role` tunable như sau:

```text
      pgaudit.role = 'auditor'
```

Như bạn có thể thấy, audit theo role linh hoạt hơn nhiều so với chỉ audit theo session: trong khi cách sau chỉ cho phép bạn chỉ định category của action cần audit, cách trước cho phép định nghĩa fine-grained chính xác những statement nào cần audit.

## Tóm tắt

PostgreSQL cung cấp một infrastructure logging đáng tin cậy và linh hoạt, cho phép database administrator monitor những gì cluster đã thực hiện trong khoảng thời gian rất gần đây. Nhờ tính linh hoạt, log có thể được configure để cho phép các external tool như pgBadger truy cập nhằm phân tích cluster. Hơn nữa, cùng infrastructure logging đó có thể được tận dụng để thực hiện audit, một dạng introspection thường được yêu cầu bởi luật của chính quyền địa phương.

Trong chapter này, bạn đã học cách configure PostgreSQL logging system để đáp ứng nhu cầu, cách monitor cluster bằng các web dashboard do pgBadger cung cấp, và cuối cùng là cách audit user và application của mình.

Trong chapter tiếp theo, bạn sẽ học cách backup cluster của mình.

## Kiểm tra kiến thức

* **Logging khác auditing như thế nào?**

  Logging là cách theo dõi một số activity xảy ra bên trong cluster mà không đặc biệt quan tâm đến “target” của activity đó. Ngược lại, auditing là cách log và theo dõi những activity cụ thể xảy ra trên các target cụ thể. Ví dụ, logging có thể theo dõi “mọi query chậm” mà không quan tâm query được chạy trên table nào, còn auditing có thể theo dõi “mọi thay đổi trên table xyz”. Xem phần *Implementing auditing* để biết thêm chi tiết.

* **pgBadger là gì?**

  pgBadger là một external command có thể inspect PostgreSQL text log và build một dashboard với activity của cluster. Xem phần *Extracting information from logs – pgBadger* để biết thêm chi tiết.

* **Database administrator quyết định nơi gửi PostgreSQL log bằng cách nào?**

  PostgreSQL cung cấp một tập logging configuration parameter, chẳng hạn `log_directory` và `log_filename`, để xác định nơi PostgreSQL sẽ lưu log. Xem phần *Where to log* để biết thêm chi tiết.

* **Logging collector là gì?**

  Logging collector là một PostgreSQL process đặc biệt, thu thập log mà daemon ghi vào standard error rồi redirect thông tin đó đến location thích hợp (ví dụ: một file trên disk). Xem phần *Where to log* để biết thêm chi tiết.

* **pgAudit extension là gì?**

  PgAudit là một extension cho phép audit các query cụ thể ở session mode hoặc user mode. Xem phần *Configuring PostgreSQL to exploit PgAudit* để biết thêm chi tiết.

## Tài liệu tham khảo

* Tài liệu chính thức của pgBadger: https://pgbadger.darold.net/documentation.html
* Official code repository của PgAudit: https://github.com/pgaudit/pgaudit
* Tài liệu chính thức về log setting của PostgreSQL: https://www.postgresql.org/docs/current/runtime-config-logging.html
* Website và documentation chính thức của PgAudit: https://www.pgaudit.org/

## Tìm hiểu thêm trên Discord

Để tham gia Discord community của cuốn sách này — nơi bạn có thể chia sẻ feedback, đặt câu hỏi cho tác giả và tìm hiểu về các bản phát hành mới — hãy theo QR code bên dưới:

https://discord.gg/jYWCjF6Tku

![Mã QR Discord](../assets/part-057-qr-discord.png)

# 15. Backup and Restore

Dù hardware và software của bạn vững chắc đến đâu, sớm hay muộn bạn cũng sẽ cần quay lại một thời điểm trong quá khứ để khôi phục data đã vô tình bị xóa hoặc hư hỏng. Đó là mục đích của backup — cung cấp một bản copy an toàn mà bạn có thể giữ trong một khoảng thời gian cụ thể, đủ để khôi phục khi mất data. Là một database cluster cấp enterprise, PostgreSQL cung cấp một tập tool chuyên biệt để database administrator xử lý việc backup và restore, và chapter này sẽ trình bày tất cả tool chính mà bạn có thể tận dụng để bảo đảm data của mình tồn tại sau mọi sự cố vô ý.

Backup và restore không phải là chủ đề quá phức tạp, nhưng đây là phần nền tảng trong mọi production system và đòi hỏi planning cẩn thận. Thực tế, với một bản backup, bạn đang giữ một bản copy chính xác khác của database phòng khi có sự cố nghiêm trọng; bản copy bổ sung này sẽ tiêu tốn resource, đáng kể nhất là storage space. Quyết định cần bao nhiêu bản copy bổ sung, thu thập chúng thường xuyên đến mức nào và phải giữ chúng trong bao lâu là việc cần được cân nhắc kỹ, nằm ngoài scope của chapter này. Trong chapter này, chúng ta sẽ xem xét các cách chính để thực hiện backup, theo logical hoặc physical, cùng tất cả tool mà một PostgreSQL distribution cung cấp để bạn quản lý backup.

Trong chapter này, chúng ta sẽ đề cập đến các chủ đề sau:

* Giới thiệu các loại backup và restore khác nhau
* Tìm hiểu logical backup
* Tìm hiểu physical backup

## Technical requirements

Bạn cần biết những nội dung sau để hoàn thành chapter này:

* Cách tương tác với command-line tool
* Cách inspect filesystem và directory `PGDATA`

Các ví dụ trong chapter có thể chạy trên Docker image `chapter_15`, có thể tìm thấy trong GitHub repository của cuốn sách: https://github.com/PacktPublishing/Learn-PostgreSQL-Second-Edition. Để biết hướng dẫn install và sử dụng các Docker image có trong cuốn sách, hãy tham khảo phần hướng dẫn ở Chapter 1, *Introduction to PostgreSQL*.

## Giới thiệu các loại backup và restore

Có hai loại backup chính áp dụng cho PostgreSQL: **logical backup** và **physical backup** (còn gọi là **hot backup**). Tùy thuộc vào loại backup bạn chọn, quy trình restore sẽ khác nhau.

PostgreSQL cung cấp đầy đủ các tool tích hợp để thực hiện logical backup kiểu truyền thống, và trong hầu hết trường hợp như vậy là đủ. Tuy nhiên, PostgreSQL có thể dễ dàng được configure để hỗ trợ physical backup, vốn hữu ích khi cluster trở nên rất lớn, cũng như khi bạn có những nhu cầu đặc biệt, như sẽ thấy ở phần sau của chapter này.

Nhưng sự khác biệt giữa hai phương thức backup này là gì? Như bạn có thể hình dung, cả hai đều đạt cùng một mục đích: cho phép bạn có được một “copy” data có thể sử dụng để restore ở một nơi nào đó. Sự khác biệt giữa hai chiến lược backup nằm ở cách data được trích xuất từ cluster.

Logical backup hoạt động tương tự một database client yêu cầu toàn bộ data trong database, lần lượt theo từng table, rồi lưu kết quả vào một storage system. Nó giống như một application mở một transaction và thực hiện `SELECT` trên mọi table, lưu data thu được trên disk. Tất nhiên, thực tế phức tạp hơn nhiều, nhưng ví dụ này cho bạn một ý tưởng đơn giản về những gì diễn ra bên dưới.

Loại backup này là “logical” vì nó chạy song song với các database connection và activity khác, dưới dạng một dedicated client application, đồng thời dựa vào database để cung cấp data nhất quán về mặt logical. Thực tế, backup được thực hiện bên trong một snapshot của database để giữ data consistent.

Ưu điểm của chiến lược backup này là (i) dễ triển khai vì PostgreSQL cung cấp mọi software cần thiết để thực hiện full backup, (ii) consistent, và (iii) có thể restore khá dễ dàng.

Tuy nhiên, phương thức backup này cũng có một vài nhược điểm: vì được thực hiện song song với các database activity khác, nó có thể làm chậm (hoặc bị làm chậm) cùng với các transaction concurrent khác đang active. Hơn nữa, database phải theo dõi backup process đang diễn ra mà không phá hỏng snapshot trong suốt thời gian backup chạy. Cuối cùng, backup set được tạo ra consistent tại thời điểm backup bắt đầu; nghĩa là nếu backup cần rất nhiều thời gian để hoàn tất, các thay đổi data xảy ra trong thời gian đó có thể không xuất hiện trong backup (vì backup phải consistent).

Mặt khác, physical backup ít xâm lấn hơn đối với các connection và transaction khác: backup yêu cầu một bản copy ở mức file của nội dung `PGDATA` — chủ yếu là database file (`PGDATA/base`) và **Write Ahead Logs (WALs)** từ instance bắt đầu backup đến instance kết thúc backup. Kết quả sẽ là một bản copy database không consistent, cần được xử lý cẩn thận để restore đúng cách. Về cơ bản, restore sẽ tiến hành như thể database đã crash và sẽ redo mọi transaction (được trích xuất từ WAL) để đạt được một state consistent.

Loại backup này phức tạp hơn nhiều để setup, và mặc dù bạn có thể tự thực hiện như sẽ thấy trong chapter này, một số tool đã xuất hiện để giúp bạn thực hiện loại backup này theo cách chuyên nghiệp và đáng tin cậy hơn. Ưu điểm chính của chiến lược backup này là tính ít xâm lấn — database sẽ không nhận thấy activity đặc biệt nào liên quan đến backup, ngoại trừ storage I/O bandwidth cần thiết để thực hiện file-level copy. Một ưu điểm quan trọng khác của chiến lược này là nó cho phép **point-in-time recovery (PITR)**, nhờ đó database administrator có thể khôi phục database về bất kỳ instance nào kể từ backup ban đầu.

Còn một consideration khác cần tính đến khi thiết kế chiến lược backup: logical backup được cho là luôn hoạt động, bất kể database version bạn đang chạy là gì (với giả định rằng bạn đang chạy latest version) và, ở một mức độ nào đó, bất kể target database có phải PostgreSQL hay không. Mặt khác, physical backup chỉ hoạt động giữa các instance PostgreSQL có cùng major version và cùng operating system architecture.

Trong phần tiếp theo, bạn sẽ học cách thực hiện cả hai phương thức backup cũng như cách restore một backup. Trước tiên, chúng ta sẽ bắt đầu với logical backup.

## Tìm hiểu logical backup

PostgreSQL cung cấp mọi tool cần thiết để thực hiện logical backup và restore. Nhiều operating system, bao gồm FreeBSD và Debian GNU/Linux, cung cấp script và wrapper cho các tool backup và restore của PostgreSQL để giúp system administrator lên lịch backup và restore. Các script và wrapper như vậy sẽ không được giải thích ở đây. Để biết thêm thông tin, hãy đọc package documentation về PostgreSQL của operating system bạn đang dùng.
