from datetime import datetime
from PRP_CDM_app.models.common_data_model import Proposals, Laboratories

# --- Retrieve the lab instance ---
lab = Laboratories.objects.get(lab_id="LAGE")

# --- Create a new proposal ---
proposal = Proposals.objects.create(
    proposal_id=1044,
    title="1st proposal",
    status="scheduling",
    submission_date=datetime(2025, 7, 23, 13, 19, 21),
    scheduled_instrument_ids=[11355, 11356],
    team_leader_username="test",
    team_leader_first_name="test",
    team_leader_last_name="test",
    team_leader_email="test@user.com",
)

# --- Link the proposal to the lab ---
proposal.labs.add(lab)

print("✅ Proposal inserted successfully:", proposal)
print("🔗 Linked labs:", proposal.labs.all())
