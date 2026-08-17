# CampusFix

## AI-Powered University Maintenance Issue Reporting System

CampusFix is a fully local AI-powered university maintenance management system designed to help students report campus infrastructure and maintenance issues efficiently. Students can submit an image and description of an issue, after which local AI models analyze the problem and generate a structured maintenance ticket that can be tracked and managed by administrators.

The system combines image understanding, local language models, a Streamlit web application, Telegram integration, and SQLite database management into a single workflow without relying on cloud AI APIs.

---

# Problem Statement

Universities and colleges often handle maintenance complaints manually through phone calls, written complaints, emails, or informal communication. This can create several problems:

* Students may not know which department should handle an issue.
* Maintenance requests may lack sufficient details.
* Administrators may find it difficult to track all complaints.
* Students may not receive updates about ticket progress.
* Important maintenance problems may be delayed or forgotten.

CampusFix addresses this problem by providing an AI-assisted maintenance reporting system where students can submit a photograph and description of an issue. The system analyzes the information, creates a structured maintenance ticket, routes it to the appropriate department, and allows both students and administrators to track ticket progress.

---

# Features

## Student Features

* Report a new maintenance issue.
* Enter student name and register number.
* Select campus building and exact location.
* Upload an image of the maintenance problem.
* Provide a description of the issue.
* Receive an automatically generated Ticket ID.
* View ticket severity and assigned department.
* Track the current ticket status.
* View administrator remarks and ticket update history.

## AI Features

* Local image analysis using LLaVA through Ollama.
* Identification of visible maintenance issues and affected areas.
* Structured image analysis with confidence information.
* Local ticket generation using Llama 3.2 through Ollama.
* Automatic generation of:

  * Issue category
  * Issue title
  * Severity
  * Description
  * Recommended action
  * Assigned department

## Administrator Features

* View all submitted maintenance tickets.
* Monitor total tickets.
* View Open, In Progress, and Resolved ticket counts.
* View complete issue information.
* Update ticket status.
* Add administrator remarks.
* Maintain ticket update history.

## Telegram Bot Features

* Report New Issue workflow.
* Student name and register number collection.
* Building and room selection.
* Image upload support.
* Local AI-based issue analysis.
* Automatic ticket creation.
* Ticket tracking.
* Update history display.
* Help and Guide section.
* `/cancel` command during operations.

---

# System Workflow

The CampusFix workflow is:

```text
Student
   │
   ▼
Upload Image + Issue Description
   │
   ▼
Local LLaVA Vision Model
   │
   ▼
Structured Image Analysis
   │
   ▼
Local Llama 3.2 Model
   │
   ▼
Maintenance Ticket Generation
   │
   ▼
SQLite Database
   │
   ├──────────────► Streamlit Student Tracking
   │
   ├──────────────► Admin Dashboard
   │
   └──────────────► Telegram Bot
```

### Step-by-Step Flow

1. A student uploads an image of a maintenance issue.
2. The student provides a description of the problem.
3. The local LLaVA model analyzes the uploaded image.
4. The system identifies the visible issue and affected object or area.
5. The local Llama 3.2 model generates a structured maintenance ticket.
6. The ticket is stored in the SQLite database.
7. A unique Ticket ID is generated.
8. The appropriate maintenance department is assigned.
9. Administrators review and update the ticket.
10. Students can track the ticket through the Streamlit application or Telegram bot.

---

# Architecture

CampusFix follows a modular architecture.

```text
                    ┌──────────────────────┐
                    │      STUDENT         │
                    │ Streamlit / Telegram │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  IMAGE + DESCRIPTION │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  LLaVA via Ollama    │
                    │ Local Vision Analysis│
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Llama 3.2 via Ollama │
                    │ Ticket Generation    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   SQLite Database    │
                    │ Tickets and Updates  │
                    └───────┬───────┬──────┘
                            │       │
                 ┌──────────▼─┐   ┌─▼──────────────┐
                 │ Streamlit  │   │ Telegram Bot   │
                 │ Dashboard  │   │ Tracking       │
                 └────────────┘   └────────────────┘
                            │
                            ▼
                    ┌──────────────────────┐
                    │ Admin Management    │
                    │ Status + Remarks    │
                    └──────────────────────┘
```

A visual architecture diagram can also be stored at:

```text
docs/architecture.png
```

The workflow diagram can be stored at:

```text
docs/workflow.png
```

---

# Project Structure

```text
CampusFix/
│
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
│
├── app.py
├── telegram_bot.py
│
├── src/
│   ├── __init__.py
│   ├── vision_analyzer.py
│   ├── ticket_generator.py
│   ├── safety_checker.py
│   └── database.py
│
├── assets/
│
├── docs/
│   ├── architecture.png
│   ├── workflow.png
│   └── screenshots/
│
├── models/
│
├── data/
│   └── campusfix.db
│
├── outputs/
│
└── demo/
    └── demo.mp4
```

---

# Technologies Used

| Technology          | Purpose                             |
| ------------------- | ----------------------------------- |
| Python              | Main programming language           |
| Streamlit           | Web application and dashboards      |
| Ollama              | Local AI model execution            |
| LLaVA               | Local image understanding           |
| Llama 3.2           | Local maintenance ticket generation |
| SQLite              | Ticket and update database          |
| python-telegram-bot | Telegram integration                |
| Pillow              | Image handling                      |

---

# Local AI Models

CampusFix uses local models through Ollama.

## Vision Model

```text
llava:latest
```

The model analyzes the uploaded maintenance issue image.

## Text Model

```text
llama3.2:3b
```

The model generates the structured maintenance ticket.

No OpenAI, Gemini, Claude, or other cloud AI API is required for the AI workflow.

---

# Installation

## 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd CampusFix
```

## 2. Create a Virtual Environment

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

## 3. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

---

# Install Ollama

Install Ollama on the local machine.

After installation, verify it:

```powershell
ollama --version
```

---

# Download Required Local Models

Download the text model:

```powershell
ollama pull llama3.2:3b
```

Download the vision model:

```powershell
ollama pull llava:latest
```

Verify the models:

```powershell
ollama list
```

Expected models include:

```text
llama3.2:3b
llava:latest
```

---

# Usage

## Start the Streamlit Application

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run:

```powershell
streamlit run app.py
```

The application will open locally in the browser.

---

## Start the Telegram Bot

Open another terminal in the CampusFix directory.

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run:

```powershell
python telegram_bot.py
```

The Telegram bot and Streamlit application can access the same SQLite database.

---

# Example Ticket

```text
Student Details

Name: Student Name
Register Number: 123456

Ticket Details

Ticket ID: 1
Issue: Faulty Ceiling Fan
Category: Electrical Maintenance
Severity: High
Created: 17 Aug 2026 19:30:45

Ticket directed to: Electrical Maintenance
```

---

# Ticket Status Flow

```text
Open
  │
  ▼
In Progress
  │
  ▼
Resolved
```

Administrators can add remarks whenever a ticket is updated. Students can later view the current status and complete update history.

---

# Database

CampusFix uses SQLite for local data storage.

The database stores:

* Student name
* Register number
* Ticket ID
* Issue category
* Issue title
* Severity
* Description
* Recommended action
* Assigned department
* Building
* Room
* Ticket status
* Creation date and time
* Administrator remarks
* Ticket update history

The database is stored locally inside the `data/` directory.

---

# Screenshots

Project screenshots should be placed inside:

```text
docs/screenshots/
```

Recommended screenshots:

1. Student issue reporting page.
2. AI-generated ticket confirmation.
3. Ticket tracking page.
4. Administrator dashboard.
5. Administrator ticket update page.
6. Telegram Report New Issue workflow.
7. Telegram ticket tracking workflow.

---

# Demo Video

The project demonstration video should be stored at:

```text
demo/demo.mp4
```

The demo should show:

1. Starting the Streamlit application.
2. Reporting a maintenance issue.
3. Uploading an image.
4. Entering an issue description.
5. Local AI image analysis.
6. Local AI ticket generation.
7. Ticket creation.
8. Viewing the ticket in the Admin Dashboard.
9. Updating the ticket status.
10. Tracking the updated ticket.
11. Using the Telegram bot.

---

# Privacy and Local Processing

CampusFix is designed with local AI processing in mind.

* LLaVA runs locally through Ollama.
* Llama 3.2 runs locally through Ollama.
* Ticket information is stored in a local SQLite database.
* No cloud AI API is required for the core AI workflow.

---

# Future Enhancements

Possible future improvements include:

* Automatic notification when ticket status changes.
* Department-specific administrator accounts.
* Automatic technician assignment.
* Priority-based maintenance queues.
* Analytics and reporting dashboard.
* Email notifications.
* Campus maintenance statistics.
* Improved object detection models.
* Authentication and role-based access.
* Mobile application integration.

---

# Demo

The complete project demonstrates a university-focused AI application that combines:

```text
Image Input
     +
Student Description
     ↓
Local Vision AI
     ↓
Local Language Model
     ↓
Structured Maintenance Ticket
     ↓
SQLite Storage
     ↓
Admin Management
     ↓
Student Tracking
     +
Telegram Integration
```

---

# Author

Developed as an academic project for an AI-powered university maintenance issue reporting system.

# License

This project is licensed under the MIT License. See the `LICENSE` file for details.
