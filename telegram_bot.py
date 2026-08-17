# ==================================================
# CAMPUSFIX TELEGRAM BOT
# ==================================================
#
# Flow:
#
# Report New Issue
#        ↓
# Student Name
#        ↓
# Register Number
#        ↓
# Select Building
#        ↓
# Select Room
#        ↓
# Upload Image
#        ↓
# Moondream AI analyzes image automatically
#        ↓
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


from src.vision_analyzer import analyze_issue_image

from src.database import (
    save_ticket,
    get_ticket_details,
    get_ticket_updates
)


# ==================================================
# TELEGRAM BOT TOKEN
# ==================================================
#
# IMPORTANT:
# Paste your CURRENT bot token below.
# If the old token was exposed, regenerate it first.
#
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

        ["📝 Report New Issue"],

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
# FORMAT TICKET DATE
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

        if key in expected_fields:

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
# START COMMAND
# ==================================================

async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data.clear()

    await update.message.reply_text(

        "🏫 Welcome to CampusFix!\n\n"

        "CampusFix uses AI to identify campus "
        "maintenance problems directly from an "
        "uploaded image.\n\n"

        "Simply upload a photo of the issue and "
        "CampusFix AI will automatically analyze it "
        "and create a maintenance ticket.",

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

        "To report a maintenance issue:\n\n"

        "1. Enter your name\n"
        "2. Enter your register number\n"
        "3. Select the building\n"
        "4. Select the room or location\n"
        "5. Upload a photo\n\n"

        "🤖 CampusFix AI automatically analyzes "
        "the uploaded image and identifies:\n\n"

        "• Issue category\n"
        "• Issue title\n"
        "• Severity\n"
        "• Description\n"
        "• Recommended action\n"
        "• Responsible department\n\n"

        "You do NOT need to describe the problem "
        "manually.\n\n"

        "🔎 TRACK TICKET\n\n"

        "Enter your Ticket ID to check:\n"

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
# REPORT NEW ISSUE START
# ==================================================

async def report_issue_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data.clear()

    await update.message.reply_text(

        "📝 REPORT NEW ISSUE\n\n"

        "CampusFix AI will automatically identify "
        "the maintenance problem from your image.\n\n"

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

        "Step 5 of 5: Upload a photo of "
        "the maintenance issue.\n\n"

        "🤖 CampusFix AI will automatically "
        "detect the problem from the image.",

        reply_markup=ReplyKeyboardRemove()

    )

    return UPLOAD_IMAGE


# ==================================================
# UPLOAD IMAGE
# AI ANALYSIS
# AUTOMATIC TICKET CREATION
# ==================================================

async def upload_image(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    image_path = None

    processing_message = None

    try:

        # ==========================================
        # GET STUDENT AND LOCATION DETAILS
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
        # GET UPLOADED IMAGE
        # ==========================================

        photo = update.message.photo[-1]


        # ==========================================
        # SHOW PROCESSING MESSAGE
        # ==========================================

        processing_message = (
            await update.message.reply_text(

                "📷 Image received successfully.\n\n"

                "🤖 CampusFix AI is analyzing "
                "the image...\n\n"

                "The AI will automatically identify "
                "the maintenance problem and create "
                "your ticket.\n\n"

                "Please wait."

            )
        )


        # ==========================================
        # DOWNLOAD TELEGRAM IMAGE
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


        context.user_data[
            "image_path"
        ] = image_path


        # ==========================================
        # AI IMAGE ANALYSIS
        #
        # asyncio.to_thread prevents Ollama's
        # blocking local processing from blocking
        # Telegram's async event loop.
        # ==========================================

        vision_result = await asyncio.to_thread(

            analyze_issue_image,

            image_path,

            "",

            location,

            room

        )


        # ==========================================
        # CHECK AI ERROR
        # ==========================================

        if str(vision_result).startswith("Error"):

            await processing_message.edit_text(

                "❌ AI image analysis failed.\n\n"

                f"{vision_result}\n\n"

                "Please try uploading another "
                "clear image."

            )

            context.user_data.clear()

            return ConversationHandler.END


        # ==========================================
        # PARSE AI RESULT
        # ==========================================

        ticket_data = parse_ai_result(
            vision_result
        )


        # ==========================================
        # GET AI DETECTED VALUES
        # ==========================================

        issue_category = ticket_data.get(

            "issue category",

            "General Maintenance"

        )


        issue_title = ticket_data.get(

            "issue title",

            "Maintenance Issue"

        )


        severity = validate_severity(

            ticket_data.get(
                "severity",
                "Normal"
            )

        )


        description = ticket_data.get(

            "description",

            "Campus maintenance issue detected "
            "from the uploaded image."

        )


        recommended_action = ticket_data.get(

            "recommended action",

            "Maintenance inspection required."

        )


        assigned_department = ticket_data.get(

            "assigned department",

            "General Maintenance"

        )


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
                "Automatically detected by AI "
                "from uploaded image.",

            "image_path": image_path

        }


        # ==========================================
        # SAVE TICKET TO DATABASE
        # ==========================================

        ticket_id = save_ticket(
            database_ticket
        )


        # ==========================================
        # CREATED DATE
        # ==========================================

        created_date = datetime.now().strftime(

            "%d %b %Y, %H:%M:%S"

        )


        # ==========================================
        # UPDATE PROCESSING MESSAGE
        # ==========================================

        await processing_message.edit_text(

            "🤖 AI analysis completed.\n\n"

            "🎫 Maintenance ticket created "
            "successfully!"

        )


        # ==========================================
        # TICKET CONFIRMATION
        # ==========================================

        confirmation_message = (

            "✅ MAINTENANCE TICKET CREATED\n"
            "━━━━━━━━━━━━━━━━━━\n\n"

            "👤 Student Details\n"

            f"Name: {student_name}\n"

            f"Register Number: "
            f"{register_number}\n\n"


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
        # CLEAR CONVERSATION DATA
        # ==========================================

        context.user_data.clear()


        return ConversationHandler.END


    except Exception as error:


        error_message = (

            "❌ Unable to create the "
            "maintenance ticket.\n\n"

            f"Error: {error}"

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


        context.user_data.clear()


        return ConversationHandler.END


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

        "CampusFix AI needs the image to "
        "automatically identify the problem."

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

        "Please enter your Ticket ID.\n\n"

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


        # ==========================================
        # GET UPDATE HISTORY
        # ==========================================

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
# CANCEL CURRENT OPERATION
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


    # ==============================================
    # CHECK TOKEN
    # ==============================================

    if (
        not BOT_TOKEN
        or
        BOT_TOKEN == "PASTE_YOUR_TELEGRAM_BOT_TOKEN_HERE"
    ):

        print(
            "ERROR: Please paste your Telegram "
            "bot token into BOT_TOKEN."
        )

        return


    # ==============================================
    # CREATE TELEGRAM APPLICATION
    # ==============================================

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


    # ==============================================
    # START BOT
    # ==============================================

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
        "Student Description: NOT REQUIRED"
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