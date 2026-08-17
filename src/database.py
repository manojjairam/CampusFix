# database.py
import sqlite3
from datetime import datetime
from pathlib import Path


DATABASE_PATH = Path("data/campusfix.db")


def get_connection():

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


def create_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
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
            image_path TEXT,
            status TEXT DEFAULT 'Open',
            created_at TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ticket_updates (
            update_id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER,
            status TEXT,
            remarks TEXT,
            updated_at TEXT,
            FOREIGN KEY (ticket_id)
            REFERENCES tickets(ticket_id)
        )
        """
    )

    cursor.execute(
        "PRAGMA table_info(tickets)"
    )

    existing_columns = [
        column["name"]
        for column in cursor.fetchall()
    ]

    if "image_path" not in existing_columns:

        cursor.execute(
            "ALTER TABLE tickets ADD COLUMN image_path TEXT"
        )

    connection.commit()

    connection.close()


def save_ticket(ticket_data):

    create_database()

    connection = get_connection()

    cursor = connection.cursor()

    created_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute(
        """
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
            image_path,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
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

            ticket_data.get(
                "image_path",
                ""
            ),

            "Open",

            created_at
        )
    )

    connection.commit()

    ticket_id = cursor.lastrowid

    connection.close()

    return ticket_id


def get_ticket(ticket_id):

    create_database()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM tickets
        WHERE ticket_id = ?
        """,
        (
            ticket_id,
        )
    )

    ticket = cursor.fetchone()

    connection.close()

    return ticket


def get_ticket_details(ticket_id):

    return get_ticket(ticket_id)


def get_all_tickets():

    create_database()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM tickets
        ORDER BY ticket_id DESC
        """
    )

    tickets = cursor.fetchall()

    connection.close()

    return tickets


def update_ticket_status(
    ticket_id,
    new_status,
    remarks
):

    create_database()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE tickets
        SET status = ?
        WHERE ticket_id = ?
        """,
        (
            new_status,
            ticket_id
        )
    )

    if cursor.rowcount == 0:

        connection.close()

        return False

    updated_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute(
        """
        INSERT INTO ticket_updates (
            ticket_id,
            status,
            remarks,
            updated_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            ticket_id,
            new_status,
            remarks,
            updated_at
        )
    )

    connection.commit()

    connection.close()

    return True


def get_ticket_updates(ticket_id):

    create_database()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM ticket_updates
        WHERE ticket_id = ?
        ORDER BY update_id DESC
        """,
        (
            ticket_id,
        )
    )

    updates = cursor.fetchall()

    connection.close()

    return updates


def format_datetime(date_string):

    if not date_string:

        return "Not available"

    try:

        date_object = datetime.strptime(
            str(date_string),
            "%Y-%m-%d %H:%M:%S"
        )

        return date_object.strftime(
            "%d %b %Y, %I:%M %p"
        )

    except ValueError:

        return str(date_string)
