import sqlite3
import argparse
import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP('sqlite-demo')

def init_db():
    """Initialize the database with proper error handling."""
    try:
        # Use absolute path for database file
        db_dir = os.path.join(os.getcwd(), 'data')
        os.makedirs(db_dir, exist_ok=True)
        db_path = os.path.join(db_dir, 'demo.db')
        
        print(f"Attempting to connect to database at: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create the table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS people (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                profession TEXT NOT NULL
            )
        ''')
        conn.commit()
        print(f"Database initialization Successfully completed")
        return conn, cursor
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error during database initialization: {e}")
        raise

@mcp.tool()
def add_data(query: str) -> bool:
    """Add new data to the people table using a SQL INSERT query.

    Args:
        query (str): SQL INSERT query following this format:
            INSERT INTO people (name, age, profession)
            VALUES ('John Doe', 30, 'Engineer')
        
    Schema:
        - name: Text field (required)
        - age: Integer field (required)
        - profession: Text field (required)
        Note: 'id' field is auto-generated
    
    Returns:
        bool: True if data was added successfully, False otherwise
    
    Example:
        >>> query = '''
        ... INSERT INTO people (name, age, profession)
        ... VALUES ('Alice Smith', 25, 'Developer')
        ... '''
        >>> add_data(query)
        True
    """
    try:
        print(f"Attempting to add data with query: {query}")
        conn, cursor = init_db()
        cursor.execute(query)
        conn.commit()
        print(f"Successfully added record")
        return True
    except sqlite3.Error as e:
        print(f"Error adding data: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

@mcp.tool()
def read_data(query: str = "SELECT * FROM people") -> list:
    """Read data from the people table using a SQL SELECT query.

    Args:
        query (str, optional): SQL SELECT query. Defaults to "SELECT * FROM people".
            Examples:
            - "SELECT * FROM people"
            - "SELECT name, age FROM people WHERE age > 25"
            - "SELECT * FROM people ORDER BY age DESC"
    
    Returns:
        list: List of tuples containing the query results.
              For default query, tuple format is (id, name, age, profession)
    
    Example:
        >>> # Read all records
        >>> read_data()
        [(1, 'John Doe', 30, 'Engineer'), (2, 'Alice Smith', 25, 'Developer')]
        
        >>> # Read with custom query
        >>> read_data("SELECT name, profession FROM people WHERE age < 30")
        [('Alice Smith', 'Developer')]
    """
    try:
        print(f"Attempting to read data with query: {query}")
        conn, cursor = init_db()
        cursor.execute(query)
        results = cursor.fetchall()
        print(f"Successfully retrieved {len(results)} records")
        return results
    except sqlite3.Error as e:
        print(f"Error reading data: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    # Start the server
    print("🚀Starting server... ")

    # Debug Mode
    #  uv run mcp dev server.py

    # Production Mode
    # uv run server.py --server_type=sse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--server_type", type=str, default="sse", choices=["sse", "stdio"]
    )

    args = parser.parse_args()
    mcp.run(args.server_type)



# # Example usage
# if __name__ == "__main__":
#     # Example INSERT query
#     insert_query = """
#     INSERT INTO people (name, age, profession)
#     VALUES ('John Doe', 30, 'Engineer')
#     """
    
#     # Add data
#     if add_data(insert_query):
#         print("Data added successfully")
    
#     # Read all data
#     results = read_data()
#     print("\nAll records:")
#     for record in results:
#         print(record)
