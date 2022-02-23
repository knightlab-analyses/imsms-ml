import sqlite3

if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")

    conn = sqlite3.connect("mimics.db")
    c = conn.cursor()

    c.execute("SELECT 1")
    print(c.fetchall())
    c.execute("SELECT log(1), log(10), log(100)")
    print(c.fetchall())
