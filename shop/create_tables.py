import psycopg2
from psycopg2 import sql
import os

# Database connection parameters
db_params = {
    'dbname': 'shop',
    'user': 'tosh',
    'password': 'jke202213',
    'host': 'localhost',
    'port': '5432'
}

def create_tables():
    try:
        print("Attempting to connect to the database...")
        # Connect to the database
        conn = psycopg2.connect(**db_params)
        print("Successfully connected to the database!")
        
        cur = conn.cursor()
        
        # Get the absolute path to the schema.sql file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        schema_file = os.path.join(script_dir, 'schema.sql')
        
        print(f"Reading SQL schema from: {schema_file}")
        # Read and execute the SQL script
        with open(schema_file, 'r') as file:
            sql_script = file.read()
            print("Executing SQL commands...")
            cur.execute(sql_script)
        
        # Commit the transaction
        conn.commit()
        print("Tables created successfully!")
        
    except psycopg2.OperationalError as e:
        print(f"Database connection error: {e}")
        print("Please check if:")
        print("1. PostgreSQL server is running")
        print("2. Database 'shop' exists")
        print("3. User 'tosh' has the correct permissions")
        print("4. The connection parameters are correct")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"An error occurred: {e}")
        if conn:
            conn.rollback()
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    create_tables() 