import sqlite3

class GodController:
 
    def handle_user_request(self, username, password, email):
        # 1. Data Access concerns mixed in
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, email TEXT)")
        
        # 2. Business logic mixed in
        if len(password) < 8:
            return "<html><body><h1>Error: Password too short</h1></body></html>"
            
        cursor.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", (username, password, email))
        conn.commit()
        conn.close()
        
        # 3. Direct HTML UI rendering mixed in (Presentation Layer)
        return f"<html><body><h1>User {username} successfully registered!</h1></body></html>"
