from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from passlib.context import CryptContext
from app import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---- Helper ----
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# ---- User & Driver creation ----
async def create_driver(db: AsyncSession, driver_in: schemas.DriverCreate) -> models.Driver:
    # 1. Create user record
    user = models.User(
        role=models.UserRole.driver,
        phone=driver_in.phone,
        email=driver_in.email,
        password_hash=hash_password(driver_in.password),
        is_active=True,
    )
    db.add(user)
    await db.flush()   # to get user.id

    # 2. Create driver record
    driver = models.Driver(
        user_id=user.id,
        full_name=driver_in.full_name,
        license_number=driver_in.license_number,
        is_verified=False,
        rating=5.0,
    )
    db.add(driver)

    # 3. Create initial driver_status row (offline by default)
    driver_status = models.DriverStatus(
        driver_id=user.id,
        status=models.DriverStatusType.offline,
    )
    db.add(driver_status)

    await db.commit()
    await db.refresh(driver)
    return driver

# ---- Driver read / update / delete ----
async def get_driver(db: AsyncSession, driver_id: UUID) -> models.Driver | None:
    result = await db.execute(
        select(models.Driver).where(models.Driver.user_id == driver_id)
    )
    return result.scalar_one_or_none()

async def list_drivers(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.Driver).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def update_driver(db: AsyncSession, driver_id: UUID, update_data: schemas.DriverUpdate) -> models.Driver | None:
    stmt = (
        update(models.Driver)
        .where(models.Driver.user_id == driver_id)
        .values(**update_data.model_dump(exclude_unset=True))
        .returning(models.Driver)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one_or_none()

async def delete_driver(db: AsyncSession, driver_id: UUID) -> bool:
    # Cascade delete will remove user, vehicles, driver_status automatically
    stmt = delete(models.Driver).where(models.Driver.user_id == driver_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0

# ---- Vehicle CRUD ----
async def create_vehicle(db: AsyncSession, driver_id: UUID, vehicle_in: schemas.VehicleCreate) -> models.Vehicle:
    vehicle = models.Vehicle(driver_id=driver_id, **vehicle_in.model_dump())
    db.add(vehicle)
    await db.commit()
    await db.refresh(vehicle)
    return vehicle

async def get_vehicle(db: AsyncSession, vehicle_id: UUID) -> models.Vehicle | None:
    result = await db.execute(
        select(models.Vehicle).where(models.Vehicle.id == vehicle_id)
    )
    return result.scalar_one_or_none()

async def list_vehicles_by_driver(db: AsyncSession, driver_id: UUID):
    result = await db.execute(
        select(models.Vehicle).where(models.Vehicle.driver_id == driver_id)
    )
    return result.scalars().all()

async def update_vehicle(db: AsyncSession, vehicle_id: UUID, update_data: schemas.VehicleUpdate) -> models.Vehicle | None:
    stmt = (
        update(models.Vehicle)
        .where(models.Vehicle.id == vehicle_id)
        .values(**update_data.model_dump(exclude_unset=True))
        .returning(models.Vehicle)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one_or_none()

async def delete_vehicle(db: AsyncSession, vehicle_id: UUID) -> bool:
    stmt = delete(models.Vehicle).where(models.Vehicle.id == vehicle_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0

# ---- Driver status flag (no GPS) ----
async def update_driver_status(db: AsyncSession, driver_id: UUID, status: str) -> models.DriverStatus | None:
    stmt = (
        update(models.DriverStatus)
        .where(models.DriverStatus.driver_id == driver_id)
        .values(status=status)
        .returning(models.DriverStatus)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one_or_none()