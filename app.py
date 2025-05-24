from flask import Flask, render_template, request, redirect, url_for, session

import psycopg2

app = Flask(__name__)

# PostgreSQL DB connection (replace with your actual credentials)
db = psycopg2.connect(
    host="dpg-d0oqt0muk2gs738vqnr0-a",
    dbname="flaskdb_xbfr",
    user="flaskdb_xbfr_user",
    password="UCty7HeGMSg64NLM0EDlcL7ljbkqnlW6",
    port="5432"
)
cursor = db.cursor()

# Create users table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username VARCHAR(50),
        password VARCHAR(50)
    );
""")
db.commit()

HTML_STYLE = """
<style>
    body { font-family: Arial, sans-serif; background-color: #f0f2f5; text-align: center; margin-top: 50px; }
    h2 { color: #333; }
    form { display: inline-block; padding: 20px; background: #fff; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
    input { margin: 10px 0; padding: 8px; width: 90%; border: 1px solid #ccc; border-radius: 4px; }
    input[type="submit"] { background-color: #007bff; color: white; border: none; cursor: pointer; }
    input[type="submit"]:hover { background-color: #0056b3; }
</style>
"""

@app.route('/')
def index():
    return HTML_STYLE + '''
    <h2>Register</h2>
    <form action="/register" method="post">
        <input name="username" placeholder="Username"><br>
        <input name="password" type="password" placeholder="Password"><br>
        <input type="submit" value="Register">
    </form>
    <p>Already registered? <a href="/login">Login here</a></p>
    '''

@app.route('/login')
def login_page():
    return HTML_STYLE + '''
    <h2>Login</h2>
    <form action="/login" method="post">
        <input name="username" placeholder="Username"><br>
        <input name="password" type="password" placeholder="Password"><br>
        <input type="submit" value="Login">
    </form>
    '''

@app.route('/register', methods=['POST'])
def register():
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (request.form['username'], request.form['password']))
    db.commit()
    return redirect("/login")

@app.route('/login', methods=['POST'])
def login():
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (request.form['username'], request.form['password']))
    if cursor.fetchone():
        return HTML_STYLE + "<h2>Login Successful ✅</h2>"
    return HTML_STYLE + "<h2>Login Failed ❌</h2><p><a href='/login'>Try Again</a></p>"

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
