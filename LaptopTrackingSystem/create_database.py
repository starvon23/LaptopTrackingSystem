"""
Database Creation Script for Laptop Borrowing Management System
Database Name: laptop_borrowing_system (SQLite: laptop_system.db)
Run this script to create the SQLite database with all tables and sample data
Usage: python create_database.py
"""

import sqlite3
from werkzeug.security import generate_password_hash

# Database configuration
DATABASE_NAME = 'laptop_system.db'  # SQLite database file name

def create_database():
    # Connect to database (creates file if doesn't exist)
    print(f"Creating database: {DATABASE_NAME}")
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    print("Creating database tables...")
    
    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'student', 'teacher'))
        )
    ''')
    print("✓ Users table created")
    
    # Create Laptops table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS laptops (
            laptop_id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'available' CHECK(status IN ('available', 'borrowed', 'maintenance'))
        )
    ''')
    print("✓ Laptops table created")
    
    # Create Borrowing Records table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS borrowing_records (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            laptop_id INTEGER NOT NULL,
            borrow_date TEXT NOT NULL,
            expected_return_date TEXT NOT NULL,
            actual_return_date TEXT,
            status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'returned')),
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (laptop_id) REFERENCES laptops(laptop_id)
        )
    ''')
    print("✓ Borrowing records table created")
    
    # Check if users already exist
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    
    if user_count == 0:
        print("\nInserting default users...")
        hashed_password = generate_password_hash('password123')
        
        users = [
            ('admin', hashed_password, 'Admin User', 'admin'),
            ('student1', hashed_password, 'John Doe', 'student'),
            ('teacher1', hashed_password, 'Jane Smith', 'teacher'),
            ('student2', hashed_password, 'Alice Johnson', 'student'),
            ('teacher2', hashed_password, 'Bob Wilson', 'teacher')
        ]
        
        cursor.executemany('INSERT INTO users (username, password, name, role) VALUES (?, ?, ?, ?)', users)
        print(f"✓ Inserted {len(users)} users")
    else:
        print(f"\n✓ Users already exist ({user_count} users)")
    
    # Check if laptops already exist
    cursor.execute('SELECT COUNT(*) FROM laptops')
    laptop_count = cursor.fetchone()[0]
    
    if laptop_count == 0:
        print("\nInserting sample laptops...")
        laptops = []
        brands = ['Dell', 'HP', 'Lenovo', 'Apple', 'Asus', 'Acer', 'MSI', 'Samsung', 'Microsoft', 'Razer']
        models = ['Latitude', 'EliteBook', 'ThinkPad', 'MacBook Pro', 'ZenBook', 'Aspire', 'Modern', 'Galaxy Book', 'Surface', 'Blade']
        statuses = ['available', 'available', 'available', 'available', 'maintenance']
        
        for i in range(1, 47):  # Create 46 laptops
            brand = brands[i % len(brands)]
            model = f"{models[i % len(models)]} {i}"
            status = statuses[i % len(statuses)]
            laptops.append((brand, model, status))
        
        cursor.executemany('INSERT INTO laptops (brand, model, status) VALUES (?, ?, ?)', laptops)
        print(f"✓ Inserted {len(laptops)} laptops")
    else:
        print(f"\n✓ Laptops already exist ({laptop_count} laptops)")
    
    # Commit changes
    conn.commit()
    
    # Display summary
    print("\n" + "="*50)
    print("DATABASE CREATED SUCCESSFULLY!")
    print("="*50)
    
    cursor.execute('SELECT COUNT(*) FROM users')
    print(f"Total Users: {cursor.fetchone()[0]}")
    
    cursor.execute('SELECT COUNT(*) FROM laptops')
    print(f"Total Laptops: {cursor.fetchone()[0]}")
    
    cursor.execute('SELECT COUNT(*) FROM laptops WHERE status = "available"')
    print(f"Available Laptops: {cursor.fetchone()[0]}")
    
    print("\nDefault Login Credentials:")
    print("-" * 50)
    print("Admin:    username: admin    | password: password123")
    print("Student:  username: student1 | password: password123")
    print("Teacher:  username: teacher1 | password: password123")
    print("-" * 50)
    
    conn.close()
    print(f"\nDatabase file: {DATABASE_NAME}")
    print("Database name: laptop_borrowing_system")
    print("\nYou can now run: python app.py")

if __name__ == '__main__':
    create_database()
