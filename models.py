from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

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
    date = Column(DateTime, default = datetime.utcnow)

    subcategory_id = Column(Integer, ForeignKey("subcategories.id"))
    subcategory = relationship("Subcategory", back_populates = 'expenses')