from pydantic import BaseModel
from datetime import datetime


# Pydantic model for input validation
class EventCreate(BaseModel):
    event_title: str
    event_description: str
    event_location: str
    event_date: datetime

class UserCreate(BaseModel):
    firstname: str
    lastname: str
    email: str
    address: str

class EventRegistrationCreate(BaseModel):
    user_id: int
    event_id: int

# Pydantic model for updating events
class EventUpdate(BaseModel):
    event_title: str
    event_description: str
    event_location: str
    event_date: datetime

class SendEmail(BaseModel):
    emails: list
    event_name: str