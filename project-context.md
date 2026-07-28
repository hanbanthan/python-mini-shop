# Project Context — Hệ thống quản lý cửa hàng mini (Python)

> File này dùng để paste vào đầu prompt mỗi khi hỏi AI về dự án, để AI nắm được bối cảnh mà không cần giải thích lại từ đầu.

## 1. Tổng quan dự án

Xây dựng một chương trình Python chạy trên giao diện dòng lệnh (CLI) để quản lý cửa hàng mini, gồm:
- Sản phẩm
- Khách hàng
- Đơn hàng
- Tồn kho
- Doanh thu

Dữ liệu được lưu trữ trong database (SQLite hoặc tương đương). Chương trình chạy liên tục cho đến khi người dùng chủ động chọn thoát.

Đây là bài tập tổng hợp dùng để đánh giá các nhóm kỹ năng: Basic Syntax, Data Type, Condition & Exception Handling, OOP, Design Pattern, Database, Unit Test và chất lượng source code.

## 2. Chức năng chính cần có

- Thêm / hiển thị danh sách / tìm kiếm / cập nhật / xóa (hoặc ngừng hoạt động) sản phẩm
- Thêm và quản lý khách hàng (thường / VIP)
- Tạo đơn hàng (nhiều sản phẩm, kiểm tra tồn kho, áp dụng giảm giá)
- Xem danh sách và chi tiết đơn hàng (tìm kiếm, lọc theo trạng thái/thời gian)
- Xem báo cáo doanh thu (tổng doanh thu, sản phẩm bán chạy, doanh thu theo danh mục/thời gian...)
- Thoát chương trình

## 3. Kiến trúc & nguyên tắc thiết kế bắt buộc

**Tổ chức code:**
- Không viết toàn bộ chương trình trong 1 file hoặc 1 hàm
- Tách theo layer: Model/Entity — Business Service — Repository/Data Access — Database — Design Pattern — Exception — Configuration — CLI — Unit Test
- Không dùng biến global để lưu dữ liệu nghiệp vụ

**Đối tượng nghiệp vụ chính:**
- Product, Customer, OrderItem, Order
- ProductRepository, CustomerRepository, OrderRepository
- ProductService, CustomerService, OrderService
- Database connection manager (Singleton)
- Discount policy component (Strategy + Factory)

**Kiểu dữ liệu:** phải dùng hợp lý String, Int, Float/Decimal, Boolean, List, Tuple, Dict, Set, Date/Time, Enum, None — ví dụ Enum cho trạng thái, Decimal cho tiền tệ, Set cho tag không trùng lặp.

**OOP:**
- Encapsulation: tồn kho, trạng thái đơn hàng, tổng tiền, giảm giá không được set trực tiếp tùy ý — phải qua nghiệp vụ
- Inheritance/Polymorphism: chính sách giảm giá theo loại khách hàng (thường 0%, VIP 10%, đơn >5,000,000đ +5%, tổng giảm tối đa 15%)
- Abstract class/Interface cho: Repository, Discount Policy, Notification, Logging, hoặc Event Handler (chọn tối thiểu 1-2 nhóm)
- Data class cho các đối tượng thuần lưu dữ liệu (cần giải thích lý do chọn)

**Design Pattern (tối thiểu 3, phải giải quyết vấn đề thực, không hình thức):**
1. Singleton — quản lý kết nối database/cấu hình dùng chung
2. Repository — tách data access khỏi business logic
3. Strategy — chính sách giảm giá độc lập, có thể đổi runtime
4. Factory — chọn/tạo discount strategy theo loại khách hàng
5. Observer (nâng cao) — khi đơn hàng tạo thành công, phát sự kiện cho: cập nhật tồn kho, gửi thông báo (giả lập), ghi audit log, cập nhật báo cáo... các thành phần này độc lập với logic tạo đơn hàng

## 4. Database

SQLite (hoặc DB quan hệ tương đương), có thể dùng ORM.

**Bảng chính:**
- `products`: id, name, category, price, stock_quantity, tags, is_active, created_at, updated_at
- `customers`: id, full_name, email (unique), phone, customer_type, created_at, updated_at
- `orders`: id, customer_id, total_before_discount, discount_amount, total_amount, status, created_at, updated_at
- `order_items`: id, order_id, product_id, product_name_snapshot, quantity, unit_price_snapshot, subtotal
  - Lưu snapshot tên/giá tại thời điểm mua để bảo toàn lịch sử

**Quan hệ:** 1 customer — N orders; 1 order — N order_items; order_items tham chiếu product. Cần khóa chính/ngoại và ràng buộc phù hợp.

**Transaction tạo đơn hàng** (phải atomic, có rollback khi lỗi):
kiểm tra khách hàng → kiểm tra sản phẩm → kiểm tra tồn kho → tính tổng tiền → tính giảm giá → tạo order → tạo order_items → cập nhật tồn kho → commit (hoặc rollback toàn bộ nếu lỗi ở bất kỳ bước nào)

**An toàn:** không nối chuỗi SQL trực tiếp từ input người dùng (dùng parameterized query), đóng connection/resource đúng cách, có script khởi tạo DB + dữ liệu mẫu, không hard-code thông tin nhạy cảm.

## 5. Exception Handling

Tự thiết kế các exception nghiệp vụ riêng biệt (tối thiểu):
- ProductNotFoundError, InvalidProductDataError, InsufficientStockError
- InvalidOrderError, CustomerNotFoundError, InvalidCustomerDataError
- DatabaseOperationError, UserInputError

Nguyên tắc: không bắt except chung chung không phân loại, không nuốt lỗi im lặng, thông báo lỗi rõ ràng cho người dùng, phân biệt lỗi nghiệp vụ vs lỗi hệ thống, đóng resource kể cả khi có lỗi (dùng context manager / finally).

## 6. Unit Test

Dùng framework test Python (vd. `unittest` hoặc `pytest`). Tối thiểu 10 test case bắt buộc, bao gồm: thêm sản phẩm hợp lệ/không hợp lệ, tìm sản phẩm tồn tại/không tồn tại, cập nhật tồn kho hợp lệ, chặn mua vượt tồn kho, chặn tạo đơn hàng rỗng, tính giảm giá khách thường/VIP, rollback khi tạo đơn hàng thất bại. Khuyến khích thêm test về sản phẩm ngừng hoạt động, email trùng, đơn hàng nhiều sản phẩm, giới hạn giảm giá, lỗi DB, mock/fake repository, dữ liệu biên.

## 7. Yêu cầu nâng cao (để lên điểm khá/giỏi, làm sau khi xong phần lõi)

Type hint đầy đủ, Decimal cho tiền tệ, context manager, logging module, file config riêng, migration DB, dependency injection, phân trang, chống SQL Injection, test coverage, README, audit log, xử lý concurrent mua hàng, Docker, linting/formatting, static type check, export báo cáo.

## 8. Những điều KHÔNG được làm (quy tắc kỹ thuật)

- Không viết toàn bộ chương trình/logic trong 1 file hoặc 1 hàm
- Không dùng biến global cho dữ liệu nghiệp vụ
- Không query DB trực tiếp trong business service (phải qua repository)
- Không nối chuỗi user input vào câu query
- Không bỏ qua exception, không bắt lỗi quá rộng
- Không trừ tồn kho trước khi validate
- Không commit nhiều lần rời rạc trong 1 transaction tạo đơn hàng
- Không xóa dữ liệu làm mất lịch sử giao dịch (sản phẩm đã bán → chuyển ngừng hoạt động, không xóa cứng)
- Không hard-code cấu hình nhạy cảm hoặc toàn bộ chính sách giảm giá trong logic tạo đơn
- Không dùng design pattern chỉ để cho có, không giải quyết vấn đề thực

## 9. Tech Stack

**Ngôn ngữ & môi trường:**
- Python 3.11+
- venv (built-in) — hoặc Poetry nếu muốn thể hiện thêm kỹ năng quản lý dependency

**CLI:**
- `input()`/`print()` thuần với vòng lặp menu (bắt buộc, đúng tinh thần Basic Syntax)
- `rich` (tuỳ chọn) — bảng, màu sắc, format tiền tệ đẹp cho danh sách sản phẩm/hóa đơn

**Database:**
- `sqlite3` (built-in) — đáp ứng đúng yêu cầu, tự kiểm soát transaction/rollback rõ ràng
- SQLAlchemy Core (tuỳ chọn, nâng cao) — query an toàn, kiểm soát transaction rõ, phù hợp thể hiện Repository Pattern
- `alembic` (nâng cao, đi kèm SQLAlchemy) — migration DB có version; nếu không dùng ORM thì viết migration bằng script SQL versioned đơn giản

**Model / Data:**
- `dataclasses` (built-in) — Product, Customer, OrderItem, Order
- `enum.Enum` (built-in) — CustomerType, ProductStatus, OrderStatus
- `decimal.Decimal` (built-in) — bắt buộc cho tiền tệ, không dùng float

**Validation:**
- Validator thủ công (regex email, kiểm tra số âm...) — đúng tinh thần Condition & Exception Handling
- `pydantic` v2 (tuỳ chọn, nâng cao) — validate tự động dựa trên type hint, cẩn thận không để thay thế hết phần OOP/exception tự thiết kế

**Design Pattern:**
- `abc.ABC` + `abstractmethod` (built-in) — đủ cho Singleton, Repository, Strategy, Factory, Observer, không cần thư viện ngoài

**Logging:**
- `logging` (built-in)

**Configuration:**
- `.env` + `python-dotenv`, hoặc file `config.py`/`config.json` đơn giản

**Unit Test:**
- `pytest` (khuyến nghị hơn `unittest`)
- `unittest.mock` / `pytest-mock` — mock/fake repository

**Dependency Injection:**
- Inject thủ công qua constructor — không cần framework DI riêng

### Phần nâng cao (Giai đoạn 12 — làm sau khi phần lõi ổn định)

| Yêu cầu nâng cao | Công cụ/thư viện đề xuất |
|---|---|
| Type hint đầy đủ + static type check | `mypy` |
| Decimal cho tiền tệ | `decimal.Decimal` (built-in, đã dùng từ đầu) |
| Context manager | `contextlib` (built-in) cho DB connection và resource khác |
| Logging | `logging` (built-in) |
| File cấu hình riêng | `python-dotenv` + `.env` |
| Migration DB | `alembic` (nếu dùng SQLAlchemy) hoặc script SQL versioned thủ công |
| Dependency Injection | Constructor injection thủ công (không cần thư viện) |
| Phân trang | Tự viết bằng `LIMIT`/`OFFSET` trong query |
| Chống SQL Injection | Parameterized query (`sqlite3` `?` placeholder hoặc SQLAlchemy) |
| Unit test dùng mock | `unittest.mock` / `pytest-mock` |
| Test coverage | `pytest-cov` |
| README | Viết tay, không cần công cụ |
| Audit log | `logging` ghi ra file riêng, hoặc bảng `audit_log` trong DB |
| Xử lý nhiều người dùng cùng mua | Row-level lock hoặc transaction isolation của SQLite/SQLAlchemy |
| Docker | `Dockerfile` đơn giản (`python:3.11-slim`), không cần docker-compose |
| Linting & formatting | `ruff` (lint, thay thế flake8/isort) + `black` (format) |
| Static type check | `mypy` |
| Export báo cáo | `csv` (built-in) cho CSV; `openpyxl` cho Excel `.xlsx` |

*(Tuỳ chọn thêm: `pre-commit` để tự động chạy ruff/black/mypy trước mỗi commit, thể hiện quy trình chuyên nghiệp.)*

## 10. Trạng thái hiện tại của dự án

*(Cập nhật mục này khi dự án tiến triển — ví dụ: "Đã hoàn thành Giai đoạn 1-3, đang làm Giai đoạn 4 (Design Pattern)")*

- Hiện tại: chưa bắt đầu code, mới có tài liệu yêu cầu và kế hoạch (xem `plan-checklist.md`).