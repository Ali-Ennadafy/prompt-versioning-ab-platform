from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from . import models, schemas, services
from .database import engine, get_db


# Create database tables
models.Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Prompt Versioning & A/B Testing API",
    description="Prompt management and versioning platform",
    version="1.0.0"
)


# Create a new prompt template with Version 1
@app.post(
    "/templates/",
    response_model=schemas.PromptTemplateResponse,
    status_code=status.HTTP_201_CREATED
)
def create_template(
    template_in: schemas.PromptTemplateCreate,
    db: Session = Depends(get_db)
):

    existing = db.query(models.PromptTemplate).filter(
        models.PromptTemplate.name == template_in.name
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="A template with this name already exists."
        )

    variables = services.extract_variables(
        template_in.initial_prompt_text
    )

    new_template = models.PromptTemplate(
        name=template_in.name,
        description=template_in.description
    )

    first_version = models.PromptVersion(
        version_number=1,
        prompt_text=template_in.initial_prompt_text,
        variables=",".join(variables),
        author=template_in.author,
        commit_message=template_in.commit_message,
        is_production=True
    )

    new_template.versions.append(first_version)

    try:
        db.add(new_template)
        db.commit()
        db.refresh(new_template)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Template already exists."
        )

    return new_template


# List all templates
@app.get(
    "/templates/",
    response_model=List[schemas.PromptTemplateResponse]
)
def list_templates(db: Session = Depends(get_db)):

    return db.query(models.PromptTemplate).all()


# Get one template
@app.get(
    "/templates/{template_id}",
    response_model=schemas.PromptTemplateResponse
)
def get_template(
    template_id: int,
    db: Session = Depends(get_db)
):

    template = db.query(models.PromptTemplate).filter(
        models.PromptTemplate.id == template_id
    ).first()

    if not template:
        raise HTTPException(
            status_code=404,
            detail="Template not found."
        )

    return template


# Create a new version
@app.post(
    "/templates/{template_id}/versions/",
    response_model=schemas.PromptVersionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_new_version(
    template_id: int,
    version_in: schemas.PromptVersionCreate,
    db: Session = Depends(get_db)
):

    template = db.query(models.PromptTemplate).filter(
        models.PromptTemplate.id == template_id
    ).first()

    if not template:
        raise HTTPException(
            status_code=404,
            detail="Template not found."
        )

    last_version = db.query(models.PromptVersion).filter(
        models.PromptVersion.template_id == template_id
    ).order_by(
        models.PromptVersion.version_number.desc()
    ).first()

    next_version = (
        last_version.version_number + 1
        if last_version else 1
    )

    variables = services.extract_variables(
        version_in.prompt_text
    )

    new_version = models.PromptVersion(
        template_id=template_id,
        version_number=next_version,
        prompt_text=version_in.prompt_text,
        variables=",".join(variables),
        author=version_in.author,
        commit_message=version_in.commit_message
    )

    try:
        db.add(new_version)
        db.commit()
        db.refresh(new_version)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Version conflict. Please retry."
        )

    return new_version


# Get version history
@app.get(
    "/templates/{template_id}/versions/",
    response_model=List[schemas.PromptVersionResponse]
)
def get_version_history(
    template_id: int,
    db: Session = Depends(get_db)
):

    template = db.query(models.PromptTemplate).filter(
        models.PromptTemplate.id == template_id
    ).first()

    if not template:
        raise HTTPException(
            status_code=404,
            detail="Template not found."
        )

    return db.query(models.PromptVersion).filter(
        models.PromptVersion.template_id == template_id
    ).order_by(
        models.PromptVersion.version_number.asc()
    ).all()


# Compare two versions
@app.get(
    "/templates/{template_id}/diff",
    response_model=schemas.DiffResponse
)
def get_version_diff(
    template_id: int,
    v1: int,
    v2: int,
    db: Session = Depends(get_db)
):

    versions = db.query(models.PromptVersion).filter(
        models.PromptVersion.template_id == template_id,
        models.PromptVersion.version_number.in_([v1, v2])
    ).all()

    version_map = {
        version.version_number: version
        for version in versions
    }

    if v1 not in version_map or v2 not in version_map:
        raise HTTPException(
            status_code=404,
            detail="One or both versions were not found."
        )

    diff_result = services.compute_text_diff(
        version_map[v1].prompt_text,
        version_map[v2].prompt_text
    )

    return {
        "template_id": template_id,
        "version_a": v1,
        "version_b": v2,
        "diff_text": diff_result
    }


@app.get("/")
def root():

    return {
        "message": "Prompt Versioning API is running."
    }
