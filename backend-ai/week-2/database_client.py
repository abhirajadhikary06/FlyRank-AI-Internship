import os
import random

import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True


def create_table():
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                age INT,
                department VARCHAR(100),
                academic_year INT,
                sgpa NUMERIC(3,2)
            );
        """)


def insert_data(name, age, department, academic_year, sgpa):
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO data (
                name,
                age,
                department,
                academic_year,
                sgpa
            )
            VALUES (%s, %s, %s, %s, %s);
        """, (name, age, department, academic_year, sgpa))


def populate_random_data(n=100):
    names = [
        "Alice",
        "Bob",
        "Charlie",
        "Diana",
        "Eve",
        "Frank"
    ]

    departments = [
        "CSE",
        "ECE",
        "ME",
        "CE",
        "IT"
    ]

    for _ in range(n):
        insert_data(
            name=random.choice(names),
            age=random.randint(18, 30),
            department=random.choice(departments),
            academic_year=random.randint(1, 4),
            sgpa=round(random.uniform(5.0, 10.0), 2)
        )

def get_all_data():
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM data;")
        return cursor.fetchall()

def get_data_by_id(data_id):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM data WHERE id = %s;", (data_id,))
        return cursor.fetchone()

def update_data(data_id, name=None, age=None, department=None, academic_year=None, sgpa=None):
    with conn.cursor() as cursor:
        update_fields = []
        update_values = []

        if name is not None:
            update_fields.append("name = %s")
            update_values.append(name)
        if age is not None:
            update_fields.append("age = %s")
            update_values.append(age)
        if department is not None:
            update_fields.append("department = %s")
            update_values.append(department)
        if academic_year is not None:
            update_fields.append("academic_year = %s")
            update_values.append(academic_year)
        if sgpa is not None:
            update_fields.append("sgpa = %s")
            update_values.append(sgpa)

        if not update_fields:
            return  

        update_query = f"UPDATE data SET {', '.join(update_fields)} WHERE id = %s;"
        update_values.append(data_id)

        cursor.execute(update_query, tuple(update_values))

def delete_data(data_id):
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM data WHERE id = %s;", (data_id,))

def delete_all_data():
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM data;")

if __name__ == "__main__":
    create_table()
    populate_random_data(10)
    print(get_all_data())
    print(get_data_by_id(1))
    print("Database initialized successfully.")