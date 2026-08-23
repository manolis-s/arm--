from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from database import Base
from datetime import datetime
from sqlalchemy.orm import relationship
import pytz

class Category(Base):
    __tablename__='categories'
    id = Column(Integer, primary_key=True, index= True)
    name = Column(String, index = True)
    is_inside_camp = Column(Boolean, default = False)

    subcategories = relationship("Subcategory", back_populates='category')

class Subcategory(Base):
    __tablename__ = 'subcategories'
    id = Column(Integer, primary_key = True, index=True)
    name = Column(String, index = True)
    category_id = Column(Integer, ForeignKey("categories.id")) #foreign key gia to categories

    category = relationship("Category", back_populates = "subcategories")
    expenses = relationship("Expense", back_populates = 'subcategory')

class Expense(Base):
    __tablename__ = 'expenses'
    id = Column(Integer, primary_key = True, index=True)
    amount = Column(Float, nullable = False)
    description = Column(String, default="")
    date = Column(DateTime, default = get_greek_time)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)

    user = relationship("User", back_populates = 'expenses')
    subcategory_id = Column(Integer, ForeignKey("subcategories.id"))
    subcategory = relationship("Subcategory", back_populates = 'expenses')

def get_greek_time():
    greece_tz = pytz.timezone('Europe/Athens')
    return datetime.now(greece_tz).replace(tzinfo=None)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    discharge_date = Column(String, nullable=False)

    expenses = relationship("Expense", back_populates="user")

