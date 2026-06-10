from pydantic import BaseModel
from typing import Optional

# Defines the exact JSON structure expected when a user submits the "Create Ticket" form
class TicketCreate(BaseModel):
    customer_name: str
    customer_email: str
    subject: str
    description: str

# Defines the JSON structure expected when updating a ticket
class TicketUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None