from confg import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
from sqlmodel import create_engine, Session, SQLModel


DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
def get_db():
    with Session(engine) as session:
        yield session

