# Create a gapminder SQL database to work with for the database design lecture
# A copy of this is also found in https://github.com/BIFX547-26/CourseInfo/assets/gapminder_db.py
# I also moved the database file to /inst/ext/gapminder.db
# need: pip install pandas

import sqlite3
import pandas as pd

# Fetch the dataset directly (no gapminder package required)
url = "https://raw.githubusercontent.com/jennybc/gapminder/master/inst/extdata/gapminder.tsv"
gapminder = pd.read_csv(url, sep='\t')

def create_database():
    print("Generating gapminder.db...")
    
    # 1. Connect to SQLite (this creates the file if it doesn't exist)
    conn = sqlite3.connect('gapminder.db')
    cursor = conn.cursor()

    # 2. Create Relational Tables (Normalized Schema)
    cursor.executescript("""
        DROP TABLE IF EXISTS observations;
        DROP TABLE IF EXISTS countries;
        DROP TABLE IF EXISTS continents;

        CREATE TABLE continents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE countries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            continent_id INTEGER,
            FOREIGN KEY (continent_id) REFERENCES continents (id)
        );

        CREATE TABLE observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_id INTEGER,
            year INTEGER,
            life_exp REAL,
            population INTEGER,
            gdp_per_cap REAL,
            FOREIGN KEY (country_id) REFERENCES countries (id)
        );
    """)

    # 3. Extract and insert Continents
    continents = gapminder['continent'].unique()
    for continent in continents:
        cursor.execute("INSERT INTO continents (name) VALUES (?)", (continent,))
    
    # Create a mapping of continent name to ID for the next step
    continent_map = {row[1]: row[0] for row in cursor.execute("SELECT id, name FROM continents").fetchall()}

    # 4. Extract and insert Countries
    # Get unique country-continent pairs
    countries = gapminder[['country', 'continent']].drop_duplicates()
    for _, row in countries.iterrows():
        continent_id = continent_map[row['continent']]
        cursor.execute("INSERT INTO countries (name, continent_id) VALUES (?, ?)", (row['country'], continent_id))
        
    # Create a mapping of country name to ID
    country_map = {row[1]: row[0] for row in cursor.execute("SELECT id, name FROM countries").fetchall()}

    # 5. Extract and insert Observations (Metrics)
    for _, row in gapminder.iterrows():
        country_id = country_map[row['country']]
        cursor.execute("""
            INSERT INTO observations (country_id, year, life_exp, population, gdp_per_cap) 
            VALUES (?, ?, ?, ?, ?)
        """, (country_id, row['year'], row['lifeExp'], row['pop'], row['gdpPercap']))

    # 6. Commit and close
    conn.commit()
    conn.close()
    print("Successfully generated gapminder.db with tables: continents, countries, observations.")

if __name__ == "__main__":
    create_database()