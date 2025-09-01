# database.py
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from os import environ

DATABASE_URL = environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(String, unique=True, index=True)
    title = Column(String)
    author = Column(String)
    is_borrowed = Column(Boolean, default=False)
    borrower_id = Column(String, nullable=True)


Base.metadata.create_all(bind=engine)
