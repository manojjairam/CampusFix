from src.database import get_ticket_details


ticket_id = 2

ticket = get_ticket_details(ticket_id)

print("\nCAMPUSFIX TICKET STATUS")
print("=" * 60)

if ticket:

    print(f"Ticket ID: {ticket['ticket_id']}")
    print(f"Issue: {ticket['issue_title']}")
    print(f"Location: {ticket['location']}")
    print(f"Severity: {ticket['severity']}")
    print(f"Department: {ticket['assigned_department']}")
    print(f"Status: {ticket['status']}")
    print(f"Created: {ticket['created_at']}")

else:

    print("Ticket not found.")