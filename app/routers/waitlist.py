from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import get_db

from app.models.waitlist import Waitlist
from app.models.reservation import Reservation
from app.models.user import User

from app.schemas.waitlist import WaitlistCreate, WaitlistResponse

from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/waitlist",
    tags=["⏳ Waitlist"]
)

# ---------------------------------------------------
# ADD TO WAITLIST (ONLY IF CONFLICT EXISTS)
# ---------------------------------------------------
@router.post("/")
def add_to_waitlist(
    request: WaitlistCreate = Body(
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
    # check if resource is actually busy
    conflict = db.query(Reservation).filter(
        Reservation.resource_id == request.resource_id,
        Reservation.status == "ACTIVE",
        Reservation.start_time < request.end_time,
        Reservation.end_time > request.start_time
    ).first()

    if not conflict:
        raise HTTPException(
            status_code=400,
            detail="Resource is available, no need for waitlist"
        )

    entry = Waitlist(
        user_id=current_user.id,
        resource_id=request.resource_id,
        start_time=request.start_time,
        end_time=request.end_time,
        status="WAITING"
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)

    return entry


# ---------------------------------------------------
# VIEW MY WAITLIST
# ---------------------------------------------------
@router.get("/me", response_model=list[WaitlistResponse])
def my_waitlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return db.query(Waitlist).filter(
        Waitlist.user_id == current_user.id
    ).all()


# ---------------------------------------------------
# ADMIN: VIEW ALL WAITLIST ENTRIES
# ---------------------------------------------------
@router.get("/", response_model=list[WaitlistResponse])
def all_waitlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    return db.query(Waitlist).all()


# ---------------------------------------------------
# CANCEL WAITLIST ENTRY
# ---------------------------------------------------
@router.delete("/{waitlist_id}")
def cancel_waitlist(
    waitlist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    entry = db.query(Waitlist).filter(Waitlist.id == waitlist_id).first()

    if not entry:
        raise HTTPException(status_code=404, detail="Not found")

    if current_user.id != entry.user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    entry.status = "CANCELLED"

    db.commit()

    return {"message": "Removed from waitlist"}


# ---------------------------------------------------
# ADMIN: PROMOTE NEXT USER (MANUAL TRIGGER)
# ---------------------------------------------------
@router.post("/promote/{resource_id}")
def promote_next_user(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    create_notification(
    db,
    next_user.user_id,
    "Slot Available",
    "A slot opened up. You have been moved from waitlist."
    )
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    next_user = db.query(Waitlist).filter(
        Waitlist.resource_id == resource_id,
        Waitlist.status == "WAITING"
    ).order_by(Waitlist.created_at.asc()).first()

    if not next_user:
        return {"message": "No users in waitlist"}

    next_user.status = "NOTIFIED"
    db.commit()

    return {
        "message": "User notified",
        "user_id": next_user.user_id
    }
