# check_db.py
import sqlite3

def check_database():
    conn = sqlite3.connect("welding_gun.db")
    cursor = conn.cursor()
    
    print("检查users表结构:")
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  列 {col[1]}: 类型 {col[2]}, 是否主键: {col[5]}")
    
    print("\n检查guns表结构:")
    cursor.execute("PRAGMA table_info(guns)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  列 {col[1]}: 类型 {col[2]}, 是否主键: {col[5]}")
    
    conn.close()

if __name__ == "__main__":
    check_database()