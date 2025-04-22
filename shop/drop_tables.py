import psycopg2
import os

# Database connection parameters
db_params = {
    'dbname': 'shop',
    'user': 'tosh',
    'password': 'jke202213',
    'host': 'localhost',
    'port': '5432'
}

def drop_tables():
    try:
        print("Attempting to connect to the database...")
        # Connect to the database
        conn = psycopg2.connect(**db_params)
        print("Successfully connected to the database!")
        
        cur = conn.cursor()
        
        # Get the absolute path to the drop_tables.sql file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sql_file = os.path.join(script_dir, 'drop_tables.sql')
        
        print(f"Reading SQL script from: {sql_file}")
        # Read and execute the SQL script
        with open(sql_file, 'r') as file:
            sql_script = file.read()
            print("Executing DROP commands...")
            cur.execute(sql_script)
        
        # Commit the transaction
        conn.commit()
        print("Tables dropped successfully!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    drop_tables() 