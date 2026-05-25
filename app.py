from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import date

app = Flask(__name__)
app.secret_key = 'vet_clinic_secret_key_2024'
DB_PATH = 'vet_clinic.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS clients (
            client_id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL, last_name TEXT NOT NULL,
            phone TEXT NOT NULL, email TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL, password TEXT NOT NULL,
            full_name TEXT NOT NULL, phone TEXT NOT NULL, email TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS services (
            service_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, description TEXT NOT NULL, price INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS veterinars (
            veterinar_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL, last_name TEXT NOT NULL,
            specialozation TEXT NOT NULL, phone TEXT NOT NULL, email TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL REFERENCES clients(client_id),
            veterinar_id INTEGER NOT NULL REFERENCES veterinars(veterinar_id),
            service_id INTEGER NOT NULL REFERENCES services(service_id),
            order_date DATE NOT NULL, start_time INTEGER NOT NULL,
            end_time INTEGER NOT NULL, comment TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS revies (
            review_id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL REFERENCES clients(client_id),
            veterinar_id INTEGER NOT NULL REFERENCES veterinars(veterinar_id),
            order_id INTEGER NOT NULL UNIQUE REFERENCES orders(order_id),
            raiting INTEGER NOT NULL, comment TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()

def seed_db():
    conn = get_db()
    if conn.execute('SELECT COUNT(*) FROM services').fetchone()[0] == 0:
        conn.executescript('''
            INSERT INTO services VALUES (1,'Чистка ушей','Чистка ушей кошкам, собакам',1000);
            INSERT INTO services VALUES (2,'Стрижка когтей','Стрижка когтей собакам, кошкам',2000);
            INSERT INTO services VALUES (3,'Прививка','Прививка собакам, кошкам',3000);
            INSERT INTO services VALUES (4,'Удаление занозы','Удаление занозы из лапы',4000);
        ''')
    if conn.execute('SELECT COUNT(*) FROM veterinars').fetchone()[0] == 0:
        conn.executescript('''
            INSERT INTO veterinars VALUES (1,'Рыбаков','Андрей','Хирург','8963453645','rybakov@ya.ru');
            INSERT INTO veterinars VALUES (2,'Собакин','Сергей','Терапевт','8963453645','sobakin@mail.ru');
            INSERT INTO veterinars VALUES (3,'Овчаренко','Андрей','Хирург','896345443','ovv@ya.ru');
            INSERT INTO veterinars VALUES (4,'Мышкин','Сергей','Терапевт','8963453612','MNB@mail.ru');
        ''')
    if not conn.execute("SELECT id FROM roles WHERE name='admin'").fetchone():
        pwd = generate_password_hash('admin123')
        conn.execute("INSERT INTO roles (name, password, full_name, phone, email) VALUES ('admin', ?, 'Главный Админ', '000', 'admin@vet.ru')", (pwd,))
        admin_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.execute("INSERT OR IGNORE INTO clients (client_id, first_name, last_name, phone, email) VALUES (?, 'Администратор', 'Системы', '000', 'admin@vet.ru')", (admin_id,))
    conn.commit()
    conn.close()

def ensure_client_exists(user_id):
    """Гарантирует, что для user_id есть запись в clients (без использования .get())"""
    conn = get_db()
    if not conn.execute('SELECT 1 FROM clients WHERE client_id = ?', (user_id,)).fetchone():
        user = conn.execute('SELECT * FROM roles WHERE id = ?', (user_id,)).fetchone()
        if user:
            names = (user['full_name'] or 'Пользователь').split()
            first = names[0]
            last = names[1] if len(names) > 1 else ''
            # ✅ ИСПРАВЛЕНИЕ: sqlite3.Row не имеет .get(), используем [] или ''
            phone = user['phone'] or ''
            email = user['email'] or ''
            conn.execute('INSERT INTO clients (client_id, first_name, last_name, phone, email) VALUES (?, ?, ?, ?, ?)',
                         (user_id, first, last, phone, email))
            conn.commit()
    conn.close()

@app.before_request
def check_auth():
    if request.endpoint not in ('login', 'register', 'static') and 'user_id' not in session:
        flash('Для доступа необходимо авторизоваться', 'warning')
        return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login = request.form.get('login', '').strip()
        password = request.form.get('password', '').strip()
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()

        if not all([login, password, full_name, phone, email]):
            flash('Заполните все обязательные поля!', 'error')
            return render_template('register.html')
        if len(login) < 6 or not login.replace('_', '').isalnum():
            flash('Логин: латиница/цифры/_, ≥ 6 символов', 'error')
            return render_template('register.html')
        if len(password) < 8:
            flash('Пароль должен содержать ≥ 8 символов', 'error')
            return render_template('register.html')

        conn = get_db()
        if conn.execute('SELECT id FROM roles WHERE name = ?', (login,)).fetchone():
            flash('Пользователь с таким логином уже существует', 'error')
            conn.close()
            return render_template('register.html')

        pwd_hash = generate_password_hash(password)
        try:
            c = conn.cursor()
            c.execute('INSERT INTO roles (name, password, full_name, phone, email) VALUES (?, ?, ?, ?, ?)',
                      (login, pwd_hash, full_name, phone, email))
            role_id = c.lastrowid
            first = full_name.split()[0] if ' ' in full_name else full_name
            last = full_name.split()[1] if ' ' in full_name else ''
            c.execute('INSERT INTO clients (client_id, first_name, last_name, phone, email) VALUES (?, ?, ?, ?, ?)',
                      (role_id, first, last, phone, email))
            conn.commit()
            flash('Регистрация успешна! Войдите в систему.', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Ошибка регистрации: {e}', 'error')
        finally:
            conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('login', '').strip()
        password = request.form.get('password', '').strip()
        if not login or not password:
            flash('Введите логин и пароль', 'error')
            return render_template('login.html')

        conn = get_db()
        user = conn.execute('SELECT * FROM roles WHERE name = ?', (login,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['role'] = user['name']
            ensure_client_exists(user['id']) 
            flash(f'Добро пожаловать, {user["full_name"]}!', 'success')
            
            role_lower = user['name'].lower()
            if role_lower in ['admin', 'директор']:
                return redirect(url_for('admin_panel'))
            return redirect(url_for('dashboard'))
        flash('Неверный логин или пароль', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    conn = get_db()
    orders = conn.execute('''
        SELECT o.order_id, o.order_date, o.start_time, o.comment,
               s.name as service_name,
               v.first_name || ' ' || v.last_name as vet_name,
               r.review_id
        FROM orders o
        JOIN services s ON o.service_id = s.service_id
        JOIN veterinars v ON o.veterinar_id = v.veterinar_id
        LEFT JOIN revies r ON r.order_id = o.order_id
        WHERE o.client_id = ?
        ORDER BY o.order_date DESC, o.start_time ASC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('dashboard.html', orders=orders)

@app.route('/new-order', methods=['GET', 'POST'])
def new_order():
    if request.method == 'POST':
        try:
            service_id = int(request.form.get('service_id', 0))
            veterinar_id = int(request.form.get('veterinar_id', 0))
        except ValueError:
            service_id = veterinar_id = 0

        order_date = request.form.get('order_date')
        start_time = request.form.get('start_time')
        comment = request.form.get('comment', '').strip()

        if not all([service_id, veterinar_id, order_date, start_time]):
            flash('Выберите услугу и врача из списка, укажите дату и время', 'error')
            conn = get_db()
            services = conn.execute('SELECT * FROM services').fetchall()
            vets = conn.execute('SELECT * FROM veterinars').fetchall()
            conn.close()
            return render_template('new_order.html', services=services, veterinars=vets)

        try:
            start_int = int(start_time)
            if not (9 <= start_int <= 18): raise ValueError
            end_time = start_int + 1
        except ValueError:
            flash('Время приёма должно быть числом от 9 до 18', 'error')
            conn = get_db()
            services = conn.execute('SELECT * FROM services').fetchall()
            vets = conn.execute('SELECT * FROM veterinars').fetchall()
            conn.close()
            return render_template('new_order.html', services=services, veterinars=vets)

        ensure_client_exists(session['user_id'])

        conn = get_db()
        try:
            conn.execute('''INSERT INTO orders (client_id, veterinar_id, service_id, order_date, start_time, end_time, comment)
                            VALUES (?, ?, ?, ?, ?, ?, ?)''',
                         (session['user_id'], veterinar_id, service_id, order_date, start_int, end_time, comment))
            conn.commit()
            flash('Заявка успешно создана!', 'success')
        except sqlite3.IntegrityError as e:
            conn.rollback()
            flash(f'Ошибка БД: проверьте, что выбраны существующие врач и услуга.', 'error')
        except Exception as e:
            conn.rollback()
            flash(f'Неожиданная ошибка: {e}', 'error')
        finally:
            conn.close()
        return redirect(url_for('dashboard'))

    conn = get_db()
    services = conn.execute('SELECT service_id, name, price FROM services').fetchall()
    veterinars = conn.execute('SELECT veterinar_id, first_name, last_name, specialozation FROM veterinars').fetchall()
    conn.close()
    return render_template('new_order.html', services=services, veterinars=veterinars)

@app.route('/add-review/<int:order_id>', methods=['GET', 'POST'])
def add_review(order_id):
    client_id = session['user_id']
    conn = get_db()
    if conn.execute('SELECT review_id FROM revies WHERE order_id = ?', (order_id,)).fetchone():
        flash('Отзыв уже оставлен для этой заявки', 'warning')
        conn.close()
        return redirect(url_for('dashboard'))

    order = conn.execute('''
        SELECT o.order_id, o.order_date, o.veterinar_id,
               s.name as service_name,
               v.first_name || ' ' || v.last_name as vet_name
        FROM orders o
        JOIN services s ON o.service_id = s.service_id
        JOIN veterinars v ON o.veterinar_id = v.veterinar_id
        WHERE o.order_id = ? AND o.client_id = ?
    ''', (order_id, client_id)).fetchone()

    if not order:
        flash('Заявка не найдена', 'error')
        conn.close()
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        rating = request.form.get('rating')
        comment = request.form.get('comment', '').strip()
        if not rating or not (1 <= int(rating) <= 10):
            flash('Оценка должна быть числом от 1 до 10', 'error')
            return render_template('add_review.html', order=order)
        
        try:
            conn.execute('INSERT INTO revies (client_id, veterinar_id, order_id, raiting, comment) VALUES (?, ?, ?, ?, ?)',
                         (client_id, order['veterinar_id'], order_id, int(rating), comment))
            conn.commit()
            flash('Отзыв сохранён!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Ошибка: {e}', 'error')
        finally:
            conn.close()
        return redirect(url_for('dashboard'))

    conn.close()
    return render_template('add_review.html', order=order)

@app.route('/admin')
def admin_panel():
    if session.get('role', '').lower() not in ['admin', 'директор']:
        flash('Доступ запрещён. Требуются права администратора.', 'error')
        return redirect(url_for('dashboard'))
        
    conn = get_db()
    today = date.today().isoformat()
    orders = conn.execute('''
        SELECT o.order_id, o.order_date, o.start_time, o.comment,
               c.first_name || ' ' || c.last_name as client_name,
               s.name as service_name,
               v.first_name || ' ' || v.last_name as vet_name
        FROM orders o
        JOIN clients c ON o.client_id = c.client_id
        JOIN services s ON o.service_id = s.service_id
        JOIN veterinars v ON o.veterinar_id = v.veterinar_id
        WHERE o.order_date >= ?
        ORDER BY o.order_date ASC, o.start_time ASC
    ''', (today,)).fetchall()
    conn.close()
    return render_template('admin.html', orders=orders)

@app.route('/api/orders', methods=['GET', 'POST'])
def api_orders():
    if 'user_id' not in session:
        return jsonify({'error': 'Не авторизован'}), 401

    if request.method == 'POST':
        data = request.get_json()
        service_id = data.get('service_id')
        veterinar_id = data.get('veterinar_id')
        order_date = data.get('order_date')
        start_time = data.get('start_time')
        comment = data.get('comment', '')

        if not all([service_id, veterinar_id, order_date, start_time]):
            return jsonify({'error': 'Заполните все поля'}), 400

        try:
            start_int = int(start_time)
            if not (9 <= start_int <= 18): raise ValueError
            end_time = start_int + 1
        except ValueError:
            return jsonify({'error': 'Время должно быть от 9 до 18'}), 400

        ensure_client_exists(session['user_id'])
        conn = get_db()
        try:
            conn.execute('''INSERT INTO orders (client_id, veterinar_id, service_id, order_date, start_time, end_time, comment)
                            VALUES (?, ?, ?, ?, ?, ?, ?)''',
                         (session['user_id'], veterinar_id, service_id, order_date, start_int, end_time, comment))
            conn.commit()
            return jsonify({'message': 'Заявка создана', 'id': conn.execute('SELECT last_insert_rowid()').fetchone()[0]}), 201
        except Exception as e:
            conn.rollback()
            return jsonify({'error': str(e)}), 500
        finally:
            conn.close()

    # GET: фильтрация
    date_from = request.args.get('date_from')
    service = request.args.get('service')
    
    query = '''SELECT o.order_id, o.order_date, o.start_time, s.name as service_name,
                      v.first_name || ' ' || v.last_name as vet_name, o.comment
               FROM orders o
               JOIN services s ON o.service_id = s.service_id
               JOIN veterinars v ON o.veterinar_id = v.veterinar_id
               WHERE o.client_id = ?'''
    params = [session['user_id']]

    if date_from:
        query += ' AND o.order_date >= ?'
        params.append(date_from)
    if service:
        query += ' AND s.name LIKE ?'
        params.append(f'%{service}%')

    query += ' ORDER BY o.order_date DESC'
    conn = get_db()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        init_db()
    seed_db()
    app.run(debug=True, host='127.0.0.1', port=5001)
