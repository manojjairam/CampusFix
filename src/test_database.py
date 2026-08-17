from src.database import create_database, save_ticket, get_ticket, get_all_tickets


create_database()

sample_ticket = {
    "issue_category": "Electrical",
    "issue_title": "Malfunctioning Ceiling Fan",
    "severity": "High",
    "description": "The ceiling fan is shaking and making a loud noise.",
    "safety_risk": "The unstable fan may fall and cause injury.",
    "recommended_action": "Inspect the fan immediately and repair or replace damaged parts.",
    "assigned_department": "Electrical",
    "location": "Academic Block A",
    "room": "Room 204",
    "student_description": "The fan is shaking and making a loud noise.",
    "escalation": "Priority Maintenance Required"
}


ticket_id = save_ticket(sample_ticket)

print("\nCAMPUSFIX DATABASE TEST")
print("=" * 60)
print(f"Ticket saved successfully!")
print(f"Generated Ticket ID: {ticket_id}")


ticket = get_ticket(ticket_id)

print("\nRETRIEVED TICKET")
print("=" * 60)
print(ticket)


all_tickets = get_all_tickets()

print("\nTOTAL TICKETS")
print("=" * 60)
print(len(all_tickets))