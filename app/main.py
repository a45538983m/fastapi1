from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError          # <-- ДОБАВИТЬ ЭТУ СТРОКУ
from uuid import UUID
from typing import List
from app import crud, schemas, database


app = FastAPI(title="Driver Service", version="1.0")

# Dependency
async def get_db():
    async for session in database.get_db():
        yield session

# ------------------- Driver Endpoints -------------------
@app.post("/drivers", response_model=schemas.DriverResponse, status_code=201)
async def register_driver(
    driver_in: schemas.DriverCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new driver (creates user + driver + initial status)"""
    try:
        driver = await crud.create_driver(db, driver_in)
    except IntegrityError as e:
        if "phone" in str(e) or "license_number" in str(e):
            raise HTTPException(status_code=409, detail="Phone or license already exists")
        raise
    return driver

@app.get("/drivers/{driver_id}", response_model=schemas.DriverResponse)
async def get_driver(driver_id: UUID, db: AsyncSession = Depends(get_db)):
    driver = await crud.get_driver(db, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver

@app.get("/drivers", response_model=List[schemas.DriverResponse])
async def list_drivers(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud.list_drivers(db, skip, limit)

@app.patch("/drivers/{driver_id}", response_model=schemas.DriverResponse)
async def update_driver(
    driver_id: UUID,
    driver_update: schemas.DriverUpdate,
    db: AsyncSession = Depends(get_db),
):
    driver = await crud.update_driver(db, driver_id, driver_update)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver

@app.delete("/drivers/{driver_id}", status_code=204)
async def delete_driver(driver_id: UUID, db: AsyncSession = Depends(get_db)):
    deleted = await crud.delete_driver(db, driver_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Driver not found")
    return None

# ------------------- Vehicle Endpoints -------------------
@app.post("/drivers/{driver_id}/vehicles", response_model=schemas.VehicleResponse, status_code=201)
async def add_vehicle(
    driver_id: UUID,
    vehicle_in: schemas.VehicleCreate,
    db: AsyncSession = Depends(get_db),
):
    driver = await crud.get_driver(db, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    try:
        vehicle = await crud.create_vehicle(db, driver_id, vehicle_in)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Plate number already used")
    return vehicle

@app.get("/drivers/{driver_id}/vehicles", response_model=List[schemas.VehicleResponse])
async def list_vehicles(driver_id: UUID, db: AsyncSession = Depends(get_db)):
    return await crud.list_vehicles_by_driver(db, driver_id)

@app.patch("/vehicles/{vehicle_id}", response_model=schemas.VehicleResponse)
async def update_vehicle(
    vehicle_id: UUID,
    vehicle_update: schemas.VehicleUpdate,
    db: AsyncSession = Depends(get_db),
):
    vehicle = await crud.update_vehicle(db, vehicle_id, vehicle_update)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle

@app.delete("/vehicles/{vehicle_id}", status_code=204)
async def delete_vehicle(vehicle_id: UUID, db: AsyncSession = Depends(get_db)):
    deleted = await crud.delete_vehicle(db, vehicle_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return None

# ------------------- Driver Status (flag only) -------------------
@app.put("/drivers/{driver_id}/status", response_model=schemas.DriverStatusResponse)
async def update_status(
    driver_id: UUID,
    status_update: schemas.DriverStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    if status_update.status not in ["offline", "available", "on_trip"]:
        raise HTTPException(status_code=400, detail="Invalid status value")
    driver = await crud.get_driver(db, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    status_row = await crud.update_driver_status(db, driver_id, status_update.status)
    if not status_row:
        raise HTTPException(status_code=404, detail="Driver status row missing")
    return status_row

@app.get("/health")
async def health():
    return {"status": "ok"}