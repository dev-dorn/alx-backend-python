# Python Generators — ALX project (python-generators-0x00)

This folder contains the project files for the Python Generators ALX project.
Files included:
- seed.py
- 0-stream_users.py
- 1-batch_processing.py
- 2-lazy_paginate.py
- 4-stream_ages.py

## Requirements
- Python 3.8+
- pip packages (if using MySQL):
  - mysql-connector-python
  Install: `pip install mysql-connector-python`
- Alternatively the scripts have a sqlite fallback; no extra packages required.

## Environment variables (optional)
- MYSQL_HOST (default: localhost)
- MYSQL_PORT (default: 3306)
- MYSQL_USER (default: root)
- MYSQL_PASSWORD (default: "")

## CSV data
Place your CSV file (named e.g. `user_data.csv`) in the same directory. The CSV file should have headers:
`user_id,name,email,age` — if `user_id` column is missing, seed will generate UUIDs.

## Steps

1. Seed the DB and create tables (run `0-main.py` from ALX harness or manually run the following):
   ```bash
   python -c "import seed; conn = seed.connect_db(); seed.create_database(conn); conn.close(); conn2 = seed.connect_to_prodev(); seed.create_table(conn2); seed.insert_data(conn2, 'user_data.csv'); conn2.close()"
