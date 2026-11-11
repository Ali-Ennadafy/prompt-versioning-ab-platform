from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint
)

from sqlalchemy.orm import relationship

from .database import Base


class PromptTemplate(Base):

    __tablename__ = "prompt_templates"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(100),
        unique=True,
        index=True,
        nullable=False
    )

    description = Column(Text, nullable=True)
    
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


    versions = relationship(
        "PromptVersion",
        back_populates="template",
        cascade="all, delete-orphan"
    )


class PromptVersion(Base):

    __tablename__ = "prompt_versions"

    id = Column(Integer, primary_key=True, index=True)

    template_id = Column(
        Integer,
        ForeignKey("prompt_templates.id"),
        nullable=False
    )

    version_number = Column(Integer, nullable=False)

    prompt_text = Column(Text, nullable=False)

    variables = Column(Text, nullable=True)

    author = Column(String(100), nullable=False)

    commit_message = Column(Text, nullable=False)

    is_locked = Column(Boolean, default=False, nullable=False)

    is_production = Column(Boolean, default=False, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    template = relationship(
        "PromptTemplate",
        back_populates="versions"
    )

    __table_args__ = (
        UniqueConstraint(
            "template_id",
            "version_number",
            name="uq_template_version"
        ),
    )
