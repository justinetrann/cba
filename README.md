# Development Overview of Store_Data Database

This section outlines the steps taken to develop the Store_Data database, detailing the creation of the database, table structures, and the data import process utilized in MySQL Workbench 8.0 CE.

**Creation of Database (Schema) and Tables**

The commands below were used to create the database **Store\_Data** to store the sample data found on **OneDrive**. 
MySQL Workbench 8.0 CE allows its users to import data through a file path. After manually converting the `.xlsx` file to a `.csv` format, I imported the file into the empty table **Store\_Data**. 

```sql
CREATE DATABASE Store_Data;
USE Store_Data;
CREATE TABLE Sales(
  id INT,
  store_code VARCHAR(10),
  total_sales VARCHAR(15),
  transaction_date VARCHAR(10)
);
```

The next step is to convert the strings into their acceptable forms; for example, `total_sales` should be converted to `DECIMAL(10,2)` to apply future mathematical operations.

**Conversion of Data Types**

**Converting total_sales from VARCHAR(15) to DECIMAL(10,2)**

To temporarily disable safe mode for proper data casting in MySQL Workbench 8.0 CE, you can set the SQL_SAFE_UPDATES variable to 0. This allows you to perform the necessary data manipulations without the restrictions of safe mode. Once you've finished these operations, be sure to re-enable safe mode by setting SQL_SAFE_UPDATES back to 1. This ensures the database's integrity is maintained by preventing unintended data modifications.

```sql
-- Creating a temporary column to store numeric values
ALTER TABLE Sales ADD COLUMN temp_total_sales DECIMAL(10,2);

-- Updating the temporary column with converted values
UPDATE Sales
SET temp_total_sales = CAST(REPLACE(REPLACE(total_sales, '$', ''), ',', '') AS DECIMAL(10,2));

-- Drop the old 'total_sales' column
ALTER TABLE Sales DROP COLUMN total_sales;

-- Rename the temporary column to 'total_sales'
ALTER TABLE Sales CHANGE COLUMN temp_total_sales total_sales DECIMAL(10,2);
```
**Converting transcation_date mm/dd/yy to yy-mm-dd DATE**

The following steps are conceptually similar to those described above.

```sql
-- Creating a temporary column to store dates
ALTER TABLE Sales ADD COLUMN temp_transaction_date DATE;

UPDATE Sales
SET temp_transaction_date = STR_TO_DATE(transaction_date, '%m/%d/%Y');

-- Drop the old 'transaction_date' column
ALTER TABLE Sales DROP COLUMN transaction_date;

-- Rename the temporary column to 'transaction_date'
ALTER TABLE Sales CHANGE COLUMN temp_transaction_date transaction_date DATE;
```

Now that the database has been created and all data types have been set appropriately, we can move forward to creating the Python Flask application in PyCharm. Here, we will create two endpoints: a GET endpoint and a POST endpoint for our CRUD application.

# Development Overview of Python Flask application

This section outlines the process of connecting to the 'Store_Data' database and creating both a GET endpoint and a POST endpoint for our application.

**Connecting a Database to PyCharm**

The database was connected to PyCharm through the IDE's graphical interface. 
The connection setup involved specifying `localhost` as the host on port `3306` and providing the necessary username and password. 
The JDBC URL used for the connection was `jdbc:mysql://localhost:3306/Store_Data`.

Reference: https://www.jetbrains.com/help/pycharm/mysql.html#reference

Next, our goal is to create a function that enables you to connect to a MySQL database and retrieve data using an SQL string query passed as a parameter.

**Development of function execute_query:**

The connection to the database is established in `db_connection.py` through the `execute_query(query, params=None)` function. This function not only creates a connection but also accepts an SQL string query as input. It executes the query using a cursor and returns a list of dictionaries containing the results. You can access these results by visiting http://127.0.0.1:5000/sales. The `query` parameter can also accept optional parameters (`params`), which will be discussed later in the section for GET and POST endpoints. Finally, if a connection is established, the cursor is closed to prevent memory leaks and free up resources.

References: https://pynative.com/python-mysql-database-connection/

In addition to the reference material used to establish the database connection, we incorporated an 'if' statement to differentiate between SELECT and INSERT queries. The SELECT queries, associated with the GET endpoint, utilize cursor.fetchall() to retrieve data. Conversely, the INSERT queries, linked to the POST endpoint, employ connection.commit() to finalize the data insertion.

```py
if query.strip().upper().startswith('INSERT'):
    connection.commit()
    return {'success': True, 'message': 'Data was successfully written in'}
elif query.strip().upper().startswith('SELECT'):
    result = cursor.fetchall()
    return result
else:
    return {'success': False, 'message': 'Query type not supported'}
```

**Development of the function sales:**

Within `app.py`, the `sales()` function supports both `GET` and `POST` methods. This function utilizes `execute_query` to connect to the database and execute SQL commands. For the `GET` method, it executes the query `SELECT * FROM Sales WHERE transaction_date BETWEEN %s AND %s`, while for the `POST` method, it uses `INSERT INTO Sales (id, store_code, total_sales, transaction_date) VALUES (%s, %s, %s, %s)`.

Lets further dive into the development of GET and POST.

**Development of GET endpoint**

A GET endpoint is created as an instance of the Flask class, which then serves as the WSGI application. It is accessible at http://127.0.0.1:5000/sales. Parameters can be passed through the URL or included in the HTTP GET request.

**URL Parameters**

To pass parameters through a URL, we append them to the query string, which begins with the '?' symbol. For example, in our GET endpoint, parameters are passed using the URL http://127.0.0.1:5000/sales?start_date=2023-02-12&end_date=2023-02-12. In this URL, `start_date` and `end_date` are retrieved using `request.args.get('start_date')` and `request.args.get('end_date')`, respectively. This method allows us to extract values directly from the query string.

Here’s a breakdown of the URL structure:

*   The `?` marks the beginning of the query string.
*   The `&` symbol separates multiple parameters.
*   The `=` connects each parameter key with its value.

The GET request triggers the `sales` function, which connects to a MySQL database via the `execute_query` function. This function retrieves data from the Sales table and returns it in the format requested by the user.

**HTTP Request**

In the project, there is a `.http` file that allows us to initiate a GET request directly. To do this, simply click the '+' button and enter the details of your GET request.

```http
GET http://127.0.0.1:5000/sales?start_date=2023-02-12&end_date=2023-02-12
Accept: application/json
```

The following code outputs the data retrieved from the query as a JSON dictionary, list, and Pandas DataFrame, as required.
```py
pandas_df = pd.DataFrame(data)
respond = {
    'JSON Dictionary': data,
    'list': [list(item.values()) for item in data],
    'Pandas Data Frame': pandas_df.to_json(orient='records')
}
```

**Development of POST**

Using the `.http` file, we can add a new row to the dataset in a MySQL database. Below is an example of an insertion:
```http
POST http://127.0.0.1:5000/sales
Content-Type: application/json

{
  "id": 1001,
  "store_code": "TX001",
  "total_sales": 530.48,
  "transaction_date": "2023-02-01"
}
###
```

Within the `sales()` function, when the requested method is POST and an insertion is requested, the function retrieves and checks the data types. It then uses the SQL query `INSERT INTO Sales (id, store_code, total_sales, transaction_date) VALUES (%s, %s, %s, %s)` to insert data into the database with the acceptable parameters: `id` (integer), `store ID` (string), `Total_sales` (decimal(10,2)), and `Date` (date). In the services console, you will receive a response message indicating a successful write, and it will display the new row that has been written into the database.

# Error handling

**Overload**

If you receive the following message from the service console while using the POST method, it may indicate that your service is experiencing issues:
```
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<title>500 Internal Server Error</title>
<h1>Internal Server Error</h1>
<p>The server encountered an internal error and was unable to complete your request.  Either the server is overloaded or there is an error in the application.</p>
```
This message suggests that port 5000 may be overloaded. In this case, restarting your computer should resolve the error.
