import ollama


# ==================================================
# LOCAL LIGHTWEIGHT VISION MODEL
# ==================================================

MODEL_NAME = "moondream"


# ==================================================
# ANALYZE IMAGE AND CREATE TICKET DATA
# ==================================================

def analyze_issue_image(
    image_path,
    user_description="",
    location="",
    room=""
):

    prompt = f"""
You are CampusFix, a university maintenance issue detection
assistant.

Your job is to examine ONE uploaded image and create the
maintenance ticket information directly.

The student may also provide a description. Use the image as
the primary source and the description only as supporting
information.

STUDENT DESCRIPTION:
{user_description if user_description.strip() else "No description provided."}

CAMPUS LOCATION:
Building: {location if location else "Not provided"}
Room / Exact Location: {room if room else "Not provided"}

Analyze the maintenance problem shown in the image and return
ONLY the following six lines.

Issue Category: <category>
Issue Title: <short professional title>
Severity: <Low, Normal, High, or Critical>
Description: <one concise description>
Recommended Action: <one short action>
Assigned Department: <responsible department>

STRICT RULES:

1. Analyze the uploaded image first.
2. Identify the main visible object or affected area.
3. Identify the maintenance problem shown in the image.
4. Do not invent objects, damage, hazards, or faults.
5. If the exact fault is unclear, use cautious wording.
6. Use the student description only as supporting information.
7. Issue Category must be relevant to university maintenance.
8. Severity must be exactly one of:
   Low
   Normal
   High
   Critical
9. Keep every value short.
10. Do not explain your reasoning.
11. Do not use markdown.
12. Do not add extra text.
13. Return all six fields.
14. Never leave a field empty.

Choose an appropriate category such as:
Electrical Maintenance
Plumbing
Furniture Maintenance
Civil Maintenance
HVAC
IT Equipment
Cleaning and Sanitation
Safety Maintenance
General Maintenance

Choose an appropriate department such as:
Electrical Maintenance Department
Plumbing Department
Civil Maintenance Department
Facilities Management
IT Support Department
Housekeeping Department
General Maintenance Department
"""

    try:

        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_path]
                }
            ],
            options={
                "temperature": 0,
                "num_predict": 120,
                "num_ctx": 1024
            },
            keep_alive="30m"
        )

        analysis = response["message"]["content"].strip()

        print("\n========== CAMPUSFIX AI RESULT ==========")
        print(analysis)
        print("==========================================\n")

        if not analysis:

            return (
                "Error: The local vision model returned "
                "an empty response."
            )

        return analysis


    except Exception as error:

        return (
            "Error: Unable to analyze the maintenance image: "
            f"{error}"
        )