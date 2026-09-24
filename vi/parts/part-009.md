Bạn không bị buộc phải chỉ dùng một configuration file; trên thực tế, có các directive cụ thể để include những configuration file khác. Configuration của cluster sẽ được trình bày chi tiết ở một chương sau.

PostgreSQL HBA file (`pg_hba.conf`) là một text file khác chứa các quy tắc cho phép connection: nó liệt kê các database, user và network được phép connect đến cluster của bạn. Phương thức HBA có thể được xem như một firewall được nhúng trong PostgreSQL. Ví dụ, sau đây là một đoạn trích từ file `pg_hba.conf`:

```text
hosts   all luca 192.168.222.1/32 md5
hostssl all enrico 192.168.222.1/32 md5
```

Nói ngắn gọn, các dòng trên có nghĩa là user `luca` có thể connect đến bất kỳ database nào trong cluster từ máy có địa chỉ IPv4 `192.168.222.1`, còn user `enrico` có thể connect đến bất kỳ database nào từ cùng máy đó nhưng chỉ qua connection được mã hóa bằng SSL. Tất cả rule có trong `pg_hba.conf` sẽ được trình bày chi tiết ở một chương sau, nhưng hiện tại chỉ cần biết rằng file này hoạt động như một “danh sách các firewall rule” cho những connection đi vào.

## Tóm tắt

PostgreSQL có thể xử lý nhiều database trong một cluster duy nhất, được phục vụ từ phần disk storage nằm trong một directory duy nhất có tên `PGDATA`. Cluster chạy nhiều process khác nhau; một process đặc biệt có tên `postmaster` chịu trách nhiệm spawn các process khác, mỗi process cho một client connection, và theo dõi trạng thái của các process maintenance.

Configuration của cluster được quản lý thông qua các text-based configuration file, trong đó file chính là `postgresql.conf`. Có thể filter incoming user connection bằng các rule được đặt trong text file `pg_hba.conf`.

Bạn có thể tương tác với trạng thái của cluster thông qua tool `pg_ctl` hoặc, tùy operating system, bằng các program khác được cung cấp như `service` hoặc `systemctl`.

Chương này đã trình bày những thông tin cần thiết để bạn không chỉ có thể install PostgreSQL mà còn có thể start và stop nó thường xuyên, integrate nó với operating system, và connect đến cluster.

Ở chương tiếp theo, bạn sẽ học cách manage user và connection.

## Kiểm tra kiến thức

* **`pg_ctl` command là gì?**

  `pg_ctl` là một command được cung cấp cùng PostgreSQL, cho phép bạn start, restart, stop cluster và thực hiện các action khác trên cluster. Nó thường được dùng để manage toàn bộ cluster. Xem phần về `pg_ctl` để biết thêm chi tiết.

* **Template database là gì?**

  Template database là một database có thể được dùng làm cơ sở để clone một database khác (mới), database mới đó ban đầu sẽ bao gồm cùng các object. Xem phần *The template databases* để biết thêm chi tiết.

* **`psql` command là gì?**

  `psql` là client application chính thức để connect đến một PostgreSQL database. Đây là một command-line application có thể được dùng để nhập các SQL statement và lấy result từ cluster. Nó được cung cấp trong mọi version của PostgreSQL. Xem phần *The psql command-line client* để biết thêm chi tiết.

* **Connection string là gì?**

  Connection string là một URI chỉ định tất cả property cần thiết để connect đến một database, thường bao gồm username, host, database, v.v. Xem phần *The connection string scction* để biết thêm chi tiết.

* **Các psql special command là gì?**

  Special command là tất cả short command bắt đầu bằng ký hiệu backslash, chẳng hạn `\d`. Đây là các command mang tính thông tin và chỉ hợp lệ bên trong `psql client`. Xem phần *A glance at the psql commands* để biết thêm chi tiết.

## Tài liệu tham khảo

* PostgreSQL PGDATA disk layout: https://www.postgresql.org/docs/current/storage-file-layout.html
* PostgreSQL initdb official documentation: https://www.postgresql.org/docs/current/app-initdb.html
* PostgreSQL pg_ctl official documentation: https://www.postgresql.org/docs/current/app-pg-ctl.html
* The pgAdmin4 graphical client for PostgreSQL: https://www.pgadmin.org/

## Tìm hiểu thêm trên Discord

Để tham gia Discord community của cuốn sách này, nơi bạn có thể chia sẻ feedback, đặt câu hỏi cho tác giả và tìm hiểu về các bản phát hành mới, hãy làm theo mã QR bên dưới:

https://discord.gg/jYWCjF6Tku

# 3. Managing Users and Connections

PostgreSQL là một hệ thống phức tạp bao gồm user, database và data. Để có thể tương tác với một database trong cluster, bạn cần có ít nhất một user. Theo mặc định, khi install một cluster mới, một administrator user duy nhất (có tên `postgres`) được tạo. Mặc dù có thể xử lý tất cả connection, application và database bằng user administrator duy nhất đó, tốt hơn nhiều về mặt security và privilege isolation nếu tạo các user khác nhau với property, privilege và login credential khác nhau cho từng task cụ thể.

PostgreSQL cung cấp một cấu trúc user-management rất phong phú, và một user có thể đồng thời được đưa vào nhiều group khác nhau. Hơn nữa, các group có thể được lồng bên trong những group khác, nhờ đó bạn có thể biểu diễn account model rất chính xác. Nhờ sự biểu diễn chính xác này, cũng như việc mỗi user và group đều có thể được gán các property và privilege khác nhau, bạn có thể áp dụng permission fine-grained cho từng user trong database, tùy theo task và activity cụ thể đang thực hiện.

Chương này giới thiệu các concept phía sau user, group và mối quan hệ giữa chúng. Chương chủ yếu tập trung vào login property của role (dù là user hay group) và cách PostgreSQL có thể ngăn những user cụ thể connect đến những database cụ thể.

Chương này đề cập đến các chủ đề chính sau:

* Introduction to users and groups
* Managing roles
* Managing incoming connections at the role level

## Technical requirements

Các ví dụ trong chương có thể chạy trên standalone Docker image mà bạn có thể tìm thấy trong GitHub repository của cuốn sách: https://github.com/PacktPublishing/Learn-PostgreSQL-Second-Edition.

Để biết hướng dẫn install và sử dụng Docker image cho cuốn sách này, hãy tham khảo Chapter 1, *Introduction to PostgreSQL*.

## Introduction to users and groups

PostgreSQL phân biệt user với group của user: user đại diện cho một người hoặc một application, có thể connect đến cluster và thực hiện activity; group đại diện cho một tập hợp user chia sẻ một số property chung, phổ biến nhất là permission trên các object của cluster.

Để connect đến một PostgreSQL database một cách interactive hoặc thông qua application, bạn cần có login credential. Cụ thể, một database user, tức user được phép connect đến database cụ thể đó, phải tồn tại.

Database user có phần tương tự operating system user: chúng có username và password (được encrypted), đồng thời được PostgreSQL cluster biết đến. Tương tự operating system user, database user có thể được group vào các user group để dễ manage hơn.

Trong SQL, và do đó cả trong PostgreSQL, concept của một user account đơn lẻ và concept của một group account đều được bao hàm trong concept role.

Một role có thể là một account đơn lẻ, một group account, hoặc thậm chí cả hai tùy theo cách bạn thiết kế; tuy nhiên, để dễ manage hơn, một role nên thể hiện một và chỉ một concept tại một thời điểm: nghĩa là nó nên là một user đơn lẻ hoặc một group đơn lẻ, không phải cả hai.

> Mặc dù một role có thể đồng thời được dùng như một group hoặc một user đơn lẻ, chúng tôi đặc biệt khuyến khích bạn tách riêng hai concept user và group; điều này sẽ đơn giản hóa việc manage infrastructure của bạn.

Mọi role phải có một name hoặc identifier duy nhất, thường được gọi là username.

Một role đại diện cho một tập hợp database permission và connection property. Hai element này là orthogonal. Bạn có thể thiết lập một role đơn giản như một container cho các role khác, cấu hình các role được chứa để giữ các permission đã gán; hoặc bạn có thể có một role giữ toàn bộ permission cho các role được chứa; hoặc kết hợp hai cách tiếp cận này.

Điều quan trọng là phải hiểu rằng role được định nghĩa ở cluster level, còn permission được định nghĩa ở database level. Điều này có nghĩa là cùng một role có thể có privilege và property khác nhau tùy theo database mà nó đang sử dụng (chẳng hạn, được phép connect đến database này nhưng không được phép connect đến database khác).

> Vì role được định nghĩa ở cluster level, nó phải có name duy nhất trong toàn bộ cluster.

## Managing roles

Role có thể được manage bằng ba SQL statement chính: `CREATE ROLE` để tạo một role từ đầu, `ALTER ROLE` để thay đổi một số property của role (ví dụ login password), và `DROP ROLE` để xóa một role hiện có.

> PostgreSQL cung cấp các operating system tool để manage role: `createuser` và `dropuser`. Cả hai command này đều mở một connection đến cluster và thực hiện các SQL command nêu trên; vì vậy, việc sử dụng các tool này sẽ không được giải thích trong chương này.

Để sử dụng SQL statement nhằm tạo role mới rồi manage chúng, cần connect đến một database trong cluster. Có thể dùng superuser role `postgres` cho mục đích đó, ít nhất là ban đầu, vì role này được tạo khi database cluster được initialize. Dùng role `postgres` và một template database là cách phổ biến nhất để tạo các role ban đầu của bạn.

Một role được định danh bằng một string đại diện cho role name, hoặc chính xác hơn là account name của role đó. Name này phải unique trên toàn system, nghĩa là bạn không thể có hai role khác nhau với name giống hệt nhau. Name phải gồm chữ cái, chữ số và một số symbol, chẳng hạn underscore.

## Creating new roles

Để tạo một role mới, dù là một user account đơn lẻ hay một group container, bạn cần dùng `CREATE ROLE` statement. Statement này có synopsis ngắn gọn sau đây và có một parameter bắt buộc là username của role:

```sql
CREATE ROLE name [ [ WITH ] option [ ... ] ]
```

Các option có thể chỉ định trong statement này trải từ account password, khả năng login interactive, đến superuser privilege. Hãy nhớ rằng, không giống các system khác, trong PostgreSQL bạn có thể có bao nhiêu superuser tùy ý, và mọi superuser đều có cùng mức quyền hạn tuyệt đối trên cluster.

Gần như mọi option của `CREATE ROLE` statement đều có form positive để thêm capability cho role, và form negative (có prefix `NO`) để loại capability đó khỏi role. Ví dụ, option `SUPERUSER` thêm capability hoạt động như cluster superuser, còn option `NOSUPERUSER` loại capability đó khỏi role.

Trong chương này, chúng ta sẽ tập trung vào login capability, tức một tập option hạn chế cho phép role login vào cluster. Các option khác sẽ được thảo luận trong Chapter 10, *Users, Roles, and Database Security*, vì chúng liên quan nhiều hơn đến security feature của role.

> Nếu bạn quên một option tại thời điểm `CREATE ROLE` thì sao? Nếu bạn đổi ý và muốn loại một option khỏi role hiện có thì sao? Có statement `ALTER ROLE` cho phép bạn (với tư cách cluster superuser) modify role hiện có mà không cần drop rồi tạo lại. Statement này sẽ được trình bày trong Chapter 10, *Users, Roles, and Database Security*, cùng một số option thú vị khác cho role.

## Role passwords, connections, and availability

Mọi connection đến PostgreSQL đều phải được thực hiện đến một database cụ thể, bất kể user mở connection là ai. Connect đến một database trong cluster có nghĩa là role phải authenticate chính nó, do đó phải có một authentication mechanism; username và password là những mechanism kinh điển nhất.

Khi user cố gắng connect đến một database, PostgreSQL kiểm tra login credential và một số property khác của user để bảo đảm user được phép login và có credential hợp lệ.

Các option chính cho phép bạn thao tác và manage login attempt gồm:

* `PASSWORD` hoặc `ENCRYPTED PASSWORD` là các option tương đương và cho phép bạn set login password cho role. Cả hai option tồn tại để backward compatibility với các PostgreSQL version cũ hơn, nhưng ngày nay cluster luôn lưu role password ở dạng encrypted, vì vậy việc dùng `ENCRYPTED PASSWORD` không thêm giá trị nào so với option `PASSWORD`.
* `PASSWORD NULL` buộc tường minh một password null (không phải password rỗng), ngăn user login bằng bất kỳ password nào. Có thể dùng option này để từ chối password-based authentication.
* `CONNECTION LIMIT <n>` cho phép user mở không quá `<n>` connection đồng thời đến cluster, không phụ thuộc vào database cụ thể nào. Điều này thường hữu ích để ngăn user sử dụng lãng phí resource trên cluster.
* `VALID UNTIL` cho phép bạn chỉ định một thời điểm (trong tương lai) khi role sẽ expire.

Việc set password cho một role cụ thể không có nghĩa là role đó sẽ có thể connect đến cluster: để được phép login interactive, role cũng phải có option `LOGIN`. Nói cách khác, statement sau đây sẽ không cho phép user login:

```text
postgres=# CREATE ROLE luca
              WITH PASSWORD 'xxx';
```

Option mặc định là `NOLOGIN` (ngăn interactive login). Vì vậy, để định nghĩa interactive user, hãy nhớ thêm option `LOGIN` khi tạo role:

```text
template1=# CREATE ROLE luca
              WITH LOGIN PASSWORD 'xxx';
```

Có thể viết nhiều option theo bất kỳ thứ tự nào, vì vậy code ở trên biểu diễn cùng statement, nhưng ở dạng kém dễ đọc hơn đối với con người:

```text
postgres=# CREATE ROLE luca
              WITH PASSWORD 'xxx' LOGIN;
```

Option `VALID UNTIL` cho phép bạn định nghĩa một date hoặc thậm chí một timestamp (tức một thời điểm) trong tương lai, khi password của role sẽ expire và role không còn được phép login vào cluster. Điều này có thể hữu ích khi đánh dấu một tập user sẽ bị loại trong tương lai.

Dĩ nhiên, option này chỉ có ý nghĩa với interactive role, tức những role có capability `LOGIN`. Ví dụ, role sau đây sẽ bị ngăn login sau Christmas 2030:

```text
postgres=# CREATE ROLE luca
              WITH LOGIN PASSWORD 'xxx'
              VALID UNTIL '2030-12-25 23:59:59';
```

## Using a role as a group

Một group là một role chứa các role khác. Đơn giản vậy thôi!

Thông thường, khi muốn tạo một group, tất cả việc bạn cần làm là tạo một role không có option `LOGIN`, sau đó lần lượt thêm từng member vào role chứa. Việc thêm một role vào role chứa biến role chứa thành một group.

Để tạo một role làm member của một group cụ thể, có thể dùng option `IN ROLE`. Option này nhận name của group (đến lượt nó cũng là một role) mà role mới tạo sẽ trở thành member. Ví dụ, trong code block sau, bạn có thể thấy việc tạo group `book_authors` và thêm các role member `luca` và `enrico`:

```text
postgres=# CREATE ROLE book_authors
              WITH NOLOGIN;
CREATE ROLE
postgres=# CREATE ROLE luca
 WITH LOGIN PASSWORD 'xxx'
 IN ROLE book_authors;
CREATE ROLE
postgres=# CREATE ROLE enrico
              WITH LOGIN PASSWORD 'xxx'
              IN ROLE book_authors;
CREATE ROLE
```

> Mệnh đề `IN GROUP` của `CREATE ROLE` là một obsolete synonym của mệnh đề `IN ROLE`.

Cũng có thể thêm member vào group bằng special `GRANT` statement. `GRANT` statement là SQL statement tổng quát cho phép fine-tune privilege (sẽ nói thêm trong Chapter 10, *Users, Roles, and Database Security*); PostgreSQL mở rộng SQL syntax để cho phép grant một role cho role khác. Khi bạn grant một role cho role khác, role nhận sẽ trở thành member của role được grant. Nói cách khác, giả sử mọi role đã tồn tại mà chưa có association cụ thể nào, dòng sau thêm role `enrico` vào group `book_authors`:

```text
postgres=# GRANT    book_authors TO enrico;
```

Mỗi group có thể có một hoặc nhiều admin member, là những member được phép thêm member mới vào group. Option `ADMIN` cho phép user chỉ định member sẽ được gắn vai trò administrator của group mới tạo. Chẳng hạn, trong code block sau, bạn có thể thấy việc tạo group mới tên `book_reviewers` với `luca` làm administrator; điều này có nghĩa là user `luca`, dù không phải cluster superuser, sẽ có thể thêm member mới vào group `book_reviewers`:

```text
postgres=# CREATE ROLE book_reviewers
              WITH NOLOGIN
              ADMIN luca;
CREATE ROLE
```

Rõ ràng, option `ADMIN` chỉ có thể được dùng trong `CREATE ROLE` nếu administrator role đã tồn tại; trong ví dụ này, role `luca` phải được tạo trước group, vì role đó sẽ là administrator.

Statement `GRANT` có thể giải quyết vấn đề này: mệnh đề `WITH ADMIN OPTION` cho phép role membership đi kèm administrative privilege.

Ví dụ, đoạn code sau cho thấy cách biến user `enrico` thành một administrator khác của group `book_reviewers`. Lưu ý rằng bạn phải viết đầy đủ `WITH ADMIN OPTION`, như được trình bày ở đây:

```text
postgres=# GRANT book_reviewers
              TO enrico
              WITH ADMIN OPTION;
GRANT ROLE
```

Điều gì xảy ra nếu một group role có option `LOGIN`? Group đó vẫn là một role container, nhưng cũng có thể hoạt động như một single user account với khả năng login. Dù có thể làm như vậy, thông lệ phổ biến hơn là từ chối quyền login của group role để tránh nhầm lẫn.

## Removing an existing role

Để xóa một role hiện có, bạn cần dùng `DROP ROLE` statement. Statement này có synopsis rất đơn giản:

```sql
DROP ROLE [ IF EXIST ] name [, ...]
```

Bạn chỉ cần chỉ định role name muốn xóa; hoặc nếu cần xóa nhiều role, bạn có thể chỉ định chúng dưới dạng một danh sách phân tách bằng dấu phẩy.

Để được xóa, role phải tồn tại; vì vậy, nếu cố remove một role không tồn tại, bạn sẽ nhận được error:

```text
postgres=# DROP ROLE this_role_does_not_exist;
ERROR:    role "this_role_does_not_exist" does not exist
```
