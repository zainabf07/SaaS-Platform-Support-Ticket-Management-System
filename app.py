from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import pyodbc

app = Flask(__name__)
app.secret_key = 'tms_secret_key'

# Database connection
def get_db():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=WIN-NTFTJ52D2DM\\SQLEXPRESS;'
        'DATABASE=tms;'
        'Trusted_Connection=yes;'
    )
    return conn

# ── AUTH ──────────────────────────────────────────────────────────────────────

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.user_id, u.name, u.email, r.role_name
            FROM Users u
            JOIN Roles r ON u.role_id = r.role_id
            WHERE u.email = ? AND u.is_active = 1
        """, email)
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user_id'] = user.user_id
            session['name'] = user.name
            session['email'] = user.email
            session['role'] = user.role_name
            return redirect(url_for('dashboard'))
        else:
            flash('Email not found or account inactive.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ── DASHBOARD ─────────────────────────────────────────────────────────────────

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cursor = conn.cursor()

    # Stats
    cursor.execute("SELECT COUNT(*) FROM Tickets")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Tickets WHERE status_id = 1")
    new_tickets = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Tickets WHERE status_id IN (2,3)")
    in_progress = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Tickets WHERE status_id = 4")
    resolved = cursor.fetchone()[0]

    # Recent tickets
    cursor.execute("""
        SELECT TOP 5 t.ticket_id, t.subject, u.name as customer,
               ts.status_name, tp.level as priority, t.created_at,
               cat.category_name
        FROM Tickets t
        JOIN Users u ON t.user_id = u.user_id
        JOIN Ticket_Status ts ON t.status_id = ts.status_id
        JOIN Ticket_Priority tp ON t.priority_id = tp.priority_id
        JOIN Categories cat ON t.category_id = cat.category_id
        ORDER BY t.created_at DESC
    """)
    recent = cursor.fetchall()
    conn.close()

    return render_template('dashboard.html',
        total=total, new_tickets=new_tickets,
        in_progress=in_progress, resolved=resolved,
        recent=recent)

# ── TICKETS ───────────────────────────────────────────────────────────────────

@app.route('/tickets')
def tickets():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.ticket_id, t.subject, u.name as customer,
               ts.status_name, tp.level as priority,
               cat.category_name, t.created_at
        FROM Tickets t
        JOIN Users u ON t.user_id = u.user_id
        JOIN Ticket_Status ts ON t.status_id = ts.status_id
        JOIN Ticket_Priority tp ON t.priority_id = tp.priority_id
        JOIN Categories cat ON t.category_id = cat.category_id
        ORDER BY t.created_at DESC
    """)
    all_tickets = cursor.fetchall()
    conn.close()
    return render_template('tickets.html', tickets=all_tickets)

@app.route('/tickets/<int:ticket_id>')
def ticket_detail(ticket_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT t.ticket_id, t.subject, t.description, u.name as customer,
               ts.status_name, tp.level as priority, cat.category_name,
               t.created_at, sla.response_time_limit, sla.resolution_time_limit,
               t.status_id
        FROM Tickets t
        JOIN Users u ON t.user_id = u.user_id
        JOIN Ticket_Status ts ON t.status_id = ts.status_id
        JOIN Ticket_Priority tp ON t.priority_id = tp.priority_id
        JOIN Categories cat ON t.category_id = cat.category_id
        JOIN SLA sla ON t.sla_id = sla.sla_id
        WHERE t.ticket_id = ?
    """, ticket_id)
    ticket = cursor.fetchone()

    cursor.execute("""
        SELECT r.message, u.name, r.created_at, r.is_internal
        FROM Responses r
        JOIN Users u ON r.user_id = u.user_id
        WHERE r.ticket_id = ?
        ORDER BY r.created_at
    """, ticket_id)
    responses = cursor.fetchall()

    cursor.execute("""
        SELECT u.name as agent, ta.assigned_at, ta.is_active
        FROM Ticket_Assignments ta
        JOIN Users u ON ta.agent_id = u.user_id
        WHERE ta.ticket_id = ?
    """, ticket_id)
    assignments = cursor.fetchall()

    cursor.execute("""
        SELECT ts.status_name, u.name as changed_by, th.changed_at
        FROM Ticket_History th
        JOIN Ticket_Status ts ON th.status_id = ts.status_id
        JOIN Users u ON th.changed_by = u.user_id
        WHERE th.ticket_id = ?
        ORDER BY th.changed_at
    """, ticket_id)
    history = cursor.fetchall()

    cursor.execute("SELECT status_id, status_name FROM Ticket_Status")
    statuses = cursor.fetchall()

    conn.close()
    return render_template('ticket_detail.html',
        ticket=ticket, responses=responses,
        assignments=assignments, history=history, statuses=statuses)

@app.route('/tickets/<int:ticket_id>/respond', methods=['POST'])
def respond(ticket_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    message = request.form['message']
    is_internal = 1 if request.form.get('is_internal') else 0
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT ISNULL(MAX(response_id),0)+1 FROM Responses")
    next_id = cursor.fetchone()[0]
    cursor.execute("""
        INSERT INTO Responses (response_id, ticket_id, user_id, message, is_internal)
        VALUES (?, ?, ?, ?, ?)
    """, next_id, ticket_id, session['user_id'], message, is_internal)
    conn.commit()
    conn.close()
    return redirect(url_for('ticket_detail', ticket_id=ticket_id))

@app.route('/tickets/<int:ticket_id>/status', methods=['POST'])
def update_status(ticket_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    new_status = request.form['status_id']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE Tickets SET status_id = ? WHERE ticket_id = ?", new_status, ticket_id)
    cursor.execute("SELECT ISNULL(MAX(history_id),0)+1 FROM Ticket_History")
    next_id = cursor.fetchone()[0]
    cursor.execute("""
        INSERT INTO Ticket_History (history_id, ticket_id, status_id, changed_by)
        VALUES (?, ?, ?, ?)
    """, next_id, ticket_id, new_status, session['user_id'])
    conn.commit()
    conn.close()
    return redirect(url_for('ticket_detail', ticket_id=ticket_id))

@app.route('/tickets/new', methods=['GET', 'POST'])
def new_ticket():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cursor = conn.cursor()
    if request.method == 'POST':
        subject = request.form['subject']
        description = request.form['description']
        category_id = request.form['category_id']
        priority_id = request.form['priority_id']
        cursor.execute("SELECT sla_id FROM SLA WHERE priority_id = ?", priority_id)
        sla = cursor.fetchone()
        sla_id = sla.sla_id if sla else 1
        cursor.execute("SELECT ISNULL(MAX(ticket_id),0)+1 FROM Tickets")
        next_id = cursor.fetchone()[0]
        cursor.execute("""
            INSERT INTO Tickets (ticket_id, subject, description, user_id, category_id, priority_id, status_id, sla_id)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?)
        """, next_id, subject, description, session['user_id'], category_id, priority_id, sla_id)
        cursor.execute("SELECT ISNULL(MAX(history_id),0)+1 FROM Ticket_History")
        hist_id = cursor.fetchone()[0]
        cursor.execute("""
            INSERT INTO Ticket_History (history_id, ticket_id, status_id, changed_by)
            VALUES (?, ?, 1, ?)
        """, hist_id, next_id, session['user_id'])
        conn.commit()
        conn.close()
        flash('Ticket created successfully!')
        return redirect(url_for('tickets'))

    cursor.execute("SELECT category_id, category_name FROM Categories")
    categories = cursor.fetchall()
    cursor.execute("SELECT priority_id, level FROM Ticket_Priority")
    priorities = cursor.fetchall()
    conn.close()
    return render_template('new_ticket.html', categories=categories, priorities=priorities)

# ── USERS ─────────────────────────────────────────────────────────────────────

@app.route('/users')
def users():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.user_id, u.name, u.email, r.role_name, u.is_active
        FROM Users u
        JOIN Roles r ON u.role_id = r.role_id
        ORDER BY u.user_id
    """)
    all_users = cursor.fetchall()
    conn.close()
    return render_template('users.html', users=all_users)

if __name__ == '__main__':
    app.run(debug=True)
