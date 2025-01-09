from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import mysql.connector

# MySQL database configuration
DB_CONFIG = {
    "host": "localhost",       # Replace with your MySQL host
    "user": "Board",   # Replace with your MySQL username
    "password": "@boardKoni1234",  # Replace with your MySQL password
    "database": "koni",  # Replace with your database name
}

# Connect to the MySQL database
try:
    db_connection = mysql.connector.connect(**DB_CONFIG)
    db_cursor = db_connection.cursor(dictionary=True)
    print("Connected to MySQL database!")

    # Create the 'customers' table in the database if it doesn't exist
    create_table_query = """
    CREATE TABLE IF NOT EXISTS customers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        address VARCHAR(255),
        email VARCHAR(255) UNIQUE,
        password VARCHAR(255),
        gender VARCHAR(50),
        date_of_birth DATE
    )
    """
    db_cursor.execute(create_table_query)
    db_connection.commit()
    print("Table 'customers' created successfully!")
except mysql.connector.Error as err:
    print(f"Error: {err}")
    raise err

app = FastAPI()

# CORS setup to allow communication from other sources if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust based on your requirements
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    """Root endpoint to display a welcome message."""
    return {"message": "Welcome to the homepage!"}

@app.post("/signup")
async def signup(
    full_name: str = Form(...),
    date_of_birth: str = Form(...),
    gender: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    """Endpoint to handle user signup."""
    try:
        # Check if the user already exists
        query = "SELECT email FROM customers WHERE email = %s"
        db_cursor.execute(query, (email,))
        existing_user = db_cursor.fetchone()
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists.")
        
        # Insert the new user into the database
        query = """
            INSERT INTO customers (name, date_of_birth, gender, email, password)
            VALUES (%s, %s, %s, %s, %s)
        """
        db_cursor.execute(query, (full_name, date_of_birth, gender, email, password))
        db_connection.commit()

        return {"message": "User signed up successfully!"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

@app.get("/users/{email}")
async def get_user(email: str):
    """Endpoint to retrieve user details by email."""
    try:
        query = "SELECT name, date_of_birth, gender, email FROM customers WHERE email = %s"
        db_cursor.execute(query, (email,))
        user = db_cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        return {"user": user}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
