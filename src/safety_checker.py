# src/safety_checker.py

import json
import ollama


# ==================================================
# LOCAL OLLAMA MODEL
# ==================================================

MODEL_NAME = "llama3.2:3b"


# ==================================================
# CHECK SAFETY
# ==================================================

def check_safety(ticket_information):
    """
    Analyze a maintenance ticket for safety risks using
    the local Llama 3.2 model through Ollama.

    Returns a dictionary containing:
    - severity
    - escalation
    - message
    """

    prompt = f"""
You are CampusFix Safety AI for a university campus.

Analyze the maintenance issue below and determine whether
it requires normal maintenance or urgent escalation.

IMPORTANT RULES:

1. Use only the provided ticket information.
2. Do not invent hazards.
3. Choose exactly one severity:
   Low, Normal, High, or Critical.
4. Choose an appropriate escalation level.
5. Critical means immediate danger or serious risk requiring
   urgent action.
6. High means a significant safety or operational risk that
   should receive priority attention.
7. Normal means routine maintenance without an urgent danger.
8. Low means minor inconvenience with minimal risk.
9. Keep the safety message short and clear.
10. Return ONLY valid JSON.
11. Do not use markdown.
12. Do not include explanations outside the JSON.

MAINTENANCE TICKET:

{ticket_information}

Return exactly this JSON format:

{{
    "severity": "Low or Normal or High or Critical",
    "escalation": "appropriate escalation level",
    "message": "short safety assessment message"
}}
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
                "temperature": 0.1
            }
        )

        generated_text = response["message"]["content"].strip()

        # ------------------------------------------
        # REMOVE POSSIBLE MARKDOWN CODE BLOCKS
        # ------------------------------------------

        if generated_text.startswith("```json"):

            generated_text = generated_text.replace(
                "```json",
                "",
                1
            ).strip()

        elif generated_text.startswith("```"):

            generated_text = generated_text.replace(
                "```",
                "",
                1
            ).strip()

        if generated_text.endswith("```"):

            generated_text = generated_text[:-3].strip()

        # ------------------------------------------
        # PARSE JSON
        # ------------------------------------------

        safety_result = json.loads(generated_text)

        severity = safety_result.get(
            "severity",
            "Normal"
        )

        escalation = safety_result.get(
            "escalation",
            "Normal Maintenance"
        )

        message = safety_result.get(
            "message",
            "Maintenance assessment completed."
        )

        # ------------------------------------------
        # VALIDATE SEVERITY
        # ------------------------------------------

        valid_severities = [
            "Low",
            "Normal",
            "High",
            "Critical"
        ]

        if severity not in valid_severities:

            severity = "Normal"

        return {
            "severity": severity,
            "escalation": escalation,
            "message": message
        }

    except json.JSONDecodeError:

        return {
            "severity": "Normal",
            "escalation": "Manual Review Required",
            "message": (
                "The local AI returned an invalid safety "
                "assessment format. Manual review is recommended."
            )
        }

    except Exception as error:

        return {
            "severity": "Normal",
            "escalation": "Safety Check Unavailable",
            "message": (
                "Unable to complete the local safety assessment: "
                f"{error}"
            )
        }