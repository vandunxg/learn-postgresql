## Các quy ước được sử dụng

Có một số quy ước về văn bản được sử dụng xuyên suốt cuốn sách này.

CodeInText: Dùng để chỉ các từ mã trong văn bản, tên table trong database, tên folder, filename, phần mở rộng file, pathname, dummy URL, user input và Twitter handle. Ví dụ: “Mount file disk image `WebStorm-10*.dmg` đã tải xuống thành một disk khác trong hệ thống của bạn.”

Một block code được trình bày như sau:

```sql
   SELECT rolname, rolcanlogin,
                  rolconnlimit, rolpassword
                  FROM pg_roles
                  WHERE rolname = 'luca';
```

Khi muốn thu hút sự chú ý của bạn đến một phần cụ thể trong code block, các dòng hoặc mục liên quan sẽ được in đậm:

```sql
   SELECT line_number, type,
                           database, user_name,
                           address, auth_method
                           FROM pg_hba_file_rules;
```

Mọi input hoặc output trên command line được viết như sau:

```bash
$ sudo cat $PGDATA/rejected_users.txt
```

**Bold:** Dùng để chỉ một thuật ngữ mới, một từ quan trọng hoặc các từ xuất hiện trên màn hình. Chẳng hạn, các từ trong menu hoặc hộp thoại sẽ xuất hiện trong văn bản theo cách này. Ví dụ: “Chọn **System info** từ panel **Administration**.”

> **Cảnh báo hoặc ghi chú quan trọng** được hiển thị như thế này.

> **Mẹo và thủ thuật** được hiển thị như thế này.

## Liên hệ

Chúng tôi luôn hoan nghênh feedback từ độc giả.

**General feedback:** Gửi email đến `feedback@packtpub.com` và ghi tên sách trong subject của email. Nếu có câu hỏi về bất kỳ khía cạnh nào của cuốn sách, vui lòng email cho chúng tôi tại `questions@packtpub.com`.

**Errata:** Mặc dù chúng tôi đã cố gắng hết sức để bảo đảm nội dung chính xác, sai sót vẫn có thể xảy ra. Nếu phát hiện một lỗi trong cuốn sách này, chúng tôi sẽ rất biết ơn nếu bạn báo cho chúng tôi. Vui lòng truy cập http://www.packtpub.com/submit-errata, nhấp vào **Submit Errata** và điền vào biểu mẫu.

**Piracy:** Nếu bắt gặp các bản sao bất hợp pháp của bất kỳ tác phẩm nào của chúng tôi dưới bất kỳ hình thức nào trên Internet, chúng tôi sẽ rất biết ơn nếu bạn cung cấp địa chỉ hoặc tên website nơi bạn tìm thấy chúng. Vui lòng liên hệ `copyright@packtpub.com` và gửi kèm link đến tài liệu.

**Nếu bạn quan tâm đến việc trở thành author:** Nếu có một chủ đề mà bạn am hiểu và muốn viết hoặc đóng góp cho một cuốn sách, vui lòng truy cập http://authors.packtpub.com.

## Chia sẻ suy nghĩ của bạn

Sau khi đọc *Learn PostgreSQL*, chúng tôi rất muốn biết suy nghĩ của bạn! Vui lòng nhấp vào đây để đi thẳng đến trang review trên Amazon của cuốn sách này và chia sẻ feedback.

Review của bạn rất quan trọng đối với cộng đồng công nghệ và sẽ giúp chúng tôi bảo đảm rằng mình đang cung cấp nội dung chất lượng cao.

## Tải bản PDF miễn phí của cuốn sách này

Cảm ơn bạn đã mua cuốn sách này!

Bạn thích đọc khi di chuyển nhưng không thể mang theo sách in ở mọi nơi?

Sách điện tử bạn mua không tương thích với thiết bị mà bạn lựa chọn?

Đừng lo, giờ đây với mỗi cuốn sách Packt, bạn sẽ nhận được một phiên bản PDF không DRM của cuốn sách đó miễn phí.

Đọc ở bất kỳ đâu, bất kỳ nơi nào, trên bất kỳ thiết bị nào. Tìm kiếm, sao chép và dán code từ những cuốn sách kỹ thuật yêu thích trực tiếp vào ứng dụng của bạn.

Các quyền lợi không dừng ở đó; bạn còn có thể nhận quyền truy cập độc quyền vào các chương trình giảm giá, newsletter và nội dung miễn phí hấp dẫn trong inbox hằng ngày.

Hãy làm theo các bước đơn giản sau để nhận các quyền lợi:

1. Quét QR code hoặc truy cập link bên dưới:

   https://packt.link/free-ebook/9781837635641

2. Gửi proof of purchase của bạn.
3. Vậy là xong! Chúng tôi sẽ gửi bản PDF miễn phí và các quyền lợi khác trực tiếp đến email của bạn.

# 1. Giới thiệu về PostgreSQL

PostgreSQL là một relational database open source nổi tiếng, và motto của dự án nêu rõ mục tiêu trở thành *the most advanced open-source database in the world*.

Những phẩm chất chính thu hút số lượng lớn user mới mỗi năm và khiến các user hiện tại tiếp tục nhiệt tình với PostgreSQL là tính ổn định vững chắc, khả năng scalability và tính an toàn, cùng với tất cả các tính năng mà một database management system cấp enterprise phải cung cấp.

Mặc dù PostgreSQL là một relational database, ecosystem của nó đã phát triển theo thời gian, tạo ra một platform phong phú với các extension, tool và language được kết nối với nhau bởi các community trải rộng khắp thế giới.

PostgreSQL là một open-source project và được phát triển hoàn toàn trong thế giới open source. Điều đó có nghĩa là không có một thực thể duy nhất nào phụ trách project, và kết quả là PostgreSQL không phải là một commercial product. Nói cách khác, PostgreSQL thuộc về tất cả mọi người, và bất kỳ ai cũng có thể đóng góp cho nó. Nhờ một BSD-style license rất permissive, PostgreSQL có thể được sử dụng trong bất kỳ project hoặc scenario nào, dù open source hay closed source.

Tất nhiên, đóng góp cho một project có quy mô và độ phức tạp như vậy đòi hỏi kinh nghiệm về software development, database concept và dĩ nhiên là thái độ tích cực đối với open source cũng như các nỗ lực cộng tác. Bản chất open source có nghĩa là PostgreSQL sẽ tiếp tục tồn tại gần như mãi mãi mà không có nguy cơ một công ty duy nhất phá sản rồi kéo database này chìm theo.

Các developer chính thức của PostgreSQL thường được gọi là **PostgreSQL Global Development Group (PGDG)**. Đây là những developer, sau khi thảo luận và phối hợp, triển khai các tính năng chính và tạo ra các release mới. PGDG phát hành một production release mới mỗi năm một lần, thường vào quý cuối cùng của năm.

Tại thời điểm viết sách, PostgreSQL 16 là production release mới nhất của database engine tuyệt vời này, và như thường lệ, các nỗ lực cho release tiếp theo (PostgreSQL 17) vẫn đang được tiến hành.

Cuốn sách này tập trung vào cách bạn có thể khai thác tốt nhất PostgreSQL, bắt đầu từ những điều cơ bản (quản lý user, data table, index, v.v.) rồi tiến tới các tính năng thú vị và phức tạp nhất (chẳng hạn như replicate data để ngăn ngừa thảm họa). Chúng tôi sẽ tiếp cận theo hướng thực hành, với nhiều example, để giúp độc giả hiểu rõ hơn từng concept và tiếp thu kiến thức theo cách thú vị, nhanh chóng hơn. Khi kết thúc, bạn sẽ có thể quản trị đầy đủ một PostgreSQL cluster và, nhờ các resource được chỉ ra trong mỗi chapter, bạn sẽ có thể nghiên cứu thêm nhiều tính năng hơn nữa.

> **Cuốn sách này trình bày PostgreSQL 16, nhưng các concept được giải thích trong sách cũng có thể áp dụng cho các version mới hơn (cũng như các version cũ hơn nếu có cùng các feature).** Trên thực tế, dù một số tool có thể thay đổi trong các release tương lai (ví dụ: thêm hoặc bỏ một số option), các concept cơ bản được trình bày trong sách nhìn chung sẽ vẫn gần như giữ nguyên bất kể version PostgreSQL nào.

Chapter này sẽ giới thiệu database open source tuyệt vời này, bắt đầu từ lịch sử và mục tiêu của project; bạn sẽ học các thuật ngữ PostgreSQL cơ bản, vốn rất quan trọng để giúp bạn tìm kiếm documentation và hiểu các error message chính khi cần. Cuối cùng, bạn sẽ thấy cách cài đặt PostgreSQL theo nhiều cách khác nhau, nhờ đó có được kiến thức cơ bản về cách cài đặt nó trên các platform và trong các context khác nhau.

Các chủ đề sau được trình bày trong chapter này:

- PostgreSQL at a glance
- Exploring PostgreSQL terminology
- Installing PostgreSQL 16 or higher

## Yêu cầu kỹ thuật

Bạn có thể tìm thấy code cho chapter này trong GitHub repository sau: https://github.com/PacktPublishing/Learn-PostgreSQL-Second-Edition.

## PostgreSQL at a glance

Là một relational database, PostgreSQL cung cấp rất nhiều feature, và khá khó để “làm PostgreSQL instance sợ hãi”.

Trên thực tế, một instance duy nhất có thể chứa hơn 4 tỷ database riêng lẻ, mỗi database có total size không giới hạn và có capacity cho hơn 1 tỷ table, mỗi table chứa 32 TB data. Hơn nữa, nếu bạn lo rằng các giới hạn trên vẫn chưa đủ, hãy nhớ rằng một table duy nhất có thể có 1.600 column, mỗi column có kích thước 1 GB, cùng số lượng multi-column index không giới hạn (tối đa 32 column). Tóm lại, PostgreSQL có thể lưu trữ nhiều data hơn những gì bạn có thể hình dung!

Mặc dù PostgreSQL có thể xử lý lượng data khổng lồ như vậy, điều đó không có nghĩa là bạn nên dùng nó làm nơi đổ mọi thứ hoặc storage cho tất cả mọi loại dữ liệu: để đạt performance tốt với một số database lớn, bạn cần hiểu PostgreSQL và các feature của nó, từ đó có thể tổ chức và quản lý dataset của mình.

PostgreSQL hoàn toàn **ACID-compliant** (xem box bên dưới) và có nền tảng rất vững chắc về data integrity và concurrency. PostgreSQL đi kèm một procedural language có tên `PL/PgSQL`, có thể dùng để viết các đoạn code có thể tái sử dụng, chẳng hạn như function và procedure; nó cũng hỗ trợ before và after trigger, view, materialized view, partitioned table, foreign data wrapper, multiple schema, generated column, v.v. Tất cả các concept này sẽ được giải thích trong những chapter tiếp theo.

> **ACID** là acronym của một tập hợp các thuộc tính, dùng để chỉ rằng database engine cung cấp atomicity, consistency, isolation và durability. Atomicity có nghĩa là một database operation phức tạp được xử lý như một instruction duy nhất, ngay cả khi operation đó được cấu thành từ nhiều operation khác nhau. Consistency có nghĩa là data bên trong database luôn được duy trì nhất quán và không bị hỏng do các operation được thực hiện không đầy đủ. Isolation cho phép database xử lý concurrency theo “đúng cách”, tức là không làm data bị hỏng do các thay đổi xen kẽ. Cuối cùng, durability có nghĩa là database engine được cho là phải bảo vệ data mà nó chứa, kể cả trong trường hợp xảy ra lỗi software hoặc hardware, trong phạm vi có thể.

PostgreSQL có thể được mở rộng bằng các embedded language khác, chẳng hạn như Perl, Python, Java và thậm chí Bash! Và nếu bạn cho rằng database chưa cung cấp đủ feature, bạn có thể cắm thêm extension để có các behavior và enhancement khác nhau, chẳng hạn như Geospatial Information System (GIS), scheduled job, data type đặc biệt và các utility nói chung. Những utility và enhancement như vậy sẽ không được trình bày trong cuốn sách này, nhưng nhờ kiến thức mà sách cung cấp, bạn sẽ có thể khai thác online documentation của các utility đó để sử dụng chúng hiệu quả nhất.

PostgreSQL chạy được trên gần như mọi operating system hiện có, bao gồm Linux, Unix, macOS X và Microsoft Windows, thậm chí có thể chạy trên commodity hardware như các board Raspberry Pi. Một số cloud computing provider cũng đưa PostgreSQL vào software catalog của họ.

Nhờ cơ chế tuning phong phú, PostgreSQL có thể thích ứng rất tốt với hosting platform. Community chịu trách nhiệm duy trì database và documentation ở mức chất lượng rất cao; ngoài ra, các mailing list và IRC channel cũng phản hồi rất nhanh và là nguồn hữu ích để tìm giải pháp cho vấn đề cũng như ý tưởng.

Theo kinh nghiệm của các tác giả, chưa từng có trường hợp nào PostgreSQL không thể thích ứng với một application scenario.

> **Project PostgreSQL** có một tập hợp mailing list rất phong phú và mở rộng, trải từ các chủ đề chung đến những chi tiết rất cụ thể. Tìm kiếm vấn đề và giải pháp trong mailing list archive là một thói quen tốt; hãy xem web page tại https://www.postgresql.org/list/ để hiểu rõ hơn.

## Lược sử ngắn gọn của PostgreSQL

PostgreSQL lấy tên từ ancestor của nó: Ingres.

Ingres là một relational database do Professor Michael Stonebraker phát triển. Năm 1986, Professor Stonebraker bắt đầu một project hậu-Ingres nhằm phát triển các feature mới, thú vị trong lĩnh vực database và đặt tên project là POSTGRES (POST-Ingres). Project này hướng đến việc phát triển một object-relational database, trong đó “object” có nghĩa là user có khả năng mở rộng database bằng các object của riêng mình, chẳng hạn như data type, function, v.v.

Năm 1994, POSTGRES được phát hành với version 4.2 và MIT license, mở ra khả năng cộng tác với các developer khác trên toàn thế giới. Khi đó, POSTGRES sử dụng một query language nội bộ có tên QUEL. Hai sinh viên Berkeley, Andrew Yu và Jolly Chen, đã thay query language QUEL bằng SQL language đang rất mới mẻ và thú vị, và feature này sáng tạo đến mức project đã đổi tên thành Postgre95 để nhấn mạnh sự khác biệt so với các version trước đó khác.

Cuối cùng, vào năm 1996, project có một public server để host code, và năm developer, trong đó có Marc G. Fournier, Tom Lane và Bruce Momjan, bắt đầu phát triển project mới mang thương hiệu PostgreSQL. Kể từ đó, project được duy trì tốt và luôn cập nhật.

Điều này cũng có nghĩa là PostgreSQL đã được phát triển gần 30 năm, một lần nữa nhấn mạnh tính vững chắc và cởi mở của chính project. Nếu tò mò, bạn cũng có thể lần theo source code đến commit đầu tiên trong thế giới open source:

```bash
   $ git log 'git rev-list --max-parents=0 HEAD'
   commit d31084e9d1118b25fd16580d9d8c2924b5740dff
       Author: Marc G. Fournier <scrappy@hub.org>
       Date:   Tue Jul 9 06:22:35 1996 +0000


       Postgres95 1.01 Distribution - Virgin Sources
```

## Có gì mới trong PostgreSQL 16?

PostgreSQL 16 được phát hành vào ngày 14 tháng 9 năm 2023. Bản phát hành này bao gồm một tập hợp phong phú các cải tiến, trong đó có:

- Một số tối ưu hóa performance, từ việc allocation và management memory nội bộ đến behavior mặc định được parallelize nhiều hơn.
- Một tập hợp permission được sửa đổi cho user và group, bao gồm các system group mới để cung cấp những capability cụ thể.
- Cơ chế configuration được cải tiến, giúp dễ dàng đưa các file vào hơn và match user cũng như host bằng regular expression.
- Một tập hợp function JSON đầy đủ hơn.
- Logical replication engine được cải tiến, cho phép decoding ngay cả trên standby server.
- Một tập hợp utility column có thêm các option mới để fine-tune những gì administrator cần thực hiện.

Cũng như các release khác, PostgreSQL 16 chứa một tập hợp thay đổi nhằm giúp cuộc sống của Database Administrator (DBA) dễ dàng hơn, chẳng hạn như loại bỏ các option xung đột và các SQL term cũng như type đã obsolete. Điều này nhấn mạnh rằng các developer PostgreSQL luôn quan tâm đến database và việc tuân thủ các SQL standard hiện hành.

## Chính sách release, version number và life cycle của PostgreSQL

Các developer PostgreSQL phát hành một major release mới mỗi năm một lần, thường vào khoảng tháng 10. Major release là một version ổn định, giới thiệu các feature mới và những incompatibility có thể có với các version trước. Trong suốt life cycle, một major release liên tục được cải thiện thông qua các minor release, thường là release sửa bug và bảo trì.

Version number của PostgreSQL xác định major release và minor release. Version number được ghi dưới dạng major.minor; vì vậy, chẳng hạn, 16.0 chỉ major release đầu tiên, 16, còn 16.1 chỉ minor release 1 của major release 16. Tóm lại, con số càng lớn thì version bạn đang quản lý càng mới.

Các major version khác nhau của PostgreSQL không tương thích với nhau, trong khi các minor version khác nhau thì tương thích. Sự không tương thích này có nghĩa là gì? PostgreSQL lưu trữ data ở dạng binary, và format này có thể thay đổi giữa các major version. Điều đó có nghĩa là bạn có thể upgrade PostgreSQL giữa các minor version ngay trong lúc hệ thống đang chạy, nhưng có lẽ sẽ phải dump và restore nội dung database khi upgrade giữa các major version.

Khuyến nghị, cũng như với nhiều software khác, là chạy version PostgreSQL mới nhất mà bạn có thể sử dụng: các developer PostgreSQL dành rất nhiều công sức để cung cấp product không có bug, nhưng feature mới có thể đưa vào bug mới, và dù PostgreSQL có platform testing rất toàn diện, suy cho cùng đây vẫn là software, mà software thì có bug. Ngoài các bug nội bộ, các release mới còn bao gồm các bản sửa cho security exploit và các cải tiến performance, vì vậy duy trì PostgreSQL server đang chạy ở trạng thái up to date là một thói quen rất tốt.

Cuối cùng nhưng không kém phần quan trọng, không phải mọi version PostgreSQL đều tồn tại mãi mãi. PostgreSQL cung cấp support và upgrade trong năm năm sau khi một release mới được phát hành; sau khoảng thời gian này, một major release sẽ đạt End Of Life (EOL) và các developer PostgreSQL sẽ không còn duy trì nó nữa. Điều đó không có nghĩa là bạn không thể chạy một version PostgreSQL cổ; nó chỉ có nghĩa là version này sẽ không nhận được bất kỳ upgrade nào từ project chính thức và vì vậy sẽ out of date. Ví dụ, do PostgreSQL 16 được phát hành vào năm 2023, nó sẽ đạt EOL vào năm 2028. Hãy nhớ rằng chạy một release EOL không chỉ là chuyện không nhận được upgrade mới, security patch và bug fix; bạn sẽ phải tự xoay xở và sẽ không tìm được trợ giúp khi gặp sự cố.

Với điều đó, bây giờ chúng ta sẽ giới thiệu các thuật ngữ PostgreSQL chính, cũng như những concept hữu ích khác cần hiểu.

## Tìm hiểu thuật ngữ PostgreSQL

Để bạn hiểu PostgreSQL hoạt động như thế nào và theo dõi các example trong các chapter của cuốn sách, chúng ta cần giới thiệu các thuật ngữ được sử dụng bên trong PostgreSQL và cộng đồng người dùng của nó.

PostgreSQL là một service, nghĩa là nó chạy như một daemon trên operating system; một PostgreSQL daemon đang chạy được gọi là instance. Một PostgreSQL instance thường được gọi là cluster vì một instance duy nhất có thể phục vụ và xử lý nhiều database. Mỗi database là một không gian độc lập, nơi user và application có thể lưu trữ data.

Một database được các user được phép truy cập, nhưng các user đã kết nối với một database không thể vượt qua ranh giới database và tương tác với data nằm trong database khác, trừ khi họ cũng kết nối rõ ràng đến database đó.

Một database có thể được tổ chức thành các namespace, gọi là schema. Schema là một tên gợi nhớ mà user có thể gán để tổ chức các database object, chẳng hạn như table, thành một collection có cấu trúc hơn. Schema không thể lồng nhau, vì vậy chúng tạo thành một flat namespace.

Database object được đại diện bởi mọi thứ mà user có thể tạo và quản lý bên trong database, chẳng hạn như table, function, trigger và data type. Mỗi object thuộc về đúng một schema duy nhất; nếu không được chỉ định, schema đó được đặt tên theo user tạo ra object.

> Trong các PostgreSQL version trước 15, mọi object mới đều thuộc về schema `public` mặc định nếu không được chỉ định theo cách khác. Kể từ PostgreSQL 15, mỗi user được gán một personal schema và các object thuộc về schema đó, trừ khi một schema name khác được chỉ định rõ ràng.

User được định nghĩa ở cấp cluster-wide, nghĩa là chúng không gắn với một database cụ thể trong cluster. Một user có thể connect đến và quản lý bất kỳ database nào trong cluster mà họ được phép.

PostgreSQL chia user thành hai category chính:

- **Normal users:** Đây là những user có thể connect đến và xử lý database cũng như object tùy theo tập hợp privilege của họ.
- **Superusers:** Những user này có thể làm bất kỳ điều gì với bất kỳ database object nào.

PostgreSQL cho phép cấu hình bao nhiêu superuser tùy nhu cầu, và mọi superuser đều có chính xác cùng permission: họ có thể làm mọi thứ với mọi database và object, và đáng chú ý nhất là cũng có thể kiểm soát life cycle của cluster (chẳng hạn, họ có thể terminate connection của normal user, reload configuration, stop toàn bộ cluster, v.v.).

PostgreSQL cung cấp internal data, chẳng hạn như user, database, namespace, configuration và database runtime status, thông qua catalog: các table và view đặc biệt trình bày thông tin theo cách tương tác được bằng SQL. Nhiều catalog bị cắt giảm tùy theo user đang inspect chúng, ngoại trừ việc superuser thường nhìn thấy toàn bộ tập thông tin hiện có.

PostgreSQL lưu trữ user data (ví dụ: table) và internal status của nó trên local filesystem.
