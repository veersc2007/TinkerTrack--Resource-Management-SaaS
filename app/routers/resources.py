from fastapi import APIRouter, Depends, HTTPException, status , Body, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc,desc
from app.database import get_db
from app.models.resource import Resource
from app.models.user import User

from app.schemas.resource import (
    ResourceCreate,
    ResourceUpdate,
    ResourceResponse,
)

from app.auth.dependencies import get_current_user
from app.auth.permissions import require_admin

router = APIRouter(
    prefix="/resources",
    tags=["📦 Resources"]
)

# --------------------------------------------------------
# CREATE RESOURCE (Admin Only)
# --------------------------------------------------------
@router.post(
    "/",
    response_model=ResourceResponse,
    status_code=status.HTTP_201_CREATED
)
def create_resource(
    resource: ResourceCreate = Body(
        ...,
        example={
            "name": "Projector A",
            "description": "4K projector for lecture halls",
            "location": "Room 204"
        }
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    require_admin(current_user)

    new_resource = Resource(
        name=resource.name,
        description=resource.description,
        location=resource.location,
        status="Available"
    )

    db.add(new_resource)
    db.commit()
    db.refresh(new_resource)

    return new_resource


# --------------------------------------------------------
# GET ALL RESOURCES
# --------------------------------------------------------
@router.get("/", response_model=list[ResourceResponse])
def get_resources(
    search: str | None = Query(None),
    category: str | None = Query(None),
    available: bool | None = Query(None),
    sort: str = Query("id"),
    order: str = Query("asc"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Resource)

    # -----------------------------
    # Search by resource name
    # -----------------------------
    if search:
        query = query.filter(Resource.name.ilike(f"%{search}%"))

    # -----------------------------
    # Filter by category
    # -----------------------------
    if category:
        query = query.filter(Resource.category == category)

    # -----------------------------
    # Filter availability
    # -----------------------------
    if available is not None:
        query = query.filter(Resource.is_available == available)

    # -----------------------------
    # Sorting
    # -----------------------------
    allowed_columns = {
        "id": Resource.id,
        "name": Resource.name,
        "category": Resource.category,
    }

    sort_column = allowed_columns.get(sort, Resource.id)

    if order.lower() == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    # -----------------------------
    # Pagination
    # -----------------------------
    query = query.offset((page - 1) * size).limit(size)

    return query.all()
# --------------------------------------------------------
# GET RESOURCE BY ID
# --------------------------------------------------------
@router.get(
    "/{resource_id}",
    response_model=ResourceResponse
)
def get_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    resource = db.query(Resource).filter(
        Resource.id == resource_id
    ).first()

    if resource is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )

    return resource


# --------------------------------------------------------
# UPDATE RESOURCE (Admin Only)
# --------------------------------------------------------
@router.put(
    "/{resource_id}",
    response_model=ResourceResponse
)
def update_resource(
    resource_id: int,
    updated: ResourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    require_admin(current_user)

    resource = db.query(Resource).filter(
        Resource.id == resource_id
    ).first()

    if resource is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )

    if updated.name is not None:
        resource.name = updated.name

    if updated.description is not None:
        resource.description = updated.description

    if updated.location is not None:
        resource.location = updated.location

    if updated.status is not None:
        resource.status = updated.status

    db.commit()
    db.refresh(resource)

    return resource


# --------------------------------------------------------
# DELETE RESOURCE (Admin Only)
# --------------------------------------------------------
@router.delete("/{resource_id}")
def delete_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    require_admin(current_user)

    resource = db.query(Resource).filter(
        Resource.id == resource_id
    ).first()

    if resource is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )

    db.delete(resource)
    db.commit()

    return {
        "message": "Resource deleted successfully"
    }
