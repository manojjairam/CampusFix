import sqlite3
from datetime import datetime
from pathlib import Path


# ==================================================
# DATABASE CONFIGURATION
# ==================================================

DATABASE_PATH = Path("data/campusfix.db")


# ==================================================
# DATABASE CONNECTION
# ==================================================

def get_connection():
    """Create a connection to the CampusFix SQLite database."""

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    return connection


# ==================================================
# CREATE DATABASE
# ==================================================

def create_database():
    """Create all required CampusFix database tables."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,

            student_name TEXT,
            register_number TEXT,

            issue_category TEXT,
            issue_title TEXT,
            severity TEXT,

            description TEXT,
            recommended_action TEXT,
            assigned_department TEXT,

            location TEXT,
            room TEXT,

            student_description TEXT,

            status TEXT DEFAULT 'Open',

            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ticket_updates (
            update_id INTEGER PRIMARY KEY AUTOINCREMENT,

            ticket_id INTEGER,
            status TEXT,
            remarks TEXT,
            updated_at TEXT,

            FOREIGN KEY (ticket_id)
            REFERENCES tickets(ticket_id)
        )
    """)

    connection.commit()
    connection.close()


# ==================================================
# SAVE TICKET
# ==================================================

def save_ticket(ticket_data):
    """
    Save a CampusFix ticket and return
    the generated ticket ID.
    """

    create_database()

    connection = get_connection()
    cursor = connection.cursor()

    created_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
        INSERT INTO tickets (
            student_name,
            register_number,

            issue_category,
            issue_title,
            severity,

            description,
            recommended_action,
            assigned_department,

            location,
            room,

            student_description,

            status,

            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ticket_data.get(
            "student_name",
            "Not provided"
        ),

        ticket_data.get(
            "register_number",
            "Not provided"
        ),

        ticket_data.get(
            "issue_category",
            "General Maintenance"
        ),

        ticket_data.get(
            "issue_title",
            "Maintenance Issue"
        ),

        ticket_data.get(
            "severity",
            "Normal"
        ),

        ticket_data.get(
            "description",
            "Not specified"
        ),

        ticket_data.get(
            "recommended_action",
            "Maintenance inspection required"
        ),

        ticket_data.get(
            "assigned_department",
            "General Maintenance"
        ),

        ticket_data.get(
            "location",
            "Not specified"
        ),

        ticket_data.get(
            "room",
            "Not specified"
        ),

        ticket_data.get(
            "student_description",
            ""
        ),

        "Open",

        created_at
    ))

    connection.commit()

    ticket_id = cursor.lastrowid

    connection.close()

    return ticket_id


# ==================================================
# GET ONE TICKET
# ==================================================

def get_ticket(ticket_id):
    """Get one ticket using its Ticket ID."""

    create_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT * FROM tickets
        WHERE ticket_id = ?
        """,
        (ticket_id,)
    )

    ticket = cursor.fetchone()

    connection.close()

    return ticket


# ==================================================
# GET COMPLETE TICKET DETAILS
# ==================================================

def get_ticket_details(ticket_id):
    """Get complete details of one ticket."""

    return get_ticket(ticket_id)


# ==================================================
# GET ALL TICKETS
# ==================================================

def get_all_tickets():
    """Return all CampusFix tickets."""

    create_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM tickets
        ORDER BY ticket_id DESC
    """)

    tickets = cursor.fetchall()

    connection.close()

    return tickets


# ==================================================
# UPDATE TICKET STATUS
# ==================================================

def update_ticket_status(
    ticket_id,
    new_status,
    remarks
):
    """
    Update the current ticket status and
    save the update in ticket history.
    """

    create_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE tickets
        SET status = ?
        WHERE ticket_id = ?
    """, (
        new_status,
        ticket_id
    ))

    if cursor.rowcount == 0:

        connection.close()

        return False

    updated_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
        INSERT INTO ticket_updates (
            ticket_id,
            status,
            remarks,
            updated_at
        )
        VALUES (?, ?, ?, ?)
    """, (
        ticket_id,
        new_status,
        remarks,
        updated_at
    ))

    connection.commit()
    connection.close()

    return True


# ==================================================
# GET TICKET UPDATE HISTORY
# ==================================================

def get_ticket_updates(ticket_id):
    """Return the complete update history of a ticket."""

    create_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM ticket_updates
        WHERE ticket_id = ?
        ORDER BY update_id DESC
    """, (
        ticket_id,
    ))

    updates = cursor.fetchall()

    connection.close()

    return updates


# ==================================================
# FORMAT DATE FOR DISPLAY
# ==================================================

def format_datetime(date_string):
    """
    Convert database date format:

    2026-08-17 10:30:00

    Into:

    17 Aug 2026, 10:30 AM
    """

    if not date_string:

        return "Not available"

    try:

        date_object = datetime.strptime(
            date_string,
            "%Y-%m-%d %H:%M:%S"
        )

        return date_object.strftime(
            "%d %b %Y, %I:%M %p"
        )

    except ValueError:

        return date_string