import sqlite3
import csv

def add_zebra():
    conn = sqlite3.connect("mimics.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS zebra(genome_id text PRIMARY KEY, covered_length int, total_length int, coverage_ratio real)")
    with open("coverage_output.tsv") as zebra_output:
        zebra_reader = csv.reader(zebra_output, delimiter='\t', quotechar='|')
        header = next(zebra_reader)
        for row in zebra_reader:
            c.execute("INSERT INTO zebra VALUES(?,?,?,?)", (row[0], row[1], row[2], row[3]))
    conn.commit()
    conn.close()

add_zebra()