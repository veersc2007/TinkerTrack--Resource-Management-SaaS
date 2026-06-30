from fastapi import FastAPI
from app.database import Base, engine
from app.routers import (
    auth,
    users,
    resources,
    reservations,
    waitlist,
    dashboard,
    notifications
)
app = FastAPI(
    title="🏢 TinkerTrack",
    description="""
    <h2>Smart Shared Resource Management System</h2>

    <p>
    TinkerTrack is a modern backend system for managing shared resources like rooms, equipment, and facilities.
    It supports smart reservations, conflict detection, waitlists, notifications, and analytics.
    </p>

    <h3>🚀 Key Features</h3>

    <ul>
        <li>📅 Smart Reservation System with conflict detection</li>
        <li>⏳ Waitlist management with auto-promotion</li>
        <li>🔔 Real-time notification system</li>
        <li>📊 Analytics dashboard for resource usage</li>
        <li>🔐 Role-based access (Admin/User)</li>
    </ul>

    <h3>⚙️ How to Use</h3>
    <p>
    1. Register/Login via /auth<br>
    2. Click "Authorize" 🔓 (JWT token)<br>
    3. Start testing APIs below
    </p>
    """,
    version="1.0.0",
    contact={
        "name": "TinkerTrack System",
        "email": "support@tinkertrack.com"
    },
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters={
        "docExpansion": "none",   # collapses endpoints (clean look)
        "defaultModelsExpandDepth": -1,  # hides schema clutter
        "displayRequestDuration": True,   # shows API speed
        "filter": True                    # enables search bar
    }
)

Base.metadata.create_all(bind=engine)

# Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(resources.router)
app.include_router(reservations.router)
app.include_router(waitlist.router)
app.include_router(dashboard.router)
app.include_router(notifications.router)

@app.get("/")
def root():
    return {
        "app": "🏢 TinkerTrack",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
        "message": "Smart Resource Booking System API"
    }
