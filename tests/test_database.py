# test_database.py
from src.database import get_db_manager
from src.database.models import Base

# Health check
db = get_db_manager()
print("✅ Database connected:" if db.health_check() else "❌ Database error")

# Create tables
db.create_tables(Base)
print("✅ Tables created")

# Test session
with db.session_context() as session:
    result = session.execute("SELECT 1")
    print("✅ Database query successful")
