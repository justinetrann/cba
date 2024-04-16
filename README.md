# Development Overview of Store_Data Database

This document outlines the steps taken to develop the Store_Data database, detailing the creation of the database, table structures, and the data import process utilized in MySQL Workbench 8.0 CE.

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

To adjust the settings in MySQL Workbench 8.0 CE for proper casting, you will need to temporarily disable safe mode. Start by setting SQL_SAFE_UPDATES to 0.
This change allows you to perform the necessary data manipulations without the restrictions of safe mode, remember to re-enable safe mode by setting SQL_SAFE_UPDATES back to 1 to ensure the database's integrity is maintained.

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
ALTER TABLE Sales ADD COLUMN temp_transaction_date DATE;

UPDATE Sales
SET temp_transaction_date = STR_TO_DATE(transaction_date, '%m/%d/%Y');

-- Drop the old 'transaction_date' column
ALTER TABLE Sales DROP COLUMN transaction_date;

-- Rename the temporary column to 'transaction_date'
ALTER TABLE Sales CHANGE COLUMN temp_transaction_date transaction_date DATE;
```

# Development Overview of Python Flask application in PyCharm
**Connecting a Database to PyCharm: Two Approaches**

**Approach One:**

The database was connected to PyCharm through the IDE's graphical interface. 
The connection setup involved specifying `localhost` as the host on port `3306` and providing the necessary username and password. 
The JDBC URL used for the connection was `jdbc:mysql://localhost:3306/Store_Data`.

Reference: https://www.jetbrains.com/help/pycharm/mysql.html#reference

**Approach Two (aka. the creation of function execute_query):**

The connection is made in `db_connection.py` through the function `execute_query()`. 
This function not only establishes a connection but also accepts a SQL string query through the cursor script
and returns a list of dictionaries containing the query results, which can be seen at [http://127.0.0.1:5000/(http://127.0.0.1:5000/). 
Finally, if a connection is established, the cursor is closed to prevent memory leaks and free up resources.

References Used:

[Python MySQL database connection tutorial](https://pynative.com/python-mysql-database-connection/)

[MySQL Connector/Python API documentation](https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-execute.html)

Example: app.py:
```py
from flask import Flask, jsonify
from db_connection import execute_query

app = Flask(__name__)


@app.route('/')
def get_data_sales():
    sql_query = "SELECT * FROM Sales"
    data = execute_query(sql_query)
    if data:
        return jsonify(data)
    else:
        return jsonify({'error': 'No data found'})


if __name__ == '__main__':
    app.run()
```

Snippt Result from http://127.0.0.1:5000/

[{"id":1,"store_code":"TX001","total_sales":"937.70","transaction_date":"Sun, 12 Feb 2023 00:00:00 GMT"},{"id":2,"store_code":"TX001","total_sales":"1117.77","transaction_date":"Sat, 25 Mar 2023 00:00:00 GMT"},{"id":3,"store_code":"TX001","total_sales":"365.68","transaction_date":"Mon, 06 Feb 2023 00:00:00 GMT"},{"id":4,"store_code":"TX001","total_sales":"199.44","transaction_date":"Mon, 20 Feb 2023 00:00:00 GMT"},{"id":5,"store_code":"TX001","total_sales":"530.48","transaction_date":"Sat, 04 Mar 2023 00:00:00 GMT"},{"id":6,"store_code":"TX001","total_sales":"396.33","transaction_date":"Fri, 03 Mar 2023 00:00:00 GMT"},...

**Development of GET endpoint**

The following code is a GET endpoint that creates an instance of the Flask class. This instance becomes the WSGI application, accessible at [http://127.0.0.1:5000/](http://127.0.0.1:5000/). 
Here, the parameters are passed through the URL, which is common for HTTP GET requests. Using the locally default URL, we pass the query parameters by using the symbol '?'. 
The part that follows this symbol contains the query parameters we defined within our GET endpoint: `start_date = request.args.get('start_date')` and `end_date = request.args.get('end_date')`. By using `request.args.get`, we extract the values from the query string.

*   `?` introduces the query string.
*   `&` separates multiple query parameters.
*   `=` links the key and the value in each parameter pair.

Example: [http://127.0.0.1:5000/?start\_date=2023-02-12&end\_date=2023-03-24](http://127.0.0.1:5000/?start_date=2023-02-12&end_date=2023-03-24)

```py
from flask import Flask, jsonify, request
from dbconnection import executequery

app = Flask(__name)


@app.route('/')
def get_data_sales():
    # Retrieve the data from a range of dates
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Checks if both dates are accessible
    if not start_date or not end_date:
        return jsonify({'error': 'start_date and end_date must be provided'}), 400

    # SQL query for selected dates within a given range
    sql_query = "SELECT * FROM Sales WHERE transaction_date BETWEEN %s AND %s"
    data = execute_query(sql_query, (start_date, end_date))

    if data:
        return jsonify(data)
    else:
        return jsonify({'error': 'No data found'})


if __name == '__main':
    app.run()
```

Note that the GET request executes the 'get\_data\_sales' function, where the function connects to MySQL through another function, `execute_query`, fetching data from a table and returning
it as the requested outputs in the required form.

