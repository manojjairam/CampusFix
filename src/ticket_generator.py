import ollama


# ==================================================
# LOCAL OLLAMA TEXT MODEL
# ==================================================

MODEL_NAME = "llama3.2:3b"


# ==================================================
# GENERATE MAINTENANCE TICKET
# ==================================================

def generate_ticket(
    vision_analysis,
    location,
    room,
    user_description
):
    """
    Generate a concise university maintenance ticket using
    local Llama 3.2 and the structured image-based issue
    detection results from CampusFix Vision AI.
    """

    prompt = f"""
You are CampusFix AI, a university maintenance ticket
generation assistant.

Create one accurate and concise maintenance ticket.

The image was analyzed by a local vision AI model. The
analysis may contain these fields:

- Detected Object/Area
- Detected Issue
- Visible Condition
- Evidence
- Possible Maintenance Concern
- Visual Confidence

Use this structured image analysis as the primary source
for identifying the affected object or area and visible
maintenance problem.

IMAGE-BASED ISSUE ANALYSIS:
{vision_analysis}

STUDENT DESCRIPTION:
{user_description}

LOCATION:
Building: {location}
Room: {room}

IMPORTANT RULES:

1. Use only information reasonably supported by the image
   analysis and student description.
2. Give priority to the detected object/area and detected
   issue when creating the ticket.
3. Use the student's description as supporting context,
   especially for problems such as noise, vibration, or
   malfunction that may not be visible in a still image.
4. Do not invent damage, objects, hazards, or technical
   causes that are not supported by the available input.
5. Keep the Issue Title short, clear, and professional.
6. Select the most appropriate maintenance category.
7. Severity must be exactly one of:
   Low, Normal, High, Critical.
8. Select the department responsible for resolving the
   maintenance issue.
9. Keep Description concise.
10. Recommended Action must be short and practical.
11. Do not include reasoning, safety analysis, markdown,
    explanations, confidence values, or extra fields.
12. Return exactly the six lines shown below.
13. Do not add anything before or after those six lines.

Return exactly in this format:

Issue Category: <category>
Issue Title: <short professional title>
Severity: <Low, Normal, High, or Critical>
Description: <concise description>
Recommended Action: <short practical action>
Assigned Department: <responsible department>
"""

    try:

        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0.1,
                "num_predict": 180
            }
        )

        ticket = response["message"]["content"].strip()

        if not ticket:

            return (
                "Error: The local ticket generation model "
                "returned an empty response."
            )

        return ticket

    except Exception as error:

        return (
            "Error: Unable to generate the maintenance ticket "
            f"using the local Llama model: {error}"
        )