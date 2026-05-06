# init_db.py
from auth.models import init_user_table

init_user_table()

print("✅ Database and users table created!")