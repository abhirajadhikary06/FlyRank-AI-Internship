import os
import random
import redis
from dotenv import load_dotenv
load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def get_data(key):
    conn = redis_client
    value = conn.get(key)
    if value is not None:
        return value
    else:
        return None
    
def get_all_data():
    conn = redis_client
    keys = conn.keys('*')
    data = {}
    for key in keys:
        data[key] = conn.get(key)
    return data

def set_data(key, value):
    conn = redis_client
    conn.set(key, value)
    return f"Data set for key: {key} with value: {value}"

def delete_data(key):
    conn = redis_client
    result = conn.delete(key)
    if result == 1:
        return f"Data deleted for key: {key}"
    else:
        return f"No data found for key: {key}"
    
def update_data(key, value):
    conn = redis_client
    if conn.exists(key):
        conn.set(key, value)
        return f"Data updated for key: {key} with new value: {value}"
    else:
        return f"No data found for key: {key}"

def insert_random_data():
    names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"]
    departments = ["CSE", "ECE", "ME", "CE", "EEE"]

    for i in range(5):
        key = f"student:{i+1}"
        value = {
            "name": random.choice(names),
            "age": random.randint(18, 25),
            "department": random.choice(departments),
            "academic_year": random.randint(1, 4),
            "sgpa": round(random.uniform(6.0, 10.0), 2)
        }
        redis_client.set(key, str(value))

if __name__ == "__main__":
    insert_random_data()
    print(get_all_data())
    print("Redis Client run successfully.")
