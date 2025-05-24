from flask import Flask, request, render_template_string, redirect, flash, url_for
import psycopg2
from psycopg2 import sql
from werkzeug.security import generate_password_hash
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Environment variable set in Render Dashboard
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# Inline HTML Template
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>User Registration</title>
    <style>
        body {
            font-family: Arial;
            background-color: #f2f2f2;
            padding: 30px;
        }
        .container {
            background-color: white;
            padding: 25px;
            max-width: 400px;
            margin: auto;
            border-radius: 12px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
        }
        h2 {
            text-align: center;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 10px;
            margin: 12px 0;
            border-radius: 5px;
            border: 1px solid #ccc;
        }
        button {
            width: 100%;
            padding: 10px;
            background-color: #4CAF50;
            border: none;
            color: white;
            font-size: 16px;
            border-radius: 5px;
        }
        .msg {
            margin-top: 15px;
            padding: 10px;
            background-color: #e7f4e4;
            border-left: 4px solid #4CAF50;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>User Registration</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Register</button>
        </form>
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                <div class="msg">{{ messages[0] }}</div>
            {% endif %}
        {% endwith %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                sql.SQL("INSERT INTO users (username, password) VALUES (%s, %s)"),
                [username, hashed_pw]
            )
            conn.commit()
            msg = "User registered successfully!"
        except Exception as e:
            msg = f"Registration failed. Maybe username already exists? {e}"
        finally:
            cur.close()
            conn.close()
        flash(msg)
        return redirect(url_for('register'))
    return render_template_string(html_template)
    
if __name__ == '__main__':
    app.run(debug=True)
