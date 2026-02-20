import pandas as pd
import os
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import logging
import time

# ---------------- Logging Setup ----------------
logging.basicConfig(
    filename="logs/ingestion_db.log",  # fixed typo
    level=logging.INFO,                 # INFO is better for large files
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)

# ---------------- Database Connection ----------------
password = quote_plus("ashitosh")
engine = create_engine(
    f"postgresql+psycopg2://postgres:{password}@127.0.0.1:5432/Vendor_performance"
)

with engine.connect() as conn:
    print("CONNECTED SUCCESSFULLY")

# ---------------- Ingest CSV Function ----------------
def ingest_csv_to_postgres(path, table_name, engine, chunksize=100_000):
    first_chunk = True
    chunk_num = 0

    for chunk in pd.read_csv(path, chunksize=chunksize, low_memory=False):
        chunk.to_sql(
            table_name.lower(),
            con=engine,
            if_exists="replace" if first_chunk else "append",
            index=False,
            method="multi"
        )
        first_chunk = False
        chunk_num += 1
        logging.info(f"{table_name}: chunk {chunk_num} inserted ({len(chunk)} rows)")

# ---------------- Load All CSVs ----------------
def load_raw_data():
    start = time.time()
    data = r'D:/DATA ANALYST/Project incomplete/data'

    logging.info("===== DATA INGESTION STARTED =====")

    for file in os.listdir(data):
        if file.endswith(".csv"):
            table = file[:-4]
            path = os.path.join(data, file)

            file_start = time.time()
            logging.info(f"Started ingesting {file}")

            ingest_csv_to_postgres(path, table, engine)

            file_end = time.time()
            file_time = (file_end - file_start) / 60
            logging.info(f"Finished {table} in {file_time:.2f} minutes")

    end = time.time()
    total_time = (end - start) / 60
    logging.info("-------------All Ingestion Completed---------------")
    logging.info(f"Total Time Taken: {total_time:.2f} minutes")

# ---------------- Main Guard ----------------
if __name__ == "__main__":
    load_raw_data()