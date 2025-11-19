"""
Database configuration and models
"""

import pandas as pd
import sqlite3
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from .config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy setup
Base = declarative_base()

class Product(Base):
    """Product database model"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String, index=True)
    subcategory = Column(String)
    description = Column(Text)
    price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class Order(Base):
    """Order database model"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, unique=True, index=True)
    customer_id = Column(String, index=True)
    product_name = Column(String)
    product_description = Column(Text)
    order_date = Column(DateTime)
    quantity = Column(Integer)
    order_amount = Column(Float)
    order_status = Column(String)
    return_status = Column(String)
    return_start_date = Column(DateTime)
    return_received_date = Column(DateTime)
    return_completed_date = Column(DateTime)
    return_reason = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class FAQ(Base):
    """FAQ database model"""
    __tablename__ = "faqs"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, index=True)
    answer = Column(Text)
    category = Column(String, index=True)
    tags = Column(String)  # Comma-separated tags
    created_at = Column(DateTime, default=datetime.utcnow)

class Conversation(Base):
    """Conversation database model"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    customer_id = Column(String, index=True)
    message = Column(Text)
    response = Column(Text)
    intent = Column(String)
    confidence = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Database engine and session
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """Initialize database and load data"""
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Load data from CSV files
        await load_products_data()
        await load_orders_data()
        await load_faq_data()
        
        logger.info("Database initialization completed")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

async def load_products_data():
    """Load products data from CSV"""
    try:
        # Check if data already exists
        db = SessionLocal()
        if db.query(Product).count() > 0:
            db.close()
            return
            
        # Load CSV data
        df = pd.read_csv(settings.PRODUCTS_CSV)
        
        # Clean and prepare data
        products = []
        for _, row in df.iterrows():
            product = Product(
                name=row['name'],
                category=row['category'],
                subcategory=row['subcategory'],
                description=row['description'],
                price=row['price']
            )
            products.append(product)
        
        # Bulk insert
        db.bulk_save_objects(products)
        db.commit()
        db.close()
        
        logger.info(f"Loaded {len(products)} products into database")
        
    except Exception as e:
        logger.error(f"Error loading products data: {str(e)}")
        raise

async def load_orders_data():
    """Load orders data from CSV"""
    try:
        # Check if data already exists
        db = SessionLocal()
        if db.query(Order).count() > 0:
            db.close()
            return
            
        # Load CSV data
        df = pd.read_csv(settings.ORDERS_CSV)
        
        # Clean and prepare data
        orders = []
        for _, row in df.iterrows():
            # Parse dates
            order_date = pd.to_datetime(row['OrderDate']) if pd.notna(row['OrderDate']) else None
            return_start_date = pd.to_datetime(row['ReturnStartDate']) if pd.notna(row['ReturnStartDate']) else None
            return_received_date = pd.to_datetime(row['ReturnReceivedDate']) if pd.notna(row['ReturnReceivedDate']) else None
            return_completed_date = pd.to_datetime(row['ReturnCompletedDate']) if pd.notna(row['ReturnCompletedDate']) else None
            
            order = Order(
                order_id=row['OrderID'],
                customer_id=row['CID'],
                product_name=row['product_name'],
                product_description=row['product_description'],
                order_date=order_date,
                quantity=row['Quantity'],
                order_amount=row['OrderAmount'],
                order_status=row['OrderStatus'],
                return_status=row['ReturnStatus'] if pd.notna(row['ReturnStatus']) else None,
                return_start_date=return_start_date,
                return_received_date=return_received_date,
                return_completed_date=return_completed_date,
                return_reason=row['ReturnReason'] if pd.notna(row['ReturnReason']) else None,
                notes=row['Notes'] if pd.notna(row['Notes']) else None
            )
            orders.append(order)
        
        # Bulk insert
        db.bulk_save_objects(orders)
        db.commit()
        db.close()
        
        logger.info(f"Loaded {len(orders)} orders into database")
        
    except Exception as e:
        logger.error(f"Error loading orders data: {str(e)}")
        raise

async def load_faq_data():
    """Load FAQ data"""
    try:
        # Check if data already exists
        db = SessionLocal()
        if db.query(FAQ).count() > 0:
            db.close()
            return
            
        # Sample FAQ data (in production, this would come from a file or API)
        faq_data = [
            {
                "question": "What are your store hours?",
                "answer": "Our store is open Monday to Friday from 9 AM to 6 PM, Saturday from 10 AM to 4 PM, and closed on Sundays.",
                "category": "store_info",
                "tags": "hours,store,time"
            },
            {
                "question": "What is your return policy?",
                "answer": "We accept returns within 30 days of purchase. Items must be in original condition with tags attached. Electronics have a 14-day return window.",
                "category": "returns",
                "tags": "return,policy,refund"
            },
            {
                "question": "How can I track my order?",
                "answer": "You can track your order by entering your order ID on our website or by contacting customer service.",
                "category": "orders",
                "tags": "tracking,order,shipping"
            },
            {
                "question": "Do you offer international shipping?",
                "answer": "Yes, we ship internationally to most countries. Shipping costs and delivery times vary by location.",
                "category": "shipping",
                "tags": "international,shipping,delivery"
            },
            {
                "question": "What payment methods do you accept?",
                "answer": "We accept all major credit cards, PayPal, and bank transfers.",
                "category": "payment",
                "tags": "payment,credit,card,paypal"
            }
        ]
        
        # Insert FAQ data
        for faq in faq_data:
            faq_obj = FAQ(
                question=faq["question"],
                answer=faq["answer"],
                category=faq["category"],
                tags=faq["tags"]
            )
            db.add(faq_obj)
        
        db.commit()
        db.close()
        
        logger.info(f"Loaded {len(faq_data)} FAQ items into database")
        
    except Exception as e:
        logger.error(f"Error loading FAQ data: {str(e)}")
        raise

def get_products_by_category(category: str) -> List[Dict[str, Any]]:
    """Get products by category"""
    db = SessionLocal()
    try:
        products = db.query(Product).filter(Product.category == category).all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "subcategory": p.subcategory,
                "description": p.description,
                "price": p.price
            }
            for p in products
        ]
    finally:
        db.close()

def get_orders_by_customer(customer_id: str) -> List[Dict[str, Any]]:
    """Get orders by customer ID"""
    db = SessionLocal()
    try:
        orders = db.query(Order).filter(Order.customer_id == customer_id).all()
        return [
            {
                "order_id": o.order_id,
                "product_name": o.product_name,
                "order_date": o.order_date,
                "quantity": o.quantity,
                "order_amount": o.order_amount,
                "order_status": o.order_status,
                "return_status": o.return_status
            }
            for o in orders
        ]
    finally:
        db.close()

def get_order_by_id(order_id: str) -> Optional[Dict[str, Any]]:
    """Get order by order ID"""
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.order_id == order_id).first()
        if order:
            return {
                "order_id": order.order_id,
                "customer_id": order.customer_id,
                "product_name": order.product_name,
                "product_description": order.product_description,
                "order_date": order.order_date,
                "quantity": order.quantity,
                "order_amount": order.order_amount,
                "order_status": order.order_status,
                "return_status": order.return_status,
                "return_reason": order.return_reason,
                "notes": order.notes
            }
        return None
    finally:
        db.close()

def search_products(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search products by query"""
    db = SessionLocal()
    try:
        products = db.query(Product).filter(
            Product.name.contains(query) | 
            Product.description.contains(query)
        ).limit(limit).all()
        
        return [
            {
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "subcategory": p.subcategory,
                "description": p.description,
                "price": p.price
            }
            for p in products
        ]
    finally:
        db.close()
