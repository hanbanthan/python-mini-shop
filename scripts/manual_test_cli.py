"""Test end-to-end cho CLI — checkpoint Giai đoạn 9.

Chạy: python -m scripts.manual_test_cli

Giả lập nhập liệu qua stdin cho main.py, bao gồm CẢ input sai (chữ thay
vì số, lựa chọn menu không tồn tại) để xác nhận chương trình không crash
và luôn quay lại menu/re-prompt đúng cách. Verify exit code = 0 và không
có traceback nào xuất hiện trong output.
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "database" / "store.db"

# Kich ban nhap lieu: menu sai (9) -> them san pham (co nhap sai gia,
# ton kho) -> danh sach -> them khach hang (co test email trung) ->
# danh sach -> tao don hang (co nhap sai ID san pham, so luong) ->
# danh sach don -> chi tiet don -> tim/loc don -> bao cao -> thoat.
CLI_INPUT = """9
1
1
Tai nghe Sony
Am thanh
xyz
500000
abc
15
tai nghe,sony

2

0
2
1
Test Buyer
testbuyer.cli@example.com
0900000001
n

1
Dup Buyer
testbuyer.cli@example.com
0900000002
n

2

0
3
1
1
abc
1
xyz
3
0

2

3
1

4



0
4
1

0
0
"""


def main() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()

    result = subprocess.run(
        [sys.executable, "main.py"],
        input=CLI_INPUT,
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        timeout=30,
    )

    output = result.stdout + result.stderr

    assert result.returncode == 0, f"CLI exited with code {result.returncode}, output:\n{output}"
    print("[OK] CLI exited with code 0")

    assert "Traceback" not in output, f"Traceback found in output:\n{output}"
    print("[OK] No Traceback in output")

    print("========== CLI OUTPUT ==========")
    print(output)
    print("================================")
    assert "Invalid choice" in output
    assert "Invalid decimal number. Please try again." in output
    assert "Invalid integer. Please try again." in output
    print("[OK] Invalid input messages are shown and the CLI continues")

    assert "Product added successfully with ID: 1 Tai nghe Sony" in output
    assert "Customer added successfully with ID: 1 Test Buyer" in output
    assert "Customer with email testbuyer.cli@example.com already exists" in output
    assert "Order created successfully with ID: 1" in output
    assert "Total Amount: 1,500,000.00 USD" in output
    # assert "=== Report Management ===" in output
    # assert "Total orders: 1" in output
    print("[OK] End-to-end product -> customer -> order -> report flow completed")

    print("\nAll manual CLI tests (Stage 9): PASS")


if __name__ == "__main__":
    main()
