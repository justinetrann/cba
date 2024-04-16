from flask import Flask, jsonify
from db_connection import execute_query

app = Flask(__name__)


@app.route('/data')
def get_data_sales():
    sql_query = "SELECT * FROM Sales"
    data = execute_query(sql_query)
    if data:
        return jsonify(data)
    else:
        return jsonify({'error': 'No data found'})


if __name__ == '__main__':
    app.run()
