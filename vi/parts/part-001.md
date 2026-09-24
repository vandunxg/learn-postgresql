> EXPERT INSIGHT

# Learn PostgreSQL

## Ấn bản thứ hai

Sử dụng, quản lý và xây dựng các database an toàn, có khả năng mở rộng với PostgreSQL 16

Luca Ferrari  
Enrico Pirozzi

# Learn PostgreSQL

## Ấn bản thứ hai

Sử dụng, quản lý và xây dựng các database an toàn, có khả năng mở rộng với PostgreSQL 16

Luca Ferrari  
Enrico Pirozzi

BIRMINGHAM—MUMBAI

## Bản quyền

© 2023 Packt Publishing

Mọi quyền được bảo lưu. Không phần nào của cuốn sách này được phép sao chép, lưu trữ trong hệ thống truy xuất hoặc truyền đi dưới bất kỳ hình thức hay bằng bất kỳ phương tiện nào, nếu không có sự cho phép trước bằng văn bản của nhà xuất bản, ngoại trừ các trích dẫn ngắn được đưa vào các bài viết phê bình hoặc bài đánh giá.

Trong quá trình chuẩn bị cuốn sách này, mọi nỗ lực đã được thực hiện để đảm bảo tính chính xác của thông tin được trình bày. Tuy nhiên, thông tin trong cuốn sách này được bán mà không có bất kỳ bảo đảm nào, dù rõ ràng hay ngụ ý. Các tác giả, Packt Publishing, cũng như các đại lý và nhà phân phối của họ sẽ không chịu trách nhiệm về bất kỳ thiệt hại nào do cuốn sách này trực tiếp hoặc gián tiếp gây ra, hoặc bị cáo buộc là do cuốn sách này gây ra.

Packt Publishing đã cố gắng cung cấp thông tin nhãn hiệu về tất cả các công ty và sản phẩm được đề cập bằng cách viết hoa phù hợp. Tuy nhiên, Packt Publishing không thể đảm bảo tính chính xác của thông tin này.

Quản lý sản phẩm xuất bản cấp cao: Gebin George  
Biên tập viên phụ trách tuyển chọn – Peer Reviews: Gaurav Gavas  
Biên tập viên dự án: Meenakshi Vijay  
Biên tập viên phát triển nội dung: Elliot Dallow  
Biên tập viên hiệu đính: Safis Editing  
Biên tập viên kỹ thuật: Kushal Sharma  
Proofreader: Safis Editing  
Indexer: Pratik Shirodkar  
Nhà thiết kế trình bày: Rajesh Shirsath  
Developer Relations Marketing Executive: Vignesh Raju

Xuất bản lần đầu: tháng 10 năm 2020  
Ấn bản thứ hai: tháng 10 năm 2023  
Mã tham chiếu sản xuất: 1251023

Xuất bản bởi Packt Publishing Ltd.  
Grosvenor House  
11 St Paul’s Square  
Birmingham  
B3 1RB, UK.

ISBN 978-1-83763-564-1

www.packt.com

Xin dành tặng người vợ xinh đẹp của tôi, Emanuela; tôi yêu cô ấy như Santa yêu những chú tuần lộc của mình.

Xin dành tặng cậu con trai tuyệt vời của tôi, Diego, người đã thay đổi cuộc đời chúng tôi vào 1283788200.

Xin dành tặng cha mẹ tôi, Miriam và Anselmo: những người hâm mộ lớn nhất của tôi ngay từ ngày đầu tiên.

– Luca Ferrari

Để tưởng nhớ cha tôi, Ilario.

– Enrico Pirozzi

# Những người đóng góp

## Về các tác giả

Luca Ferrari đã say mê computer science từ thời Commodore 64, và hiện có bằng thạc sĩ (loại xuất sắc) cùng bằng Ph.D. từ University of Modena and Reggio Emilia. Ông đã viết một số bài báo nghiên cứu, bài viết kỹ thuật và chương sách. Năm 2011, ông được Nipissing University bổ nhiệm làm adjunct professor. Là một người dùng Unix nhiệt thành, ông là người ủng hộ mạnh mẽ open-source, và trong thời gian rảnh, ông cộng tác cho một vài dự án. Ông lần đầu biết đến PostgreSQL vào thời release 7.3; ông là người sáng lập và cựu chủ tịch của Italian PostgreSQL Users’ Group (ITPUG). Ông cũng thường xuyên nói chuyện tại các hội nghị và sự kiện kỹ thuật, đồng thời thực hiện hoạt động đào tạo chuyên môn.

Enrico Pirozzi đã say mê computer science từ khi mới 13 tuổi. Chiếc máy tính đầu tiên của ông là Commodore 64, và hiện ông có bằng thạc sĩ từ University of Bologna. Ông đã tham gia với tư cách diễn giả tại các hội nghị PostgreSQL trong nước và quốc tế. Ông lần đầu biết đến PostgreSQL từ release 7.2; ông là đồng sáng lập mailing list PostgreSQL đầu tiên của Ý và website PostgreSQL đầu tiên của Ý, đồng thời thường xuyên nói chuyện tại các hội nghị và sự kiện kỹ thuật cũng như thực hiện hoạt động đào tạo chuyên môn. Hiện tại, ông làm PostgreSQL database administrator tại Zucchetti Hospitality (Zucchetti Group S.p.a).

## Về các reviewer

Chris Mair có bằng thạc sĩ từ University of Trento, Italy, và làm việc freelance từ năm 2003. Portfolio của ông gồm các đóng góp cho hơn 25 công ty, trong đó có công việc tư vấn về database programming, performance optimization và seamless migration. Chris có chuyên môn về system programming và network programming, data processing, ML và nhiều lĩnh vực khác. Ông đặc biệt yêu thích PostgreSQL. Ông đã giảng dạy hơn 200 khóa học về nhiều chủ đề IT và đam mê open-source software.

Silvio Trancanella là software engineer với khoảng 12 năm kinh nghiệm phát triển backend, chủ yếu sử dụng Java Enterprise và PostgreSQL. Ông luôn bị cuốn hút bởi database management và ngay từ đầu sự nghiệp đã lập tức bị PostgreSQL thu hút. Ông đã làm việc khoảng 10 năm với phần mềm trong ngành du lịch, phát triển và duy trì các service quan trọng dựa trên PostgreSQL DBMS.

## Tìm hiểu thêm trên Discord

Để tham gia cộng đồng Discord dành cho cuốn sách này – nơi bạn có thể chia sẻ feedback, đặt câu hỏi cho tác giả và tìm hiểu về các bản phát hành mới – hãy quét mã QR bên dưới:

https://discord.gg/jYWCjF6Tku

# Mục lục

- Lời nói đầu • xxv
- Chương 1: Giới thiệu về PostgreSQL • 1
  - Yêu cầu kỹ thuật • 2
  - Tổng quan về PostgreSQL • 2
    - Lược sử PostgreSQL • 4
    - Có gì mới trong PostgreSQL 16? • 5
    - Chính sách release, version number và life cycle của PostgreSQL • 5
  - Khám phá thuật ngữ PostgreSQL • 6
  - Cài đặt PostgreSQL • 10
    - Cần cài đặt gì • 11
    - Cài đặt PostgreSQL từ binary package • 12
      - Sử dụng Docker image của cuốn sách • 13
      - Cài đặt PostgreSQL trên GNU/Linux Debian, Ubuntu và các bản phân phối phái sinh • 14
      - Cài đặt PostgreSQL trên Fedora Linux • 15
      - Cài đặt PostgreSQL trên FreeBSD • 16
    - Cài đặt PostgreSQL từ source • 17
    - Cài đặt PostgreSQL qua pgenv • 18
  - Tóm tắt • 19
  - Tài liệu tham khảo • 20
- Chương 2: Làm quen với cluster của bạn • 21
  - Yêu cầu kỹ thuật • 22
  - Quản lý cluster của bạn • 22
    - pg_ctl • 22
    - PostgreSQL processes • 28
  - Kết nối tới cluster • 31
      - Các template database • 31
    - Client command-line psql • 33
      - Nhập SQL statement qua psql • 35
      - Tổng quan về các command của psql • 38
    - Giới thiệu connection string • 39
  - Giải quyết các vấn đề connection thường gặp • 40
    - Database “foo” không tồn tại • 40
    - Connection bị từ chối • 40
    - Không có entry trong pg_hba.conf • 41
  - Khám phá disk layout của PGDATA • 42
     - Các object trong thư mục PGDATA • 43
       - Các tablespace • 45
  - Khám phá các configuration file và parameter • 46
  - Tóm tắt • 48
  - Kiểm tra kiến thức của bạn • 49
  - Tài liệu tham khảo • 49
- Chương 3: Quản lý user và connection • 51
  - Yêu cầu kỹ thuật • 52
  - Giới thiệu về user và group • 52
  - Quản lý role • 53
    - Tạo role mới • 53
      - Password, connection và availability của role • 54
    - Dùng role như một group • 55
    - Xóa role hiện có • 57
    - Kiểm tra role hiện có • 58
  - Quản lý incoming connection ở cấp role • 61
    - Cú pháp của pg_hba.conf • 62
    - Thứ tự các rule trong pg_hba.conf • 64
    - Gộp nhiều rule thành một rule duy nhất • 64
    - Dùng group thay cho các role đơn lẻ • 65
    - Dùng file thay cho các role đơn lẻ • 66
    - Kiểm tra các rule của pg_hba.conf • 67
    - Include các file khác trong pg_hba.conf • 68
  - Tóm tắt • 68
  - Kiểm tra kiến thức của bạn • 69
  - Tài liệu tham khảo • 69
- Chương 4: Các statement cơ bản • 71
  - Yêu cầu kỹ thuật • 72
    - Sử dụng Docker image • 72
    - Kết nối database • 72
  - Tạo và quản lý database • 73
    - Tạo database • 73
    - Quản lý database • 74
    - Giới thiệu schema • 74
    - PostgreSQL và schema public • 74
     - Biến search_path • 75
    - Cách bắt đầu làm việc đúng • 75
    - Liệt kê tất cả table • 76
    - Tạo database mới từ template đã sửa đổi • 77
    - Xóa table và database • 78
    - Xóa table • 78
    - Xóa database • 79
    - Tạo bản sao database • 79
