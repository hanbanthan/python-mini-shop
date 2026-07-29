# Plan Checklist — Hệ thống quản lý cửa hàng mini (Python)

> Đánh dấu `[x]` khi hoàn thành. Đi theo thứ tự giai đoạn — mỗi giai đoạn nên chạy được (runnable) trước khi qua giai đoạn tiếp theo.

---

## Giai đoạn 0 — Khởi tạo dự án

- [ x] Tạo repo/thư mục dự án, khởi tạo git
- [ x] Tạo virtual environment (venv/poetry/pipenv)
- [ x] Tạo cấu trúc thư mục ban đầu (ví dụ):
  - `models/`, `services/`, `repositories/`, `database/`, `patterns/` (hoặc `discount/`, `factories/`), `exceptions/`, `config/`, `cli/`, `tests/`
- [ x] Tạo file `requirements.txt` (hoặc `pyproject.toml`)
- [ x] Tạo file `.gitignore`
- [ x] Tạo file `README.md` (mục lục ban đầu, sẽ điền chi tiết ở cuối)
- [ x] Tạo `main.py` (entry point) chỉ in "Hello" để xác nhận chạy được

## Giai đoạn 1 — Nền tảng: Config, Exception, Model (chưa có DB)

### 1.1 Configuration
- [ x] Tạo file cấu hình riêng (đường dẫn DB, hằng số giảm giá tối đa, v.v.), không hard-code trong logic

### 1.2 Exception classes
- [ x] Tạo base exception cho ứng dụng
- [ x] `ProductNotFoundError`
- [ x] `InvalidProductDataError`
- [ x] `InsufficientStockError`
- [ x] `InvalidOrderError`
- [ x] `CustomerNotFoundError`
- [ x] `InvalidCustomerDataError`
- [ x] `DatabaseOperationError`
- [ x] `UserInputError`

### 1.3 Enum
- [ x] Enum trạng thái sản phẩm (active/inactive)
- [ x] Enum loại khách hàng (thường/VIP)
- [ x] Enum trạng thái đơn hàng (pending/completed/cancelled...)

### 1.4 Model / Entity (chưa cần lưu DB, chỉ là class Python thuần)
- [ x] Class `Product` (id, name, category, price, stock_quantity, tags: set, is_active, created_at, updated_at) — encapsulation cho stock_quantity
- [ x] Class `Customer` (id, full_name, email, phone, customer_type, timestamps)
- [ x] Class `OrderItem` (product_id, product_name_snapshot, quantity, unit_price_snapshot, subtotal — tính từ quantity*unit_price)
- [ x] Class `Order` (id, customer_id, items: list[OrderItem], total_before_discount, discount_amount, total_amount, status, timestamps) — tổng tiền tính từ items, không set trực tiếp
- [ x] Quyết định class nào dùng data class, ghi chú lý do (comment/docstring)
- [ x] Viết docstring/type hint cơ bản cho tất cả class trên

**Checkpoint:** import được các model, tạo object thử nghiệm trong `main.py`, không lỗi.

## Giai đoạn 2 — Database layer

- [ ] Thiết kế schema SQL cho 4 bảng: `products`, `customers`, `orders`, `order_items`
- [ ] Viết script khởi tạo database (tạo bảng, khóa chính/ngoại, ràng buộc UNIQUE cho email)
- [ ] Viết script/seed dữ liệu mẫu
- [ ] Tạo class quản lý kết nối DB theo **Singleton pattern**
- [ ] Đảm bảo đóng connection/cursor đúng cách (context manager)
- [ ] Viết hàm helper thực thi query an toàn (parameterized query — chống SQL Injection)
- [ ] Test thủ công: chạy script khởi tạo, kiểm tra bảng được tạo đúng trong SQLite

**Checkpoint:** DB file được tạo, có thể connect/query thủ công qua sqlite3 CLI để xác nhận bảng đúng.

## Giai đoạn 3 — Repository layer (Repository Pattern)

- [ ] Định nghĩa abstract base class/interface cho Repository (contract: add, get_by_id, get_all, update, delete/deactivate, ...)
- [ ] `ProductRepository` (implement CRUD dùng DB layer ở Giai đoạn 2)
- [ ] `CustomerRepository` (implement CRUD, kiểm tra email trùng ở tầng này hoặc service)
- [ ] `OrderRepository` (tạo order + order_items, đọc order kèm chi tiết, lọc theo trạng thái/thời gian/khách hàng)
- [ ] Đảm bảo mỗi repository tự bắt lỗi DB và raise `DatabaseOperationError` (không để lộ raw DB exception ra ngoài)
- [ ] Viết test thủ công nhanh cho từng repository (script tạm hoặc REPL)

**Checkpoint:** có thể add/get/update/delete Product và Customer qua repository, dữ liệu lưu đúng trong DB.

## Giai đoạn 4 — Discount Policy (Strategy + Factory Pattern)

- [ ] Định nghĩa abstract class/interface `DiscountPolicy` (method tính discount)
- [ ] `RegularCustomerDiscount` (0%)
- [ ] `VIPCustomerDiscount` (10%, +5% nếu đơn > 5,000,000đ)
- [ ] Áp giới hạn tổng giảm giá không vượt quá 15% (đặt ở nơi hợp lý — trong policy hoặc 1 lớp validate chung)
- [ ] `DiscountPolicyFactory` — chọn policy theo loại khách hàng
- [ ] Viết test thủ công: tính giảm giá cho khách thường, VIP, VIP đơn lớn, kiểm tra giới hạn 15%

**Checkpoint:** factory trả về đúng policy, tính đúng số tiền giảm giá cho các case.

## Giai đoạn 5 — Business Service layer (Product & Customer)

### 5.1 ProductService
- [ ] Thêm sản phẩm (validate: tên không rỗng, giá > 0, tồn kho là int không âm)
- [ ] Hiển thị danh sách sản phẩm
- [ ] Tìm kiếm sản phẩm (theo id, tên không phân biệt hoa/thường, danh mục, khoảng giá, tag, trạng thái)
- [ ] Cập nhật sản phẩm (chỉ cập nhật trường được nhập, giữ nguyên trường bỏ trống, validate trước khi lưu, chặn nếu không tồn tại, chặn tồn kho âm)
- [ ] Xóa/ngừng hoạt động sản phẩm (nếu chưa từng bán → xóa; nếu đã từng bán → chuyển inactive)
- [ ] Viết exception phù hợp khi input sai hoặc không tìm thấy

### 5.2 CustomerService
- [ ] Thêm khách hàng (validate email format cơ bản, chặn email trùng)
- [ ] Hiển thị danh sách khách hàng
- [ ] Tìm kiếm khách hàng
- [ ] Cập nhật khách hàng
- [ ] Phân loại khách hàng thường/VIP
- [ ] Không cho xóa khách hàng đã có đơn hàng (nếu làm mất lịch sử)

**Checkpoint:** viết 1 script CLI tạm test được add/search/update/deactivate sản phẩm và khách hàng qua service (chưa cần menu đầy đủ).

## Giai đoạn 6 — Order Service (nghiệp vụ phức tạp nhất)

- [ ] Thiết kế method tạo đơn hàng nhận: customer_id, list[(product_id, quantity)]
- [ ] Bước kiểm tra: khách hàng tồn tại
- [ ] Bước kiểm tra: từng sản phẩm tồn tại và đang active
- [ ] Bước kiểm tra: đủ tồn kho cho từng sản phẩm
- [ ] Bước kiểm tra: đơn hàng phải có ít nhất 1 sản phẩm
- [ ] Tính tổng tiền từng sản phẩm và tổng tiền đơn hàng (snapshot tên + giá tại thời điểm mua)
- [ ] Gọi DiscountPolicyFactory để áp dụng giảm giá theo loại khách hàng
- [ ] Tính số tiền cuối cùng
- [ ] Thực hiện toàn bộ trong 1 **transaction**: tạo order → tạo order_items → cập nhật tồn kho → commit
- [ ] Rollback toàn bộ nếu có bước nào lỗi (không để order tồn tại mà tồn kho chưa trừ, hoặc ngược lại)
- [ ] Method xem danh sách đơn hàng (lọc theo trạng thái, khoảng thời gian, khách hàng)
- [ ] Method xem chi tiết 1 đơn hàng (kèm danh sách sản phẩm, tổng tiền, giảm giá)

**Checkpoint:** tạo được 1 đơn hàng hoàn chỉnh qua service, kiểm tra DB: order, order_items, và stock_quantity đều cập nhật đúng. Thử case lỗi giữa chừng (vd sản phẩm hết hàng) → xác nhận rollback, không có dữ liệu rác.

## Giai đoạn 7 — Observer Pattern (nâng cao, sau khi đơn hàng hoạt động ổn định)

- [ ] Định nghĩa interface/abstract class cho Event Handler / Observer
- [ ] Cơ chế đăng ký (subscribe) các observer vào OrderService (không hard-code phụ thuộc trực tiếp)
- [ ] Observer: xác nhận cập nhật tồn kho (log hoặc thông báo)
- [ ] Observer: gửi thông báo khách hàng (giả lập, chỉ print/log — không cần gửi email thật)
- [ ] Observer: ghi audit log khi tạo đơn hàng thành công
- [ ] Phát sự kiện ngay sau khi tạo đơn hàng thành công trong OrderService
- [ ] Đảm bảo logic tạo đơn hàng không phụ thuộc trực tiếp vào từng observer cụ thể

**Checkpoint:** khi tạo đơn hàng thành công, thấy log/thông báo từ các observer chạy độc lập.

## Giai đoạn 8 — Báo cáo doanh thu

- [ ] Tổng số đơn hàng
- [ ] Tổng doanh thu trước giảm giá / tổng tiền giảm giá / doanh thu thực nhận
- [ ] Sản phẩm bán chạy nhất + số lượng đã bán
- [ ] Doanh thu theo danh mục
- [ ] Doanh thu theo ngày/tháng
- [ ] Giá trị đơn hàng trung bình
- [ ] (Nâng cao) chọn khoảng thời gian báo cáo tùy chỉnh
- [ ] (Nâng cao) top đơn hàng giá trị cao nhất, top khách hàng chi tiêu nhiều nhất

**Checkpoint:** chạy báo cáo trên dữ liệu mẫu, số liệu khớp thủ công.

## Giai đoạn 9 — CLI hoàn chỉnh (giao diện dòng lệnh)

- [ ] Thiết kế menu chính (loop chạy đến khi chọn thoát)
- [ ] Menu: Thêm sản phẩm / danh sách / tìm kiếm / cập nhật / xóa-ngừng hoạt động
- [ ] Menu: Thêm/quản lý khách hàng
- [ ] Menu: Tạo đơn hàng (chọn khách hàng, chọn nhiều sản phẩm, nhập số lượng, hiển thị hóa đơn)
- [ ] Menu: Xem đơn hàng (danh sách, chi tiết, tìm/lọc)
- [ ] Menu: Xem báo cáo doanh thu
- [ ] Menu: Thoát chương trình
- [ ] Bắt lỗi input sai (nhập chữ thay vì số, lựa chọn menu không tồn tại...) — chương trình không crash, quay lại menu
- [ ] Hiển thị thông báo lỗi rõ ràng, dễ hiểu cho người dùng
- [ ] (Nâng cao) phân trang cho danh sách dài

**Checkpoint:** chạy `main.py`, thao tác được toàn bộ luồng nghiệp vụ từ đầu đến cuối qua menu, không bị crash khi nhập sai.

## Giai đoạn 10 — Unit Test

- [ ] Chọn framework (`unittest` hoặc `pytest`), cấu hình thư mục `tests/`
- [ ] Test: thêm sản phẩm hợp lệ
- [ ] Test: thêm sản phẩm giá không hợp lệ
- [ ] Test: tìm sản phẩm tồn tại
- [ ] Test: tìm sản phẩm không tồn tại
- [ ] Test: cập nhật tồn kho hợp lệ
- [ ] Test: chặn mua vượt quá tồn kho
- [ ] Test: chặn tạo đơn hàng không có sản phẩm
- [ ] Test: tính giảm giá khách hàng thường
- [ ] Test: tính giảm giá khách hàng VIP
- [ ] Test: rollback khi tạo đơn hàng thất bại
- [ ] (Khuyến khích) test sản phẩm ngừng hoạt động
- [ ] (Khuyến khích) test khách hàng trùng email
- [ ] (Khuyến khích) test đơn hàng nhiều sản phẩm
- [ ] (Khuyến khích) test giới hạn giảm giá tối đa 15%
- [ ] (Khuyến khích) test lỗi database (mock)
- [ ] (Khuyến khích) test truy vấn tìm kiếm/lọc
- [ ] (Khuyến khích) test dữ liệu biên (giá = 0, số lượng = 0...)
- [ ] (Khuyến khích) test dùng mock/fake repository thay vì DB thật

**Checkpoint:** toàn bộ test pass, chạy `pytest`/`python -m unittest` không lỗi.

## Giai đoạn 11 — Rà soát quy tắc bắt buộc (trước khi coi là "xong phần lõi")

- [ ] Không có file/hàm nào chứa toàn bộ logic chương trình
- [ ] Không dùng biến global cho dữ liệu nghiệp vụ
- [ ] Service không query DB trực tiếp (luôn qua Repository)
- [ ] Không có chỗ nào nối chuỗi SQL từ input người dùng
- [ ] Không có `except:` bắt lỗi chung chung không phân loại
- [ ] Không có nơi nào bỏ qua exception im lặng
- [ ] Không trừ tồn kho trước khi validate xong
- [ ] Transaction tạo đơn hàng chỉ commit 1 lần duy nhất khi mọi bước thành công
- [ ] Sản phẩm đã bán không bị xóa cứng (chỉ chuyển inactive)
- [ ] Không có cấu hình nhạy cảm hard-code trong source
- [ ] Chính sách giảm giá không hard-code trong OrderService (đi qua Strategy/Factory)
- [ ] Cả 4 pattern (Singleton, Repository, Strategy, Factory) đều giải quyết vấn đề thực, không chỉ hình thức

## Giai đoạn 12 — Yêu cầu nâng cao (tùy thời gian còn lại, làm sau khi phần lõi ổn định)

- [ ] Type hint đầy đủ cho toàn bộ codebase
- [ ] Dùng `Decimal` cho các giá trị tiền tệ (thay float)
- [ ] Dùng context manager (`with`) cho DB connection và các resource khác
- [ ] Thiết lập logging bằng module `logging` (thay vì print cho log hệ thống)
- [ ] Tách file cấu hình riêng (env/json/yaml) nếu chưa làm ở Giai đoạn 1
- [ ] Cơ chế migration DB đơn giản (versioning schema)
- [ ] Dependency injection cho service/repository (constructor injection)
- [ ] Phân trang cho danh sách sản phẩm/đơn hàng/khách hàng
- [ ] Rà soát lại chống SQL Injection toàn bộ query
- [ ] Bổ sung test dùng mock, đo test coverage
- [ ] Viết README đầy đủ (cài đặt, chạy, cấu trúc thư mục, cách test)
- [ ] Cơ chế audit log riêng biệt (không chỉ qua Observer ở Giai đoạn 7)
- [ ] Xử lý concurrent — nhiều người cùng mua 1 sản phẩm (khóa/lock ở tầng DB hoặc service)
- [ ] Dockerfile / docker-compose để chạy độc lập
- [ ] Thiết lập linting + formatting (ví dụ: flake8/ruff + black)
- [ ] Static type checking (mypy)
- [ ] Cơ chế export báo cáo (CSV/Excel/PDF)

## Giai đoạn 13 — Hoàn thiện

- [ ] Đọc lại toàn bộ yêu cầu gốc, đối chiếu từng mục đã làm
- [ ] Dọn dẹp code thừa, xóa đoạn debug/print thử nghiệm
- [ ] Cập nhật README lần cuối
- [ ] Cập nhật mục "Trạng thái hiện tại" trong `project-context.md`
- [ ] Chạy lại toàn bộ test suite lần cuối
- [ ] Demo thử toàn bộ luồng nghiệp vụ end-to-end trên dữ liệu sạch
