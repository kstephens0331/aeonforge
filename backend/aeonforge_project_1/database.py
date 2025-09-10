#!/usr/bin/env python3
"""
Database Management System
Advanced database operations with SQLAlchemy
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import logging
from typing import List, Dict, Optional

Base = declarative_base()

class Product(Base):
    """Product database model"""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    price = Column(String(50))
    url = Column(Text, unique=True)
    availability = Column(String(100))
    description = Column(Text)
    category = Column(String(100))
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Product(name='{self.name}', price='{self.price}')>"

class DatabaseManager:
    """Database operations manager"""
    
    def __init__(self, db_url: str = "sqlite:///products.db"):
        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.logger = logging.getLogger(__name__)
        
    def initialize(self):
        """Initialize database tables"""
        Base.metadata.create_all(bind=self.engine)
        self.logger.info("Database initialized")
        
    def store_products(self, products_data: List[Dict]):
        """Store products in database"""
        session = self.SessionLocal()
        try:
            for product_data in products_data:
                # Check if product exists
                existing = session.query(Product).filter_by(url=product_data.get('url')).first()
                
                if existing:
                    # Update existing product
                    for key, value in product_data.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                else:
                    # Create new product
                    product = Product(**product_data)
                    session.add(product)
                    
            session.commit()
            self.logger.info(f"Stored {len(products_data)} products")
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error storing products: {e}")
            raise
        finally:
            session.close()
            
    def get_products(self, limit: int = 100) -> List[Product]:
        """Retrieve products from database"""
        session = self.SessionLocal()
        try:
            products = session.query(Product).limit(limit).all()
            return products
        finally:
            session.close()
            
    def search_products(self, query: str) -> List[Product]:
        """Search products by name"""
        session = self.SessionLocal()
        try:
            products = session.query(Product).filter(
                Product.name.contains(query)
            ).all()
            return products
        finally:
            session.close()
