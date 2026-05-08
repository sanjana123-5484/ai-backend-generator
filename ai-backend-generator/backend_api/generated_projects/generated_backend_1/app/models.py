
from sqlalchemy import Column, Integer, String, Date, Float
from .database import Base

class Books(Base):
    __tablename__ = "Books"

    BookID = Column(Integer, primary_key=True)
    Title = Column(String)
    Author = Column(String)
    Publisher = Column(String)
    PublicationDate = Column(Date)
    ISBN = Column(String)
    Status = Column(String)


class Members(Base):
    __tablename__ = "Members"

    MemberID = Column(Integer, primary_key=True)
    FirstName = Column(String)
    LastName = Column(String)
    Email = Column(String)
    PhoneNumber = Column(String)
    Address = Column(String)
    JoinDate = Column(Date)


class Borrowrecords(Base):
    __tablename__ = "BorrowRecords"

    RecordID = Column(Integer, primary_key=True)
    BookID = Column(Integer)
    MemberID = Column(Integer)
    BorrowDate = Column(Date)
    DueDate = Column(Date)
    ReturnDate = Column(Date)
    Fine = Column(Float)

