from pydantic import BaseModel, ConfigDict


class ResourceCreate(BaseModel):
    name: str
    description: str
    location: str
    approval_required: bool = False

class ResourceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    location: str | None = None
    status: str | None = None
    approval_required: bool
    

class ResourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    location: str
    status: str
