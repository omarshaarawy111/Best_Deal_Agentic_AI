"""
FastAPI application entry point for the Best Deal project.

Description:
    This module creates the application, configures static assets, initializes
    the database schema, and registers the application routers.
"""

from fastapi import FastAPI
from .models import Base
from starlette import status
from .routers import auth, deals, admin, users
from .database import engine


app = FastAPI()
# app.mount("/static", StaticFiles(directory="static"), name="static")

"""
Create the database tables based on the defined models
"""
Base.metadata.create_all(bind=engine)

@app.get("/healthy", status_code=status.HTTP_200_OK)
def health_check():
    """
    Report the availability of the application.

    Returns:
        A health status response.
    """
    return {'Status': 'Healthy'}

app.include_router(auth.router)
# app.include_router(deals.router)
# app.include_router(admin.router)
# app.include_router(users.router)