"""
SQLAlchemy models for users, global deals and deals.

Description:
    This module defines the ORM tables used by the Best Deal application and their
    persisted fields.
"""

from datetime import datetime, timezone
from .database import Base
from sqlalchemy import Column, Integer, Numeric, String, Text, Boolean, DateTime, JSON, ForeignKey

class Users(Base):
    """
    Represent an authenticated application user.

    Returns:
        A SQLAlchemy model mapped to the users table.
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    preferred_category = Column(JSON, nullable=True)
    preferred_product = Column(JSON, nullable=True)
    preferred_country_market = Column(JSON, nullable=True)
    role = Column(String(50), default="user", nullable=False)
    status = Column(String(20),default="active",nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class GlobalDeals(Base):
    """
    This model represents a deal item that is available globally.

    Returns:
        A SQLAlchemy model mapped to the global_deals table.
    """
    __tablename__ = 'global_deals'  
    
    id = Column(Integer, primary_key=True, index=True)
    product_title = Column(String(300), nullable=True)
    product_description = Column(Text, nullable=True)
    product_url = Column(String(1000), nullable=True)
    actual_price = Column(Numeric(12, 2), nullable=True)
    estimated_price = Column(Numeric(12, 2), nullable=True)
    discount = Column(Numeric(5, 2), nullable=True)
    currency = Column(String(10), nullable=True)
    country = Column(String(100), nullable=True)
    created_at = Column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            nullable=False
        )

class UserDeals(Base):
    """
    This model represents a relation between a user and a global deal.

    Returns:
        A SQLAlchemy model mapped to the user_deals table.
    """

    __tablename__ = 'user_deals'  
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    deal_id = Column(Integer, ForeignKey('global_deals.id'), nullable=False)
    recommended_at = Column(
                DateTime(timezone=True),
                default=lambda: datetime.now(timezone.utc),
                nullable=False
            )
    is_seen = Column(Boolean, default=False, nullable=False)
    is_saved = Column(Boolean, default=False, nullable=False)