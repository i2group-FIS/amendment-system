#!/usr/bin/env python3
"""
Migration script to import amendments from old fis-amendments SQL Server database dump.

This script parses the script.sql file from the old system and imports amendments
into the new SQLite-based amendment tracking system.
"""

import re
import sys
import os
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import from backend
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.database import SessionLocal, init_db
from backend.app import models, schemas, crud


def parse_sql_insert(insert_statement):
    """
    Parse a SQL INSERT statement and extract values.

    Returns a list of tuples, where each tuple represents a row of data.
    """
    # Extract values from INSERT INTO ... VALUES (...), (...), ...
    values_pattern = r'VALUES\s*(.+?)(?:;|$)'
    values_match = re.search(values_pattern, insert_statement, re.IGNORECASE | re.DOTALL)

    if not values_match:
        return []

    values_text = values_match.group(1)

    # Split by '),(' to get individual rows
    rows = []
    # This is a simple parser - may need enhancement for complex SQL
    row_pattern = r'\(([^)]+)\)'
    for match in re.finditer(row_pattern, values_text):
        row_data = match.group(1)
        # Split by comma but respect quotes
        values = []
        current = ''
        in_quote = False
        quote_char = None

        for char in row_data:
            if char in ('"', "'") and not in_quote:
                in_quote = True
                quote_char = char
            elif char == quote_char and in_quote:
                in_quote = False
                quote_char = None
            elif char == ',' and not in_quote:
                values.append(current.strip())
                current = ''
                continue
            current += char

        if current.strip():
            values.append(current.strip())

        rows.append(values)

    return rows


def clean_sql_value(value):
    """Clean a SQL value (remove quotes, handle NULL, etc.)"""
    if not value:
        return None

    value = value.strip()

    if value.upper() == 'NULL':
        return None

    # Remove surrounding quotes
    if (value.startswith("'") and value.endswith("'")) or \
       (value.startswith('"') and value.endswith('"')):
        value = value[1:-1]

    # Unescape single quotes
    value = value.replace("''", "'")

    return value if value else None


def parse_date(date_str):
    """Parse a date string from SQL Server format."""
    if not date_str or date_str.upper() == 'NULL':
        return None

    # Try various date formats
    formats = [
        '%Y-%m-%d %H:%M:%S.%f',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    return None


def migrate_amendments(sql_file_path):
    """
    Migrate amendments from the SQL dump file.
    """
    print(f"Reading SQL file: {sql_file_path}")

    with open(sql_file_path, 'r', encoding='utf-16', errors='ignore') as f:
        sql_content = f.read()

    print(f"SQL file size: {len(sql_content)} characters")

    # Find all INSERT statements for Amendments table
    # Pattern to match: INSERT INTO [dbo].[Amendments] or INSERT INTO Amendments
    amendment_inserts = re.findall(
        r'INSERT\s+INTO\s+(?:\[dbo\]\.)?\[?Amendments\]?\s+.+?VALUES.+?;',
        sql_content,
        re.IGNORECASE | re.DOTALL
    )

    print(f"Found {len(amendment_inserts)} INSERT statements for Amendments")

    if not amendment_inserts:
        print("No amendment data found in SQL file")
        # Let's try a simpler search
        print("\nSearching for any table inserts...")
        all_inserts = re.findall(
            r'INSERT\s+INTO\s+(\[?\w+\]?)',
            sql_content,
            re.IGNORECASE
        )
        table_names = set(all_inserts[:50])  # First 50 unique tables
        print(f"Found INSERT statements for tables: {table_names}")
        return 0

    db = SessionLocal()
    imported_count = 0

    try:
        for insert_stmt in amendment_inserts:
            rows = parse_sql_insert(insert_stmt)

            for row in rows:
                try:
                    # Map SQL Server columns to our schema
                    # This mapping depends on the exact column order in the SQL dump
                    # You may need to adjust based on the actual schema

                    amendment_data = schemas.AmendmentCreate(
                        amendment_type=clean_sql_value(row[1]) or 'Bug',
                        description=clean_sql_value(row[2]) or 'No description',
                        amendment_status=clean_sql_value(row[3]) or 'Open',
                        development_status=clean_sql_value(row[4]) or 'Not Started',
                        priority=clean_sql_value(row[5]) or 'Medium',
                        force=clean_sql_value(row[6]),
                        application=clean_sql_value(row[7]),
                        notes=clean_sql_value(row[8]),
                        reported_by=clean_sql_value(row[9]),
                        assigned_to=clean_sql_value(row[10]),
                        date_reported=parse_date(clean_sql_value(row[11])),
                        database_changes=clean_sql_value(row[12]) == '1' if len(row) > 12 else False,
                        db_upgrade_changes=clean_sql_value(row[13]) == '1' if len(row) > 13 else False,
                        release_notes=clean_sql_value(row[14]) if len(row) > 14 else None,
                    )

                    # Create the amendment
                    created_by = clean_sql_value(row[15]) if len(row) > 15 else 'migration_script'
                    db_amendment = crud.create_amendment(db, amendment_data, created_by)
                    imported_count += 1

                    if imported_count % 10 == 0:
                        print(f"Imported {imported_count} amendments...")

                except Exception as e:
                    print(f"Error importing amendment: {e}")
                    print(f"Row data (first 5 fields): {row[:5]}")
                    continue

        db.commit()
        print(f"\nSuccessfully imported {imported_count} amendments!")

    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
        raise
    finally:
        db.close()

    return imported_count


def main():
    """Main migration function."""
    print("=" * 60)
    print("Amendment System Data Migration")
    print("=" * 60)
    print()

    # Initialize database
    print("Initializing database...")
    init_db()

    # Path to old SQL dump
    old_sql_path = Path(__file__).parent.parent.parent / 'fis-amendments' / 'script.sql'

    if not old_sql_path.exists():
        print(f"Error: SQL dump file not found at {old_sql_path}")
        print("\nPlease provide the path to the script.sql file:")
        custom_path = input("> ").strip()
        if custom_path:
            old_sql_path = Path(custom_path)

        if not old_sql_path.exists():
            print("Error: File not found. Exiting.")
            return 1

    # Run migration
    try:
        count = migrate_amendments(old_sql_path)
        print(f"\nMigration complete! Imported {count} amendments.")
        return 0
    except Exception as e:
        print(f"\nMigration failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
