import ollama


# ==================================================
# LOCAL IMAGE VALIDATION MODEL
# ==================================================

MODEL_NAME = "moondream"


# ==================================================
# VALIDATE MAINTENANCE IMAGE
# ==================================================

def validate_maintenance_image(image_path):
    """
    Checks whether an uploaded image is relevant to a
    university or campus maintenance issue.

    Returns a dictionary:
    {
        "valid": True/False,
        "reason": "..."
    }
    """

    prompt = """
You are an image validation system for CampusFix, a
university maintenance issue reporting application.

Your ONLY task is to decide whether the uploaded image
is relevant to a campus maintenance, infrastructure,
facility, equipment, cleanliness, or safety issue.

A VALID image may show things such as:

- Broken or damaged furniture
- Faulty electrical equipment
- Damaged lights or fans
- Water leakage or plumbing problems
- Damaged walls, floors, ceilings, doors, or windows
- HVAC problems
- Damaged IT or laboratory equipment
- Cleaning or sanitation problems
- Campus safety or infrastructure problems
- Any visible object or area that reasonably requires
  maintenance or repair

An INVALID image includes:

- Selfies or unrelated people
- Random portraits
- Food
- Animals or pets
- Memes
- Random screenshots
- Landscapes
- Vehicles
- Entertainment images
- Images with no visible maintenance-related object,
  infrastructure, facility, equipment, or issue

IMPORTANT:

1. Do not assume an issue exists if the image does not
   reasonably show one.
2. If the image is unclear, unrelated, or cannot be
   verified as maintenance-related, mark it INVALID.
3. Do not invent maintenance problems.
4. Return ONLY these two lines.
5. Do not use markdown.
6. Do not add explanations before or after the two lines.

Return exactly:

VALID: YES or NO
REASON: <short reason>
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
                "num_predict": 60,
                "num_ctx": 1024
            },
            keep_alive="15m"
        )

        result = response["message"]["content"].strip()

        valid = False
        reason = "Unable to verify whether the image is relevant."

        for line in result.splitlines():

            line = line.strip()

            if ":" not in line:
                continue

            key, value = line.split(":", 1)

            key = key.strip().lower()
            value = value.strip()

            if key == "valid":

                valid = value.upper() == "YES"

            elif key == "reason":

                reason = value

        return {
            "valid": valid,
            "reason": reason
        }

    except Exception as error:

        return {
            "valid": False,
            "reason": (
                "Image validation failed: "
                f"{error}"
            )
        }