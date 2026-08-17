from src.safety_checker import check_safety


test_ticket = """
Issue Category: Electrical
Issue Title: Sparking Switchboard
Severity: High
Description: Sparks are coming from an exposed wire near the switchboard.
Safety Risk: Electric shock and fire hazard.
Recommended Action: Shut off power and inspect immediately.
Assigned Department: Electrical
"""


result = check_safety(test_ticket)

print("\nCAMPUSFIX SAFETY CHECK")
print("=" * 60)
print(f"Severity: {result['severity']}")
print(f"Escalation: {result['escalation']}")
print(f"Message: {result['message']}")