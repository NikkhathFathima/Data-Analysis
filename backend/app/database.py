from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "sqlite:///./sales_platform.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)
    role = Column(String, default="user")  # admin / user
    created_at = Column(DateTime, default=datetime.utcnow)
    uploads = relationship("SalesData", back_populates="owner")
    reports = relationship("Report", back_populates="owner")

class SalesData(Base):
    __tablename__ = "sales_data"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    row_count = Column(Integer)
    status = Column(String, default="processing")  # processing / ready / error
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="uploads")
    records = relationship("ProcessedData", back_populates="dataset")

class ProcessedData(Base):
    __tablename__ = "processed_data"
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("sales_data.id"))
    order_id = Column(String)
    order_date = Column(DateTime)
    ship_date = Column(DateTime)
    customer_name = Column(String)
    segment = Column(String)
    region = Column(String)
    category = Column(String)
    sub_category = Column(String)
    product_name = Column(String)
    sales = Column(Float)
    quantity = Column(Integer)
    discount = Column(Float)
    profit = Column(Float)
    profit_pct = Column(Float)
    month_year = Column(String)
    dataset = relationship("SalesData", back_populates="records")

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="reports")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
