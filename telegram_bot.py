# ==================================================
# CAMPUSFIX TELEGRAM BOT
# ==================================================
#
# Flow:
#
# /start
#    ↓
# Report New Issue
#    ↓
# Student Name
#    ↓
# Register Number
#    ↓
# Select Building
#    ↓
# Select Room
#    ↓
# Upload Image
#    ↓
# Moondream AI analyzes image
#    ↓
# Ticket created automatically
#
# ==================================================


import os
import uuid
import asyncio
from datetime import datetime


from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)


# ==================================================
# CAMPUSFIX AI
# ==================================================
#
# IMPORTANT:
# We now use ONLY image analysis.
# No strict validation.
#
# ==================================================

from src.vision_analyzer import analyze_issue_image


# ==================================================
# DATABASE
# ==================================================

from src.database import (
    save_ticket,
    get_ticket_details,
    get_ticket_updates
)


# ==================================================
# TELEGRAM BOT TOKEN
# ==================================================

BOT_TOKEN = "8951240259:AAHe6J3BJGn-DCd3mwnp0KOjuRAW0-2niZE"


# ==================================================
# CAMPUS LOCATIONS
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
# CONVERSATION STATES
# ==================================================

(
    ENTER_STUDENT_NAME,
    ENTER_REGISTER_NUMBER,
    SELECT_BUILDING,
    SELECT_ROOM,
    UPLOAD_IMAGE,
    TRACK_TICKET
) = range(6)


# ==================================================
# MAIN MENU
# ==================================================

def get_main_menu():

    keyboard = [

        [
            "📝 Report New Issue"
        ],

        [
            "🔎 Track Ticket",
            "ℹ️ Help & Guide"
        ]

    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


# ==================================================
# FORMAT DATE
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
            "%d %b %Y, %H:%M:%S"
        )

    except ValueError:

        return str(date_value)


# ==================================================
# PARSE AI RESULT
# ==================================================

def parse_ai_result(ai_result):

    ticket_data = {}

    expected_fields = {
        "issue category",
        "issue title",
        "severity",
        "description",
        "recommended action",
        "assigned department"
    }


    for line in str(ai_result).splitlines():

        line = line.strip()

        if ":" not in line:
            continue


        key, value = line.split(
            ":",
            1
        )


        key = key.strip().lower()
        value = value.strip()


        if key in expected_fields and value:
            ticket_data[key] = value


    return ticket_data


# ==================================================
# VALIDATE SEVERITY
# ==================================================

def validate_severity(severity):

    valid_severities = [
        "Low",
        "Normal",
        "High",
        "Critical"
    ]


    if not severity:
        return "Normal"


    severity = severity.strip().title()


    if severity in valid_severities:
        return severity


    return "Normal"


# ==================================================
# DETERMINE CATEGORY FROM ISSUE TITLE
# ==================================================

def determine_category(issue_title):

    title = issue_title.lower()


    if any(
        word in title
        for word in [
            "chair",
            "table",
            "desk",
            "bench",
            "furniture",
            "cupboard",
            "cabinet"
        ]
    ):
        return "Furniture Maintenance"


    if any(
        word in title
        for word in [
            "light",
            "switch",
            "socket",
            "wire",
            "electrical",
            "power"
        ]
    ):
        return "Electrical Maintenance"


    if any(
        word in title
        for word in [
            "pipe",
            "tap",
            "sink",
            "leak",
            "water",
            "toilet"
        ]
    ):
        return "Plumbing"


    if any(
        word in title
        for word in [
            "wall",
            "ceiling",
            "floor",
            "tile",
            "door",
            "window",
            "crack"
        ]
    ):
        return "Civil Maintenance"


    if any(
        word in title
        for word in [
            "fan",
            "air conditioner",
            "ac",
            "hvac"
        ]
    ):
        return "HVAC"


    if any(
        word in title
        for word in [
            "computer",
            "monitor",
            "keyboard",
            "mouse",
            "printer"
        ]
    ):
        return "IT Equipment"


    return "General Maintenance"


# ==================================================
# DETERMINE DEPARTMENT
# ==================================================

def determine_department(category):

    department_map = {

        "Furniture Maintenance":
            "Facilities Management",

        "Electrical Maintenance":
            "Electrical Maintenance Department",

        "Plumbing":
            "Plumbing Department",

        "Civil Maintenance":
            "Civil Maintenance Department",

        "HVAC":
            "Facilities Management",

        "IT Equipment":
            "IT Support Department",

        "Cleaning and Sanitation":
            "Housekeeping Department",

        "Safety Maintenance":
            "Facilities Management",

        "General Maintenance":
            "General Maintenance Department"
    }


    return department_map.get(
        category,
        "General Maintenance Department"
    )


# ==================================================
# COMPLETE PARTIAL AI RESULT
# ==================================================
#
# This is the important fix.
#
# Even if Moondream returns only:
#
# Issue Title: Broken chair leg
#
# We automatically complete the ticket.
#
# ==================================================

def complete_ticket_data(ticket_data):


    issue_title = ticket_data.get(
        "issue title",
        ""
    ).strip()


    # ----------------------------------------------
    # If no title was detected, return None
    # ----------------------------------------------

    if not issue_title:

        return None


    # ----------------------------------------------
    # CATEGORY
    # ----------------------------------------------

    issue_category = ticket_data.get(
        "issue category"
    )


    if not issue_category:

        issue_category = determine_category(
            issue_title
        )


    # ----------------------------------------------
    # SEVERITY
    # ----------------------------------------------

    severity = validate_severity(
        ticket_data.get(
            "severity",
            "Normal"
        )
    )


    # ----------------------------------------------
    # DESCRIPTION
    # ----------------------------------------------

    description = ticket_data.get(
        "description"
    )


    if not description:

        description = (
            f"Visible maintenance issue detected: "
            f"{issue_title}."
        )


    # ----------------------------------------------
    # RECOMMENDED ACTION
    # ----------------------------------------------

    recommended_action = ticket_data.get(
        "recommended action"
    )


    if not recommended_action:

        recommended_action = (
            "Inspect and repair the affected item."
        )


    # ----------------------------------------------
    # ASSIGNED DEPARTMENT
    # ----------------------------------------------

    assigned_department = ticket_data.get(
        "assigned department"
    )


    if not assigned_department:

        assigned_department = determine_department(
            issue_category
        )


    return {

        "issue category":
            issue_category,

        "issue title":
            issue_title,

        "severity":
            severity,

        "description":
            description,

        "recommended action":
            recommended_action,

        "assigned department":
            assigned_department

    }


# ==================================================
# START COMMAND
# ==================================================

async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data.clear()


    await update.message.reply_text(

        "🏫 Welcome to CampusFix!\n\n"

        "CampusFix uses local AI to identify campus "
        "maintenance problems from uploaded images.\n\n"

        "Simply upload a clear image of the issue and "
        "CampusFix AI will analyze it and automatically "
        "create a maintenance ticket.",

        reply_markup=get_main_menu()

    )


# ==================================================
# HELP COMMAND
# ==================================================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    help_message = (

        "ℹ️ CAMPUSFIX HELP & GUIDE\n"
        "━━━━━━━━━━━━━━━━━━\n\n"

        "📝 REPORT NEW ISSUE\n\n"

        "1. Enter your name\n"
        "2. Enter your register number\n"
        "3. Select the building\n"
        "4. Select the room or location\n"
        "5. Upload a clear photo\n\n"

        "🤖 CampusFix AI analyzes the uploaded "
        "image and automatically creates the "
        "maintenance ticket.\n\n"

        "🔎 TRACK TICKET\n\n"

        "Enter your Ticket ID to check:\n\n"

        "• Current ticket status\n"
        "• Admin remarks\n"
        "• Previous updates\n\n"

        "❌ CANCEL\n\n"

        "Type /cancel at any time."

    )


    await update.message.reply_text(

        help_message,

        reply_markup=get_main_menu()

    )


# ==================================================
# REPORT ISSUE START
# ==================================================

async def report_issue_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data.clear()


    await update.message.reply_text(

        "📝 REPORT NEW ISSUE\n\n"

        "CampusFix AI will identify the maintenance "
        "problem from your uploaded image.\n\n"

        "Step 1 of 5: Please enter your full name.",

        reply_markup=ReplyKeyboardRemove()

    )


    return ENTER_STUDENT_NAME


# ==================================================
# ENTER STUDENT NAME
# ==================================================

async def enter_student_name(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    student_name = update.message.text.strip()


    if not student_name:

        await update.message.reply_text(
            "Please enter your full name."
        )

        return ENTER_STUDENT_NAME


    context.user_data[
        "student_name"
    ] = student_name


    await update.message.reply_text(

        "Step 2 of 5: Please enter your "
        "register number."

    )


    return ENTER_REGISTER_NUMBER


# ==================================================
# ENTER REGISTER NUMBER
# ==================================================

async def enter_register_number(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    register_number = update.message.text.strip()


    if not register_number:

        await update.message.reply_text(
            "Please enter your register number."
        )

        return ENTER_REGISTER_NUMBER


    context.user_data[
        "register_number"
    ] = register_number


    building_keyboard = [

        [building]

        for building in CAMPUS_LOCATIONS.keys()

    ]


    await update.message.reply_text(

        "Step 3 of 5: Select the building "
        "or location:",

        reply_markup=ReplyKeyboardMarkup(
            building_keyboard,
            resize_keyboard=True
        )

    )


    return SELECT_BUILDING


# ==================================================
# SELECT BUILDING
# ==================================================

async def select_building(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    building = update.message.text.strip()


    if building not in CAMPUS_LOCATIONS:

        await update.message.reply_text(

            "Please select a building using "
            "the buttons."

        )

        return SELECT_BUILDING


    context.user_data[
        "location"
    ] = building


    room_keyboard = [

        [room]

        for room in CAMPUS_LOCATIONS[building]

    ]


    await update.message.reply_text(

        f"Selected Building: {building}\n\n"

        "Step 4 of 5: Select the room or "
        "exact location:",

        reply_markup=ReplyKeyboardMarkup(
            room_keyboard,
            resize_keyboard=True
        )

    )


    return SELECT_ROOM


# ==================================================
# SELECT ROOM
# ==================================================

async def select_room(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    room = update.message.text.strip()


    building = context.user_data.get(
        "location"
    )


    if building not in CAMPUS_LOCATIONS:

        await update.message.reply_text(

            "Something went wrong. "
            "Please start again.",

            reply_markup=get_main_menu()

        )

        return ConversationHandler.END


    if room not in CAMPUS_LOCATIONS[building]:

        await update.message.reply_text(

            "Please select a room using "
            "the buttons."

        )

        return SELECT_ROOM


    context.user_data[
        "room"
    ] = room


    await update.message.reply_text(

        f"Building: {building}\n"
        f"Location: {room}\n\n"

        "Step 5 of 5: Upload a clear photo "
        "of the maintenance issue.\n\n"

        "🤖 CampusFix AI will automatically "
        "analyze the image and create your ticket.",

        reply_markup=ReplyKeyboardRemove()

    )


    return UPLOAD_IMAGE


# ==================================================
# UPLOAD IMAGE
# ANALYZE IMAGE
# CREATE TICKET
# ==================================================

async def upload_image(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    image_path = None
    processing_message = None


    try:


        # ==========================================
        # GET USER DATA
        # ==========================================

        student_name = context.user_data.get(
            "student_name"
        )

        register_number = context.user_data.get(
            "register_number"
        )

        location = context.user_data.get(
            "location"
        )

        room = context.user_data.get(
            "room"
        )


        # ==========================================
        # CHECK REQUIRED DATA
        # ==========================================

        if not all([
            student_name,
            register_number,
            location,
            room
        ]):

            await update.message.reply_text(

                "❌ Your previous information is missing.\n\n"

                "Please start the report again.",

                reply_markup=get_main_menu()

            )

            context.user_data.clear()

            return ConversationHandler.END


        # ==========================================
        # CHECK PHOTO
        # ==========================================

        if (
            not update.message
            or
            not update.message.photo
        ):

            await update.message.reply_text(

                "📷 Please upload a photo of the "
                "maintenance issue."

            )

            return UPLOAD_IMAGE


        photo = update.message.photo[-1]


        # ==========================================
        # PROCESSING MESSAGE
        # ==========================================

        processing_message = (

            await update.message.reply_text(

                "📷 Image received successfully.\n\n"

                "🤖 CampusFix AI is analyzing "
                "the image...\n\n"

                "Please wait."

            )

        )


        # ==========================================
        # DOWNLOAD IMAGE
        # ==========================================

        telegram_file = await photo.get_file()


        os.makedirs(
            "data",
            exist_ok=True
        )


        image_filename = (
            f"telegram_issue_"
            f"{uuid.uuid4().hex}.jpg"
        )


        image_path = os.path.join(
            "data",
            image_filename
        )


        await telegram_file.download_to_drive(
            image_path
        )


        # ==========================================
        # RUN AI ANALYSIS
        # ==========================================

        vision_result = await asyncio.to_thread(

            analyze_issue_image,

            image_path,

            "",

            location,

            room

        )


        # ==========================================
        # PRINT RESULT FOR DEBUGGING
        # ==========================================

        print("\n========== CAMPUSFIX AI RESULT ==========")

        print(vision_result)

        print("==========================================\n")


        # ==========================================
        # CHECK AI ERROR
        # ==========================================

        if str(vision_result).startswith("Error"):

            await processing_message.edit_text(

                "❌ AI image analysis failed.\n\n"

                f"{vision_result}\n\n"

                "📷 Please upload another image."

            )

            return UPLOAD_IMAGE


        # ==========================================
        # PARSE AI RESULT
        # ==========================================

        ticket_data = parse_ai_result(
            vision_result
        )


        # ==========================================
        # COMPLETE PARTIAL AI RESPONSE
        # ==========================================

        ticket_data = complete_ticket_data(
            ticket_data
        )


        # ==========================================
        # NO ISSUE TITLE
        # ==========================================

        if ticket_data is None:

            print(
                "AI did not return an Issue Title."
            )


            await processing_message.edit_text(

                "❌ CampusFix AI could not identify "
                "a maintenance issue from this image.\n\n"

                "📷 Please upload another clearer "
                "image showing the problem."

            )

            return UPLOAD_IMAGE


        # ==========================================
        # GET TICKET VALUES
        # ==========================================

        issue_category = ticket_data[
            "issue category"
        ]

        issue_title = ticket_data[
            "issue title"
        ]

        severity = ticket_data[
            "severity"
        ]

        description = ticket_data[
            "description"
        ]

        recommended_action = ticket_data[
            "recommended action"
        ]

        assigned_department = ticket_data[
            "assigned department"
        ]


        # ==========================================
        # PREPARE DATABASE TICKET
        # ==========================================

        database_ticket = {

            "student_name": student_name,

            "register_number": register_number,

            "issue_category": issue_category,

            "issue_title": issue_title,

            "severity": severity,

            "description": description,

            "recommended_action": recommended_action,

            "assigned_department": assigned_department,

            "location": location,

            "room": room,

            "student_description":
                "Automatically detected from "
                "uploaded image using CampusFix AI.",

            "image_path": image_path

        }


        # ==========================================
        # SAVE TICKET
        # ==========================================

        ticket_id = save_ticket(
            database_ticket
        )


        # ==========================================
        # DATE
        # ==========================================

        created_date = datetime.now().strftime(
            "%d %b %Y, %H:%M:%S"
        )


        # ==========================================
        # SUCCESS MESSAGE
        # ==========================================

        await processing_message.edit_text(

            "🤖 AI analysis completed.\n\n"

            "🎫 Maintenance ticket created "
            "successfully!"

        )


        # ==========================================
        # CONFIRMATION MESSAGE
        # ==========================================

        confirmation_message = (

            "✅ MAINTENANCE TICKET CREATED\n"
            "━━━━━━━━━━━━━━━━━━\n\n"

            "👤 Student Details\n"

            f"Name: {student_name}\n"

            f"Register Number: {register_number}\n\n"


            "📍 Location\n"

            f"Building: {location}\n"

            f"Room: {room}\n\n"


            "🤖 AI DETECTED ISSUE\n"

            f"Issue: {issue_title}\n"

            f"Category: {issue_category}\n"

            f"Severity: {severity}\n\n"


            "Description:\n"

            f"{description}\n\n"


            "Recommended Action:\n"

            f"{recommended_action}\n\n"


            "Ticket Directed To:\n"

            f"{assigned_department}\n\n"


            f"🎫 Ticket ID: {ticket_id}\n"

            f"Created: {created_date}\n\n"


            "Please save your Ticket ID to "
            "track future updates."

        )


        await update.message.reply_text(

            confirmation_message,

            reply_markup=get_main_menu()

        )


        # ==========================================
        # CLEAR DATA AFTER SUCCESS
        # ==========================================

        context.user_data.clear()


        return ConversationHandler.END


    except Exception as error:


        print(
            f"\nTicket creation error: {error}\n"
        )


        error_message = (

            "❌ Unable to create the maintenance "
            "ticket.\n\n"

            f"Error: {error}\n\n"

            "📷 Please upload the image again."
        )


        if processing_message:

            try:

                await processing_message.edit_text(
                    error_message
                )

            except Exception:

                await update.message.reply_text(
                    error_message
                )

        else:

            await update.message.reply_text(
                error_message
            )


        return UPLOAD_IMAGE


# ==================================================
# IMAGE REQUIRED
# ==================================================

async def image_required(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(

        "📷 Please upload a photo of the "
        "maintenance issue.\n\n"

        "You are still on Step 5 of 5."

    )


    return UPLOAD_IMAGE


# ==================================================
# TRACK TICKET START
# ==================================================

async def track_ticket_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data.clear()


    await update.message.reply_text(

        "🔎 TRACK YOUR MAINTENANCE TICKET\n\n"

        "Please enter your numeric Ticket ID.\n\n"

        "Example: 1",

        reply_markup=ReplyKeyboardRemove()

    )


    return TRACK_TICKET


# ==================================================
# SHOW TICKET DETAILS
# ==================================================

async def show_ticket_details(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    ticket_id_text = update.message.text.strip()


    if not ticket_id_text.isdigit():

        await update.message.reply_text(

            "Please enter a valid numeric "
            "Ticket ID.\n\n"

            "Example: 1"

        )

        return TRACK_TICKET


    ticket_id = int(ticket_id_text)


    try:


        ticket = get_ticket_details(
            ticket_id
        )


        if ticket is None:

            await update.message.reply_text(

                f"Ticket #{ticket_id} was not found.\n\n"

                "Please check the Ticket ID "
                "and try again."

            )

            return TRACK_TICKET


        created_date = format_ticket_date(
            ticket["created_at"]
        )


        ticket_message = (

            f"🎫 TICKET #{ticket['ticket_id']}\n"
            "━━━━━━━━━━━━━━━━━━\n\n"

            "👤 Student Details\n"

            f"Name: {ticket['student_name']}\n"

            f"Register Number: "
            f"{ticket['register_number']}\n\n"


            "📍 Location\n"

            f"Building: {ticket['location']}\n"

            f"Room: {ticket['room']}\n\n"


            "🎫 Ticket Details\n"

            f"Issue: {ticket['issue_title']}\n"

            f"Category: "
            f"{ticket['issue_category']}\n"

            f"Severity: {ticket['severity']}\n"

            f"Status: {ticket['status']}\n"

            f"Created: {created_date}\n\n"


            "Ticket Directed To:\n"

            f"{ticket['assigned_department']}\n\n"


            "Description:\n"

            f"{ticket['description']}\n\n"


            "Recommended Action:\n"

            f"{ticket['recommended_action']}"

        )


        await update.message.reply_text(
            ticket_message
        )


        updates = get_ticket_updates(
            ticket_id
        )


        if len(updates) == 0:

            await update.message.reply_text(

                "📜 UPDATE HISTORY\n\n"

                "No admin updates have been "
                "added yet."

            )


        else:

            history_message = (

                "📜 UPDATE HISTORY\n"
                "━━━━━━━━━━━━━━━━━━"
            )


            for update_item in updates:

                remarks = (

                    update_item["remarks"]

                    if update_item["remarks"]

                    else "No remarks"

                )


                updated_date = format_ticket_date(
                    update_item["updated_at"]
                )


                history_message += (

                    f"\n\nStatus: "
                    f"{update_item['status']}\n"

                    f"Remarks: {remarks}\n"

                    f"Updated: {updated_date}"

                )


            await update.message.reply_text(
                history_message
            )


        await update.message.reply_text(

            "Use the menu below to continue.",

            reply_markup=get_main_menu()

        )


        return ConversationHandler.END


    except Exception as error:


        await update.message.reply_text(

            "Unable to retrieve the ticket.\n\n"

            f"Error: {error}",

            reply_markup=get_main_menu()

        )


        return ConversationHandler.END


# ==================================================
# CANCEL
# ==================================================

async def cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data.clear()


    await update.message.reply_text(

        "Current operation cancelled.",

        reply_markup=get_main_menu()

    )


    return ConversationHandler.END


# ==================================================
# MENU HANDLER
# ==================================================

async def handle_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_choice = update.message.text


    if user_choice == "ℹ️ Help & Guide":

        await help_command(
            update,
            context
        )


    else:

        await update.message.reply_text(

            "Please select an option using "
            "the buttons below.",

            reply_markup=get_main_menu()

        )


# ==================================================
# ERROR HANDLER
# ==================================================

async def error_handler(
    update,
    context
):

    print(
        f"Telegram Error: {context.error}"
    )


    if update and update.effective_message:

        try:

            await update.effective_message.reply_text(

                "⚠️ A temporary error occurred.\n\n"

                "Please try again."

            )

        except Exception:

            pass


# ==================================================
# MAIN FUNCTION
# ==================================================

def main():


    if (

        not BOT_TOKEN

        or

        BOT_TOKEN == "PASTE_YOUR_NEW_TELEGRAM_BOT_TOKEN_HERE"

    ):

        print(
            "ERROR: Please paste your Telegram "
            "bot token into BOT_TOKEN."
        )

        return


    application = (

        ApplicationBuilder()

        .token(BOT_TOKEN)

        .connect_timeout(60)

        .read_timeout(120)

        .write_timeout(120)

        .pool_timeout(60)

        .build()

    )


    # ==============================================
    # REPORT ISSUE CONVERSATION
    # ==============================================

    report_conversation = ConversationHandler(

        entry_points=[

            MessageHandler(

                filters.Regex(
                    "^📝 Report New Issue$"
                ),

                report_issue_start

            )

        ],


        states={


            ENTER_STUDENT_NAME: [

                MessageHandler(

                    filters.TEXT
                    &
                    ~filters.COMMAND,

                    enter_student_name

                )

            ],


            ENTER_REGISTER_NUMBER: [

                MessageHandler(

                    filters.TEXT
                    &
                    ~filters.COMMAND,

                    enter_register_number

                )

            ],


            SELECT_BUILDING: [

                MessageHandler(

                    filters.TEXT
                    &
                    ~filters.COMMAND,

                    select_building

                )

            ],


            SELECT_ROOM: [

                MessageHandler(

                    filters.TEXT
                    &
                    ~filters.COMMAND,

                    select_room

                )

            ],


            UPLOAD_IMAGE: [

                MessageHandler(
                    filters.PHOTO,
                    upload_image
                ),

                MessageHandler(
                    ~filters.PHOTO,
                    image_required
                )

            ]

        },


        fallbacks=[

            CommandHandler(
                "cancel",
                cancel
            )

        ]

    )


    # ==============================================
    # TRACK TICKET CONVERSATION
    # ==============================================

    track_conversation = ConversationHandler(

        entry_points=[

            MessageHandler(

                filters.Regex(
                    "^🔎 Track Ticket$"
                ),

                track_ticket_start

            )

        ],


        states={


            TRACK_TICKET: [

                MessageHandler(

                    filters.TEXT
                    &
                    ~filters.COMMAND,

                    show_ticket_details

                )

            ]

        },


        fallbacks=[

            CommandHandler(
                "cancel",
                cancel
            )

        ]

    )


    # ==============================================
    # REGISTER HANDLERS
    # ==============================================

    application.add_handler(

        CommandHandler(
            "start",
            start_command
        )

    )


    application.add_handler(

        CommandHandler(
            "help",
            help_command
        )

    )


    application.add_handler(
        report_conversation
    )


    application.add_handler(
        track_conversation
    )


    application.add_handler(

        MessageHandler(

            filters.TEXT
            &
            ~filters.COMMAND,

            handle_menu

        )

    )


    application.add_error_handler(
        error_handler
    )


    print(
        "========================================"
    )

    print(
        "CampusFix Telegram Bot is starting..."
    )

    print(
        "AI Image Detection: ENABLED"
    )

    print(
        "AI Image Validation: DISABLED"
    )

    print(
        "Partial AI Response Handling: ENABLED"
    )

    print(
        "Ticket Generation: AUTOMATIC"
    )

    print(
        "Press Ctrl + C to stop the bot."
    )

    print(
        "========================================"
    )


    application.run_polling(
        bootstrap_retries=5
    )


# ==================================================
# RUN BOT
# ==================================================

if __name__ == "__main__":

    main()