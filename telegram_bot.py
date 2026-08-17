# telegram_bot.py

import os
import uuid
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
from src.ticket_generator import generate_ticket
from src.safety_checker import check_safety
from src.database import (
    save_ticket,
    get_ticket_details,
    get_ticket_updates
)


# ==================================================
# BOT TOKEN
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
    ENTER_DESCRIPTION,
    TRACK_TICKET
) = range(7)


# ==================================================
# MAIN MENU
# ==================================================

def get_main_menu():

    keyboard = [
        ["📝 Report New Issue"],
        ["🔎 Track Ticket", "ℹ️ Help & Guide"]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


# ==================================================
# DATE FORMAT
# ==================================================

def format_ticket_date(date_value):

    if not date_value:
        return "Not available"

    try:

        date_object = datetime.strptime(
            date_value,
            "%Y-%m-%d %H:%M:%S"
        )

        return date_object.strftime(
            "%d %b %Y, %H:%M:%S"
        )

    except ValueError:

        return date_value


# ==================================================
# START COMMAND
# ==================================================

async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "🏫 Welcome to CampusFix!\n\n"
        "CampusFix helps students report campus maintenance "
        "problems using AI.\n\n"
        "You can report a new issue, track an existing ticket, "
        "or use the Help & Guide to understand how the system works.",
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
        "Use this option when you find a maintenance problem "
        "on campus.\n\n"

        "You will be asked to:\n"
        "1. Enter your name\n"
        "2. Enter your register number\n"
        "3. Select the building\n"
        "4. Select the room or exact location\n"
        "5. Upload a photo of the problem\n"
        "6. Describe the issue\n\n"

        "CampusFix AI will analyze the image and description "
        "and create a maintenance ticket.\n\n"

        "🔎 TRACK TICKET\n\n"
        "Enter your Ticket ID to check:\n"
        "• Current ticket status\n"
        "• Admin remarks\n"
        "• Previous update history\n\n"

        "🎫 IMPORTANT\n\n"
        "After creating a ticket, save your Ticket ID. "
        "You will need it to track your maintenance issue.\n\n"

        "❌ CANCEL AN OPERATION\n\n"
        "You can type /cancel at any time while reporting "
        "or tracking a ticket.\n\n"

        "Choose an option from the menu below to continue."
    )

    await update.message.reply_text(
        help_message,
        reply_markup=get_main_menu()
    )


# ==================================================
# REPORT NEW ISSUE - START
# ==================================================

async def report_issue_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data.clear()

    await update.message.reply_text(
        "📝 REPORT NEW ISSUE\n\n"
        "Let's create a maintenance ticket.\n\n"
        "Step 1 of 6: Please enter your full name.",
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

    context.user_data["student_name"] = student_name

    await update.message.reply_text(
        "Step 2 of 6: Please enter your register number."
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

    context.user_data["register_number"] = register_number

    building_keyboard = [
        [building]
        for building in CAMPUS_LOCATIONS.keys()
    ]

    await update.message.reply_text(
        "Step 3 of 6: Select the building or location:",
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

    building = update.message.text

    if building not in CAMPUS_LOCATIONS:

        await update.message.reply_text(
            "Please select a building using the buttons."
        )

        return SELECT_BUILDING

    context.user_data["location"] = building

    room_keyboard = [
        [room]
        for room in CAMPUS_LOCATIONS[building]
    ]

    await update.message.reply_text(
        f"Selected Building: {building}\n\n"
        "Step 4 of 6: Select the room or exact location:",
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

    room = update.message.text

    building = context.user_data.get("location")

    if building not in CAMPUS_LOCATIONS:

        await update.message.reply_text(
            "Something went wrong. Please start again.",
            reply_markup=get_main_menu()
        )

        return ConversationHandler.END

    if room not in CAMPUS_LOCATIONS[building]:

        await update.message.reply_text(
            "Please select a room using the buttons."
        )

        return SELECT_ROOM

    context.user_data["room"] = room

    await update.message.reply_text(
        f"Building: {building}\n"
        f"Room: {room}\n\n"
        "Step 5 of 6: Please upload a photo of the "
        "maintenance issue.",
        reply_markup=ReplyKeyboardRemove()
    )

    return UPLOAD_IMAGE


# ==================================================
# UPLOAD IMAGE
# ==================================================

async def upload_image(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    photo = update.message.photo[-1]

    telegram_file = await photo.get_file()

    image_filename = (
        f"telegram_issue_{uuid.uuid4().hex}.jpg"
    )

    image_path = os.path.join(
        "data",
        image_filename
    )

    os.makedirs(
        "data",
        exist_ok=True
    )

    await telegram_file.download_to_drive(
        image_path
    )

    context.user_data["image_path"] = image_path

    await update.message.reply_text(
        "Image received successfully.\n\n"
        "Step 6 of 6: Briefly describe the problem.\n\n"
        "Example: The ceiling fan is shaking and making "
        "a loud noise."
    )

    return ENTER_DESCRIPTION


# ==================================================
# IMAGE REQUIRED
# ==================================================

async def image_required(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "Please upload a photo of the maintenance issue."
    )

    return UPLOAD_IMAGE


# ==================================================
# ENTER DESCRIPTION AND CREATE TICKET
# ==================================================

async def enter_description(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    student_description = update.message.text.strip()

    if not student_description:

        await update.message.reply_text(
            "Please enter a short description of the issue."
        )

        return ENTER_DESCRIPTION

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

    image_path = context.user_data.get(
        "image_path"
    )

    await update.message.reply_text(
        "🤖 CampusFix AI is analyzing your maintenance issue...\n\n"
        "Please wait."
    )

    try:

        # ------------------------------------------
        # IMAGE ANALYSIS
        # ------------------------------------------

        vision_result = analyze_issue_image(
            image_path,
            student_description
        )

        if str(vision_result).startswith("Error"):

            await update.message.reply_text(
                f"Image analysis failed:\n\n{vision_result}",
                reply_markup=get_main_menu()
            )

            return ConversationHandler.END

        # ------------------------------------------
        # GENERATE TICKET
        # ------------------------------------------

        ticket_result = generate_ticket(
            vision_analysis=vision_result,
            location=location,
            room=room,
            user_description=student_description
        )

        if str(ticket_result).startswith("Error"):

            await update.message.reply_text(
                f"Ticket generation failed:\n\n{ticket_result}",
                reply_markup=get_main_menu()
            )

            return ConversationHandler.END

        # ------------------------------------------
        # PARSE GENERATED TICKET
        # ------------------------------------------

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

        # ------------------------------------------
        # SAFETY CHECK
        # ------------------------------------------

        safety_result = check_safety(
            ticket_result
        )

        if isinstance(safety_result, dict):

            severity = safety_result.get(
                "severity",
                ticket_data.get(
                    "severity",
                    "Normal"
                )
            )

            assigned_department = safety_result.get(
                "assigned_department",
                ticket_data.get(
                    "assigned department",
                    "General Maintenance"
                )
            )

        else:

            severity = ticket_data.get(
                "severity",
                "Normal"
            )

            assigned_department = ticket_data.get(
                "assigned department",
                "General Maintenance"
            )

        # ------------------------------------------
        # PREPARE DATABASE TICKET
        # ------------------------------------------

        database_ticket = {
            "student_name": student_name,

            "register_number": register_number,

            "issue_category": ticket_data.get(
                "issue category",
                "General Maintenance"
            ),

            "issue_title": ticket_data.get(
                "issue title",
                "Maintenance Issue"
            ),

            "severity": severity,

            "description": ticket_data.get(
                "description",
                student_description
            ),

            "recommended_action": ticket_data.get(
                "recommended action",
                "Maintenance inspection required"
            ),

            "assigned_department": assigned_department,

            "location": location,

            "room": room,

            "student_description": student_description,

            "escalation": assigned_department
        }

        # ------------------------------------------
        # SAVE TICKET
        # ------------------------------------------

        ticket_id = save_ticket(
            database_ticket
        )

        # ------------------------------------------
        # MILITARY TIME WITH SECONDS
        # ------------------------------------------

        created_date = datetime.now().strftime(
            "%d %b %Y, %H:%M:%S"
        )

        # ------------------------------------------
        # SEND TICKET CONFIRMATION
        # ------------------------------------------

        confirmation_message = (
            "✅ MAINTENANCE TICKET CREATED\n"
            "━━━━━━━━━━━━━━━━━━\n\n"

            "👤 *Student Details*\n"
            f"Name: {student_name}\n"
            f"Register Number: {register_number}\n\n"

            "🎫 *Ticket Details*\n"
            f"Ticket ID: {ticket_id}\n"
            f"Issue: {database_ticket['issue_title']}\n"
            f"Category: {database_ticket['issue_category']}\n"
            f"Severity: {severity}\n"
            f"Created: {created_date}\n\n"

            f"Ticket directed to: "
            f"{assigned_department}\n\n"

            "Please save your Ticket ID to track future updates."
        )

        await update.message.reply_text(
            confirmation_message,
            parse_mode="Markdown",
            reply_markup=get_main_menu()
        )

        context.user_data.clear()

        if image_path and os.path.exists(image_path):

            os.remove(image_path)

        return ConversationHandler.END

    except Exception as error:

        await update.message.reply_text(
            f"Unable to create the maintenance ticket:\n\n"
            f"{error}",
            reply_markup=get_main_menu()
        )

        context.user_data.clear()

        if image_path and os.path.exists(image_path):

            os.remove(image_path)

        return ConversationHandler.END


# ==================================================
# TRACK TICKET - START
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
            "Please enter a valid numeric Ticket ID.\n\n"
            "Example: 1"
        )

        return TRACK_TICKET

    ticket_id = int(ticket_id_text)

    try:

        ticket = get_ticket_details(ticket_id)

        if ticket is None:

            await update.message.reply_text(
                f"Ticket #{ticket_id} was not found.\n\n"
                "Please check the Ticket ID and try again."
            )

            return TRACK_TICKET

        created_date = format_ticket_date(
            ticket["created_at"]
        )

        # ------------------------------------------
        # SIMPLIFIED TICKET DETAILS
        # ------------------------------------------

        ticket_message = (
            f"🎫 TICKET #{ticket['ticket_id']}\n"
            "━━━━━━━━━━━━━━━━━━\n\n"

            "👤 *Student Details*\n"
            f"Name: {ticket['student_name']}\n"
            f"Register Number: {ticket['register_number']}\n\n"

            "🎫 *Ticket Details*\n"
            f"Issue: {ticket['issue_title']}\n"
            f"Category: {ticket['issue_category']}\n"
            f"Severity: {ticket['severity']}\n"
            f"Status: {ticket['status']}\n"
            f"Created: {created_date}\n\n"

            f"Ticket directed to: "
            f"{ticket['assigned_department']}"
        )

        await update.message.reply_text(
            ticket_message,
            parse_mode="Markdown"
        )

        # ------------------------------------------
        # GET UPDATE HISTORY
        # ------------------------------------------

        updates = get_ticket_updates(
            ticket_id
        )

        if len(updates) == 0:

            await update.message.reply_text(
                "📜 *Update History*\n\n"
                "No admin updates have been added yet.",
                parse_mode="Markdown"
            )

        else:

            history_message = (
                "📜 *Update History*\n"
                "━━━━━━━━━━━━━━━━━━\n"
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
                    f"\nStatus: {update_item['status']}\n"
                    f"Remarks: {remarks}\n"
                    f"Updated: {updated_date}\n"
                    "──────────────────\n"
                )

            await update.message.reply_text(
                history_message,
                parse_mode="Markdown"
            )

        await update.message.reply_text(
            "Use the menu below to continue.",
            reply_markup=get_main_menu()
        )

        return ConversationHandler.END

    except Exception as error:

        await update.message.reply_text(
            f"Unable to retrieve the ticket:\n\n{error}",
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

    image_path = context.user_data.get(
        "image_path"
    )

    if image_path and os.path.exists(image_path):

        os.remove(image_path)

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
            "Please select an option using the buttons below.",
            reply_markup=get_main_menu()
        )


# ==================================================
# MAIN FUNCTION
# ==================================================

def main():

    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .pool_timeout(30)
        .build()
    )

    # ----------------------------------------------
    # REPORT NEW ISSUE CONVERSATION
    # ----------------------------------------------

    report_conversation = ConversationHandler(

        entry_points=[
            MessageHandler(
                filters.Regex("^📝 Report New Issue$"),
                report_issue_start
            )
        ],

        states={

            ENTER_STUDENT_NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    enter_student_name
                )
            ],

            ENTER_REGISTER_NUMBER: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    enter_register_number
                )
            ],

            SELECT_BUILDING: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    select_building
                )
            ],

            SELECT_ROOM: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    select_room
                )
            ],

            UPLOAD_IMAGE: [
                MessageHandler(
                    filters.PHOTO,
                    upload_image
                ),

                MessageHandler(
                    filters.ALL,
                    image_required
                )
            ],

            ENTER_DESCRIPTION: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    enter_description
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

    # ----------------------------------------------
    # TRACK TICKET CONVERSATION
    # ----------------------------------------------

    track_conversation = ConversationHandler(

        entry_points=[
            MessageHandler(
                filters.Regex("^🔎 Track Ticket$"),
                track_ticket_start
            )
        ],

        states={

            TRACK_TICKET: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
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

    # ----------------------------------------------
    # REGISTER HANDLERS
    # ----------------------------------------------

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
            filters.TEXT & ~filters.COMMAND,
            handle_menu
        )
    )

    # ----------------------------------------------
    # START BOT
    # ----------------------------------------------

    print("CampusFix Telegram Bot is starting...")
    print("Press Ctrl + C to stop the bot.")

    application.run_polling(
        bootstrap_retries=3
    )


if __name__ == "__main__":
    main()