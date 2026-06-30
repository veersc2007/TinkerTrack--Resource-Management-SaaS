from datetime import datetime
from pydantic import BaseModel

# -------------------------------
# Main Dashboard
# -------------------------------
class DashboardResponse(BaseModel):
    total_users: int
    admins: int
    students: int

    total_resources: int
    available_resources: int
    maintenance_resources: int
    reserved_resources: int

    total_reservations: int
    active_reservations: int
    completed_reservations: int
    cancelled_reservations: int


# -------------------------------
# Top Resources
# -------------------------------
class TopResource(BaseModel):
    resource_id: int
    resource_name: str
    reservation_count: int


# -------------------------------
# Most Active Users
# -------------------------------
class ActiveUser(BaseModel):
    user_id: int
    name: str
    reservations: int


# -------------------------------
# Reservation Details
# -------------------------------
class ReservationDetails(BaseModel):
    reservation_id: int

    user_name: str

    resource_name: str

    start_time: datetime

    end_time: datetime

    status: str
