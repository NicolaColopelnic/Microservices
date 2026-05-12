import sqlite3

def init_db():
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        desc TEXT NOT NULL
        )
    ''')

    movies = [
        (1, "The devil wears Prada 2", "The movie reunites Miranda Priestly and a seasoned Andy Sachs to save a struggling Runway magazine in a digital-first world."),
        (2, "Michael", "A musical biographical drama that chronicles the life of Michael Jackson, from his childhood stardom in the Jackson 5 to his peak as the King of Pop"),
        (3, "Wuthering Heights", "An adaptation after the gothic novel exploring an intense, destructive love between Catherine Earnshaw and Heathcliff.")
    ]

    cursor.executemany('INSERT OR REPLACE INTO movies VALUES (?, ?, ?)', movies)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()