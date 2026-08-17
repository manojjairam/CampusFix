import streamlit as st
import os
import shutil
import time
from datetime import datetime
from pathlib import Path

from src.vision_analyzer import analyze_issue_image
from src.database import (
    save_ticket,
    get_ticket_details,
    get_all_tickets,
    update_ticket_status,
    get_ticket_updates
)


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="CampusFix",
    page_icon="🏫",
    layout="wide"
)


# ==================================================
# IMAGE STORAGE CONFIGURATION
# ==================================================

UPLOAD_FOLDER = Path("data/uploads")

UPLOAD_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


# ==================================================
# CAMPUS BUILDINGS AND LOCATIONS
# ==================================================

CAMPUS_LOCATIONS = {
    "Academic Block A": [
        "Room 101",
        "Room 102",
        "Room 103",
        "Room 104",
        "Room 105",
        "Room 201",
        "Room 202",
        "Room 203",
        "Room 204",
        "Room 205",
        "Room 206",
        "Room 207"
    ],

    "Academic Block B": [
        "Room 101",
        "Room 102",
        "Room 103",
        "Room 104",
        "Room 105",
        "Room 201",
        "Room 202",
        "Room 203",
        "Room 204",
        "Room 205"
    ],

    "Academic Block C": [
        "Room 101",
        "Room 102",
        "Room 103",
        "Room 104",
        "Room 105",
        "Room 201",
        "Room 202",
        "Room 203",
        "Room 204",
        "Room 205"
    ],

    "Laboratory Block": [
        "Computer Lab",
        "AI Lab",
        "Physics Lab",
        "Chemistry Lab",
        "Electronics Lab"
    ],

    "Library": [
        "Ground Floor",
        "First Floor",
        "Reading Hall",
        "Digital Library",
        "Reference Section"
    ],

    "Administration Block": [
        "Reception",
        "Accounts Office",
        "Principal Office",
        "Staff Room",
        "Meeting Room"
    ],

    "Hostel Block": [
        "Block Entrance",
        "Ground Floor Corridor",
        "First Floor Corridor",
        "Common Area",
        "Room 101",
        "Room 102",
        "Room 103",
        "Room 104",
        "Room 105"
    ],

    "Cafeteria": [
        "Dining Area",
        "Kitchen Area",
        "Seating Area",
        "Wash Area",
        "Entrance"
    ]
}


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def format_ticket_datetime(date_value):

    if not date_value:

        return "Not available"

    try:

        date_object = datetime.strptime(
            str(date_value),
            "%Y-%m-%d %H:%M:%S"
        )

        return date_object.strftime(
            "%d %b %Y, %I:%M %p"
        )

    except ValueError:

        return str(date_value)


def parse_ticket_result(ticket_result):

    ticket_data = {}

    for line in str(ticket_result).split("\n"):

        if ":" in line:

            key, value = line.split(
                ":",
                1
            )

            ticket_data[
                key.strip().lower()
            ] = value.strip()

    return ticket_data


def save_uploaded_image(
    uploaded_image,
    prefix
):

    if uploaded_image is None:

        return ""

    file_extension = Path(
        uploaded_image.name
    ).suffix.lower()

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    image_filename = (
        f"{prefix}_{timestamp}{file_extension}"
    )

    permanent_path = (
        UPLOAD_FOLDER / image_filename
    )

    with open(
        permanent_path,
        "wb"
    ) as destination:

        shutil.copyfileobj(
            uploaded_image,
            destination
        )

    return str(permanent_path)


def display_ticket_image(ticket):

    image_path = ""

    try:

        image_path = ticket["image_path"]

    except (
        IndexError,
        KeyError,
        TypeError
    ):

        image_path = ""

    if image_path and os.path.exists(image_path):

        st.subheader(
            "📷 Uploaded Issue Image"
        )

        st.image(
            image_path,
            caption="Maintenance Issue Image",
            use_container_width=True
        )


# ==================================================
# CREATE MAINTENANCE TICKET
# ==================================================

def create_maintenance_ticket(
    student_name,
    register_number,
    location,
    room,
    description,
    uploaded_image,
    image_prefix
):

    # ==============================================
    # STEP 1 - SAVE IMAGE
    # ==============================================

    start_time = time.time()

    permanent_image_path = save_uploaded_image(
        uploaded_image,
        image_prefix
    )

    image_save_time = round(
        time.time() - start_time,
        3
    )

    # ==============================================
    # STEP 2 - FAST ISSUE ANALYSIS
    # ==============================================

    start_time = time.time()

    analysis_result = analyze_issue_image(
        image_path=permanent_image_path,
        user_description=description,
        location=location,
        room=room
    )

    analysis_time = round(
        time.time() - start_time,
        3
    )

    if str(analysis_result).startswith("Error"):

        return (
            None,
            analysis_result,
            ""
        )

    # ==============================================
    # STEP 3 - PARSE RESULT
    # ==============================================

    start_time = time.time()

    ticket_data = parse_ticket_result(
        analysis_result
    )

    parse_time = round(
        time.time() - start_time,
        3
    )

    # ==============================================
    # STEP 4 - PREPARE DATABASE DATA
    # ==============================================

    database_ticket = {
        "student_name": student_name.strip(),

        "register_number": register_number.strip(),

        "issue_category": ticket_data.get(
            "issue category",
            "General Maintenance"
        ),

        "issue_title": ticket_data.get(
            "issue title",
            "Maintenance Issue"
        ),

        "severity": ticket_data.get(
            "severity",
            "Normal"
        ),

        "description": ticket_data.get(
            "description",
            description
        ),

        "recommended_action": ticket_data.get(
            "recommended action",
            "Maintenance inspection required"
        ),

        "assigned_department": ticket_data.get(
            "assigned department",
            "General Maintenance"
        ),

        "location": location,

        "room": room,

        "student_description": description,

        "image_path": permanent_image_path
    }

    # ==============================================
    # STEP 5 - SAVE TO DATABASE
    # ==============================================

    start_time = time.time()

    ticket_id = save_ticket(
        database_ticket
    )

    database_time = round(
        time.time() - start_time,
        3
    )

    # ==============================================
    # PERFORMANCE RESULT
    # ==============================================

    performance_info = (
        f"Image Save: {image_save_time}s | "
        f"Analysis: {analysis_time}s | "
        f"Parsing: {parse_time}s | "
        f"Database: {database_time}s"
    )

    print(
        f"CampusFix Performance: {performance_info}"
    )

    return (
        ticket_id,
        database_ticket,
        performance_info
    )


# ==================================================
# DISPLAY CREATED TICKET
# ==================================================

def display_created_ticket(
    ticket_id,
    ticket_data,
    student_name,
    register_number,
    performance_info=""
):

    created_datetime = datetime.now().strftime(
        "%d %b %Y, %I:%M %p"
    )

    st.success(
        "Maintenance ticket created successfully!"
    )

    if performance_info:

        st.caption(
            f"⚡ {performance_info}"
        )

    st.divider()

    st.subheader(
        "👤 Student Details"
    )

    st.write(
        f"**Name:** {student_name}"
    )

    st.write(
        f"**Register Number:** {register_number}"
    )

    st.divider()

    st.subheader(
        "🎫 Ticket Details"
    )

    st.write(
        f"**Ticket ID:** {ticket_id}"
    )

    st.write(
        f"**Issue:** "
        f"{ticket_data['issue_title']}"
    )

    st.write(
        f"**Category:** "
        f"{ticket_data['issue_category']}"
    )

    st.write(
        f"**Severity:** "
        f"{ticket_data['severity']}"
    )

    st.write(
        f"**Created:** {created_datetime}"
    )

    st.write(
        f"**Ticket Directed To:** "
        f"{ticket_data['assigned_department']}"
    )

    st.info(
        "Please save your Ticket ID to track "
        "future updates."
    )


# ==================================================
# APP HEADER
# ==================================================

st.title("🏫 CampusFix")

st.subheader(
    "AI-Powered Campus Maintenance Issue Reporting System"
)

st.write(
    "Report campus maintenance issues using images and "
    "intelligent issue analysis. CampusFix creates maintenance "
    "tickets and allows students and administrators to track "
    "their progress."
)

st.divider()


# ==================================================
# NAVIGATION
# ==================================================

report_tab, track_tab, admin_tab, bot_tab = st.tabs([
    "📝 Report Issue",
    "🔎 Track Ticket",
    "🛠️ Admin Dashboard",
    "🤖 CampusFix Assistant"
])


# ==================================================
# REPORT ISSUE
# ==================================================

with report_tab:

    st.header(
        "Report a Maintenance Issue"
    )

    st.subheader(
        "👤 Student Details"
    )

    student_name = st.text_input(
        "Student Name",
        placeholder="Enter your full name",
        key="report_student_name"
    )

    register_number = st.text_input(
        "Register Number",
        placeholder="Enter your register number",
        key="report_register_number"
    )

    st.divider()

    st.subheader(
        "🎫 Issue Details"
    )

    location = st.selectbox(
        "Select Building / Location",
        options=list(CAMPUS_LOCATIONS.keys()),
        key="report_location"
    )

    room = st.selectbox(
        "Select Room / Exact Location",
        options=CAMPUS_LOCATIONS[location],
        key="report_room"
    )

    student_description = st.text_area(
        "Describe the Issue",
        placeholder=(
            "Example: The ceiling fan is shaking "
            "and making a loud noise."
        ),
        key="report_description"
    )

    uploaded_image = st.file_uploader(
        "Upload an Image of the Issue",
        type=["jpg", "jpeg", "png"],
        key="report_image"
    )

    if uploaded_image is not None:

        st.image(
            uploaded_image,
            caption="Uploaded Maintenance Issue Image",
            use_container_width=True
        )

    if st.button(
        "🔍 Analyze and Create Ticket",
        type="primary",
        key="report_create_ticket"
    ):

        if not student_name.strip():

            st.error(
                "Please enter the student name."
            )

        elif not register_number.strip():

            st.error(
                "Please enter the register number."
            )

        elif uploaded_image is None:

            st.error(
                "Please upload an image of the "
                "maintenance issue."
            )

        else:

            try:

                with st.spinner(
                    "Creating your maintenance ticket..."
                ):

                    ticket_id, result, performance_info = (
                        create_maintenance_ticket(
                            student_name,
                            register_number,
                            location,
                            room,
                            student_description,
                            uploaded_image,
                            "ticket"
                        )
                    )

                if ticket_id is None:

                    st.error(result)

                else:

                    display_created_ticket(
                        ticket_id,
                        result,
                        student_name,
                        register_number,
                        performance_info
                    )

            except Exception as error:

                st.error(
                    f"Unable to process the maintenance "
                    f"issue: {error}"
                )


# ==================================================
# TRACK TICKET
# ==================================================

with track_tab:

    st.header(
        "🔎 Track Your Maintenance Ticket"
    )

    st.write(
        "Enter your Ticket ID to view its current "
        "status and update history."
    )

    ticket_id_input = st.number_input(
        "Enter Ticket ID",
        min_value=1,
        step=1,
        value=1,
        key="track_ticket_id"
    )

    if st.button(
        "Check Ticket Status",
        type="primary",
        key="track_button"
    ):

        try:

            ticket = get_ticket_details(
                ticket_id_input
            )

            if ticket is None:

                st.error(
                    f"Ticket #{ticket_id_input} was not found."
                )

            else:

                created_datetime = (
                    format_ticket_datetime(
                        ticket["created_at"]
                    )
                )

                st.success(
                    f"Ticket #{ticket['ticket_id']} found!"
                )

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Ticket ID",
                    ticket["ticket_id"]
                )

                col2.metric(
                    "Status",
                    ticket["status"]
                )

                col3.metric(
                    "Severity",
                    ticket["severity"]
                )

                st.divider()

                st.subheader(
                    "👤 Student Details"
                )

                st.write(
                    f"**Name:** {ticket['student_name']}"
                )

                st.write(
                    f"**Register Number:** "
                    f"{ticket['register_number']}"
                )

                st.divider()

                st.subheader(
                    "🎫 Ticket Details"
                )

                st.write(
                    f"**Issue:** {ticket['issue_title']}"
                )

                st.write(
                    f"**Category:** "
                    f"{ticket['issue_category']}"
                )

                st.write(
                    f"**Building:** {ticket['location']}"
                )

                st.write(
                    f"**Room / Exact Location:** "
                    f"{ticket['room']}"
                )

                st.write(
                    f"**Description:** "
                    f"{ticket['description']}"
                )

                st.write(
                    f"**Recommended Action:** "
                    f"{ticket['recommended_action']}"
                )

                st.write(
                    f"**Created:** {created_datetime}"
                )

                st.write(
                    f"**Ticket Directed To:** "
                    f"{ticket['assigned_department']}"
                )

                st.divider()

                display_ticket_image(ticket)

                st.divider()

                st.subheader(
                    "📜 Update History"
                )

                updates = get_ticket_updates(
                    ticket["ticket_id"]
                )

                if len(updates) == 0:

                    st.info(
                        "There are no updates for this "
                        "ticket yet."
                    )

                else:

                    for update in updates:

                        with st.container(border=True):

                            updated_datetime = (
                                format_ticket_datetime(
                                    update["updated_at"]
                                )
                            )

                            st.write(
                                f"**Status:** "
                                f"{update['status']}"
                            )

                            if update["remarks"]:

                                st.write(
                                    f"**Admin Remarks:** "
                                    f"{update['remarks']}"
                                )

                            st.write(
                                f"**Updated:** "
                                f"{updated_datetime}"
                            )

        except Exception as error:

            st.error(
                f"Unable to load ticket: {error}"
            )


# ==================================================
# ADMIN DASHBOARD
# ==================================================

with admin_tab:

    st.header(
        "🛠️ CampusFix Admin Dashboard"
    )

    st.write(
        "View, manage, and update all maintenance tickets."
    )

    try:

        tickets = get_all_tickets()

        total_tickets = len(tickets)

        open_tickets = sum(
            1
            for ticket in tickets
            if ticket["status"] == "Open"
        )

        in_progress_tickets = sum(
            1
            for ticket in tickets
            if ticket["status"] == "In Progress"
        )

        resolved_tickets = sum(
            1
            for ticket in tickets
            if ticket["status"] == "Resolved"
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Tickets",
            total_tickets
        )

        col2.metric(
            "Open",
            open_tickets
        )

        col3.metric(
            "In Progress",
            in_progress_tickets
        )

        col4.metric(
            "Resolved",
            resolved_tickets
        )

        st.divider()

        if total_tickets == 0:

            st.info(
                "No maintenance tickets have been "
                "created yet."
            )

        else:

            st.subheader(
                "All Maintenance Tickets"
            )

            for ticket in tickets:

                ticket_id = ticket["ticket_id"]

                created_datetime = (
                    format_ticket_datetime(
                        ticket["created_at"]
                    )
                )

                with st.expander(
                    f"Ticket #{ticket_id} — "
                    f"{ticket['issue_title']} "
                    f"({ticket['status']})"
                ):

                    st.subheader(
                        "👤 Student Details"
                    )

                    st.write(
                        f"**Name:** "
                        f"{ticket['student_name']}"
                    )

                    st.write(
                        f"**Register Number:** "
                        f"{ticket['register_number']}"
                    )

                    st.divider()

                    st.subheader(
                        "🎫 Ticket Details"
                    )

                    st.write(
                        f"**Ticket ID:** {ticket_id}"
                    )

                    st.write(
                        f"**Issue:** "
                        f"{ticket['issue_title']}"
                    )

                    st.write(
                        f"**Category:** "
                        f"{ticket['issue_category']}"
                    )

                    st.write(
                        f"**Severity:** "
                        f"{ticket['severity']}"
                    )

                    st.write(
                        f"**Status:** "
                        f"{ticket['status']}"
                    )

                    st.write(
                        f"**Building:** "
                        f"{ticket['location']}"
                    )

                    st.write(
                        f"**Room / Exact Location:** "
                        f"{ticket['room']}"
                    )

                    st.write(
                        f"**Description:** "
                        f"{ticket['description']}"
                    )

                    st.write(
                        f"**Recommended Action:** "
                        f"{ticket['recommended_action']}"
                    )

                    st.write(
                        f"**Ticket Directed To:** "
                        f"{ticket['assigned_department']}"
                    )

                    st.write(
                        f"**Created:** "
                        f"{created_datetime}"
                    )

                    st.divider()

                    display_ticket_image(ticket)

                    st.divider()

                    st.subheader(
                        "Update Ticket"
                    )

                    status_options = [
                        "Open",
                        "In Progress",
                        "Resolved"
                    ]

                    current_status = ticket["status"]

                    if current_status in status_options:

                        status_index = status_options.index(
                            current_status
                        )

                    else:

                        status_index = 0

                    new_status = st.selectbox(
                        "Status",
                        status_options,
                        index=status_index,
                        key=f"status_{ticket_id}"
                    )

                    remarks = st.text_area(
                        "Admin Remarks",
                        placeholder=(
                            "Example: Technician inspected "
                            "the issue. Work is currently "
                            "in progress."
                        ),
                        key=f"remarks_{ticket_id}"
                    )

                    if st.button(
                        "Save Ticket Update",
                        type="primary",
                        key=f"save_{ticket_id}"
                    ):

                        if not remarks.strip():

                            st.warning(
                                "Please enter remarks before "
                                "saving the update."
                            )

                        else:

                            success = update_ticket_status(
                                ticket_id,
                                new_status,
                                remarks.strip()
                            )

                            if success:

                                st.success(
                                    f"Ticket #{ticket_id} "
                                    f"updated successfully!"
                                )

                                st.rerun()

                            else:

                                st.error(
                                    "Ticket update failed."
                                )

    except Exception as error:

        st.error(
            "Unable to load the Admin Dashboard."
        )

        st.exception(error)


# ==================================================
# CAMPUSFIX ASSISTANT
# ==================================================

with bot_tab:

    st.header(
        "🤖 CampusFix Assistant"
    )

    st.write(
        "I can help you report a maintenance issue, "
        "track an existing ticket, or explain how "
        "CampusFix works."
    )

    st.divider()

    bot_option = st.radio(
        "How can I help you today?",
        [
            "📝 Report New Issue",
            "🔎 Track My Ticket",
            "ℹ️ Help & Guide"
        ],
        key="bot_option"
    )


    # ==============================================
    # BOT - REPORT NEW ISSUE
    # ==============================================

    if bot_option == "📝 Report New Issue":

        st.subheader(
            "🤖 Let's report your maintenance issue"
        )

        bot_student_name = st.text_input(
            "Student Name",
            key="bot_student_name"
        )

        bot_register_number = st.text_input(
            "Register Number",
            key="bot_register_number"
        )

        bot_location = st.selectbox(
            "Select Building / Location",
            options=list(CAMPUS_LOCATIONS.keys()),
            key="bot_location"
        )

        bot_room = st.selectbox(
            "Select Room / Exact Location",
            options=CAMPUS_LOCATIONS[bot_location],
            key="bot_room"
        )

        bot_description = st.text_area(
            "Describe what is wrong",
            placeholder=(
                "Example: The ceiling fan is shaking "
                "and making a loud noise."
            ),
            key="bot_description"
        )

        bot_uploaded_image = st.file_uploader(
            "Upload Issue Image",
            type=["jpg", "jpeg", "png"],
            key="bot_image"
        )

        if bot_uploaded_image is not None:

            st.image(
                bot_uploaded_image,
                caption=(
                    "Image received by CampusFix Assistant"
                ),
                use_container_width=True
            )

        if st.button(
            "🤖 Create My Ticket",
            type="primary",
            key="bot_create_ticket"
        ):

            if not bot_student_name.strip():

                st.error(
                    "🤖 Please enter your name."
                )

            elif not bot_register_number.strip():

                st.error(
                    "🤖 Please enter your register number."
                )

            elif bot_uploaded_image is None:

                st.error(
                    "🤖 Please upload an image of the "
                    "maintenance issue."
                )

            else:

                try:

                    with st.spinner(
                        "🤖 Creating your maintenance ticket..."
                    ):

                        (
                            bot_ticket_id,
                            result,
                            performance_info
                        ) = create_maintenance_ticket(
                            bot_student_name,
                            bot_register_number,
                            bot_location,
                            bot_room,
                            bot_description,
                            bot_uploaded_image,
                            "bot_ticket"
                        )

                    if bot_ticket_id is None:

                        st.error(
                            f"🤖 {result}"
                        )

                    else:

                        display_created_ticket(
                            bot_ticket_id,
                            result,
                            bot_student_name,
                            bot_register_number,
                            performance_info
                        )

                except Exception as error:

                    st.error(
                        f"🤖 I was unable to process the "
                        f"issue: {error}"
                    )


    # ==============================================
    # BOT - TRACK TICKET
    # ==============================================

    elif bot_option == "🔎 Track My Ticket":

        st.subheader(
            "🤖 Let's track your maintenance ticket"
        )

        bot_track_id = st.number_input(
            "Enter Ticket ID",
            min_value=1,
            step=1,
            value=1,
            key="bot_track_id"
        )

        if st.button(
            "🤖 Check My Ticket",
            type="primary",
            key="bot_track_button"
        ):

            try:

                ticket = get_ticket_details(
                    bot_track_id
                )

                if ticket is None:

                    st.error(
                        f"🤖 I could not find Ticket "
                        f"#{bot_track_id}."
                    )

                else:

                    st.success(
                        f"🤖 I found your Ticket "
                        f"#{ticket['ticket_id']}!"
                    )

                    st.write(
                        f"**Issue:** "
                        f"{ticket['issue_title']}"
                    )

                    st.write(
                        f"**Category:** "
                        f"{ticket['issue_category']}"
                    )

                    st.write(
                        f"**Severity:** "
                        f"{ticket['severity']}"
                    )

                    st.write(
                        f"**Status:** "
                        f"{ticket['status']}"
                    )

                    st.write(
                        f"**Description:** "
                        f"{ticket['description']}"
                    )

                    st.write(
                        f"**Recommended Action:** "
                        f"{ticket['recommended_action']}"
                    )

                    st.write(
                        f"**Ticket Directed To:** "
                        f"{ticket['assigned_department']}"
                    )

                    display_ticket_image(ticket)

                    updates = get_ticket_updates(
                        ticket["ticket_id"]
                    )

                    st.divider()

                    st.subheader(
                        "🤖 Latest Updates"
                    )

                    if len(updates) == 0:

                        st.info(
                            "🤖 There are no admin updates "
                            "for this ticket yet."
                        )

                    else:

                        for update in updates:

                            with st.container(border=True):

                                st.write(
                                    f"**Status:** "
                                    f"{update['status']}"
                                )

                                if update["remarks"]:

                                    st.write(
                                        f"**Admin Remarks:** "
                                        f"{update['remarks']}"
                                    )

                                st.write(
                                    f"**Updated:** "
                                    f"{format_ticket_datetime(update['updated_at'])}"
                                )

            except Exception as error:

                st.error(
                    f"🤖 Unable to retrieve your ticket: "
                    f"{error}"
                )


    # ==============================================
    # BOT - HELP & GUIDE
    # ==============================================

    elif bot_option == "ℹ️ Help & Guide":

        st.subheader(
            "🤖 CampusFix Help & Guide"
        )

        st.write(
            "CampusFix helps students report and track "
            "campus maintenance problems quickly."
        )

        st.divider()

        st.subheader(
            "📝 Report New Issue"
        )

        st.write(
            "Enter your details, select the location, "
            "describe the problem, and upload an image."
        )

        st.write(
            "CampusFix quickly analyzes the reported "
            "information and creates a maintenance ticket."
        )

        st.divider()

        st.subheader(
            "🔎 Track My Ticket"
        )

        st.write(
            "Use your Ticket ID to check its status "
            "and administrator updates."
        )

        st.divider()

        st.subheader(
            "🛠️ How Ticket Updates Work"
        )

        st.write(
            "Administrators can update tickets as Open, "
            "In Progress, or Resolved and add remarks."
        )

        st.write(
            "You can view these updates later using "
            "your Ticket ID."
        )

        st.info(
            "Tip: Always save your Ticket ID after "
            "creating a maintenance ticket."
        )