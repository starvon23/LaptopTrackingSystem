from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'laptop-system-secret-key-flask'

# Database configuration
DATABASE_NAME = 'laptop_borrowing_system'  # Logical database name
DATABASE = 'laptop_system.db'  # SQLite file name

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'student', 'teacher'))
        )
    ''')
    
    # Laptops table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS laptops (
            laptop_id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'available' CHECK(status IN ('available', 'borrowed', 'maintenance'))
        )
    ''')
    
    # Borrowing records table
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
    
    # Insert default users
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        hashed_password = generate_password_hash('password123')
        cursor.execute('INSERT INTO users (username, password, name, role) VALUES (?, ?, ?, ?)',
                      ('admin', hashed_password, 'Admin User', 'admin'))
        cursor.execute('INSERT INTO users (username, password, name, role) VALUES (?, ?, ?, ?)',
                      ('student1', hashed_password, 'John Doe', 'student'))
        cursor.execute('INSERT INTO users (username, password, name, role) VALUES (?, ?, ?, ?)',
                      ('teacher1', hashed_password, 'Jane Smith', 'teacher'))
    
    # Insert sample laptops
    cursor.execute('SELECT COUNT(*) FROM laptops')
    if cursor.fetchone()[0] == 0:
        laptops = [
            ('Dell', 'Latitude 5420', 'available'),
            ('HP', 'EliteBook 840', 'available'),
            ('Lenovo', 'ThinkPad X1', 'available'),
            ('Apple', 'MacBook Pro', 'available'),
            ('Asus', 'ZenBook 14', 'maintenance')
        ]
        cursor.executemany('INSERT INTO laptops (brand, model, status) VALUES (?, ?, ?)', laptops)
    
    conn.commit()
    conn.close()

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Borrower-only decorator
def borrower_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') == 'admin':
            flash('Admins cannot perform borrowing actions', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['name'] = user['name']
            session['role'] = user['role']
            flash(f'Welcome, {user["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        
        flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        name = request.form['name']
        role = request.form['role']
        
        # Validation
        if not username or not password or not name or not role:
            flash('All fields are required', 'error')
            return redirect(url_for('register'))
        
        if role not in ['student', 'teacher']:
            flash('Invalid role selected', 'error')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return redirect(url_for('register'))
        
        conn = get_db()
        
        # Check if username already exists
        existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if existing_user:
            conn.close()
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        
        # Create new user
        hashed_password = generate_password_hash(password)
        conn.execute('INSERT INTO users (username, password, name, role) VALUES (?, ?, ?, ?)',
                    (username, hashed_password, name, role))
        conn.commit()
        conn.close()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    laptops_raw = conn.execute('SELECT * FROM laptops').fetchall()
    
    # Convert Row objects to dictionaries
    laptops = [dict(row) for row in laptops_raw]
    
    user_records = conn.execute('''
        SELECT br.*, l.brand, l.model 
        FROM borrowing_records br 
        JOIN laptops l ON br.laptop_id = l.laptop_id 
        WHERE br.user_id = ? 
        ORDER BY br.borrow_date DESC
    ''', (session['user_id'],)).fetchall()
    
    # Get active borrowers for admin
    active_borrowers = []
    if session.get('role') == 'admin':
        active_borrowers = conn.execute('''
            SELECT u.name, u.role, l.brand, l.model, l.laptop_id, br.borrow_date, br.expected_return_date
            FROM borrowing_records br
            JOIN users u ON br.user_id = u.user_id
            JOIN laptops l ON br.laptop_id = l.laptop_id
            WHERE br.status = 'active'
            ORDER BY br.borrow_date DESC
        ''').fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', laptops=laptops, user_records=user_records, active_borrowers=active_borrowers)

@app.route('/borrow', methods=['POST'])
@login_required
@borrower_required
def borrow():
    laptop_id = request.form['laptop_id']
    expected_return_date = request.form['expected_return_date']
    
    conn = get_db()
    laptop = conn.execute('SELECT * FROM laptops WHERE laptop_id = ? AND status = ?', 
                         (laptop_id, 'available')).fetchone()
    
    if not laptop:
        conn.close()
        flash('Laptop not available', 'error')
        return redirect(url_for('dashboard'))
    
    borrow_date = datetime.now().isoformat()
    
    conn.execute('INSERT INTO borrowing_records (user_id, laptop_id, borrow_date, expected_return_date) VALUES (?, ?, ?, ?)',
                (session['user_id'], laptop_id, borrow_date, expected_return_date))
    
    conn.execute('UPDATE laptops SET status = ? WHERE laptop_id = ?', ('borrowed', laptop_id))
    
    conn.commit()
    conn.close()
    
    flash('Laptop borrowed successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/return', methods=['POST'])
@login_required
@borrower_required
def return_laptop():
    record_id = request.form['record_id']
    
    conn = get_db()
    record = conn.execute('SELECT * FROM borrowing_records WHERE record_id = ? AND user_id = ? AND status = ?',
                         (record_id, session['user_id'], 'active')).fetchone()
    
    if not record:
        conn.close()
        flash('Invalid record', 'error')
        return redirect(url_for('dashboard'))
    
    return_date = datetime.now().isoformat()
    
    conn.execute('UPDATE borrowing_records SET actual_return_date = ?, status = ? WHERE record_id = ?',
                (return_date, 'returned', record_id))
    
    conn.execute('UPDATE laptops SET status = ? WHERE laptop_id = ?', ('available', record['laptop_id']))
    
    conn.commit()
    conn.close()
    
    flash('Laptop returned successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/admin/laptops')
@login_required
def admin_laptops():
    if session.get('role') != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    conn = get_db()
    
    # Get total count
    total = conn.execute('SELECT COUNT(*) FROM laptops').fetchone()[0]
    
    # Get paginated laptops
    offset = (page - 1) * per_page
    laptops = conn.execute('SELECT * FROM laptops ORDER BY laptop_id LIMIT ? OFFSET ?', 
                          (per_page, offset)).fetchall()
    conn.close()
    
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('admin_laptops.html', 
                         laptops=laptops, 
                         page=page, 
                         total_pages=total_pages,
                         total=total)

@app.route('/admin/laptop/<int:laptop_id>')
@login_required
def laptop_history(laptop_id):
    if session.get('role') != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    conn = get_db()
    laptop = conn.execute('SELECT * FROM laptops WHERE laptop_id = ?', (laptop_id,)).fetchone()
    
    if not laptop:
        conn.close()
        flash('Laptop not found', 'error')
        return redirect(url_for('admin_laptops'))
    
    # Get all borrowing history for this laptop
    history = conn.execute('''
        SELECT br.*, u.name as user_name, u.role 
        FROM borrowing_records br 
        JOIN users u ON br.user_id = u.user_id 
        WHERE br.laptop_id = ? 
        ORDER BY br.borrow_date DESC
    ''', (laptop_id,)).fetchall()
    
    # Get current borrower if any
    current_borrower = conn.execute('''
        SELECT u.name, u.role, br.borrow_date, br.expected_return_date
        FROM borrowing_records br 
        JOIN users u ON br.user_id = u.user_id 
        WHERE br.laptop_id = ? AND br.status = 'active'
    ''', (laptop_id,)).fetchone()
    
    conn.close()
    
    return render_template('laptop_history.html', laptop=laptop, history=history, current_borrower=current_borrower)

@app.route('/admin/laptop/add', methods=['GET', 'POST'])
@login_required
def add_laptop():
    if session.get('role') != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        brand = request.form['brand']
        model = request.form['model']
        status = request.form['status']
        
        conn = get_db()
        conn.execute('INSERT INTO laptops (brand, model, status) VALUES (?, ?, ?)', (brand, model, status))
        conn.commit()
        conn.close()
        
        flash('Laptop added successfully!', 'success')
        return redirect(url_for('admin_laptops'))
    
    return render_template('laptop_form.html', laptop=None, action='Add')

@app.route('/admin/laptop/<int:laptop_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_laptop(laptop_id):
    if session.get('role') != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    conn = get_db()
    
    if request.method == 'POST':
        brand = request.form['brand']
        model = request.form['model']
        status = request.form['status']
        
        conn.execute('UPDATE laptops SET brand = ?, model = ?, status = ? WHERE laptop_id = ?',
                    (brand, model, status, laptop_id))
        conn.commit()
        conn.close()
        
        flash('Laptop updated successfully!', 'success')
        return redirect(url_for('laptop_history', laptop_id=laptop_id))
    
    laptop = conn.execute('SELECT * FROM laptops WHERE laptop_id = ?', (laptop_id,)).fetchone()
    conn.close()
    
    if not laptop:
        flash('Laptop not found', 'error')
        return redirect(url_for('admin_laptops'))
    
    return render_template('laptop_form.html', laptop=laptop, action='Edit')

@app.route('/admin/laptop/<int:laptop_id>/delete', methods=['POST'])
@login_required
def delete_laptop(laptop_id):
    if session.get('role') != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    conn = get_db()
    
    # Check if laptop has active borrowings
    active = conn.execute('SELECT COUNT(*) FROM borrowing_records WHERE laptop_id = ? AND status = ?',
                         (laptop_id, 'active')).fetchone()[0]
    
    if active > 0:
        conn.close()
        flash('Cannot delete laptop with active borrowings', 'error')
        return redirect(url_for('laptop_history', laptop_id=laptop_id))
    
    conn.execute('DELETE FROM laptops WHERE laptop_id = ?', (laptop_id,))
    conn.commit()
    conn.close()
    
    flash('Laptop deleted successfully!', 'success')
    return redirect(url_for('admin_laptops'))

@app.route('/admin/records')
@login_required
def admin_records():
    if session.get('role') != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    conn = get_db()
    records = conn.execute('''
        SELECT br.*, u.name as user_name, u.role, l.brand, l.model 
        FROM borrowing_records br 
        JOIN users u ON br.user_id = u.user_id 
        JOIN laptops l ON br.laptop_id = l.laptop_id 
        ORDER BY br.borrow_date DESC
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin_records.html', records=records)

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True, port=5000)
