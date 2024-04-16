from flask import Flask, jsonify, request
import pandas as pd
from db_connection import execute_query

app = Flask(__name__)


@app.route('/getData')
# Outputs data based on inputted data range: start_date & end_date
# Sample Dataset is outputted in three ways:
# (1) JSON Dictionary
# (2) List (Jsonify)
# (3) Pandas Data Frame (pd)
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

    if not data:
        return jsonify({'error': 'No data found'})

    # Converting data to different formats
    pandas_df = pd.DataFrame(data)

    # Responding with multiple formats
    respond = {
        'JSON Dictionary': data,
        'list': [list(item.values()) for item in data],
        'Pandas Data Frame': pandas_df.to_json(orient='records')
    }

    return jsonify(respond)


if __name__ == '__main__':
    app.run()
