-- ============================================
-- Laptop Borrowing Management System - MySQL Version
-- Database Name: laptop_borrowing_system
-- ============================================

-- Create and use database
CREATE DATABASE IF NOT EXISTS laptop_borrowing_system;
USE laptop_borrowing_system;

-- ============================================
-- 1. CREATE TABLES
-- ============================================

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    role ENUM('admin', 'student', 'teacher') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Laptops Table
CREATE TABLE IF NOT EXISTS laptops (
    laptop_id INT AUTO_INCREMENT PRIMARY KEY,
    brand VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    status ENUM('available', 'borrowed', 'maintenance') NOT NULL DEFAULT 'available'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Borrowing Records Table
CREATE TABLE IF NOT EXISTS borrowing_records (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    laptop_id INT NOT NULL,
    borrow_date DATETIME NOT NULL,
    expected_return_date DATE NOT NULL,
    actual_return_date DATETIME,
    status ENUM('active', 'returned') NOT NULL DEFAULT 'active',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (laptop_id) REFERENCES laptops(laptop_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- 2. INSERT DEFAULT USERS
-- ============================================
-- Note: These are example hashed passwords for 'password123'
-- In production, generate proper hashed passwords using your application

INSERT INTO users (username, password, name, role) VALUES 
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqYqYqYqYq', 'Admin User', 'admin'),
('student1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqYqYqYqYq', 'John Doe', 'student'),
('teacher1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqYqYqYqYq', 'Jane Smith', 'teacher'),
('student2', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqYqYqYqYq', 'Alice Johnson', 'student'),
('teacher2', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqYqYqYqYq', 'Bob Wilson', 'teacher');

-- ============================================
-- 3. INSERT SAMPLE LAPTOPS
-- ============================================

INSERT INTO laptops (brand, model, status) VALUES 
('Dell', 'Latitude 5420', 'available'),
('HP', 'EliteBook 840', 'available'),
('Lenovo', 'ThinkPad X1', 'available'),
('Apple', 'MacBook Pro', 'available'),
('Asus', 'ZenBook 14', 'maintenance'),
('Acer', 'Aspire 5', 'available'),
('MSI', 'Modern 14', 'available'),
('Samsung', 'Galaxy Book', 'available'),
('Microsoft', 'Surface Laptop', 'available'),
('Razer', 'Blade 15', 'available');

-- ============================================
-- 4. INSERT SAMPLE BORROWING RECORDS (Optional)
-- ============================================

INSERT INTO borrowing_records (user_id, laptop_id, borrow_date, expected_return_date, actual_return_date, status) VALUES 
(2, 1, '2024-01-15 10:30:00', '2024-01-20', '2024-01-19 14:20:00', 'returned'),
(3, 2, '2024-01-18 09:15:00', '2024-01-25', NULL, 'active');

-- ============================================
-- 5. VERIFICATION QUERIES
-- ============================================

-- Check all users
SELECT * FROM users;

-- Check all laptops
SELECT * FROM laptops;

-- Check all borrowing records
SELECT * FROM borrowing_records;

-- Check available laptops
SELECT * FROM laptops WHERE status = 'available';

-- Check active borrowings with user and laptop details
SELECT 
    br.record_id,
    u.name as user_name,
    u.role,
    l.brand,
    l.model,
    br.borrow_date,
    br.expected_return_date
FROM borrowing_records br
JOIN users u ON br.user_id = u.user_id
JOIN laptops l ON br.laptop_id = l.laptop_id
WHERE br.status = 'active';

-- ============================================
-- 6. USEFUL QUERIES FOR MANAGEMENT
-- ============================================

-- Count laptops by status
SELECT status, COUNT(*) as count 
FROM laptops 
GROUP BY status;

-- View overdue borrowings (past expected return date)
SELECT 
    br.record_id,
    u.name as borrower,
    l.brand,
    l.model,
    br.borrow_date,
    br.expected_return_date,
    DATEDIFF(CURDATE(), br.expected_return_date) as days_overdue
FROM borrowing_records br
JOIN users u ON br.user_id = u.user_id
JOIN laptops l ON br.laptop_id = l.laptop_id
WHERE br.status = 'active' 
AND br.expected_return_date < CURDATE();

-- User borrowing history
SELECT 
    u.name,
    COUNT(*) as total_borrowings,
    SUM(CASE WHEN br.status = 'active' THEN 1 ELSE 0 END) as active_borrowings
FROM users u
LEFT JOIN borrowing_records br ON u.user_id = br.user_id
WHERE u.role IN ('student', 'teacher')
GROUP BY u.user_id, u.name;
