Output của VACUUM FULL gần như giống plain VACUUM: nó cho thấy 1 triệu tuple có thể bị loại bỏ. Tuy nhiên, kết quả cuối cùng là toàn bộ table đã thu được phần space do các tuple nói trên chiếm giữ. Dù vậy, điều quan trọng cần nhớ là, mặc dù rất hấp dẫn, VACUUM FULL buộc phải rewrite toàn bộ table và do đó đẩy rất nhiều công việc xuống I/O system, dẫn tới các performance penalty tiềm ẩn.

Có thể tóm tắt các effect chính của VACUUM bằng hình ảnh. Hãy hình dung một tình huống như trong figure sau, trong đó một table chiếm hai data page, lần lượt có bốn và ba tuple hợp lệ (các tuple màu xanh lá):

![Hình 11.6: Các tuple hợp lệ và không hợp lệ trên hai data page](../assets/part-045-figure-11-6-000.jpg)

*Hình 11.6: Các tuple hợp lệ và không hợp lệ trên hai data page*

Dead tuple (các tuple màu đỏ) tạo ra fragmentation bên trong page, vì chúng xen kẽ với các tuple visible. Effect cuối cùng là table chiếm storage space cho hai page, trong khi toàn bộ visible tuple có thể được “đóng gói” vào một page duy nhất.

Nếu plain VACUUM được thực thi, tổng số page sẽ giữ nguyên, nhưng mọi page sẽ giải phóng space do dead tuple chiếm giữ và compact các tuple hợp lệ lại với nhau, như trong figure sau:

![Hình 11.7: Kết quả của plain VACUUM](../assets/part-045-figure-11-7-000.jpg)

*Hình 11.7: Kết quả của plain VACUUM*

Nếu VACUUM FULL được thực thi, các data page của table sẽ được rewrite hoàn toàn để compact tất cả tuple hợp lệ lại với nhau. Trong tình huống này, data page thứ hai của table trở nên rỗng và do đó có thể bị loại bỏ, giải phóng storage space. Tình huống trở thành như trong diagram sau:

![Hình 11.8: Kết quả của FULL VACUUM](../assets/part-045-figure-11-8-000.jpg)

*Hình 11.8: Kết quả của FULL VACUUM*

Bây giờ hẳn đã rõ sự khác biệt chính giữa plain VACUUM và FULL VACUUM: theo rule of thumb, plain VACUUM không giải phóng storage space và ít aggressive hơn nhiều so với VACUUM FULL; ngược lại, VACUUM FULL giải phóng disk space. Chỉ có một tình huống đặc biệt trong đó plain VACUUM có thể trả lại một phần rất nhỏ storage space: nếu tất cả tuple trên page cuối cùng đều dead, chính page đó sẽ được deallocate.

Thông thường, bạn không chạy VACUUM bằng tay, vì PostgreSQL cung cấp một approach tốt hơn nhiều để kiểm soát fragmentation bằng automatic vacuuming, được giải thích trong section tiếp theo.

## Automatic VACUUM

Kể từ PostgreSQL 8.4, đã có một background job tên là autovacuum, chịu trách nhiệm chạy VACUUM thay cho system administrator.

Ý tưởng là vì VACUUM là một operation I/O-intensive, background job có thể thực hiện các micro-vacuum nhỏ mà không can thiệp vào database activity bình thường.

Thông thường, bạn không cần lo lắng về autovacuum, vì nó được enable mặc định và có các setting tổng quát có thể hữu ích trong nhiều scenario; tuy nhiên, cũng như hầu hết mọi thứ trong PostgreSQL, bạn có thể dùng các setting cụ thể để fine-tune behavior của automatic vacuuming. Một system có autovacuum configuration tốt thường không cần VACUUM thủ công, và traits của manual VACUUM thường có nghĩa là autovacuum phải được configure để chạy thường xuyên hơn.

Automatic vacuum hoạt động với một nhóm background process, được gọi là autovacuum worker. Mỗi worker được assign cho một database để làm việc; khi process hoàn tất activity của mình, nó sẽ terminate. PostgreSQL thường xuyên start các autovacuum worker process mới, để mọi database (và table) trong cluster có cơ hội được vacuum tự động. Tuy nhiên, PostgreSQL cho phép database administrator thiết lập cẩn thận behavior của activity spawn process này: configuration setting `autovacuum_max_workers` quy định số process active tối đa có thể đang chạy tại một thời điểm.

Autovacuum worker thực hiện ba activity chính:

- Thực thi plain VACUUM trên các data table, nhằm giảm fragmentation và liên tục allocate space mới để xử lý các tuple version mới.
- Update system statistics về quantity và quality của data được lưu trong user table, tương tự như manual ANALYZE. Việc này rất hữu ích để query executor quyết định plan tốt nhất nhằm truy cập data, chẳng hạn thực hiện tuple freeze bất cứ khi nào cần thiết, từ đó ngăn chặn vấn đề xid wraparound.
- Thực hiện tuple freeze bất cứ khi nào cần thiết, từ đó ngăn chặn vấn đề xid wraparound.

autovacuum được bật mặc định, nhưng bạn luôn có thể chọn disable nó, dù việc này chẳng có ý nghĩa gì; thông thường, bạn cần autovacuum chạy nhiều hơn chứ không phải ít hơn. Tuy nhiên, điều quan trọng cần nhớ là ngay cả khi đã bị tắt, một emergency autovacuum process vẫn có thể start để ngăn chặn vấn đề xid wraparound.


> Nói cách khác, PostgreSQL cố gắng hết sức để vẫn vận hành được ngay cả khi bạn configure sai nó!

Các setting chính của autovacuum có thể được inspect từ configuration file `$PGDATA/postgresql.conf` hoặc, như thường lệ, từ catalog `pg_settings`. Các configuration parameter quan trọng nhất là:

- `autovacuum` enable hoặc disable autovacuum background machinery. Ngoài việc thực hiện experiment, như chúng ta đã làm trong section trước, không có lý do gì để giữ autovacuum disabled.
- `autovacuum_vacuum_threshold` cho biết sẽ cho phép bao nhiêu tuple version mới trước khi autovacuum có thể được activate trên một table. Ý tưởng là chúng ta không muốn autovacuum trigger nếu chỉ có một số ít tuple thay đổi trong table, vì điều đó tạo ra I/O penalty mà không đem lại gain hiệu quả. Mặc định, parameter này được đặt là 50 tuple, nghĩa là bất kỳ thay đổi nào trong table không tạo ra ít nhất 50 tuple version mới sẽ không được xem là đủ để trigger autovacuum.
- `autovacuum_vacuum_scale_factor` cho biết lượng tuple, tính theo phần trăm, phải được thay đổi trước khi autovacuum thực hiện một VACUUM thực sự trên table. Ý tưởng là table càng lớn thì autovacuum càng chờ nhiều dead tuple hơn trước khi thực hiện activity của nó. Trong một installation mặc định, setting này là `0.2`, nghĩa là autovacuum sẽ trigger khi ít nhất 20% tuple đã được đánh dấu là dead.
- `autovacuum_cost_limit` là một value đo threshold tối đa mà vượt qua đó background process phải tự suspend để tiếp tục sau.
- `autovacuum_cost_delay` cho biết autovacuum sẽ bị suspend trong bao nhiêu millisecond (theo bội số của mười) để không can thiệp vào database activity khác. Việc suspend chỉ được thực hiện khi cost delay đạt tới ngưỡng.

Về cơ bản, activity của autovacuum diễn ra như sau: nó scan mọi table trong một database, và nếu số tuple đã thay đổi lớn hơn `autovacuum_vacuum_threshold + ( table-tuples * autovacuum_vacuum_scale_factor )`, autovacuum process sẽ activate. Sau đó, nó thực hiện vacuum trên table và đo lượng work. Nếu lượng work đạt tới giá trị được đặt cho `autovacuum_cost_limit`, process sẽ tự suspend trong `autovacuum_cost_delay` millisecond, rồi resume và tiếp tục. Mỗi khi autovacuum đạt threshold, nó sẽ tự suspend, tạo ra effect của một VACUUM incremental. Behavior stop-and-go này của autovacuum nhằm giảm overall impact lên cluster đang chạy: autovacuum sẽ tự suspend để dành resource cho interactive connection và user.

Nhưng autovacuum tính cost của activity mà nó đang thực hiện như thế nào? Có một tập tunable value biểu thị cost của việc fetch một data page mới, scan một dirty page, v.v.

Các value đó được dùng chung với manual VACUUM:

```text
   forumdb=> SELECT name, setting       FROM pg_settings
      WHERE name like 'vacuum_cost%';
             name          | setting
   ------------------------+---------
   vacuum_cost_delay        | 0
   vacuum_cost_limit        | 200
   vacuum_cost_page_dirty | 20
   vacuum_cost_page_hit     | 1
   vacuum_cost_page_miss    | 2
   (5 rows)
```

Các value đó được dùng cho cả manual VACUUM và autovacuum, ngoại trừ việc autovacuum có `autovacuum_vacuum_cost_limit` riêng, thường được đặt là 200. Mặt khác, manual VACUUM có `vacuum_cost_delay` đặt là 0, về cơ bản có nghĩa là một manual VACUUM process sẽ không bao giờ tự suspend. Sau cùng, database administrator muốn manual VACUUM hoàn tất nhanh nhất có thể.

Các parameter tương tự cũng tồn tại cho phần ANALYZE, vì autovacuum background process thực hiện VACUUM ANALYZE, và do đó bạn có `autovacuum_analyze_threshold` và `autovacuum_analyze_scale_factor`, chịu trách nhiệm xác định activity window cho phần ANALYZE (phần này liên quan đến việc update statistics về nội dung của table).

## Tóm tắt

PostgreSQL khai thác MVCC để cung cấp quyền truy cập concurrent cao vào underlying data, và điều này có nghĩa là mỗi transaction nhận biết một snapshot của data trong khi system duy trì các version khác nhau của cùng các tuple. Sớm hay muộn, các tuple không hợp lệ sẽ bị loại bỏ và storage space sẽ được reclaim. Một mặt, MVCC cung cấp concurrency tốt hơn, nhưng mặt khác, nó đòi hỏi thêm effort để reclaim storage space sau khi các transaction không còn reference dead tuple. PostgreSQL cung cấp VACUUM cho mục đích này và cũng có một background process machinery tên là autovacuum để định kỳ và không xâm lấn giữ cho system sạch sẽ, khỏe mạnh.

Để cải thiện I/O và reliability, PostgreSQL lưu data trong một journal được ghi tuần tự, là WAL. WAL được chia thành các segment, và tại những khoảng thời gian nhất định, được gọi là checkpoint, toàn bộ dirty data trong memory được force tới một vị trí xác định trong storage, còn các WAL segment được recycle.

Trong chapter này, bạn đã tìm hiểu về internals của WAL và MVCC, cũng như transaction boundary và savepoint. Bạn cũng đã thấy cách áp đặt một transaction isolation level cụ thể; tùy thuộc vào nhu cầu, level đó có thể bảo vệ data của bạn trước các update concurrent trên cùng tuple.

Trong chapter tiếp theo, bạn sẽ khám phá cách PostgreSQL có thể được mở rộng vượt ra ngoài các functionality thông thường thông qua các pluggable module được gọi là extension.

## Kiểm tra kiến thức

- **Transaction là gì?**

  Transaction là một unit công việc được xác nhận hoặc loại bỏ toàn bộ. Một transaction có thể được tạo bởi một statement hoặc nhiều statement, và có thể là implicit hoặc explicit. Xem section *Giới thiệu transaction* để biết thêm chi tiết.

- **`xid` là gì và nó gặp vấn đề nào?**

  `xid` là transaction identifier, một number đại diện duy nhất cho một transaction trong toàn bộ cluster. Vì được lưu dưới dạng counter, value này gặp vấn đề gọi là xid wraparound, vấn đề được giải quyết bằng freezing của VACUUM và autovacuum. Xem section *Thông tin thêm về transaction identifier – vấn đề XID wraparound* để biết thêm chi tiết.

- **MVCC là gì?**

  MVCC là một technique theo đó, tại một thời điểm nhất định, nhiều version của một tuple có thể tồn tại trong một database. Tùy thuộc vào các transaction đang chạy và commit status của chúng, một version khác nhau sẽ được sử dụng. Xem section *Giải thích MVCC* để biết thêm chi tiết.

- **WAL là gì và tại sao nó quan trọng?**

  WAL là intent log của một database; trước khi thực hiện bất kỳ modification nào lên storage, PostgreSQL ghi các thay đổi vào WAL. Nhờ vậy, write sẽ nhanh hơn và không có data nào bị mất trong trường hợp crash. Xem section *Cách PostgreSQL xử lý persistency và consistency: WAL* để biết thêm chi tiết.

- **Checkpoint là gì?**

  Checkpoint là một thời điểm tại đó cluster đồng bộ data trong memory với data trên disk, bảo đảm storage phản ánh các thay đổi mới nhất. Sau khi checkpoint hoàn tất, các WAL segment cũ có thể được recycle. Xem section *Checkpoint* để biết thêm chi tiết.

## Tài liệu tham khảo

- PostgreSQL transaction isolation levels – official documentation: https://www.postgresql.org/docs/current/sql-set-transaction.html
- PostgreSQL transaction isolation level SERIALIZABLE – official documentation: https://www.postgresql.org/docs/current/transaction-iso.html#XACT-SERIALIZABLE
- PostgreSQL savepoints – official documentation: https://www.postgresql.org/docs/current/sql-savepoint.html
- PostgreSQL VACUUM – official documentation: https://www.postgresql.org/docs/current/sql-vacuum.html

## Tìm hiểu thêm trên Discord

Để tham gia cộng đồng Discord của cuốn sách, nơi bạn có thể chia sẻ feedback, đặt câu hỏi cho tác giả và tìm hiểu về các bản phát hành mới, hãy follow QR code bên dưới:

https://discord.gg/jYWCjF6Tku

# 12. Mở rộng Database – Hệ sinh thái Extension

Extension là một cách mạnh mẽ để đóng gói các database object liên quan, chẳng hạn như function, routine và table, giúp việc quản lý các object đó như một unit duy nhất trở nên dễ dàng hơn. Extension cho phép bạn và các developer khác mở rộng tập feature vốn đã phong phú của PostgreSQL bằng cách cung cấp một cách rõ ràng, súc tích và chính xác để install, upgrade và remove feature cũng như object. Trong chapter này, bạn sẽ thấy extension là gì và cách install, upgrade hoặc remove chúng bằng các tool khác nhau. Hơn nữa, bạn sẽ học cách build extension của riêng mình từ đầu để có thể ngay lập tức đóng gói các script và tool riêng nhằm phân phối chúng trên các database và PostgreSQL instance khác.

Chapter này gồm các topic sau:

- Giới thiệu extension
- Quản lý extension
- Khám phá PGXN client
- Cài đặt extension
- Tự tạo extension

## Yêu cầu kỹ thuật

Các example của chapter có thể chạy trên Docker image `chapter_12`, có thể tìm thấy trong GitHub repository của cuốn sách: https://github.com/PacktPublishing/Learn-PostgreSQL-Second-Edition. Để biết hướng dẫn cài đặt và sử dụng Docker image cho cuốn sách này, hãy xem Chapter 1, *Giới thiệu PostgreSQL*.

## Giới thiệu extension

SQL là một declarative language cho phép bạn tạo và thao tác với object cũng như data. Bạn có thể group các SQL statement thành script để chạy script theo cách dễ dự đoán và reproducible hơn. Tuy nhiên, PostgreSQL xem các script như vậy là một sequence gồm các command không liên quan, nghĩa là bạn phải chịu trách nhiệm correlate các command đó vào những script phù hợp. Tình hình còn tệ hơn khi bạn phải xử lý các foreign programming language (ví dụ PL/Perl và những language không dựa trên SQL khác) hoặc binary library; cluster không biết gì về mục đích của bạn hay về mối quan hệ giữa các object. May mắn là extension giúp bạn lập lại order trong chaos.

Extension là một tập file được đóng gói, có thể được install vào cluster để cung cấp thêm functionality, tức là “extend” tập feature hiện tại của cluster. Không giống script, extension được quản lý nghiêm ngặt thông qua các command cụ thể để install, deploy, load và upgrade toàn bộ extension như một thể thống nhất, ngay cả khi nó gồm nhiều file khác nhau.

Extension có thể là một thứ tổng quát, chẳng hạn data type mới, index type mới hoặc service gửi email trực tiếp từ bên trong PostgreSQL; hoặc có thể là thứ rất cụ thể cho một use case nhất định, chẳng hạn một tập table và data cung cấp ad hoc configuration. Extension không áp đặt opinion về cách bạn sẽ sử dụng nó, vì vậy bạn có thể tự do install rồi bỏ đó, hoặc dùng nó trong mọi database của cluster.

Mục tiêu chính của extension mechanism là cung cấp một common interface để administer feature mới. Nhờ extension, bạn có một tập statement chung để deploy, install, upgrade và remove một extension như một thể thống nhất trong cluster. Extension của bạn gồm một function duy nhất hay cả một tập object được liên kết với nhau không quan trọng; extension mechanism sẽ xử lý tất cả object cùng lúc, giúp việc administration dễ dàng hơn. Hơn nữa, extension machinery định nghĩa một cách standard để thêm feature theo cách có cấu trúc và sạch sẽ, nhờ đó mọi người dễ đóng góp cho PostgreSQL hơn.

PostgreSQL đi kèm một tập extension hữu ích nằm trong `contrib` package và do chính các PostgreSQL developer phát triển. Vì vậy, tập contrib extension này vững chắc và an toàn để sử dụng, vì chúng được build gắn chặt với chính PostgreSQL database. Tuy nhiên, extension cũng có thể đến từ third party, và đây chính là điểm hay của approach này: bất kỳ ai cũng có thể đóng góp cho PostgreSQL bằng cách cung cấp feature mới thông qua extension. Lưu ý rằng các PostgreSQL developer không bảo đảm stability của third-party extension.

> Các operating system package thường cung cấp package `postgrsql-contrib`, package này install toàn bộ PostgreSQL contrib extension. Package này được tách riêng để user có thể chọn có install các extension đó hay không. Rõ ràng, PostgreSQL vẫn hoạt động tốt ngay cả khi không có module `contrib`, vốn thực tế bổ sung feature thông qua extension.

PostgreSQL đã xây dựng cả một ecosystem xung quanh concept extension, vì vậy nó không chỉ cung cấp các statement để quản lý extension mà còn cung cấp một platform để build extension mới và chuyển các script hiện có thành extension. Sau đó, extension có thể được cung cấp công khai thông qua một global repository có tên **PostgreSQL eXtensions Network (PGXN)**.

Bạn có thể hình dung extension PostgreSQL như các reusable library trong programming language, chẳng hạn module cho Perl, gem cho Ruby, JAR cho Java, v.v. Tương tự, PGXN infrastructure có thể được xem như CPAN đối với Perl (hoặc PEAR đối với PHP, v.v.).

## Hệ sinh thái extension

Điểm hay của extension là chúng cung cấp một cách thống nhất để bundle các module có thể được deploy (install) và sử dụng trong PostgreSQL. Developer được tự do đóng góp để mở rộng số lượng module có sẵn cho PostgreSQL, và số lượng này đã nhanh chóng phát triển thành một ecosystem hoàn chỉnh như hiện nay.

Tương tự các programming language như Perl, Python và những language khác, PostgreSQL giờ đây có thể được customize bằng add-on và module dùng chung một infrastructure và architecture, đồng thời được quản lý bằng cùng các statement mà không phụ thuộc vào feature chúng cung cấp.

Extension chủ yếu được tập hợp trong PGXN, một online repository có thể được query để lấy thông tin về một extension hoặc download một extension (và một version cụ thể của nó), đồng thời có thể được update bằng các module mới.

> Hãy nhớ rằng PGXN đối với PostgreSQL cũng giống như CPAN đối với Perl, CTAN đối với LaTeX, PEAR đối với PHP, v.v.
