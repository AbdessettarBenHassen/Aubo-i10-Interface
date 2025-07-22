import sqlite3

def dump_table(cursor, table):
    print(f"\n=== {table.upper()} ===")

    # Get columns
    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()
    col_names = [col[1] for col in columns]
    print("Columns:", col_names)

    # Count records
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"Total records in {table}: {count}")

    if count == 0:
        print("No records found.")
        return

    # Print first 5 records
    cursor.execute(f"SELECT * FROM {table} ORDER BY rowid ASC LIMIT 5")
    first_rows = cursor.fetchall()
    print("\nFirst 5 records:")
    for i, row in enumerate(first_rows, 1):
        print(f" Record {i}: {row}")

    # Print last 5 records
    cursor.execute(f"SELECT * FROM {table} ORDER BY rowid DESC LIMIT 5")
    last_rows = cursor.fetchall()
    print("\nLast 5 records:")
    for i, row in enumerate(last_rows, 1):
        print(f" Record {i}: {row}")

    # Fetch all records (comment out if too long)
    cursor.execute(f"SELECT * FROM {table}")
    all_rows = cursor.fetchall()

    # Write all records to file for full inspection
    with open(f"db_dump_{table}.txt", "w", encoding="utf-8") as f:
        f.write(f"Table: {table}\nColumns: {col_names}\nTotal records: {count}\n\n")
        for i, row in enumerate(all_rows, 1):
            f.write(f"--- Record {i} ---\n")
            for col_name, value in zip(col_names, row):
                f.write(f"{col_name}: {value}\n")
            f.write("\n")

    print(f"\nAll records dumped to db_dump_{table}.txt\n")

def main():
    db_path = 'C:/Users/Emna/Desktop/tool_coord_param.db'
    tables = ['tool_dynamics_param', 'tool_kinematics_calibrate_point', 'tool_kinematics_param', 'tool_param', 'coord_param',]

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # List all tables in DB
    print("\n--- Tables in Database ---")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables_in_db = cursor.fetchall()
    print(tables_in_db)

    # Dump info for each relevant table
    for table in tables:
        dump_table(cursor, table)

    conn.close()

if __name__ == "__main__":
    main()
