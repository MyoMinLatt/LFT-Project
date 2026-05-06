import sqlite3

conn = sqlite3.connect("users.db")
c = conn.cursor()

c.execute("UPDATE users SET role='admin' WHERE email='minlatt.myo@gmail.com'")

conn.commit()
conn.close()

print("Role updated to admin")