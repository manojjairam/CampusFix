import streamlit as st
import os
from datetime import datetime

from src.vision_analyzer import analyze_issue_image
from src.ticket_generator import generate_ticket
from src.safety_checker import check_safety
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

def format_ticket_date(date_value):

    if not date_value:
        return "Not available"

    try:

        date_object = datetime.strptime(
            str(date_value),
            "%Y-%m-%d %H:%M:%S"
        )

        return date_object.strftime(
            "%d %b %Y"
        )

    except ValueError:

        return str(date_value)


def parse_ticket_result(ticket_result):

    ticket_data = {}

    for line in str(ticket_result).split("\n"):

        if ":" in line:

            key, value = line.split(":", 1)

            ticket_data[
                key.strip().lower()
            ] = value.strip()

    return ticket_data


# ==================================================
# APP HEADER
# ==================================================

st.title("🏫 CampusFix")

st.subheader(
    "AI-Powered Campus Maintenance Issue Reporting System"
)

st.write(
    "Report campus maintenance issues using images and AI. "
    "CampusFix analyzes the issue, generates maintenance tickets, "
    "checks severity, and allows students to track ticket updates."
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

    st.header("Report a Maintenance Issue")

    st.subheader("👤 Student Details")

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

    st.subheader("🎫 Issue Details")

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
            "Example: The ceiling fan is shaking and making "
            "a loud noise."
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
                "Please upload an image of the maintenance issue."
            )

        else:

            image_path = "temp_issue_image.jpg"

            try:

                with st.spinner(
                    "CampusFix AI is analyzing the maintenance issue..."
                ):

                    with open(
                        image_path,
                        "wb"
                    ) as file:

                        file.write(
                            uploaded_image.getbuffer()
                        )

                    # ------------------------------------------
                    # IMAGE ANALYSIS
                    # ------------------------------------------

                    vision_result = analyze_issue_image(
                        image_path,
                        student_description
                    )

                    if str(vision_result).startswith("Error"):

                        st.error(
                            vision_result
                        )

                    else:

                        # --------------------------------------
                        # TICKET GENERATION
                        # --------------------------------------

                        ticket_result = generate_ticket(
                            vision_analysis=vision_result,
                            location=location,
                            room=room,
                            user_description=student_description
                        )

                        if str(ticket_result).startswith("Error"):

                            st.error(
                                ticket_result
                            )

                        else:

                            ticket_data = parse_ticket_result(
                                ticket_result
                            )

                            # ----------------------------------
                            # SAFETY / SEVERITY CHECK
                            # ----------------------------------

                            safety_result = check_safety(
                                ticket_result
                            )

                            if isinstance(
                                safety_result,
                                dict
                            ):

                                severity = safety_result.get(
                                    "severity",
                                    ticket_data.get(
                                        "severity",
                                        "Normal"
                                    )
                                )

                                assigned_department = (
                                    safety_result.get(
                                        "assigned_department",
                                        ticket_data.get(
                                            "assigned department",
                                            "General Maintenance"
                                        )
                                    )
                                )

                            else:

                                severity = ticket_data.get(
                                    "severity",
                                    "Normal"
                                )

                                assigned_department = (
                                    ticket_data.get(
                                        "assigned department",
                                        "General Maintenance"
                                    )
                                )

                            # ----------------------------------
                            # DATABASE TICKET
                            # ----------------------------------

                            database_ticket = {

                                "student_name": (
                                    student_name.strip()
                                ),

                                "register_number": (
                                    register_number.strip()
                                ),

                                "issue_category": (
                                    ticket_data.get(
                                        "issue category",
                                        "General Maintenance"
                                    )
                                ),

                                "issue_title": (
                                    ticket_data.get(
                                        "issue title",
                                        "Maintenance Issue"
                                    )
                                ),

                                "severity": severity,

                                "description": (
                                    ticket_data.get(
                                        "description",
                                        student_description
                                    )
                                ),

                                "recommended_action": (
                                    ticket_data.get(
                                        "recommended action",
                                        "Maintenance inspection required"
                                    )
                                ),

                                "assigned_department": (
                                    assigned_department
                                ),

                                "location": location,

                                "room": room,

                                "student_description": (
                                    student_description
                                ),

                                "escalation": (
                                    assigned_department
                                )
                            }

                            ticket_id = save_ticket(
                                database_ticket
                            )

                            created_date = datetime.now().strftime(
                                "%d %b %Y"
                            )

                            st.success(
                                "Maintenance ticket created successfully!"
                            )

                            st.divider()

                            st.subheader("👤 Student Details")

                            st.write(
                                f"**Name:** {student_name}"
                            )

                            st.write(
                                f"**Register Number:** "
                                f"{register_number}"
                            )

                            st.divider()

                            st.subheader("🎫 Ticket Details")

                            st.write(
                                f"**Ticket ID:** {ticket_id}"
                            )

                            st.write(
                                f"**Issue:** "
                                f"{database_ticket['issue_title']}"
                            )

                            st.write(
                                f"**Category:** "
                                f"{database_ticket['issue_category']}"
                            )

                            st.write(
                                f"**Severity:** {severity}"
                            )

                            st.write(
                                f"**Created:** {created_date}"
                            )

                            st.write(
                                f"**Ticket Directed To:** "
                                f"{assigned_department}"
                            )

                            st.info(
                                "Please save your Ticket ID to track "
                                "future updates."
                            )

            except Exception as error:

                st.error(
                    f"Unable to process the maintenance issue: {error}"
                )

            finally:

                if os.path.exists(image_path):

                    os.remove(image_path)


# ==================================================
# TRACK TICKET
# ==================================================

with track_tab:

    st.header("🔎 Track Your Maintenance Ticket")

    st.write(
        "Enter your Ticket ID to view its current status "
        "and update history."
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

                created_date = format_ticket_date(
                    ticket["created_at"]
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

                st.subheader("👤 Student Details")

                st.write(
                    f"**Name:** {ticket['student_name']}"
                )

                st.write(
                    f"**Register Number:** "
                    f"{ticket['register_number']}"
                )

                st.divider()

                st.subheader("🎫 Ticket Details")

                st.write(
                    f"**Issue:** {ticket['issue_title']}"
                )

                st.write(
                    f"**Category:** "
                    f"{ticket['issue_category']}"
                )

                st.write(
                    f"**Created:** {created_date}"
                )

                st.write(
                    f"**Ticket Directed To:** "
                    f"{ticket['assigned_department']}"
                )

                st.divider()

                st.subheader("📜 Update History")

                updates = get_ticket_updates(
                    ticket["ticket_id"]
                )

                if len(updates) == 0:

                    st.info(
                        "There are no updates for this ticket yet."
                    )

                else:

                    for update in updates:

                        with st.container(border=True):

                            updated_date = format_ticket_date(
                                update["updated_at"]
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
                                f"**Updated:** {updated_date}"
                            )

        except Exception as error:

            st.error(
                f"Unable to load ticket: {error}"
            )


# ==================================================
# ADMIN DASHBOARD
# ==================================================

with admin_tab:

    st.header("🛠️ CampusFix Admin Dashboard")

    st.write(
        "View, manage, and update all maintenance tickets."
    )

    try:

        tickets = get_all_tickets()

        total_tickets = len(tickets)

        open_tickets = sum(
            1 for ticket in tickets
            if ticket["status"] == "Open"
        )

        in_progress_tickets = sum(
            1 for ticket in tickets
            if ticket["status"] == "In Progress"
        )

        resolved_tickets = sum(
            1 for ticket in tickets
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
                "No maintenance tickets have been created yet."
            )

        else:

            st.subheader(
                "All Maintenance Tickets"
            )

            for ticket in tickets:

                ticket_id = ticket["ticket_id"]

                created_date = format_ticket_date(
                    ticket["created_at"]
                )

                with st.expander(
                    f"Ticket #{ticket_id} — "
                    f"{ticket['issue_title']} "
                    f"({ticket['status']})"
                ):

                    # ------------------------------
                    # STUDENT DETAILS
                    # ------------------------------

                    st.subheader("👤 Student Details")

                    st.write(
                        f"**Name:** "
                        f"{ticket['student_name']}"
                    )

                    st.write(
                        f"**Register Number:** "
                        f"{ticket['register_number']}"
                    )

                    st.divider()

                    # ------------------------------
                    # TICKET DETAILS
                    # ------------------------------

                    st.subheader("🎫 Ticket Details")

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
                        f"{created_date}"
                    )

                    # IMPORTANT:
                    # safety_risk has been completely removed.
                    # There must be NO reference to:
                    # ticket["safety_risk"]

                    st.divider()

                    # ------------------------------
                    # UPDATE TICKET
                    # ------------------------------

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
                            "Example: Technician inspected the "
                            "issue. Work is currently in progress."
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
                                "Please enter remarks before saving "
                                "the update."
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

    st.header("🤖 CampusFix Assistant")

    st.write(
        "I can help you report a new maintenance issue, "
        "track an existing ticket, or explain how CampusFix works."
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


    # ==================================================
    # BOT - REPORT NEW ISSUE
    # ==================================================

    if bot_option == "📝 Report New Issue":

        st.subheader(
            "🤖 Let's report your maintenance issue"
        )

        st.write(
            "**Step 1 of 8 — Enter your full name.**"
        )

        bot_student_name = st.text_input(
            "Student Name",
            key="bot_student_name"
        )

        st.write(
            "**Step 2 of 8 — Enter your register number.**"
        )

        bot_register_number = st.text_input(
            "Register Number",
            key="bot_register_number"
        )

        st.write(
            "**Step 3 of 8 — Select the building or location.**"
        )

        bot_location = st.selectbox(
            "Select Building / Location",
            options=list(CAMPUS_LOCATIONS.keys()),
            key="bot_location"
        )

        st.write(
            "**Step 4 of 8 — Select the room or exact location.**"
        )

        bot_room = st.selectbox(
            "Select Room / Exact Location",
            options=CAMPUS_LOCATIONS[bot_location],
            key="bot_room"
        )

        st.write(
            "**Step 5 of 8 — Describe the issue.**"
        )

        bot_description = st.text_area(
            "Describe what is wrong",
            placeholder=(
                "Example: The ceiling fan is shaking and making "
                "a loud noise."
            ),
            key="bot_description"
        )

        st.write(
            "**Step 6 of 8 — Upload an image of the issue.**"
        )

        bot_uploaded_image = st.file_uploader(
            "Upload Issue Image",
            type=["jpg", "jpeg", "png"],
            key="bot_image"
        )

        if bot_uploaded_image is not None:

            st.image(
                bot_uploaded_image,
                caption="Image received by CampusFix Assistant",
                use_container_width=True
            )

        if st.button(
            "🤖 Analyze Issue and Create Ticket",
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
                    "🤖 Please upload an image so I can analyze "
                    "the maintenance issue."
                )

            else:

                bot_image_path = (
                    "temp_bot_issue_image.jpg"
                )

                try:

                    with st.spinner(
                        "🤖 CampusFix Assistant is analyzing "
                        "your maintenance issue..."
                    ):

                        with open(
                            bot_image_path,
                            "wb"
                        ) as file:

                            file.write(
                                bot_uploaded_image.getbuffer()
                            )

                        vision_result = analyze_issue_image(
                            bot_image_path,
                            bot_description
                        )

                        if str(
                            vision_result
                        ).startswith("Error"):

                            st.error(
                                vision_result
                            )

                        else:

                            ticket_result = generate_ticket(
                                vision_analysis=vision_result,
                                location=bot_location,
                                room=bot_room,
                                user_description=bot_description
                            )

                            if str(
                                ticket_result
                            ).startswith("Error"):

                                st.error(
                                    ticket_result
                                )

                            else:

                                ticket_data = (
                                    parse_ticket_result(
                                        ticket_result
                                    )
                                )

                                safety_result = (
                                    check_safety(
                                        ticket_result
                                    )
                                )

                                if isinstance(
                                    safety_result,
                                    dict
                                ):

                                    bot_severity = (
                                        safety_result.get(
                                            "severity",
                                            ticket_data.get(
                                                "severity",
                                                "Normal"
                                            )
                                        )
                                    )

                                    bot_assigned_department = (
                                        safety_result.get(
                                            "assigned_department",
                                            ticket_data.get(
                                                "assigned department",
                                                "General Maintenance"
                                            )
                                        )
                                    )

                                else:

                                    bot_severity = (
                                        ticket_data.get(
                                            "severity",
                                            "Normal"
                                        )
                                    )

                                    bot_assigned_department = (
                                        ticket_data.get(
                                            "assigned department",
                                            "General Maintenance"
                                        )
                                    )

                                database_ticket = {

                                    "student_name": (
                                        bot_student_name.strip()
                                    ),

                                    "register_number": (
                                        bot_register_number.strip()
                                    ),

                                    "issue_category": (
                                        ticket_data.get(
                                            "issue category",
                                            "General Maintenance"
                                        )
                                    ),

                                    "issue_title": (
                                        ticket_data.get(
                                            "issue title",
                                            "Maintenance Issue"
                                        )
                                    ),

                                    "severity": (
                                        bot_severity
                                    ),

                                    "description": (
                                        ticket_data.get(
                                            "description",
                                            bot_description
                                        )
                                    ),

                                    "recommended_action": (
                                        ticket_data.get(
                                            "recommended action",
                                            "Maintenance inspection "
                                            "required"
                                        )
                                    ),

                                    "assigned_department": (
                                        bot_assigned_department
                                    ),

                                    "location": (
                                        bot_location
                                    ),

                                    "room": (
                                        bot_room
                                    ),

                                    "student_description": (
                                        bot_description
                                    ),

                                    "escalation": (
                                        bot_assigned_department
                                    )
                                }

                                bot_ticket_id = save_ticket(
                                    database_ticket
                                )

                                created_date = (
                                    datetime.now().strftime(
                                        "%d %b %Y"
                                    )
                                )

                                st.success(
                                    "🤖 Your maintenance ticket has "
                                    "been created successfully!"
                                )

                                st.divider()

                                st.subheader(
                                    "👤 Student Details"
                                )

                                st.write(
                                    f"**Name:** "
                                    f"{bot_student_name}"
                                )

                                st.write(
                                    f"**Register Number:** "
                                    f"{bot_register_number}"
                                )

                                st.divider()

                                st.subheader(
                                    "🎫 Ticket Details"
                                )

                                st.write(
                                    f"**Ticket ID:** "
                                    f"{bot_ticket_id}"
                                )

                                st.write(
                                    f"**Issue:** "
                                    f"{database_ticket['issue_title']}"
                                )

                                st.write(
                                    f"**Category:** "
                                    f"{database_ticket['issue_category']}"
                                )

                                st.write(
                                    f"**Severity:** "
                                    f"{bot_severity}"
                                )

                                st.write(
                                    f"**Created:** "
                                    f"{created_date}"
                                )

                                st.write(
                                    f"**Ticket Directed To:** "
                                    f"{bot_assigned_department}"
                                )

                                st.info(
                                    "🤖 Please save your Ticket ID. "
                                    "You can use it later to track "
                                    "the maintenance status."
                                )

                except Exception as error:

                    st.error(
                        f"🤖 I was unable to process the issue: "
                        f"{error}"
                    )

                finally:

                    if os.path.exists(
                        bot_image_path
                    ):

                        os.remove(
                            bot_image_path
                        )


    # ==================================================
    # BOT - TRACK TICKET
    # ==================================================

    elif bot_option == "🔎 Track My Ticket":

        st.subheader(
            "🤖 Let's track your maintenance ticket"
        )

        st.write(
            "Please enter the Ticket ID you received when "
            "your issue was created."
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
                        f"#{bot_track_id}. Please check the "
                        "Ticket ID and try again."
                    )

                else:

                    created_date = format_ticket_date(
                        ticket["created_at"]
                    )

                    st.success(
                        f"🤖 I found your Ticket "
                        f"#{ticket['ticket_id']}!"
                    )

                    st.divider()

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
                        f"**Ticket ID:** "
                        f"{ticket['ticket_id']}"
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
                        f"**Created:** "
                        f"{created_date}"
                    )

                    st.write(
                        f"**Ticket Directed To:** "
                        f"{ticket['assigned_department']}"
                    )

                    st.divider()

                    st.subheader(
                        "🤖 Latest Updates"
                    )

                    updates = get_ticket_updates(
                        ticket["ticket_id"]
                    )

                    if len(updates) == 0:

                        st.info(
                            "🤖 There are currently no admin "
                            "updates. Your ticket is still being "
                            "processed."
                        )

                    else:

                        for update in updates:

                            with st.container(
                                border=True
                            ):

                                updated_date = (
                                    format_ticket_date(
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
                                    f"{updated_date}"
                                )

            except Exception as error:

                st.error(
                    f"🤖 I was unable to retrieve your ticket: "
                    f"{error}"
                )


    # ==================================================
    # BOT - HELP & GUIDE
    # ==================================================

    elif bot_option == "ℹ️ Help & Guide":

        st.subheader(
            "🤖 CampusFix Help & Guide"
        )

        st.write(
            "CampusFix helps students report and track "
            "campus maintenance problems."
        )

        st.divider()

        st.subheader(
            "📝 Report New Issue"
        )

        st.write(
            "Enter your name and register number, select the "
            "building and room, upload an image, and describe "
            "the problem."
        )

        st.write(
            "The local AI analyzes the image and generates a "
            "maintenance ticket."
        )

        st.divider()

        st.subheader(
            "🔎 Track My Ticket"
        )

        st.write(
            "Use the Ticket ID received after creating an issue "
            "to check the current status and administrator "
            "updates."
        )

        st.divider()

        st.subheader(
            "🛠️ How Ticket Updates Work"
        )

        st.write(
            "Campus administrators can view every submitted "
            "ticket from the Admin Dashboard."
        )

        st.write(
            "They can change the ticket status to Open, "
            "In Progress, or Resolved and add remarks."
        )

        st.write(
            "Students can later see these updates using their "
            "Ticket ID."
        )

        st.info(
            "Tip: Always save your Ticket ID after successfully "
            "creating a maintenance ticket."
        )