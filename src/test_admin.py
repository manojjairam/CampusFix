from src.database import (
    get_all_tickets,
    get_ticket_details,
    update_ticket_status
)


print("\nCAMPUSFIX ADMIN TEST")
print("=" * 60)

tickets = get_all_tickets()

print(f"\nTotal Tickets: {len(tickets)}\n")

for ticket in tickets:
    print(
        f"ID: {ticket['ticket_id']} | "
        f"Issue: {ticket['issue_title']} | "
        f"Severity: {ticket['severity']} | "
        f"Status: {ticket['status']}"
    )


if tickets:

    ticket_id = tickets[0]["ticket_id"]

    print("\nUpdating latest ticket...")
    updated = update_ticket_status(ticket_id, "In Progress")

    if updated:
        print(f"Ticket {ticket_id} updated successfully!")

        ticket = get_ticket_details(ticket_id)

        print("\nUPDATED TICKET")
        print("=" * 60)
        print(f"Ticket ID: {ticket['ticket_id']}")
        print(f"Issue: {ticket['issue_title']}")
        print(f"Status: {ticket['status']}")

    else:
        print("Ticket update failed.")