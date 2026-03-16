"""Constants specific to GitHub Actions endpoint tests."""

# Public repo with known Actions workflows
TEST_ACTIONS_OWNER = "actions"
TEST_ACTIONS_REPO = "checkout"

WORKFLOW_REQUIRED_FIELDS = [
    "id",
    "name",
    "path",
    "state",
    "created_at",
    "updated_at",
]

WORKFLOW_RUN_REQUIRED_FIELDS = [
    "id",
    "name",
    "status",
    "conclusion",
    "workflow_id",
    "created_at",
]

WORKFLOW_STATES = ["active", "disabled_manually", "disabled_inactivity"]
RUN_STATUSES = ["queued", "in_progress", "completed"]
RUN_CONCLUSIONS = ["success", "failure", "cancelled", "skipped", "timed_out"]
