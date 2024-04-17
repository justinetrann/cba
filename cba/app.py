from flask import Flask, request, jsonify
import pandas as pd
from db_connection import execute_query

app = Flask(__name__)


@app.route('/sales', methods=['GET', 'POST'])
def sales():
    if request.method == 'GET':
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
            return jsonify({'error': 'No data found'}), 400

        # Converting data to different formats
        pandas_df = pd.DataFrame(data)

        # Responding with multiple formats
        respond = {
            'JSON Dictionary': data,
            'list': [list(item.values()) for item in data],
            'Pandas Data Frame': pandas_df.to_json(orient='records')
        }

        return jsonify(respond)

    elif request.method == 'POST':
        data = request.get_json()
        try:
            # Retrieving data and type-checking params
            id_sales = int(data['id'])
            store_id = str(data['store_code'])
            total_sales = float(data['total_sales'])
            date = str(data['transaction_date'])

            # Inserting data into Sales table in Sales_Data db
            sql_insert_query = (
                "INSERT INTO Sales (id, store_code, total_sales, transaction_date) "
                "VALUES (%s, %s, %s, %s)"
            )
            response = execute_query(sql_insert_query, (id_sales, store_id, total_sales, date))

            if response.get('success', False):
                sql_select_query = "SELECT * FROM Sales WHERE id = %s"
                select_response = execute_query(sql_select_query, (id_sales,))

                if select_response:
                    return jsonify({
                        'success': True,
                        'message': 'Data inserted and verified successfully',
                        'id': id_sales
                    }), 200
                else:
                    return jsonify({'success': False, 'message': 'Data was inserted but could not be verified'}), 500
            else:
                return jsonify({'success': False, 'message': 'Failed to insert data into database'}), 500

        except ValueError as ve:
            return jsonify({'success': False, 'message': 'Invalid data types provided. Error: ' + str(ve)}), 400
        except KeyError as ke:
            return jsonify({'success': False, 'message': 'Missing data for: ' + str(ke)}), 400


if __name__ == '__main__':
    app.run()
