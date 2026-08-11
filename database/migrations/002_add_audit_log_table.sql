-- 002_add_audit_log_table.sql
-- Them bang audit log - luu audit log duoi dang du lieu co the truy van
-- (bo sung cho file logs/audit.log o Giai doan 7, khong thay the)

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    order_id INTEGER,
    customer_id INTEGER,
    details TEXT NOT NULL,
    created_at TEXT NOT NULL 
);

CREATE INDEX IF NOT EXISTS idx_audit_log_order_id ON audit_log (order_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log (created_at);

