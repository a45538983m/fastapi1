from sqlalchemy import (
    Column, String, Boolean, Numeric, Integer, Text,
    TIMESTAMP, ForeignKey, Uuid, Enum as SQLAEnum
)
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geography
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()

# Enums – use same names as in DB
class UserRole:
    passenger = "passenger"
    driver = "driver"
    admin = "admin"

class DriverStatusType:
    offline = "offline"
    available = "available"
    on_trip = "on_trip"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role = Column(SQLAEnum("passenger", "driver", "admin", name="user_role"), nullable=False)
    phone = Column(String(32), nullable=False, unique=True)
    email = Column(String(255), unique=True)
    password_hash = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, onupdate=func.now())

class Driver(Base):
    __tablename__ = "drivers"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    full_name = Column(String(255))
    license_number = Column(String(64), nullable=False, unique=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    rating = Column(Numeric(3,2), default=5.0)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    driver_id = Column(UUID(as_uuid=True), ForeignKey("drivers.user_id", ondelete="CASCADE"), nullable=False)
    brand = Column(String(64), nullable=False)
    model = Column(String(64), nullable=False)
    plate_number = Column(String(32), nullable=False, unique=True)
    color = Column(String(32))
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

class DriverStatus(Base):
    __tablename__ = "driver_status"

    driver_id = Column(UUID(as_uuid=True), ForeignKey("drivers.user_id", ondelete="CASCADE"), primary_key=True)
    status = Column(SQLAEnum("offline", "available", "on_trip", name="driver_status_type"), nullable=False)
    current_location = Column(Geography(geometry_type="POINT", srid=4326), nullable=True)   # not used in this service
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())