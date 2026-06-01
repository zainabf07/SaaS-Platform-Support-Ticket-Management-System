# TicketDesk — SaaS Support Ticket Management System

A full-stack web application for managing customer support tickets, built with Python (Flask) and Microsoft SQL Server.

---

## Features

- Role-based login — Admin, Agent, and Customer roles
- Dashboard — Live stats (total, new, in-progress, resolved tickets)
- Ticket Management — Create, view, and update support tickets
- Responses — Reply to tickets with internal/external notes
- Ticket History — Full audit trail of status changes
- User Management — View all users and their roles
- SLA Tracking — Response and resolution time limits per priority
- Status Updates — Agents and Admins can update ticket status

---

## Tech Stack

| Layer      | Technology              |
|------------|-------------------------|
| Frontend   | HTML, CSS, JavaScript   |
| Backend    | Python 3.x, Flask       |
| Database   | Microsoft SQL Server    |
| Driver     | pyodbc                  |

---

## Project Structure

```
tms-project/
│
├── app.py                  # Main Flask application & routes
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── LICENSE                 # MIT License
│
└── templates/              # HTML frontend templates
    ├── base.html           # Shared layout & sidebar
    ├── login.html          # Login page
    ├── dashboard.html      # Main dashboard
    ├── tickets.html        # All tickets list
    ├── ticket_detail.html  # Single ticket view
    ├── new_ticket.html     # Create ticket form
    └── users.html          # Users list
```

---

## Setup & Installation

### Prerequisites
- Python 3.8 or higher
- Microsoft SQL Server (Express or higher)
- SQL Server Management Studio (SSMS)
- ODBC Driver 17 for SQL Server

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/support-ticket-system.git
cd support-ticket-system
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up the Database
- Open SSMS and connect to your SQL Server instance
- Run the SQL script to create the `tms` database, tables, and sample data

### 4. Configure Database Connection
In `app.py`, update the connection string if needed:
```python
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=YOUR_SERVER_NAME\\SQLEXPRESS;'
    'DATABASE=tms;'
    'Trusted_Connection=yes;'
)
```

### 5. Run the Application
```bash
python app.py
```

Visit http://127.0.0.1:5000 in your browser.

---

## Demo Accounts

| Role     | Email                 |
|----------|-----------------------|
| Admin    | admin@example.com     |
| Agent    | usman@example.com     |
| Agent    | hina@example.com      |
| Customer | ali@example.com       |
| Customer | sara@example.com      |

No password required — login is email-based for demo purposes.

---

## Database Schema

| Table                | Description                            |
|----------------------|----------------------------------------|
| Roles                | User roles (Admin, Agent, Customer)    |
| Users                | Registered users                       |
| Tickets              | Support tickets                        |
| Ticket_Status        | Status types (New, Assigned, etc.)     |
| Ticket_Priority      | Priority levels (Low, Medium, High)    |
| Categories           | Ticket categories                      |
| SLA                  | SLA time limits per priority           |
| Ticket_Assignments   | Agent-to-ticket assignments            |
| Responses            | Ticket replies and internal notes      |
| Ticket_History       | Audit log of status changes            |

---

## Future Improvements

- Password authentication
- Email notifications on ticket updates
- File attachments on tickets
- Search and filter on ticket list
- Agent assignment from the UI
- Charts and analytics on dashboard

---

## Author

**Your Name**
- GitHub: https://github.com/zainabf07
- Email: zainabfaatima007@email.com

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

Built as a DBMS course project.
