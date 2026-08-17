from src.ticket_generator import generate_ticket


vision_analysis = """
Object/Fixture: Ceiling fan
Fault Type: Fan is shaking and appears to be malfunctioning
Safety Risk: High
Issue Description: The ceiling fan appears unstable and may have a mechanical problem.
Suggested Action: Inspect the fan immediately and repair or replace damaged components.
Department: Electrical
"""


ticket = generate_ticket(
    vision_analysis=vision_analysis,
    location="Academic Block A",
    room="Room 204",
    user_description="The fan is shaking and making a loud noise."
)


print("\nCAMPUSFIX MAINTENANCE TICKET")
print("=" * 60)
print(ticket)