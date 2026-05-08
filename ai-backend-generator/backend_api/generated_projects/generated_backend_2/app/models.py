
from sqlalchemy import Column, Integer, String, Date, Float
from .database import Base

class Books(Base):
    __tablename__ = "Books"

    BookID = Column(Integer, primary_key=True)
    Title = Column(String)
    Author = Column(String)
    Publisher = Column(String)
    PublicationYear = Column(Integer)
    ISBN = Column(String)
    Status = Column(String)


class Members(Base):
    __tablename__ = "Members"

    MemberID = Column(Integer, primary_key=True)
    Name = Column(String)
    Email = Column(String)
    Phone = Column(String)
    Address = Column(String)
    MembershipDate = Column(Date)
    ExpirationDate = Column(Date)


class Borrowrecords(Base):
    __tablename__ = "BorrowRecords"

    RecordID = Column(Integer, primary_key=True)
    BookID = Column(Integer)
    MemberID = Column(Integer)
    BorrowDate = Column(Date)
    ReturnDate = Column(Date)
    DueDate = Column(Date)
    Fine = Column(Float)
    2) = Column(String)

