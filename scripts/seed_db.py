#!/usr/bin/env python3
"""
Database seeding script to populate test data for the amendment system.
Generates sample amendments with progress updates, applications, and links.
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database import SessionLocal, init_db
from app.models import (
    Amendment, AmendmentProgress, AmendmentApplication, AmendmentLink,
    AmendmentType, AmendmentStatus, DevelopmentStatus, Priority, Force, LinkType
)


def clear_database(db):
    """Clear all data from the database."""
    print("Clearing existing data...")
    db.query(AmendmentLink).delete()
    db.query(AmendmentProgress).delete()
    db.query(AmendmentApplication).delete()
    db.query(Amendment).delete()
    db.commit()
    print("Database cleared.")


def generate_reference(date: datetime, sequence: int) -> str:
    """Generate an amendment reference in the format YYYYMMDD-XXX."""
    date_str = date.strftime("%Y%m%d")
    return f"{date_str}-{sequence:03d}"


def seed_amendments(db, count: int = 50):
    """Create sample amendments."""
    print(f"\nCreating {count} sample amendments...")

    developers = ["John Smith", "Sarah Johnson", "Mike Davis", "Emma Wilson", "Tom Brown"]
    qa_team = ["Alice Cooper", "Bob Taylor", "Carol White"]
    reporters = ["User A", "User B", "User C", "System Admin", "Project Manager"]
    applications = ["FIS-Core", "FIS-Web", "FIS-Mobile", "FIS-Reports", "FIS-Admin"]

    descriptions = [
        "Fix login authentication issue",
        "Add export functionality to reports",
        "Update user interface for better accessibility",
        "Optimize database queries for performance",
        "Fix data validation error on form submission",
        "Implement new dashboard widgets",
        "Add bulk update capability",
        "Fix memory leak in background service",
        "Update API endpoints for new requirements",
        "Add support for multi-language interface",
        "Fix incorrect date formatting",
        "Improve error handling and logging",
        "Add user preference settings",
        "Fix security vulnerability in authentication",
        "Implement caching for frequently accessed data",
        "Update documentation for API changes",
        "Add notification system for important events",
        "Fix report generation timeout issues",
        "Implement data archival functionality",
        "Add search filters to main listing page",
    ]

    amendments = []
    start_date = datetime.now() - timedelta(days=90)

    for i in range(count):
        # Generate date within last 90 days
        days_ago = random.randint(0, 89)
        date_reported = start_date + timedelta(days=days_ago)

        # Generate reference
        sequence = i + 1
        reference = generate_reference(date_reported, sequence)

        # Random status weights (more recent = more likely to be open/in progress)
        if days_ago < 10:
            status_pool = [AmendmentStatus.OPEN, AmendmentStatus.IN_PROGRESS] * 3 + \
                         [AmendmentStatus.TESTING, AmendmentStatus.COMPLETED]
        elif days_ago < 30:
            status_pool = [AmendmentStatus.IN_PROGRESS, AmendmentStatus.TESTING] * 2 + \
                         [AmendmentStatus.COMPLETED, AmendmentStatus.DEPLOYED]
        else:
            status_pool = [AmendmentStatus.COMPLETED, AmendmentStatus.DEPLOYED] * 3 + \
                         [AmendmentStatus.TESTING]

        status = random.choice(status_pool)

        # Development status based on amendment status
        dev_status_map = {
            AmendmentStatus.OPEN: [DevelopmentStatus.NOT_STARTED, DevelopmentStatus.IN_DEVELOPMENT],
            AmendmentStatus.IN_PROGRESS: [DevelopmentStatus.IN_DEVELOPMENT, DevelopmentStatus.CODE_REVIEW],
            AmendmentStatus.TESTING: [DevelopmentStatus.READY_FOR_QA],
            AmendmentStatus.COMPLETED: [DevelopmentStatus.READY_FOR_QA],
            AmendmentStatus.DEPLOYED: [DevelopmentStatus.READY_FOR_QA],
        }
        dev_status = random.choice(dev_status_map[status])

        # QA fields
        qa_completed = status in [AmendmentStatus.COMPLETED, AmendmentStatus.DEPLOYED]
        qa_assigned = status in [AmendmentStatus.TESTING, AmendmentStatus.COMPLETED, AmendmentStatus.DEPLOYED]

        amendment = Amendment(
            amendment_reference=reference,
            amendment_type=random.choice(list(AmendmentType)),
            description=random.choice(descriptions),
            amendment_status=status,
            development_status=dev_status,
            priority=random.choice(list(Priority)),
            force=random.choice(list(Force)).value if random.random() > 0.3 else None,
            application=random.choice(applications) if random.random() > 0.2 else None,
            notes=f"Notes for amendment {reference}" if random.random() > 0.5 else None,
            reported_by=random.choice(reporters),
            assigned_to=random.choice(developers) if random.random() > 0.2 else None,
            date_reported=date_reported,
            database_changes=random.random() > 0.7,
            db_upgrade_changes=random.random() > 0.85,
            release_notes=f"Release notes for {reference}" if status in [AmendmentStatus.COMPLETED, AmendmentStatus.DEPLOYED] else None,
            qa_assigned_id=random.randint(1, 3) if qa_assigned else None,
            qa_assigned_date=date_reported + timedelta(days=random.randint(1, 5)) if qa_assigned else None,
            qa_test_plan_check=qa_completed and random.random() > 0.3,
            qa_test_release_notes_check=qa_completed and random.random() > 0.3,
            qa_completed=qa_completed,
            qa_signature=random.choice(qa_team) if qa_completed else None,
            qa_completed_date=date_reported + timedelta(days=random.randint(5, 15)) if qa_completed else None,
            qa_notes=f"QA notes for {reference}" if qa_completed and random.random() > 0.5 else None,
            created_by=random.choice(reporters),
            created_on=date_reported,
            modified_by=random.choice(developers) if random.random() > 0.3 else None,
            modified_on=date_reported + timedelta(days=random.randint(1, days_ago + 1)) if days_ago > 0 else date_reported,
        )

        db.add(amendment)
        amendments.append(amendment)

    db.commit()
    print(f"Created {count} amendments")
    return amendments


def seed_progress(db, amendments):
    """Add progress updates to amendments."""
    print("\nAdding progress updates...")

    developers = ["John Smith", "Sarah Johnson", "Mike Davis", "Emma Wilson", "Tom Brown"]

    progress_templates = [
        "Started initial analysis and planning",
        "Completed code implementation",
        "Fixed review comments",
        "Deployed to test environment",
        "Ready for QA testing",
        "Fixed reported bugs",
        "Updated documentation",
        "Deployed to production",
        "Investigating issue",
        "Awaiting client feedback",
        "Design review completed",
        "Database changes implemented",
    ]

    count = 0
    for amendment in amendments:
        # Add 1-5 progress entries per amendment based on status
        if amendment.amendment_status == AmendmentStatus.OPEN:
            num_entries = random.randint(0, 2)
        elif amendment.amendment_status == AmendmentStatus.IN_PROGRESS:
            num_entries = random.randint(1, 3)
        else:
            num_entries = random.randint(2, 5)

        for i in range(num_entries):
            days_after = i * random.randint(1, 3)
            progress_date = amendment.date_reported + timedelta(days=days_after)

            progress = AmendmentProgress(
                amendment_id=amendment.amendment_id,
                start_date=progress_date,
                description=random.choice(progress_templates),
                notes=f"Additional notes for progress update {i+1}" if random.random() > 0.6 else None,
                created_by=random.choice(developers),
                created_on=progress_date,
            )
            db.add(progress)
            count += 1

    db.commit()
    print(f"Added {count} progress entries")


def seed_applications(db, amendments):
    """Add application mappings to amendments."""
    print("\nAdding application mappings...")

    apps = [
        ("FIS-Core", "2.1.0"),
        ("FIS-Web", "1.5.2"),
        ("FIS-Mobile", "3.0.1"),
        ("FIS-Reports", "1.2.0"),
        ("FIS-Admin", "2.0.0"),
    ]

    count = 0
    for amendment in amendments:
        # 30% chance to add application mappings
        if random.random() > 0.3 and amendment.application:
            num_apps = random.randint(1, 2)
            selected_apps = random.sample(apps, min(num_apps, len(apps)))

            for app_name, version in selected_apps:
                app = AmendmentApplication(
                    amendment_id=amendment.amendment_id,
                    application_name=app_name,
                    version=version if random.random() > 0.3 else None,
                )
                db.add(app)
                count += 1

    db.commit()
    print(f"Added {count} application mappings")


def seed_links(db, amendments):
    """Add links between amendments."""
    print("\nAdding amendment links...")

    count = 0
    # Create some related/duplicate/blocking relationships
    for i in range(len(amendments)):
        # 20% chance to create links
        if random.random() < 0.2 and i > 0:
            # Link to a previous amendment
            target_idx = random.randint(0, i - 1)
            link_type = random.choice(list(LinkType))

            link = AmendmentLink(
                amendment_id=amendments[i].amendment_id,
                linked_amendment_id=amendments[target_idx].amendment_id,
                link_type=link_type,
            )
            db.add(link)
            count += 1

            # If it's a BLOCKS relationship, create reverse BLOCKED_BY
            if link_type == LinkType.BLOCKS:
                reverse_link = AmendmentLink(
                    amendment_id=amendments[target_idx].amendment_id,
                    linked_amendment_id=amendments[i].amendment_id,
                    link_type=LinkType.BLOCKED_BY,
                )
                db.add(reverse_link)
                count += 1

    db.commit()
    print(f"Added {count} amendment links")


def print_statistics(db):
    """Print database statistics."""
    print("\n" + "="*60)
    print("DATABASE STATISTICS")
    print("="*60)

    total_amendments = db.query(Amendment).count()
    print(f"\nTotal Amendments: {total_amendments}")

    print("\nBy Status:")
    for status in AmendmentStatus:
        count = db.query(Amendment).filter(Amendment.amendment_status == status).count()
        print(f"  {status.value}: {count}")

    print("\nBy Priority:")
    for priority in Priority:
        count = db.query(Amendment).filter(Amendment.priority == priority).count()
        print(f"  {priority.value}: {count}")

    print("\nBy Type:")
    for atype in AmendmentType:
        count = db.query(Amendment).filter(Amendment.amendment_type == atype).count()
        print(f"  {atype.value}: {count}")

    total_progress = db.query(AmendmentProgress).count()
    print(f"\nTotal Progress Entries: {total_progress}")

    total_applications = db.query(AmendmentApplication).count()
    print(f"Total Application Mappings: {total_applications}")

    total_links = db.query(AmendmentLink).count()
    print(f"Total Amendment Links: {total_links}")

    qa_completed = db.query(Amendment).filter(Amendment.qa_completed == True).count()
    print(f"\nQA Completed: {qa_completed}")

    with_db_changes = db.query(Amendment).filter(Amendment.database_changes == True).count()
    print(f"With Database Changes: {with_db_changes}")

    print("\n" + "="*60)


def main():
    """Main seeding function."""
    print("="*60)
    print("AMENDMENT SYSTEM - DATABASE SEEDING SCRIPT")
    print("="*60)

    # Initialize database
    init_db()

    # Create session
    db = SessionLocal()

    try:
        # Clear existing data
        clear_database(db)

        # Seed data
        amendments = seed_amendments(db, count=50)
        seed_progress(db, amendments)
        seed_applications(db, amendments)
        seed_links(db, amendments)

        # Print statistics
        print_statistics(db)

        print("\n" + "="*60)
        print("SEEDING COMPLETED SUCCESSFULLY!")
        print("="*60)

    except Exception as e:
        print(f"\nError during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
