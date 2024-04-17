import mysql.connector
from mysql.connector import Error


# Connects to MySQL db 'Store_Data' executes query and returns result
# Parameters: query (str): The SQL query to execute, params based on GET n POST
# GET: start_date end_date
# POST: id, store_code, total_sales, transaction_date
# Returns: dict list containing results, http://127.0.0.1:5000/sales
def execute_query(query, params=None):
    # connecting to local db Store_Data Function
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='12345cbatest',
            port=3306,
            database='Store_Data'
        )
        print(f"Connected to MySQL Server version {connection.get_server_info()}")
        print("You're connected to database: Store_Data")

        # Creating cursor to execute the query
        cursor = connection.cursor(dictionary=True)

        # Checks if query is an INSERT operation
        # Currently used for POST
        cursor.execute(query, params)
        if query.strip().upper().startswith('INSERT'):
            connection.commit()
            return {'success': True, 'message': 'Data was successfully written in'}
        # Execute the query and fetch all results
        # Currently used for GET
        elif query.strip().upper().startswith('SELECT'):
            result = cursor.fetchall()
            return result
        else:
            return {'success': False, 'message': 'Query type not supported'}

    except Error as e:
        print(f"Error: {e}")
        return {'success': False, 'message': str(e)}
    finally:
        # Ensure the cursor and connection are closed properly
        if cursor is not None:
            cursor.close()
        if connection.is_connected():
            connection.close()
            print("MySQL connection is closed")
