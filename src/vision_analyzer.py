import ollama


# ==================================================
# LOCAL OLLAMA VISION MODEL
# ==================================================

MODEL_NAME = "llava:latest"


# ==================================================
# ANALYZE MAINTENANCE ISSUE IMAGE
# ==================================================

def analyze_issue_image(
    image_path,
    user_description=""
):
    """
    Analyze a university maintenance issue image using
    the local LLaVA vision model through Ollama.

    The analysis focuses on:
    - Detecting the visible object or affected area
    - Identifying visible maintenance problems
    - Describing the observed condition
    - Estimating confidence based on the image

    Parameters:
        image_path: Local path of the uploaded image.
        user_description: Optional description provided
                          by the student.

    Returns:
        A structured maintenance issue analysis.
    """

    prompt = f"""
You are CampusFix Vision AI, an image-based maintenance
issue detection assistant for a university campus.

Analyze the uploaded image carefully.

Your primary task is to identify the MAIN visible object,
equipment, infrastructure, or campus area related to the
reported maintenance problem.

Then identify the visible maintenance issue affecting it.

STUDENT DESCRIPTION:
{user_description if user_description else "No description provided."}

IMPORTANT RULES:

1. Analyze the actual uploaded image first.
2. Identify the main affected object or area that is visible.
3. Identify only maintenance issues reasonably supported by
   the image or the student's description.
4. Do not invent damage, hazards, objects, or conditions.
5. The student description can provide supporting context,
   especially when a problem such as noise, vibration, or
   malfunction cannot be directly seen in a still image.
6. If the exact issue cannot be visually confirmed, clearly
   state that the reported problem is based on the student's
   description.
7. Focus only on university maintenance-related issues.
8. Keep every field concise and useful for ticket generation.
9. Return ONLY the exact format below.
10. Do not add explanations before or after the analysis.

Return exactly in this format:

Detected Object/Area: <main visible object or affected area>
Detected Issue: <main maintenance problem>
Visible Condition: <observed condition>
Evidence: <brief visual evidence or description-supported evidence>
Possible Maintenance Concern: <likely maintenance concern>
Visual Confidence: <High, Medium, or Low>
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
                "temperature": 0.1
            }
        )

        analysis = response["message"]["content"].strip()

        if not analysis:

            return (
                "Error: The local vision model returned "
                "an empty analysis."
            )

        return analysis

    except Exception as error:

        return (
            "Error: Unable to analyze the image using "
            f"the local LLaVA vision model: {error}"
        )
