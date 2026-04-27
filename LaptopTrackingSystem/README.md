# 🖥️ Laptop Borrowing Management System

A web-based system for managing laptop borrowing with role-based access control.

## Features

- **Role-Based Access Control**
  - Admin: View-only access to all records
  - Students/Teachers: Can borrow and return laptops

- **Laptop Inventory Management**
  - Track laptop status (Available, Borrowed, Maintenance)
  - Real-time availability updates

- **Borrowing Process**
  - Select available laptops
  - Set expected return dates
  - Track borrowing history

- **Admin Dashboard**
  - View all borrowing records
  - Search and filter functionality
  - System statistics

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Start the Flask server:
```bash
python app.py
```

3. Access the system at `http://localhost:5000`

## Default Credentials

- **Admin**: username: `admin`, password: `password123`
- **Student**: username: `student1`, password: `password123`
- **Teacher**: username: `teacher1`, password: `password123`

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite3 (laptop_system.db) / MySQL (laptop_borrowing_system)
- **Frontend**: HTML, CSS, Jinja2 templates
- **Authentication**: Werkzeug password hashing, Flask sessions

## Database Information

- **Database Name**: laptop_borrowing_system
- **SQLite File**: laptop_system.db
- **MySQL Database**: laptop_borrowing_system (use database_mysql.sql)

## Database Schema

### Users Table
- user_id (Primary Key)
- username
- password (hashed)
- name
- role (admin/student/teacher)

### Laptops Table
- laptop_id (Primary Key)
- brand
- model
- status (available/borrowed/maintenance)

### Borrowing Records Table
- record_id (Primary Key)
- user_id (Foreign Key)
- laptop_id (Foreign Key)
- borrow_date
- expected_return_date
- actual_return_date
- status (active/returned)

## Access Control

- Admins can only view records, cannot borrow laptops
- Students and teachers can borrow/return laptops
- All users must authenticate to access the system
