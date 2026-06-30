from datetime import datetime
from pydantic import BaseModel, ConfigDict


class WaitlistCreate(BaseModel):
    resource_id: int
    start_time: datetime
    end_time: datetime


class WaitlistResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    resource_id: int
    start_time: datetime
    end_time: datetime
    status: str
