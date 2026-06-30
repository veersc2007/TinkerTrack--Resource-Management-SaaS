from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.schemas.reservation import ReservationFilter
from app.database import get_db
from app.models.user import User
from app.models.resource import Resource
from app.models.reservation import Reservation
from app.services.scheduling import (
    find_alternative_resources,
    next_available_slot
)
from typing import Optional
from datetime import datetime
from app.core.booking_rules import ROLE_BOOKING_LIMITS
from app.schemas.reservation import (
    ReservationCreate,
    ReservationUpdate,
    ReservationResponse
)

from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/reservations",
    tags=["📅 Reservations"]
)
from app.services.notification_service import create_notification

# ---------------------------------------------------
# CREATE RESERVATION
# ---------------------------------------------------
@router.post(
    "/",
    response_model=ReservationResponse,
    responses={
        200: {
            "description": "Reservation created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "user_id": 2,
                        "resource_id": 1,
                        "start_time": "2026-01-10T10:00:00",
                        "end_time": "2026-01-10T12:00:00",
                        "status": "ACTIVE"
                    }
                }
            }
        },
        409: {
            "description": "Time conflict",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Resource already reserved during this time."
                    }
                }
            }
        }
    }
)
def create_reservation(
    reservation: ReservationCreate = Body(
        ...,
        example={
            "resource_id": 1,
            "start_time": "2026-01-10T10:00:00",
            "end_time": "2026-01-10T12:00:00"
        }
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    create_notification(
    db,
    current_user.id,
    "Reservation Created",
    "Your reservation has been successfully created."
    )
    if reservation.end_time <= reservation.start_time:
        raise HTTPException(status_code=400, detail="Invalid time range")

    # Check resource
    resource = db.query(Resource).filter(
        Resource.id == reservation.resource_id
    ).first()

    if resource is None:
        raise HTTPException(
            status_code=404,
            detail="Resource not found"
        )

# ---------------------------------------------------
# BOOKING QUOTA CHECK
# ---------------------------------------------------
    limit = ROLE_BOOKING_LIMITS.get(current_user.role.lower())

    if limit is not None:

        active_bookings = db.query(Reservation).filter(
            Reservation.user_id == current_user.id,
            Reservation.status.in_(["APPROVED", "PENDING"])
        ).count()

        if active_bookings >= limit:
            raise HTTPException(
                status_code=403,
                detail=f"Booking quota exceeded. Maximum allowed: {limit} active reservations."
            )

# ---------------------------------------------------
# CONFLICT DETECTION
# ---------------------------------------------------
    conflict = db.query(Reservation).filter(
        Reservation.resource_id == reservation.resource_id,
        Reservation.status.in_(["APPROVED", "PENDING"]),
        Reservation.start_time < reservation.end_time,
        Reservation.end_time > reservation.start_time
    ).first()
    
    if conflict:

        alternatives = find_alternative_resources(
            db=db,
            requested_resource_id=reservation.resource_id,
            start_time=reservation.start_time,
            end_time=reservation.end_time,
    )

    next_slot = next_available_slot(
        db=db,
        resource_id=reservation.resource_id,
    )

    return {
        "message": "Requested slot is unavailable.",

        "requested_resource": reservation.resource_id,

        "next_available_slot": next_slot,

        "alternative_resources": [
            {
                "id": resource.id,
                "name": resource.name,
            }
            for resource in alternatives
        ]
    }

    status = (
        "PENDING"
        if resource.approval_required
        else "APPROVED"
    )

    new_reservation = Reservation(
        user_id=current_user.id,
        resource_id=reservation.resource_id,
        start_time=reservation.start_time,
        end_time=reservation.end_time,
        status=status
    )

    db.add(new_reservation)
    db.commit()
    db.refresh(new_reservation)
    if resource.approval_required:

        admins = db.query(User).filter(
            User.role == "admin"
        ).all()

        for admin in admins:
            create_notification(
                db=db,
                user_id=admin.id,
                title="Approval Required",
                message=(
                    f"Reservation #{new_reservation.id} "
                    f"for '{resource.name}' requires approval."
                )
            )
    return new_reservation


# ---------------------------------------------------
# GET ALL (ADMIN ONLY)
# ---------------------------------------------------
@router.get("/", response_model=list[ReservationResponse])
def get_reservations(
    user_id: int | None = None,
    resource_id: int | None = None,
    status: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    query = db.query(Reservation)

    # 🔐 USER ACCESS CONTROL
    if current_user.role != "admin":
        query = query.filter(Reservation.user_id == current_user.id)

    # 🔍 FILTERS

    if user_id and current_user.role == "admin":
        query = query.filter(Reservation.user_id == user_id)

    if resource_id:
        query = query.filter(Reservation.resource_id == resource_id)

    if status:
        query = query.filter(Reservation.status == status)

    if start_date:
        query = query.filter(Reservation.start_time >= start_date)

    if end_date:
        query = query.filter(Reservation.end_time <= end_date)

    return query.all()
# ---------------------------------------------------
# GET SINGLE
# ---------------------------------------------------
@router.get("/{reservation_id}", response_model=ReservationResponse)
def get_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()

    if not reservation:
        raise HTTPException(status_code=404, detail="Not found")

    if current_user.id != reservation.user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    return reservation


# ---------------------------------------------------
# UPDATE RESERVATION
# ---------------------------------------------------
@router.put("/{reservation_id}", response_model=ReservationResponse)
def update_reservation(
    reservation_id: int,
    updated: ReservationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()

    if not reservation:
        raise HTTPException(status_code=404, detail="Not found")

    if current_user.id != reservation.user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    new_start = updated.start_time or reservation.start_time
    new_end = updated.end_time or reservation.end_time

    if new_end <= new_start:
        raise HTTPException(status_code=400, detail="Invalid time range")

    conflict = db.query(Reservation).filter(
        Reservation.id != reservation.id,
        Reservation.resource_id == reservation.resource_id,
        Reservation.status.in_(["ACTIVE", "APPROVED"]),
        Reservation.start_time < new_end,
        Reservation.end_time > new_start
    ).first()

    if conflict:

        alternatives = find_alternative_resources(
            db=db,
            requested_resource_id=reservation.resource_id,
            start_time=new_start,
            end_time=new_end,
    )

    next_slot = next_available_slot(
        db=db,
        resource_id=reservation.resource_id,
    )

    return {
        "message": "Updated reservation conflicts with an existing booking.",

        "next_available_slot": next_slot,

        "alternative_resources": [
            {
                "id": resource.id,
                "name": resource.name,
            }
            for resource in alternatives
        ]
    }
    reservation.start_time = new_start
    reservation.end_time = new_end

    db.commit()
    db.refresh(reservation)

    return reservation


# ---------------------------------------------------
# CANCEL RESERVATION
# ---------------------------------------------------
@router.delete("/{reservation_id}")
def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    create_notification(
    db,
    reservation.user_id,
    "Reservation Cancelled",
    "Your reservation has been cancelled."
    )
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    
    if not reservation:
        raise HTTPException(status_code=404, detail="Not found")

    if current_user.id != reservation.user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    reservation.status = "CANCELLED"
    db.commit()

    return {"message": "Cancelled"}


# ===================================================
# HISTORY + FILTERS + PAGINATION
# ===================================================

@router.get("/history/me")
def my_history(
    status: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    page: int = 1,
    size: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    query = db.query(Reservation).filter(
        Reservation.user_id == current_user.id
    )

    if status:
        query = query.filter(Reservation.status == status)

    if start_date:
        query = query.filter(Reservation.start_time >= start_date)

    if end_date:
        query = query.filter(Reservation.end_time <= end_date)

    total = query.count()

    data = query.order_by(Reservation.start_time.desc()) \
                .offset((page - 1) * size) \
                .limit(size) \
                .all()

    return {"total": total, "page": page, "size": size, "data": data}


@router.get("/history")
def admin_history(
    user_id: int | None = None,
    resource_id: int | None = None,
    status: str | None = None,
    page: int = 1,
    size: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    query = db.query(Reservation)

    if user_id:
        query = query.filter(Reservation.user_id == user_id)

    if resource_id:
        query = query.filter(Reservation.resource_id == resource_id)

    if status:
        query = query.filter(Reservation.status == status)

    total = query.count()

    data = query.order_by(Reservation.start_time.desc()) \
                .offset((page - 1) * size) \
                .limit(size) \
                .all()

    return {"total": total, "page": page, "size": size, "data": data}


@router.get("/resource/{resource_id}/history")
def resource_history(
    resource_id: int,
    status: str | None = None,
    page: int = 1,
    size: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    resource = db.query(Resource).filter(Resource.id == resource_id).first()

    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    query = db.query(Reservation).filter(
        Reservation.resource_id == resource_id
    )

    if status:
        query = query.filter(Reservation.status == status)

    total = query.count()

    data = query.order_by(Reservation.start_time.desc()) \
                .offset((page - 1) * size) \
                .limit(size) \
                .all()

    return {"total": total, "page": page, "size": size, "data": data}


# ---------------------------------------------------
# ADMIN LIFECYCLE CONTROL
# ---------------------------------------------------
@router.put("/{reservation_id}/approve")
def approve_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    reservation.status = "APPROVED"

    db.commit()
    return reservation


@router.put("/{reservation_id}/reject")
def reject_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    reservation.status = "REJECTED"

    db.commit()
    return reservation

@router.get("/history/me")
def my_booking_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return db.query(Reservation).filter(
        Reservation.user_id == current_user.id
    ).order_by(Reservation.start_time.desc()).all()


@router.get("/history/all")
def all_booking_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    return db.query(Reservation).order_by(
        Reservation.start_time.desc()
    ).all()

@router.get("/history/filter")
def filter_booking_history(
    resource_id: Optional[int] = None,
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    query = db.query(Reservation)

    # Non-admin users can only see their own history
    if current_user.role != "admin":
        query = query.filter(Reservation.user_id == current_user.id)

    # Admin can filter by user_id
    if user_id and current_user.role == "admin":
        query = query.filter(Reservation.user_id == user_id)

    if resource_id:
        query = query.filter(Reservation.resource_id == resource_id)

    if status:
        query = query.filter(Reservation.status == status)

    if start_date:
        query = query.filter(Reservation.start_time >= start_date)

    if end_date:
        query = query.filter(Reservation.end_time <= end_date)

    return query.order_by(Reservation.start_time.desc()).all()

@router.get("/pending")
def get_pending_reservations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin only"
        )

    return db.query(Reservation).filter(
        Reservation.status == "PENDING"
    ).all()

@router.put("/{reservation_id}/approve")
def approve_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin only"
        )

    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id
    ).first()

    if not reservation:
        raise HTTPException(
            status_code=404,
            detail="Reservation not found"
        )

    reservation.status = "APPROVED"

    db.commit()

    create_notification(
        db,
        reservation.user_id,
        "Reservation Approved",
        "Your reservation has been approved."
    )

    return reservation

@router.put("/{reservation_id}/reject")
def reject_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin only"
        )

    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id
    ).first()

    if not reservation:
        raise HTTPException(
            status_code=404,
            detail="Reservation not found"
        )

    reservation.status = "REJECTED"

    db.commit()

    create_notification(
        db,
        reservation.user_id,
        "Reservation Rejected",
        "Your reservation request was rejected."
    )

    return reservation

@router.get("/pending", response_model=list[ReservationResponse])
def get_pending_reservations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admins only."
        )

    return db.query(Reservation).filter(
        Reservation.status == "PENDING"
    ).all()

@router.put(
    "/{reservation_id}/approve",
    summary="Approve a pending reservation",
    description="Allows administrators to approve reservations requiring approval."
)
def approve_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admins only."
        )

    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id
    ).first()

    if reservation is None:
        raise HTTPException(
            status_code=404,
            detail="Reservation not found."
        )

    reservation.status = "APPROVED"

    db.commit()
    db.refresh(reservation)

    create_notification(
        db=db,
        user_id=reservation.user_id,
        title="Reservation Approved",
        message=f"Your reservation #{reservation.id} has been approved."
    )

    return reservation

@router.put(
    "/{reservation_id}/approve",
    summary="Reject a pending reservation",
    description="Allows administrators to reject reservations requiring approval."
)
def reject_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admins only."
        )

    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id
    ).first()

    if reservation is None:
        raise HTTPException(
            status_code=404,
            detail="Reservation not found."
        )

    reservation.status = "REJECTED"

    db.commit()
    db.refresh(reservation)

    create_notification(
        db=db,
        user_id=reservation.user_id,
        title="Reservation Rejected",
        message=f"Your reservation #{reservation.id} has been rejected."
    )

    return reservation

