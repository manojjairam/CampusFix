from src.vision_analyzer import analyze_issue_image

image_path = "test_image.jpg"

result = analyze_issue_image(
    image_path,
    "Please identify the maintenance issue in this image."
)

print("\nVISION ANALYSIS RESULT")
print("=" * 50)
print(result)