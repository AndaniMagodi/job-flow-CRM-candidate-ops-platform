from datetime import date
from pydantic import BaseModel
from typing import Optional

VALID_STATUSES = {"Applied", "Interview", "Offer", "Rejected"}

class ApplicationCreate(BaseModel):
    company: str
    role: str
    status: str = "Applied"
    date_applied: date
    follow_up_date: Optional[date] = None
    link: Optional[str] = None
    notes: Optional[str] = None

    model_config = {"from_attributes": True}

class ApplicationUpdate(BaseModel):
    status: str

    def validate_status(self):
        if self.status not in VALID_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {VALID_STATUSES}")

class ApplicationResponse(BaseModel):
    id: int
    user_id: int
    company: str
    role: str
    status: str
    date_applied: date
    follow_up_date: Optional[date] = None
    link: Optional[str] = None
    notes: Optional[str] = None

    model_config = {"from_attributes": True}


class FollowUpUpdate(BaseModel):
    follow_up_date: date