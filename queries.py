create_survey_table_query = '''
    CREATE TABLE IF NOT EXISTS survey (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        occupation TEXT,
        salary INTEGER
    )
'''
