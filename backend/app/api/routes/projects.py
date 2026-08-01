from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from ...db.database import get_db
from ...models.project import Project
from ...models.user import User
from ...schemas.project import ProjectCreate, ProjectOut
from ...utils.auth import get_current_user, require_roles

router = APIRouter()


@router.post("", response_model=ProjectOut)
def create_project(project: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_project = Project(project_name=project.project_name, description=project.description, created_by=current_user.id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.get("", response_model=list[ProjectOut])
def get_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Project).filter(Project.created_by == current_user.id).all()


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, project: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    if db_project.created_by != current_user.id and current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db_project.project_name = project.project_name
    db_project.description = project.description
    db.commit()
    db.refresh(db_project)
    return db_project


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    if db_project.created_by != current_user.id and current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db.delete(db_project)
    db.commit()
    return {"message": "Project deleted"}
