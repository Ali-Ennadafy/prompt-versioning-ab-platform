
from pydantic import BaseModel, ConfigDict, field_validator
from typing import List, Optional
from datetime import datetime

from . import services


# Create a new prompt version
class PromptVersionCreate(BaseModel):

    prompt_text: str
    author: str
    commit_message: str

    @field_validator("prompt_text")
    @classmethod
    def validate_prompt(cls, value):

        if not services.validate_variables(value):
            raise ValueError(
                "Invalid dynamic variable syntax."
            )

        return value


# Prompt version response
class PromptVersionResponse(BaseModel):

    id: int
    template_id: int
    version_number: int
    prompt_text: str
    variables: List[str] = []
    author: str
    commit_message: str
    is_locked: bool
    is_production: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("variables", mode="before")
    @classmethod
    def parse_variables(cls, value):

        if isinstance(value, str):
            return [
                item for item in value.split(",") if item
            ]

        return value or []


# Create prompt template
class PromptTemplateCreate(BaseModel):

    name: str
    description: Optional[str] = None
    initial_prompt_text: str
    author: str
    commit_message: str

    @field_validator("initial_prompt_text")
    @classmethod
    def validate_prompt(cls, value):

        if not services.validate_variables(value):
            raise ValueError(
                "Invalid dynamic variable syntax."
            )

        return value


# Prompt template response
class PromptTemplateResponse(BaseModel):

    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    versions: List[PromptVersionResponse] = []

    model_config = ConfigDict(from_attributes=True)


# Diff response
class DiffResponse(BaseModel):

    template_id: int
    version_a: int
    version_b: int
    diff_text: str
