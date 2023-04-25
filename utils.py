from sqlalchemy import create_engine
from sqlalchemy.engine import URL

url = URL.create(
        drivername="postgresql+psycopg2",
        username="user",
        password="password",
        host="localhost",
        port=5432,
        database="edge_db"
        )

engine = create_engine(url)

connection = engine.connect()
