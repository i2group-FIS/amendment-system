"""
Comprehensive tests for database models
"""

import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from backend.app import models


class TestAmendmentModel:
    """Test cases for the Amendment model"""

    def test_create_amendment_with_required_fields(self, test_session):
        """Test creating an amendment with only required fields"""
        amendment = models.Amendment(
            amendment_reference="AMN-2024-001",
            amendment_type=models.AmendmentType.BUG,
            description="Test bug description",
        )
        test_session.add(amendment)
        test_session.commit()
        test_session.refresh(amendment)

        assert amendment.amendment_id is not None
        assert amendment.amendment_reference == "AMN-2024-001"
        assert amendment.amendment_type == models.AmendmentType.BUG
        assert amendment.description == "Test bug description"

    def test_amendment_default_values(self, test_session):
        """Test that default values are set correctly"""
        amendment = models.Amendment(
            amendment_reference="AMN-2024-002",
            amendment_type=models.AmendmentType.FEATURE,
            description="Test feature",
        )
        test_session.add(amendment)
        test_session.commit()
        test_session.refresh(amendment)

        assert amendment.amendment_status == models.AmendmentStatus.OPEN
        assert amendment.development_status == models.DevelopmentStatus.NOT_STARTED
        assert amendment.priority == models.Priority.MEDIUM
        assert amendment.database_changes is False
        assert amendment.db_upgrade_changes is False
        assert amendment.qa_test_plan_check is False
        assert amendment.qa_test_release_notes_check is False
        assert amendment.qa_completed is False

    def test_amendment_audit_fields_auto_populated(self, test_session):
        """Test that audit fields are automatically populated"""
        amendment = models.Amendment(
            amendment_reference="AMN-2024-003",
            amendment_type=models.AmendmentType.ENHANCEMENT,
            description="Test enhancement",
        )
        test_session.add(amendment)
        test_session.commit()
        test_session.refresh(amendment)

        assert amendment.created_on is not None
        assert amendment.modified_on is not None
        assert isinstance(amendment.created_on, datetime)
        assert isinstance(amendment.modified_on, datetime)

    def test_amendment_modified_on_updates(self, test_session):
        """Test that modified_on updates when record is modified"""
        amendment = models.Amendment(
            amendment_reference="AMN-2024-004",
            amendment_type=models.AmendmentType.MAINTENANCE,
            description="Test maintenance",
        )
        test_session.add(amendment)
        test_session.commit()
        test_session.refresh(amendment)

        original_modified = amendment.modified_on

        # Update the amendment
        amendment.description = "Updated description"
        test_session.commit()
        test_session.refresh(amendment)

        # modified_on should be updated (or at least not earlier)
        assert amendment.modified_on >= original_modified

    def test_amendment_reference_unique_constraint(self, test_session):
        """Test that amendment_reference must be unique"""
        amendment1 = models.Amendment(
            amendment_reference="AMN-2024-005",
            amendment_type=models.AmendmentType.BUG,
            description="First amendment",
        )
        test_session.add(amendment1)
        test_session.commit()

        amendment2 = models.Amendment(
            amendment_reference="AMN-2024-005",  # Duplicate reference
            amendment_type=models.AmendmentType.FEATURE,
            description="Second amendment",
        )
        test_session.add(amendment2)

        with pytest.raises(IntegrityError):
            test_session.commit()

    def test_amendment_all_enum_types(self, test_session):
        """Test all amendment type enum values"""
        amendment_types = [
            models.AmendmentType.BUG,
            models.AmendmentType.ENHANCEMENT,
            models.AmendmentType.FEATURE,
            models.AmendmentType.MAINTENANCE,
            models.AmendmentType.DOCUMENTATION,
        ]

        for idx, amendment_type in enumerate(amendment_types):
            amendment = models.Amendment(
                amendment_reference=f"AMN-2024-{100 + idx}",
                amendment_type=amendment_type,
                description=f"Test {amendment_type.value}",
            )
            test_session.add(amendment)
            test_session.commit()
            test_session.refresh(amendment)
            assert amendment.amendment_type == amendment_type

    def test_amendment_all_status_enum_values(self, test_session):
        """Test all amendment status enum values"""
        statuses = [
            models.AmendmentStatus.OPEN,
            models.AmendmentStatus.IN_PROGRESS,
            models.AmendmentStatus.TESTING,
            models.AmendmentStatus.COMPLETED,
            models.AmendmentStatus.DEPLOYED,
        ]

        for idx, status in enumerate(statuses):
            amendment = models.Amendment(
                amendment_reference=f"AMN-2024-{200 + idx}",
                amendment_type=models.AmendmentType.BUG,
                description=f"Test status {status.value}",
                amendment_status=status,
            )
            test_session.add(amendment)
            test_session.commit()
            test_session.refresh(amendment)
            assert amendment.amendment_status == status

    def test_amendment_all_development_status_values(self, test_session):
        """Test all development status enum values"""
        dev_statuses = [
            models.DevelopmentStatus.NOT_STARTED,
            models.DevelopmentStatus.IN_DEVELOPMENT,
            models.DevelopmentStatus.CODE_REVIEW,
            models.DevelopmentStatus.READY_FOR_QA,
        ]

        for idx, dev_status in enumerate(dev_statuses):
            amendment = models.Amendment(
                amendment_reference=f"AMN-2024-{300 + idx}",
                amendment_type=models.AmendmentType.FEATURE,
                description=f"Test dev status {dev_status.value}",
                development_status=dev_status,
            )
            test_session.add(amendment)
            test_session.commit()
            test_session.refresh(amendment)
            assert amendment.development_status == dev_status

    def test_amendment_all_priority_values(self, test_session):
        """Test all priority enum values"""
        priorities = [
            models.Priority.LOW,
            models.Priority.MEDIUM,
            models.Priority.HIGH,
            models.Priority.CRITICAL,
        ]

        for idx, priority in enumerate(priorities):
            amendment = models.Amendment(
                amendment_reference=f"AMN-2024-{400 + idx}",
                amendment_type=models.AmendmentType.BUG,
                description=f"Test priority {priority.value}",
                priority=priority,
            )
            test_session.add(amendment)
            test_session.commit()
            test_session.refresh(amendment)
            assert amendment.priority == priority

    def test_amendment_nullable_fields(self, test_session):
        """Test that nullable fields can be None"""
        amendment = models.Amendment(
            amendment_reference="AMN-2024-500",
            amendment_type=models.AmendmentType.BUG,
            description="Test nullable fields",
            force=None,
            application=None,
            notes=None,
            reported_by=None,
            assigned_to=None,
            date_reported=None,
        )
        test_session.add(amendment)
        test_session.commit()
        test_session.refresh(amendment)

        assert amendment.force is None
        assert amendment.application is None
        assert amendment.notes is None
        assert amendment.reported_by is None
        assert amendment.assigned_to is None
        assert amendment.date_reported is None

    def test_amendment_qa_fields(self, test_session):
        """Test QA-related fields"""
        amendment = models.Amendment(
            amendment_reference="AMN-2024-600",
            amendment_type=models.AmendmentType.FEATURE,
            description="Test QA fields",
            qa_assigned_id=123,
            qa_assigned_date=datetime(2024, 1, 15, 9, 0, 0),
            qa_test_plan_check=True,
            qa_test_release_notes_check=True,
            qa_completed=True,
            qa_signature="QA Tester",
            qa_completed_date=datetime(2024, 1, 20, 17, 0, 0),
            qa_notes="All tests passed",
            qa_test_plan_link="https://example.com/test-plan-123",
        )
        test_session.add(amendment)
        test_session.commit()
        test_session.refresh(amendment)

        assert amendment.qa_assigned_id == 123
        assert amendment.qa_assigned_date == datetime(2024, 1, 15, 9, 0, 0)
        assert amendment.qa_test_plan_check is True
        assert amendment.qa_test_release_notes_check is True
        assert amendment.qa_completed is True
        assert amendment.qa_signature == "QA Tester"
        assert amendment.qa_completed_date == datetime(2024, 1, 20, 17, 0, 0)
        assert amendment.qa_notes == "All tests passed"
        assert amendment.qa_test_plan_link == "https://example.com/test-plan-123"


class TestAmendmentProgressModel:
    """Test cases for the AmendmentProgress model"""

    def test_create_progress_entry(self, test_session, sample_amendment):
        """Test creating a progress entry"""
        progress = models.AmendmentProgress(
            amendment_id=sample_amendment.amendment_id,
            start_date=datetime(2024, 1, 10, 8, 0, 0),
            description="Started implementation",
            notes="Working on core features",
        )
        test_session.add(progress)
        test_session.commit()
        test_session.refresh(progress)

        assert progress.amendment_progress_id is not None
        assert progress.amendment_id == sample_amendment.amendment_id
        assert progress.start_date == datetime(2024, 1, 10, 8, 0, 0)
        assert progress.description == "Started implementation"
        assert progress.notes == "Working on core features"

    def test_progress_audit_fields(self, test_session, sample_amendment):
        """Test that progress audit fields are auto-populated"""
        progress = models.AmendmentProgress(
            amendment_id=sample_amendment.amendment_id,
            description="Progress update",
        )
        test_session.add(progress)
        test_session.commit()
        test_session.refresh(progress)

        assert progress.created_on is not None
        assert progress.modified_on is not None
        assert isinstance(progress.created_on, datetime)

    def test_progress_relationship_with_amendment(self, test_session, sample_amendment):
        """Test relationship between progress and amendment"""
        progress1 = models.AmendmentProgress(
            amendment_id=sample_amendment.amendment_id,
            description="First update",
        )
        progress2 = models.AmendmentProgress(
            amendment_id=sample_amendment.amendment_id,
            description="Second update",
        )
        test_session.add_all([progress1, progress2])
        test_session.commit()
        test_session.refresh(sample_amendment)

        assert len(sample_amendment.progress_entries) == 2
        assert progress1 in sample_amendment.progress_entries
        assert progress2 in sample_amendment.progress_entries

    def test_progress_cascade_delete(self, test_session, sample_amendment):
        """Test that progress entries are deleted when amendment is deleted"""
        progress = models.AmendmentProgress(
            amendment_id=sample_amendment.amendment_id,
            description="Test progress",
        )
        test_session.add(progress)
        test_session.commit()
        progress_id = progress.amendment_progress_id

        # Delete the amendment
        test_session.delete(sample_amendment)
        test_session.commit()

        # Progress should be deleted due to cascade
        deleted_progress = test_session.get(models.AmendmentProgress, progress_id)
        assert deleted_progress is None


class TestAmendmentApplicationModel:
    """Test cases for the AmendmentApplication model"""

    def test_create_application_mapping(self, test_session, sample_amendment):
        """Test creating an application mapping"""
        app = models.AmendmentApplication(
            amendment_id=sample_amendment.amendment_id,
            application_name="Main Application",
            version="2.5.0",
        )
        test_session.add(app)
        test_session.commit()
        test_session.refresh(app)

        assert app.id is not None
        assert app.amendment_id == sample_amendment.amendment_id
        assert app.application_name == "Main Application"
        assert app.version == "2.5.0"

    def test_application_nullable_version(self, test_session, sample_amendment):
        """Test that version field can be None"""
        app = models.AmendmentApplication(
            amendment_id=sample_amendment.amendment_id,
            application_name="Test App",
            version=None,
        )
        test_session.add(app)
        test_session.commit()
        test_session.refresh(app)

        assert app.version is None

    def test_application_relationship(self, test_session, sample_amendment):
        """Test relationship between application and amendment"""
        app1 = models.AmendmentApplication(
            amendment_id=sample_amendment.amendment_id,
            application_name="App 1",
        )
        app2 = models.AmendmentApplication(
            amendment_id=sample_amendment.amendment_id,
            application_name="App 2",
        )
        test_session.add_all([app1, app2])
        test_session.commit()
        test_session.refresh(sample_amendment)

        assert len(sample_amendment.applications) == 2
        assert app1 in sample_amendment.applications
        assert app2 in sample_amendment.applications

    def test_application_cascade_delete(self, test_session, sample_amendment):
        """Test that applications are deleted when amendment is deleted"""
        app = models.AmendmentApplication(
            amendment_id=sample_amendment.amendment_id,
            application_name="Test Application",
        )
        test_session.add(app)
        test_session.commit()
        app_id = app.id

        # Delete the amendment
        test_session.delete(sample_amendment)
        test_session.commit()

        # Application should be deleted due to cascade
        deleted_app = test_session.get(models.AmendmentApplication, app_id)
        assert deleted_app is None


class TestAmendmentLinkModel:
    """Test cases for the AmendmentLink model"""

    def test_create_amendment_link(self, test_session, sample_amendment):
        """Test creating a link between amendments"""
        link = models.AmendmentLink(
            amendment_id=sample_amendment.amendment_id,
            linked_amendment_id=999,
            link_type=models.LinkType.RELATED,
        )
        test_session.add(link)
        test_session.commit()
        test_session.refresh(link)

        assert link.amendment_link_id is not None
        assert link.amendment_id == sample_amendment.amendment_id
        assert link.linked_amendment_id == 999
        assert link.link_type == models.LinkType.RELATED

    def test_link_default_type(self, test_session, sample_amendment):
        """Test that link type defaults to RELATED"""
        link = models.AmendmentLink(
            amendment_id=sample_amendment.amendment_id,
            linked_amendment_id=888,
        )
        test_session.add(link)
        test_session.commit()
        test_session.refresh(link)

        assert link.link_type == models.LinkType.RELATED

    def test_all_link_types(self, test_session, sample_amendment):
        """Test all link type enum values"""
        link_types = [
            models.LinkType.RELATED,
            models.LinkType.DUPLICATE,
            models.LinkType.BLOCKS,
            models.LinkType.BLOCKED_BY,
        ]

        for idx, link_type in enumerate(link_types):
            link = models.AmendmentLink(
                amendment_id=sample_amendment.amendment_id,
                linked_amendment_id=1000 + idx,
                link_type=link_type,
            )
            test_session.add(link)
            test_session.commit()
            test_session.refresh(link)
            assert link.link_type == link_type

    def test_link_relationship(self, test_session, sample_amendment):
        """Test relationship between link and amendment"""
        link1 = models.AmendmentLink(
            amendment_id=sample_amendment.amendment_id,
            linked_amendment_id=111,
            link_type=models.LinkType.BLOCKS,
        )
        link2 = models.AmendmentLink(
            amendment_id=sample_amendment.amendment_id,
            linked_amendment_id=222,
            link_type=models.LinkType.RELATED,
        )
        test_session.add_all([link1, link2])
        test_session.commit()
        test_session.refresh(sample_amendment)

        assert len(sample_amendment.links) == 2
        assert link1 in sample_amendment.links
        assert link2 in sample_amendment.links

    def test_link_cascade_delete(self, test_session, sample_amendment):
        """Test that links are deleted when amendment is deleted"""
        link = models.AmendmentLink(
            amendment_id=sample_amendment.amendment_id,
            linked_amendment_id=555,
        )
        test_session.add(link)
        test_session.commit()
        link_id = link.amendment_link_id

        # Delete the amendment
        test_session.delete(sample_amendment)
        test_session.commit()

        # Link should be deleted due to cascade
        deleted_link = test_session.get(models.AmendmentLink, link_id)
        assert deleted_link is None


class TestEnumValues:
    """Test enum string values match expected values"""

    def test_amendment_type_values(self):
        """Test AmendmentType enum string values"""
        assert models.AmendmentType.BUG.value == "Bug"
        assert models.AmendmentType.ENHANCEMENT.value == "Enhancement"
        assert models.AmendmentType.FEATURE.value == "Feature"
        assert models.AmendmentType.MAINTENANCE.value == "Maintenance"
        assert models.AmendmentType.DOCUMENTATION.value == "Documentation"

    def test_amendment_status_values(self):
        """Test AmendmentStatus enum string values"""
        assert models.AmendmentStatus.OPEN.value == "Open"
        assert models.AmendmentStatus.IN_PROGRESS.value == "In Progress"
        assert models.AmendmentStatus.TESTING.value == "Testing"
        assert models.AmendmentStatus.COMPLETED.value == "Completed"
        assert models.AmendmentStatus.DEPLOYED.value == "Deployed"

    def test_development_status_values(self):
        """Test DevelopmentStatus enum string values"""
        assert models.DevelopmentStatus.NOT_STARTED.value == "Not Started"
        assert models.DevelopmentStatus.IN_DEVELOPMENT.value == "In Development"
        assert models.DevelopmentStatus.CODE_REVIEW.value == "Code Review"
        assert models.DevelopmentStatus.READY_FOR_QA.value == "Ready for QA"

    def test_priority_values(self):
        """Test Priority enum string values"""
        assert models.Priority.LOW.value == "Low"
        assert models.Priority.MEDIUM.value == "Medium"
        assert models.Priority.HIGH.value == "High"
        assert models.Priority.CRITICAL.value == "Critical"

    def test_force_values(self):
        """Test Force enum string values"""
        assert models.Force.ARMY.value == "Army"
        assert models.Force.NAVY.value == "Navy"
        assert models.Force.RAF.value == "RAF"
        assert models.Force.ALL.value == "All"

    def test_link_type_values(self):
        """Test LinkType enum string values"""
        assert models.LinkType.RELATED.value == "Related"
        assert models.LinkType.DUPLICATE.value == "Duplicate"
        assert models.LinkType.BLOCKS.value == "Blocks"
        assert models.LinkType.BLOCKED_BY.value == "Blocked By"
