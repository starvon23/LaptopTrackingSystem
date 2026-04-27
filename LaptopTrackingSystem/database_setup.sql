CREATE DATABASE IF NOT EXISTS laptop_borrowing_system;
USE laptop_borrowing_system;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role ENUM('admin', 'student', 'teacher') NOT NULL
);

CREATE TABLE laptops (
    laptop_id INT AUTO_INCREMENT PRIMARY KEY,
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    status ENUM('available', 'borrowed', 'maintenance') DEFAULT 'available'
);

CREATE TABLE borrowing_records (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    laptop_id INT NOT NULL,
    borrow_date DATETIME NOT NULL,
    expected_return_date DATE NOT NULL,
    actual_return_date DATETIME,
    status ENUM('active', 'returned') DEFAULT 'active',
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (laptop_id) REFERENCES laptops(laptop_id)
);