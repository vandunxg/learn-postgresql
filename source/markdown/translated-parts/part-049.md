# 13. Query Tuning, Index và Tối ưu hóa Performance

Tuning performance là một trong những công việc phức tạp nhất trong công việc hằng ngày của một **database administrator (DBA)**. SQL là một ngôn ngữ khai báo, vì vậy nó không định nghĩa cách truy cập data bên dưới – trách nhiệm đó thuộc về database engine. Do đó, PostgreSQL phải chọn access tốt nhất hiện có tới data cho mỗi statement.

Một component cụ thể, planner, chịu trách nhiệm quyết định path tốt nhất trong tất cả các path khả dụng tới data bên dưới, trong khi một component khác, optimizer, chịu trách nhiệm thực thi statement với một access plan cụ thể như vậy.

Mục tiêu của chapter này là dạy bạn cách PostgreSQL thực thi một query, cách planner tính execution plan tốt nhất, và cách bạn có thể hỗ trợ cải thiện performance bằng index.

Trong chapter này, bạn sẽ tìm hiểu các chủ đề sau:

- Thực thi một statement
- Index
- Statement `EXPLAIN`
- Một ví dụ về query tuning
- `ANALYZE` và cách cập nhật statistics
- Auto-explain

## Yêu cầu kỹ thuật

Bạn cần biết những nội dung sau:

- Cách thực thi query trên database
- Cách thực thi các statement **data description language (DDL)**

Các example trong chapter có thể chạy trên image `chapter_13` trong GitHub repository của cuốn sách: https://github.com/PacktPublishing/Learn-PostgreSQL-Second-Edition. Để biết cách cài đặt và sử dụng các Docker image có sẵn cho cuốn sách này, hãy xem phần hướng dẫn trong Chapter 1, Introduction to PostgreSQL.

## Thực thi một statement

SQL là một ngôn ngữ khai báo: bạn yêu cầu database thực hiện một việc gì đó trên data mà nó chứa, nhưng không chỉ định cách database phải hoàn thành SQL statement. Chẳng hạn, khi yêu cầu lấy về một số data, bạn thực thi một statement `SELECT`, nhưng chỉ cung cấp các clause xác định subset data cần lấy, chứ không cung cấp cách database phải lấy data từ persistent storage. Bạn phải tin tưởng database – cụ thể là PostgreSQL – có thể thực hiện công việc và luôn tìm được path nhanh nhất tới data, trong mọi hoàn cảnh workload. Tin tốt là PostgreSQL thực sự rất giỏi ở việc này và có thể hiểu (và ở một mức độ nào đó, diễn giải) các SQL statement cũng như workload hiện tại của nó để cung cấp cho bạn access tới data theo cách nhanh nhất.

Tuy nhiên, việc tìm path nhanh nhất tới data thường đòi hỏi sự cân bằng giữa việc tìm path tuyệt đối nhanh nhất và thời gian dành cho việc suy luận về path đó; nói cách khác, PostgreSQL đôi khi chọn một thỏa hiệp để lấy data cho bạn theo cách đủ nhanh, dù đó không phải là cách nhanh nhất tuyệt đối.

Mặt khác, đôi khi PostgreSQL không thể hiểu thật tốt cách tìm path nhanh nhất tới data, và DBA có thể hỗ trợ cải thiện performance. Thông thường, thêm một index có thể giúp PostgreSQL retrieve data bên dưới nhanh hơn. Những lúc khác, một statement chậm che giấu một query viết sai (tức là một statement được viết với các clause không đúng hoặc mâu thuẫn). Ngoài ra, query chậm có thể xuất phát từ việc PostgreSQL suy luận sai về kích thước dataset mà nó phải xử lý. Trong mọi trường hợp này, DBA phải thực hiện một số tuning trong database hoặc các statement để giúp PostgreSQL đưa ra quyết định tốt nhất.

Để có thể hỗ trợ cluster tối ưu các statement, trước tiên bạn cần hiểu PostgreSQL xử lý một SQL statement như thế nào. Trong phần tiếp theo, bạn sẽ học toàn bộ nền tảng về cách một SQL statement được chuyển thành một tập các action mà PostgreSQL thực thi để quản lý data.

## Các giai đoạn thực thi

Một SQL statement – gọi ngắn gọn là query – được xử lý qua bốn giai đoạn chính:

1. Giai đoạn đầu tiên là parsing; một component chuyên dụng, parser, xử lý dạng text của statement (SQL text) và xác minh nó có đúng hay không. Nếu statement có bất kỳ syntax error nào, việc thực thi dừng lại ở giai đoạn sớm này; nếu không, parser phân rã statement thành các phần chính, chẳng hạn danh sách table và column liên quan, các clause để filter data, việc sort, v.v.
2. Khi parser hoàn tất thành công, statement chuyển sang giai đoạn thứ hai: rewriting. Rewriter chịu trách nhiệm áp dụng mọi rule cú pháp để rewrite SQL statement ban đầu thành thứ thực sự sẽ được thực thi. Cụ thể, rewriter chịu trách nhiệm áp dụng các rule (tham khảo Chapter 8, Triggers and Rules). Khi rewriter hoàn thành nhiệm vụ, tạo ra statement hiệu lực mà database sẽ xử lý, statement này chuyển sang giai đoạn tiếp theo: optimization.
3. Trong giai đoạn optimization, query được optimizer xử lý; optimizer chịu trách nhiệm tìm path nhanh nhất tới data. Việc tìm path nhanh nhất này không đơn giản: optimizer phải quyết định cách đi tới data trong tất cả access method khả dụng, chẳng hạn index hoặc direct access. Như bạn có thể hình dung, việc suy luận và lặp qua tất cả access method khả dụng tiêu tốn thời gian và resource, vì vậy nhiệm vụ của optimizer không chỉ là tìm access method nhanh nhất mà còn phải tìm ra nó trong thời gian ngắn.
4. Cuối cùng, khi optimizer đã quyết định cách access data, query chuyển sang phase cuối: execution. Execution phase do component executor xử lý; component này chịu trách nhiệm thực sự đi tới storage và retrieve (hoặc insert) data bằng access method do executor quyết định.

Tóm lại, một SQL statement duy nhất đi qua bốn giai đoạn, tất cả được thể hiện trong diagram sau: parsing phase kiểm tra syntax của statement, rewriting phase biến đổi query thành một thứ cụ thể hơn, optimization phase quyết định cách access data mà query yêu cầu, và cuối cùng là execution phase, thực hiện physical access tới data.

![Hình 13.1: Các giai đoạn của query PostgreSQL](../assets/part-049-figure-13-1-000.jpg)

*Hình 13.1: Các giai đoạn của query PostgreSQL*

DBA chỉ có thể tương tác với database trong optimization phase, cố gắng giúp PostgreSQL hiểu statement tốt hơn và optimize nó đúng cách bất cứ khi nào PostgreSQL không thực hiện công việc một cách tối ưu. Phần tiếp theo xem xét kỹ hơn optimizer, nhằm chuẩn bị cho bạn các cách tune query và database để xử lý query thông minh hơn và nhanh hơn.

## Optimizer

Optimizer là component chịu trách nhiệm quyết định dùng cách nào để access data nhanh nhất có thể. Nếu một table không cung cấp index nào, thì chỉ có một cách access data của nó, do đó không có gì phải suy luận về cách lấy data từ table.

Mặt khác, nếu một table cung cấp một vài index, optimizer phải quyết định index nào phù hợp nhất với statement sẽ được thực thi. Tình huống trở nên phức tạp hơn nhiều nếu có nhiều table, mỗi table lại có nhiều index: optimizer phải suy luận về mọi cách khả dĩ để đi tới kết quả cuối cùng.

Optimizer chọn giữa các cách access data khác nhau như thế nào? Optimizer sử dụng concept cost: mỗi cách access data được gán một cost, và cách có cost thấp nhất sẽ thắng, được chọn làm access method tốt nhất.

Đó là lý do PostgreSQL optimizer được gọi là cost-based optimizer.

PostgreSQL được cấu hình để gán một cost cụ thể cho mọi operation mà nó thực hiện: tìm data từ storage, thực hiện một operation dựa trên CPU (chẳng hạn sort trong memory), v.v. Optimizer lặp qua mọi cách khả dĩ để access data và xử lý data đó nhằm trả về kết quả mong muốn cho user, tính tổng cost cho từng cách – tức là tổng cost của mọi operation PostgreSQL sẽ thực hiện. Sau đó, plan có cost thấp nhất được truyền cho executor dưới dạng một chuỗi action cần thực hiện, và data được xử lý theo đó.

Tuy nhiên, đây mới chỉ là một nửa câu chuyện. Có những trường hợp công việc của optimizer thực sự đơn giản: nếu chỉ có một access method, việc quyết định cách access data là hiển nhiên. Tuy nhiên, có những statement liên quan đến quá nhiều object và table khiến việc lặp qua mọi khả năng mất rất nhiều thời gian, đến mức kết quả sẽ bị thời gian tính toán cách access data tối ưu vượt qua. Vì lý do này, nếu statement liên quan đến hơn 12 table join, optimizer không lặp qua mọi khả năng mà thay vào đó thực thi một genetic algorithm để tìm một cách access data mang tính thỏa hiệp. Sự thỏa hiệp nằm giữa thời gian dành cho việc tính path tới data và việc tìm một access path không quá tệ.

Executor cũng có thể thực hiện data access bằng các parallel job. Điều này có nghĩa là, chẳng hạn, việc retrieve một tập data rất lớn có thể được thực hiện bằng cách chia lượng công việc cho các parallel worker khác nhau (ví dụ, thread), mỗi worker được gán một subset data nhỏ hơn.

Trong mọi trường hợp, optimizer chia tập action cần truyền cho executor thành các node; một node là một action cần thực thi để cung cấp kết quả cuối cùng hoặc kết quả trung gian. Ví dụ, giả sử bạn thực thi một query chung yêu cầu data theo một thứ tự cụ thể như sau:

```text
   SELECT * FROM categories ORDER BY description;
```

Optimizer sẽ truyền hai action cho executor, và do đó là hai node: một node để retrieve toàn bộ data và một node để sort data.

Trong các subsection sau, chúng ta sẽ trình bày các node chính mà optimizer xem xét và truyền cho executor. Chúng ta sẽ bắt đầu với các sequential node – những node được thực thi bằng một job duy nhất – sau đó xem PostgreSQL xây dựng parallelism trên nền tảng của chúng như thế nào.

## Các node optimizer sử dụng

Trong phần này, chúng ta sẽ trình bày các node chính mà bạn có thể gặp trong optimizer plan. Có các node khác nhau cho từng operation có thể thực hiện, và cho từng access method khác nhau mà PostgreSQL chấp nhận.

Điều quan trọng cần lưu ý là các node có thể stack: output của một node có thể được dùng làm input cho node khác. Điều này cho phép xây dựng các execution plan rất phức tạp từ nhiều node khác nhau, tạo ra một access method rất chi tiết tới data.

### Các sequential node

Sequential node là những node được thực thi tuần tự, lần lượt từng node một, để đạt được kết quả cuối cùng. Các node chính được liệt kê ở đây và sẽ được giải thích trong các subsection sau:

- Sequential Scan
- Index Scan, Index-Only Scan, và Bitmap Index Scan
- Nested Loop, Hash Join, và Merge Join
- Các parallel node Gather và Gather Merge

### Sequential Scan

**Sequential Scan (Seq Scan)** là node duy nhất luôn có sẵn cho optimizer và executor, đặc biệt khi không có alternative nào khác có giá trị. Trong một sequential scan, executor sẽ đi tới đầu dataset trên disk – ví dụ, đầu file tương ứng với một table – và đọc toàn bộ data, lần lượt từng block theo thứ tự tuần tự.

Node này, chẳng hạn, luôn được sử dụng khi bạn yêu cầu nội dung của một table mà không có filtering clause cụ thể nào, như trong example sau:

```text
   SELECT * FROM categories;
```

Node **Sequential Scan** cũng được sử dụng khi filtering clause không giới hạn nhiều trong query, khiến kết quả cuối cùng là lấy gần như toàn bộ nội dung table. Trong trường hợp đó, database có thể thực hiện operation read-all tuần tự nhanh hơn, loại bỏ những tuple bị các query clause filter ra.

### Các index node

Một index scan access data có liên quan đến index để nhanh chóng tìm dataset được yêu cầu. Trong PostgreSQL, tất cả index đều là secondary, nghĩa là chúng tồn tại bên cạnh table; vì vậy, trong storage bạn sẽ có một data file cho table và một file cho mỗi index được build trên table. Điều này có nghĩa một index scan luôn yêu cầu hai access riêng biệt tới storage: một access để đọc disk và lấy thông tin về vị trí của các tuple được yêu cầu trong table, và một access khác tới disk để tìm các tuple mà index trỏ tới.

Từ đó, có thể thấy rõ PostgreSQL tránh sử dụng index khi chúng không hữu ích, tức là khi việc access storage hai lần nói trên gây ra nhiều bất lợi hơn lợi ích.

Tuy nhiên, khi PostgreSQL tin rằng access data qua một index có thể có giá trị, nó sẽ tạo ra một index node có thể chuyên biệt thành ba loại khác nhau.

**Index Scan**, đúng như tên gọi, là access method index “cổ điển”: PostgreSQL đọc index đã chọn, rồi từ đó tìm các tuple, lại đọc chúng từ storage.

**Index-Only Scan** là một loại **Index Scan** cụ thể: nếu data được yêu cầu chỉ liên quan đến các column thuộc index, PostgreSQL đủ thông minh để tránh chuyến đi thứ hai tới storage vì nó có thể lấy trực tiếp toàn bộ thông tin cần thiết từ index.

Loại index-based node cuối cùng bạn có thể gặp là **Bitmap Index Scan**: PostgreSQL xây dựng một bitmap trong memory về vị trí của các tuple thỏa các clause của statement, sau đó bitmap này được dùng để định vị các tuple đó. **Bitmap Index Scan** thường được kết hợp với **Bitmap Heap Scan**, như bạn sẽ thấy trong các example ở những phần sau.

### Các join node

Khi PostgreSQL thực hiện join giữa hai (hoặc nhiều) table, nó sử dụng một trong ba node khả dĩ. Trong phần này, chúng ta sẽ mô tả các join node đó, xét một join giữa hai table: một outer table (ở bên trái của join) và một inner table (table ở phía bên phải của join).

Node dễ hiểu nhất là **Nested Loop**: cả hai table đều được scan bằng method tuần tự hoặc dựa trên index, và mọi tuple được kiểm tra để xem có match hay không. Về cơ bản, algorithm có thể được mô tả bằng đoạn pseudo-Java code sau:

```text
   for ( Tuple o : outerTable )
       for ( Tuple i : innerTable )
             if ( o.matches( i ) )
                appendTupleToResultDataSet( o, i );
```

Như bạn có thể thấy từ pseudo-code trước đó, **Nested Loop** được đặt tên theo việc lồng các loop mà nó thực hiện để đánh giá mọi tuple giữa inner table và outer table.

Như vậy, một **Nested Loop** không bị buộc phải thực hiện sequential scan trên cả hai table; trên thực tế, tùy context, mỗi table có thể được duyệt bằng sequential access method hoặc indexed-based access method. Tuy nhiên, phần cốt lõi của **Nested Loop** không thay đổi: sẽ luôn có một double loop lồng nhau để tìm các match giữa các tuple.

PostgreSQL chỉ chọn **Nested Loop** nếu inner table đủ nhỏ để việc lặp qua nó mỗi lần không tạo ra penalty đáng kể.

Một cách khác để thực hiện join là dùng node **Hash Join**: inner table được ánh xạ vào một hash, là một tập bucket chứa các tuple của table; sau đó outer table được duyệt, và với mỗi tuple lấy ra từ outer table, hash được tìm kiếm để xem có match hay không. Đoạn pseudo-Java code sau minh họa cơ chế của **Hash Join**:

```text
   Hash innerHash = buildHash( innerTable );
   for ( Tuple o : outerTable )
        if ( innerHash.containsKey( buildHash( o ) ) )
            appendTupleToResultDataSet( o, i );
```

Như bạn có thể thấy từ example trước, bước đầu tiên gồm việc hash inner table, sau đó duyệt qua outer table để xem có tuple nào của nó match với các value trong hash map của inner table hay không.

Loại join cuối cùng bạn có thể gặp trong PostgreSQL là **Merge Join**. Đúng như tên gọi, **Merge Join** gồm một bước sort: trước tiên cả hai table được sort theo các join key, sau đó được duyệt tuần tự. Với mỗi tuple của outer table, tất cả tuple match trong inner table được lấy ra. Vì cả hai table đã được sort, một tuple không match cho biết đã đến lúc chuyển sang join key tiếp theo.

Đoạn pseudo-Java code sau minh họa algorithm của **Merge Join**:

```text
   outerTable = sort( outerTable );
   innerTable = sort( innerTable );
   int innerIdx = 0;


   for ( Tuple o : outerTable )
       for ( ; innerIdx < innerTable.length(); innerIdx++ ){
           Tuple i = innerTable[ innerIdx ];
             if ( o.matches( i ) )
                appendTupleToResultSet( o, i );
             else
                break;
       }
```

Như bạn có thể thấy, sau khi các table được sort, một tuple được lấy ra từ outer table và so sánh với tất cả tuple trong inner table. Ngay khi các tuple không còn match, một tuple khác từ outer table được lấy ra và inner table khởi động lại loop từ vị trí trước đó. Nói cách khác, cả hai table được duyệt đúng một lần.

Bây giờ chúng ta sẽ chuyển sang các parallel node.

### Các parallel node

Parallel node là những node mà PostgreSQL có thể thực thi để phân phối lượng công việc giữa các parallel process, nhờ đó đạt được kết quả cuối cùng nhanh hơn. Điều quan trọng cần lưu ý là parallel execution không phải lúc nào cũng là lựa chọn đúng: có thời gian setup để phân phối job giữa các parallel process, cũng như thời gian và resource cần thiết để trả về kết quả của từng process. Vì lý do này, PostgreSQL chỉ enable parallel execution của một số node nhất định nếu phiên bản parallel được ước tính sẽ đem lại lợi ích so với sequential execution.

Ví dụ đơn giản, hãy xét trường hợp bạn có một table rất nhỏ chỉ gồm vài tuple, chẳng hạn bốn tuple. Nếu bạn yêu cầu toàn bộ nội dung table, resource và thời gian dành cho việc khởi chạy cũng như đồng bộ các parallel process sẽ lớn hơn nhiều so với việc đi thẳng tới table và lấy result dataset về theo cách tuần tự. Quy tắc kinh nghiệm là: nếu dataset được yêu cầu đủ nhỏ, PostgreSQL sẽ không bao giờ chọn parallel execution.

Điều quan trọng là phải hiểu rằng chỉ vì planner tạo ra một parallel plan, tức là một execution plan gồm các parallel node, không có nghĩa executor sẽ tuân theo parallelism này. Có thể có các điều kiện, đặc biệt là tại runtime, ngăn PostgreSQL thực thi một parallel plan, ngay cả khi đó là lựa chọn tối ưu (chẳng hạn PostgreSQL không có đủ chỗ để spawn số parallel process cần thiết).

Trong subsection sau, bạn sẽ tìm hiểu các parallel node chính hiện có.

### Các Gather node

Một parallel execution plan luôn bao gồm hai loại node **Gather**: một node **Gather** thông thường và một Gather Merge node.
