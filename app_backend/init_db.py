import mysql.connector
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

sql_file = Path(__file__).parent / "init_db.sql"

with open(sql_file, "r", encoding="utf-8") as file:
    sql_script = file.read()

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

cursor = conn.cursor()

for statement in sql_script.split(";"):
    if statement.strip():
        cursor.execute(statement)

conn.commit()

cursor.close()
conn.close()

print("Base de datos inicializada correctamente.")