# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from src.database import SessionLocal, Book


# Pydantic models for request/response validation
class BookCreate(BaseModel):
    book_id: str
    title: str
    author: str


class BookUpdate(BaseModel):
    is_borrowed: bool
    borrower_id: str | None = None


class BookOut(BaseModel):
    book_id: str
    title: str
    author: str
    is_borrowed: bool
    borrower_id: str | None

    class Config:
        orm_mode = True


app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 1) Add a new book
@app.post("/books/", response_model=BookOut, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.book_id == book.book_id).first()
    if db_book:
        raise HTTPException(status_code=400, detail="Book with this ID already exists.")

    new_book = Book(**book.dict())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book


# 2) Delete a book
@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: str, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.book_id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found.")

    db.delete(db_book)
    db.commit()
    return {"message": "Book deleted successfully."}


# 3) Download the list of all the books
@app.get("/books/", response_model=list[BookOut])
def get_all_books(db: Session = Depends(get_db)):
    books = db.query(Book).all()
    return books


# 4) Update the status of the given book
@app.put("/books/{book_id}", response_model=BookOut)
def update_book_status(book_id: str, update: BookUpdate, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.book_id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found.")

    db_book.is_borrowed = update.is_borrowed
    db_book.borrower_id = update.borrower_id

    db.commit()
    db.refresh(db_book)
    return db_book
