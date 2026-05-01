from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from typing import Optional

# ---- User schemas ----
class UserBase(BaseModel):
    phone: str
    email: Optional[str] = None
    role: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ---- Driver schemas ----
class DriverBase(BaseModel):
    full_name: Optional[str] = None
    license_number: str

class DriverCreate(DriverBase):
    phone: str
    email: Optional[str] = None
    password: str

class DriverUpdate(BaseModel):
    full_name: Optional[str] = None
    license_number: Optional[str] = None
    is_verified: Optional[bool] = None

class DriverResponse(DriverBase):
    user_id: UUID
    is_verified: bool
    rating: Decimal
    created_at: datetime
    user: Optional[UserResponse] = None   # nested user info

    model_config = ConfigDict(from_attributes=True)

# ---- Vehicle schemas ----
class VehicleBase(BaseModel):
    brand: str
    model: str
    plate_number: str
    color: Optional[str] = None

class VehicleCreate(VehicleBase):
    pass

class VehicleUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    plate_number: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None

class VehicleResponse(VehicleBase):
    id: UUID
    driver_id: UUID
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ---- Driver status (flags only) ----
class DriverStatusUpdate(BaseModel):
    status: str   # "offline", "available", "on_trip"

class DriverStatusResponse(BaseModel):
    driver_id: UUID
    status: str
    updated_at: datetime