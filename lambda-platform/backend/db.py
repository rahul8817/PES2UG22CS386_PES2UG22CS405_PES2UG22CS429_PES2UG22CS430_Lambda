from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./functions.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class Function(Base):
    __tablename__ = "functions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    route = Column(String)
    language = Column(String)
    timeout = Column(Integer)
    file_path = Column(String)

# Initialize DB
def init_db():
    Base.metadata.create_all(bind=engine)
