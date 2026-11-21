CREATE DATABASE IF NOT EXISTS integration_demo;
USE integration_demo;

CREATE TABLE IF NOT EXISTS client_records (
    client_id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(32),
    created_at DATE NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO client_records (client_id, name, email, phone, created_at)
VALUES
('C1001', 'Asha Rao', 'asha@example.com', '+91-9000000001', '2026-01-15'),
('C1002', 'Rohan Das', 'rohan@example.com', '+91-9000000002', '2026-02-02')
ON DUPLICATE KEY UPDATE
name = VALUES(name),
email = VALUES(email),
phone = VALUES(phone),
created_at = VALUES(created_at);
