import sqlite3


def get_latest_value(db_path, table, column):

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = f'''
        SELECT "{column}"
        FROM "{table}"
        ORDER BY rowid DESC
        LIMIT 1
    '''

    try:
        cursor.execute(query)
        row = cursor.fetchone()
    except Exception as e:
        print("DB ERROR:", table, column, e)
        conn.close()
        return ""

    conn.close()

    if row and row[0] is not None:
        return row[0]

    return ""