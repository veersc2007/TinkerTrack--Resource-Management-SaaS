from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ReservationCreate(BaseModel):
    resource_id: int
    start_time: datetime
    end_time: datetime


class ReservationUpdate(BaseModel):
    start_time: datetime | None = None
    end_time: datetime | None = None


class ReservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    resource_id: int
    start_time: datetime
    end_time: datetime
    status: str


class ReservationHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resource_id: int
    start_time: datetime
    end_time: datetime
    status: str
    created_at: datetime | None = None

class ReservationFilter(BaseModel):
    user_id: int | None = None
    resource_id: int | None = None
    status: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
