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

**Development of GET endpoint**

The following code is a GET endpoint that creates an instance of the Flask class. This instance becomes the WSGI application, accessible at [http://127.0.0.1:5000/getData](http://127.0.0.1:5000/). 
Here, the parameters are passed through the URL, which is common for HTTP GET requests. Using the locally default URL, we pass the query parameters by using the symbol '?'. 
The part that follows this symbol contains the query parameters we defined within our GET endpoint: `start_date = request.args.get('start_date')` and `end_date = request.args.get('end_date')`. By using `request.args.get`, we extract the values from the query string.

*   `?` introduces the query string.
*   `&` separates multiple query parameters.
*   `=` links the key and the value in each parameter pair.

Example: http://127.0.0.1:5000/getData?start\_date=2023-02-12&end\_date=2023-03-24

Note that the GET request executes the 'get\_data\_sales' function, where the function connects to MySQL through another function, `execute_query`, fetching data from a table and returning
it as the requested outputs in the required form.

**GET endpoint output: JSON Dictionary, List, and Pandas Data Frame**

We will enhance the above code to print the required outputs—JSON Dictionary, List, and Pandas DataFrame—based on the modifications made. The URL provided by the Flask application will reflect these data transformations.

Since the current implementation integrates all changes on a single page, it appears somewhat cluttered. To improve code clarity and maintainability, a future modification could introduce the &format parameter in the URL. This addition would allow users to specify their preferred output format, making the application more flexible and user-friendly.
