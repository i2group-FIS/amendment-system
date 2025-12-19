from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from .database import Base


class AmendmentType(str, enum.Enum):
    BUG = "Bug"
    ENHANCEMENT = "Enhancement"
    FEATURE = "Feature"
    MAINTENANCE = "Maintenance"
    DOCUMENTATION = "Documentation"


class AmendmentStatus(str, enum.Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    TESTING = "Testing"
    COMPLETED = "Completed"
    DEPLOYED = "Deployed"


class DevelopmentStatus(str, enum.Enum):
    NOT_STARTED = "Not Started"
    IN_DEVELOPMENT = "In Development"
    CODE_REVIEW = "Code Review"
    READY_FOR_QA = "Ready for QA"


class Priority(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class Force(str, enum.Enum):
    ARMY = "Army"
    NAVY = "Navy"
    RAF = "RAF"
    ALL = "All"


class LinkType(str, enum.Enum):
    RELATED = "Related"
    DUPLICATE = "Duplicate"
    BLOCKS = "Blocks"
    BLOCKED_BY = "Blocked By"


class Amendment(Base):
    __tablename__ = "amendments"

    # Primary identification
    amendment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    amendment_reference = Column(String(50), unique=True, nullable=False, index=True)

    # Basic information
    amendment_type = Column(SQLEnum(AmendmentType), nullable=False)
    description = Column(Text, nullable=False)
    amendment_status = Column(
        SQLEnum(AmendmentStatus), nullable=False, default=AmendmentStatus.OPEN
    )
    development_status = Column(
        SQLEnum(DevelopmentStatus),
        nullable=False,
        default=DevelopmentStatus.NOT_STARTED,
    )
    priority = Column(SQLEnum(Priority), nullable=False, default=Priority.MEDIUM)
    force = Column(String(50), nullable=True)
    application = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

    # Assignment and reporting
    reported_by = Column(String(100), nullable=True)
    assigned_to = Column(String(100), nullable=True)
    date_reported = Column(DateTime, nullable=True)

    # Development fields
    database_changes = Column(Boolean, default=False)
    db_upgrade_changes = Column(Boolean, default=False)
    release_notes = Column(Text, nullable=True)

    # QA fields
    qa_assigned_id = Column(Integer, nullable=True)
    qa_assigned_date = Column(DateTime, nullable=True)
    qa_test_plan_check = Column(Boolean, default=False)
    qa_test_release_notes_check = Column(Boolean, default=False)
    qa_completed = Column(Boolean, default=False)
    qa_signature = Column(String(100), nullable=True)
    qa_completed_date = Column(DateTime, nullable=True)
    qa_notes = Column(Text, nullable=True)
    qa_test_plan_link = Column(String(500), nullable=True)

    # Audit fields
    created_by = Column(String(100), nullable=True)
    created_on = Column(DateTime, default=func.now(), nullable=False)
    modified_by = Column(String(100), nullable=True)
    modified_on = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    progress_entries = relationship(
        "AmendmentProgress", back_populates="amendment", cascade="all, delete-orphan"
    )
    applications = relationship(
        "AmendmentApplication", back_populates="amendment", cascade="all, delete-orphan"
    )
    links = relationship(
        "AmendmentLink",
        foreign_keys="AmendmentLink.amendment_id",
        back_populates="amendment",
        cascade="all, delete-orphan",
    )


class AmendmentProgress(Base):
    __tablename__ = "amendment_progress"

    amendment_progress_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    amendment_id = Column(Integer, ForeignKey("amendments.amendment_id"), nullable=False)

    start_date = Column(DateTime, nullable=True)
    description = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)

    # Audit fields
    created_by = Column(String(100), nullable=True)
    created_on = Column(DateTime, default=func.now(), nullable=False)
    modified_by = Column(String(100), nullable=True)
    modified_on = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship
    amendment = relationship("Amendment", back_populates="progress_entries")


class AmendmentApplication(Base):
    __tablename__ = "amendment_applications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    amendment_id = Column(Integer, ForeignKey("amendments.amendment_id"), nullable=False)
    application_name = Column(String(100), nullable=False)
    version = Column(String(50), nullable=True)

    # Relationship
    amendment = relationship("Amendment", back_populates="applications")


class AmendmentLink(Base):
    __tablename__ = "amendment_links"

    amendment_link_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    amendment_id = Column(Integer, ForeignKey("amendments.amendment_id"), nullable=False)
    linked_amendment_id = Column(Integer, nullable=False)
    link_type = Column(SQLEnum(LinkType), nullable=False, default=LinkType.RELATED)

    # Relationship
    amendment = relationship(
        "Amendment", foreign_keys=[amendment_id], back_populates="links"
    )
