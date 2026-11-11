import logging

from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.models.projects import Project as ProjectModel
from app.schemas.project import (
    Project,
    ProjectUpdate,
    ProjectCreate,
)
from app.schemas.error import ErrorResponse
from app.dependencies import require_roles
from app.models.users import User

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/projects",
    tags=["Projects"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]
AdminUser = Annotated[
    User,
    Depends(require_roles("admin"))]


# Public: List all projects
@router.get(
        "/",
        response_model=list[Project],
        summary="List all projects",
        description="Retrive all portfolio projects, ordered by their database ID.",
        response_description="A list of portfolio projects.",
        )
def get_projects(
    db: DatabaseSession
):
    statement = select(ProjectModel).order_by(ProjectModel.id)
    projects = db.scalars(statement).all()
    return projects


# Public: Retrive one Project
@router.get(
        "/{project_id}",
        response_model=Project,
        responses={404: {
            "model": ErrorResponse,
            "description": "Project not found.",
            },
        },
        summary="Retrive a project",
        description="Retrive a single portfolio project using its unique ID.",
        response_description="The requested project.",
    )
def get_project(
    project_id: int,
    db: DatabaseSession
):
    """for project in projects:
        if project.id == project_id:
            return project
    """
    project = db.get(ProjectModel, project_id)
#    return {"message": "Project not found."}

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project


"""
projects: list[Project] = [
        Project(
            id= 1,
            title= "Real-Time  Messaging Platform",
            description= "Real-Time chat application built with FastAI, and WebSockets.",
            technologies= ["Python", "FastAPI", "WebSockets", "PostgreSQL"],
        ),
        Project(
            id= 2,
            title= "Real-Time  Messaging Platform",
            description= "Real-Time chat application built with FastAI, and WebSockets.",
            technologies= ["Python", "FastAPI", "WebSockets", "PostgreSQL"],
        ),
        Project(
            id= 3,
            title= "Real-Time  Messaging Platform",
            description= "Real-Time chat application built with FastAI, and WebSockets.",
            technologies= ["Python", "FastAPI", "WebSockets", "PostgreSQL"],
        ),
        Project(
            id= 4,
            title= "Real-Time  Messaging Platform",
            description= "Real-Time chat application built with FastAI, and WebSockets.",
            technologies= ["Python", "FastAPI", "WebSockets", "PostgreSQL"],
        ),
        # On Day 2 step-5 we changed from normal dictionary to JSON response using schemas
        #{
        #"id": 6,
        #"Title": "Real-Time  Messaging Platform",
        #"description": "Real-Time chat application built with FastAI, and WebSockets.",
        #"Technologies": ["Python", "FastAPI", "WebSockets", "PostgreSQL"],
        #},

]
"""

# Admin Only: Create a project
@router.post(
        "/",
        response_model=Project,
        status_code=status.HTTP_201_CREATED,
        responses={
            401: {
                "model": ErrorResponse,
                "description": "Authentication required.",
            },
            403: {
                "model": ErrorResponse,
                "description": "Administrative priviledges required.",
            },
            500: {
                "model": ErrorResponse,
                "description": "Database operation failed.",
            },
        },
        summary="Create a project",
        description="Create a new portfolio project. Requires administrative priviledges.",
        response_description="The newly created project.",
)
def create_project(
    project_data: ProjectCreate,
    db: DatabaseSession,
    admin: AdminUser,
):
    project = ProjectModel(
        title=project_data.title,
        description=project_data.description,
        technologies=project_data.technologies,
    )

    try:
        db.add(project)
        db.commit()
        db.refresh(project)
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Failed to create project.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="unable to create project. Please try again.",
        ) from exc
    return(project)

# Admin only: Edit/Update projects updatable fields
@router.put(
        "/{project_id}",
        response_model=Project,
        responses={
            401: {
                "model": ErrorResponse,
                "description": "Authentication required.",
            },
            403: {
                "model": ErrorResponse,
                "description": "Administrative priviledges required.",
            },
            404: {
                "model": ErrorResponse,
                "description": "Project not found.",
            },
            500: {
                "model": ErrorResponse,
                "description": "Database operation failed.",
            },
        },
        summary="Update a project",
        description="Replace the editable fields of an existing project. Requires administrative priviledges.",
        response_description="The updated project.",
)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: DatabaseSession,
    admin: AdminUser,
):
    project = db.get(ProjectModel, project_id)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    try:
        project.title = project_data.title
        project.description = project_data.description
        project.technologies = project_data.technologies

        db.commit()
        db.refresh(project)

    except SQLAlchemyError as exc:
        db.rollback()

        logger.exception("Failed to update project with ID %s.",
        project_id)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update project. Please try again.",
        ) from exc

    return(project)

# Admin Only Delete the project
@router.delete(
        "/{project_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        responses={
                    401: {
                        "model": ErrorResponse,
                        "description": "Authentication required.",
                    },
                    403: {
                        "model": ErrorResponse,
                        "description": "Administrative priviledges required.",
                    },
                    404: {
                        "model": ErrorResponse,
                        "description": "Project not found.",
                    },
                    500: {
                        "model": ErrorResponse,
                        "description": "Database operation failed.",
                    },
                },
        summary="Update a project",
        description="Permanently delete an existing project. Requires administrative priviledges.",
        response_description="Project successfully deleted. No response body is returned.",
)
def delete_project(
    project_id: int,
    db: DatabaseSession,
    admin: AdminUser,
):
    project = db.get(ProjectModel, project_id)

    if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

    try:
        db.delete(project)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception(
            "Failed to delete project with ID $s.",
            project_id)
        raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Unable to delete project. Please try again.",
                ) from exc
    return None