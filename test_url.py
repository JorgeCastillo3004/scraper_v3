import psycopg2

# Function to establish the database connection
def getdb():
    return psycopg2.connect(
        host="localhost",
        user="wohhu",
        password="caracas123",
        dbname='sports_db',
    )

# Function to create the URL column if it doesn't exist
def create_url_column(cursor, table_name):
    query = f"""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                           WHERE table_name=%(table_name)s AND column_name='url') THEN
                ALTER TABLE {table_name} ADD COLUMN url TEXT;
            END IF;
        END
        $$;
    """
    cursor.execute(query, {'table_name': table_name})
    print(f"URL column checked/created in table {table_name}.")

# Function to update the URL column
def update_url_column(cursor, table_name, col1, col2):
    if table_name == 'team':
        query_select = query_select = f"""
            SELECT t.team_id, s.name, t.{col1}, t.{col2}
            FROM {table_name} t
            JOIN sport s ON t.sport_id = s.sport_id
        """
        cursor.execute(query_select)
        rows = cursor.fetchall()

        query_update = f"UPDATE {table_name} SET url = %(url)s WHERE {table_name}_id = %(id)s"
        
        for row in rows:
            team_id = row[0]
            sport_name = row[1]
            col1_value = row[2]
            col2_value = row[3]

            # Concatenate and format the URL            
            url = f"{sport_name}_{col1_value}_{col2_value}"
            print(url)
            url = url.replace("/", "_").replace(" - ", "_")
            url = url.replace(" ", "_").replace(".","").lower()
            print(url)

            # Update the URL column
            cursor.execute(query_update, {'url': url, 'id': team_id})            
    else:
        query_select = f"SELECT {table_name}_id, {col1}, {col2} FROM {table_name}"

        cursor.execute(query_select)
        rows = cursor.fetchall()

        query_update = f"UPDATE {table_name} SET url = %(url)s WHERE {table_name}_id = %(id)s"
        
        for row in rows:
            league_id = row[0]
            col1_value = row[1]
            col2_value = row[2]

            # Concatenate and format the URL
            if col1_value!='':
                url = f"{col1_value}_{col2_value}"
            else:
                url = f"{col2_value}"
            print(url)
            url = url.replace("/", "_").replace(" - ", "_")
            url = url.replace(" ", "_").replace('.', '').lower()
            print(url)

            # Update the URL column
            cursor.execute(query_update, {'url': url, 'id': league_id})        

    print(f"URL column updated in table {table_name}.")

# Main function to run the script
def main(table_name, col1, col2):
    conn = None
    try:
        conn = getdb()
        cursor = conn.cursor()
        create_url_column(cursor, table_name)
        update_url_column(cursor, table_name, col1, col2)
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error in main function: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    table_name = "team"
    col1 = "team_country"
    col2 = "team_name"
    main(table_name, col1, col2)
