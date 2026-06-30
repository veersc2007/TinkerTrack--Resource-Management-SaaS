from sqlalchemy.orm import Session

from app.models.resource import Resource
from app.models.reservation import Reservation


def find_alternative_resources(
    db: Session,
    requested_resource_id: int,
    start_time,
    end_time,
):
    """
    Returns resources that are free during the requested interval.
    """

    resources = db.query(Resource).all()

    available = []

    for resource in resources:

        if resource.id == requested_resource_id:
            continue

        conflict = (
            db.query(Reservation)
            .filter(
                Reservation.resource_id == resource.id,
                Reservation.status == "Active",
                Reservation.start_time < end_time,
                Reservation.end_time > start_time,
            )
            .first()
        )

        if not conflict:
            available.append(resource)

    return available


def next_available_slot(db: Session, resource_id: int):

    latest = (
        db.query(Reservation)
        .filter(
            Reservation.resource_id == resource_id,
            Reservation.status == "Active",
        )
        .order_by(Reservation.end_time.desc())
        .first()
    )

    if latest:
        return latest.end_time

    return None

