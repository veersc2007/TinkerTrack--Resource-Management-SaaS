from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.user import User
from app.models.resource import Resource
from app.models.reservation import Reservation
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/dashboard",
    tags=["📊 Analytics"]
)

# ---------------------------------------------------
# ADMIN CHECK HELPER
# ---------------------------------------------------
def admin_only(current_user: User):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")


# ---------------------------------------------------
# 1. SUMMARY DASHBOARD
# ---------------------------------------------------
@router.get(
    "/summary",
    responses={
        200: {
            "description": "System analytics summary",
            "example": {
                "total_users": 120,
                "total_resources": 25,
                "total_reservations": 340,
                "active_reservations": 40,
                "cancelled_reservations": 15
            }
        }
    }
)
def summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    admin_only(current_user)

    return {
        "total_users": db.query(User).count(),
        "total_resources": db.query(Resource).count(),
        "total_reservations": db.query(Reservation).count(),
        "active_reservations": db.query(Reservation)
            .filter(Reservation.status == "ACTIVE").count(),
        "cancelled_reservations": db.query(Reservation)
            .filter(Reservation.status == "CANCELLED").count(),
    }


# ---------------------------------------------------
# 2. TOP RESOURCES
# ---------------------------------------------------
@router.get("/top-resources")
def top_resources(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    admin_only(current_user)

    result = db.query(
        Resource.id,
        Resource.name,
        func.count(Reservation.id).label("booking_count")
    ).join(Reservation, Reservation.resource_id == Resource.id) \
     .group_by(Resource.id) \
     .order_by(func.count(Reservation.id).desc()) \
     .limit(5).all()

    return [
        {
            "resource_id": r.id,
            "resource_name": r.name,
            "bookings": r.booking_count
        }
        for r in result
    ]


# ---------------------------------------------------
# 3. TOP USERS
# ---------------------------------------------------
@router.get("/top-users")
def top_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    admin_only(current_user)

    result = db.query(
        User.id,
        User.name,
        func.count(Reservation.id).label("booking_count")
    ).join(Reservation, Reservation.user_id == User.id) \
     .group_by(User.id) \
     .order_by(func.count(Reservation.id).desc()) \
     .limit(5).all()

    return [
        {
            "user_id": u.id,
            "user_name": u.name,
            "bookings": u.booking_count
        }
        for u in result
    ]


# ---------------------------------------------------
# 4. RESOURCE UTILIZATION
# ---------------------------------------------------
@router.get("/utilization")
def utilization(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    admin_only(current_user)

    resources = db.query(Resource).all()

    output = []

    for r in resources:
        total = db.query(Reservation).filter(
            Reservation.resource_id == r.id
        ).count()

        output.append({
            "resource_id": r.id,
            "resource_name": r.name,
            "total_bookings": total
        })

    return output


# ---------------------------------------------------
# 5. PEAK HOURS ANALYTICS
# ---------------------------------------------------
@router.get("/peak-hours")
def peak_hours(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    admin_only(current_user)

    results = db.query(
        func.strftime("%H", Reservation.start_time).label("hour"),
        func.count(Reservation.id)
    ).group_by("hour").all()

    return [
        {
            "hour": r[0],
            "bookings": r[1]
        }
        for r in results
    ]


# ---------------------------------------------------
# 6. CANCELLATION RATE
# ---------------------------------------------------
@router.get("/cancellation-rate")
def cancellation_rate(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    admin_only(current_user)

    total = db.query(Reservation).count()
    cancelled = db.query(Reservation).filter(
        Reservation.status == "CANCELLED"
    ).count()

    return {
        "total_reservations": total,
        "cancelled": cancelled,
        "cancellation_rate": round((cancelled / total) * 100, 2) if total else 0
    }

@router.get("/booking-trends")
def booking_trends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "admin":
        return {"detail": "Only admins can access analytics"}

    results = (
        db.query(
            func.date(Reservation.start_time).label("date"),
            func.count(Reservation.id)
        )
        .group_by(func.date(Reservation.start_time))
        .order_by(func.date(Reservation.start_time))
        .all()
    )

    return [
        {"date": str(r.date), "bookings": r[1]}
        for r in results
    ]

@router.get("/user-activity")
def user_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "admin":
        return {"detail": "Only admins can access analytics"}

    results = (
        db.query(
            User.id,
            User.name,
            func.count(Reservation.id).label("total")
        )
        .join(Reservation, Reservation.user_id == User.id)
        .group_by(User.id)
        .order_by(func.count(Reservation.id).desc())
        .all()
    )

    return [
        {"user_id": r.id, "name": r.name, "bookings": r.total}
        for r in results
    ]

