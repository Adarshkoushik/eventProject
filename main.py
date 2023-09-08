from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from databases import Database
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import smtplib
import os

from models import Event, User, EventRegistration
from schema import EventCreate, UserCreate, EventUpdate, EventRegistrationCreate, UserUpdate, SendEmail

load_dotenv(".env")

# FastAPI app
app = FastAPI()

# Database setup
engine = create_engine(os.getenv("DATABASE_URL"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
database = Database(os.getenv("DATABASE_URL"))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Route to create a new event
@app.post("/events/")
async def create_event(event: EventCreate, db: SessionLocal = Depends(get_db)):
    event_db = Event(**event.dict())
    db.add(event_db)
    db.commit()
    db.refresh(event_db)
    return event

# Route to update an event by ID
@app.put("/events/{event_id}/")
async def update_event(event_id: int, event_data: EventUpdate, db: SessionLocal = Depends(get_db)):
    # Check if the event with the specified ID exists
    event = db.query(Event).filter(Event.event_id == event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Update the event data
    event.event_title = event_data.event_title
    event.event_description = event_data.event_description
    event.event_location = event_data.event_location
    event.event_date = event_data.event_date

    db.commit()
    db.refresh(event)

    return event

# Route to delete an event by ID
@app.delete("/events/{event_id}/")
async def delete_event(event_id: int, db: SessionLocal = Depends(get_db)):
    # Check if the event with the specified ID exists
    event = db.query(Event).filter(Event.event_id == event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Delete the event
    db.delete(event)
    db.commit()

    return {"message": "Event deleted successfully"}


# Register a new user
@app.post("/users/")
async def create_user(user: UserCreate, db: SessionLocal = Depends(get_db)):
    user_db = User(**user.dict())
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return user_db

# Route to update a user by ID
@app.put("/users/{user_id}/")
async def update_user(user_id: int, user_data: UserUpdate, db: SessionLocal = Depends(get_db)):
    # Check if the user with the specified ID exists
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update the user's information
    user.firstname = user_data.firstname
    user.lastname = user_data.lastname
    user.email = user_data.email
    user.address = user_data.address

    db.commit()
    db.refresh(user)

    return user

# Route to delete a user by ID
@app.delete("/users/{user_id}/")
async def delete_user(user_id: int, db: SessionLocal = Depends(get_db)):
    # Check if the user with the specified ID exists
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete the user
    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}

# Register a user for an event
@app.post("/events/register/")
async def register_user_for_event(event_registration: EventRegistrationCreate, db: SessionLocal = Depends(get_db)):
    # Check if the user and event exist
    user = db.query(User).filter(User.user_id == event_registration.user_id).first()
    event = db.query(Event).filter(Event.event_id == event_registration.event_id).first()

    if not user or not event:
        raise HTTPException(status_code=404, detail="User or Event not found")

    # Check if the user is already registered for the event
    existing_registration = db.query(EventRegistration).filter(
        EventRegistration.user_id == event_registration.user_id,
        EventRegistration.event_id == event_registration.event_id
    ).first()

    if existing_registration:
        raise HTTPException(status_code=400, detail="User is already registered for this event")

    # Register the user for the event
    registration_db = EventRegistration(**event_registration.dict(),registration_date=datetime.utcnow())
    db.add(registration_db)
    db.commit()
    db.refresh(registration_db)
    return registration_db

# Route to get all users registered for a specific event
@app.get("/events/{event_id}/registered_users/")
async def get_registered_users(event_id: int, db: SessionLocal = Depends(get_db)):
    event = db.query(Event).filter(Event.event_id == event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Query users registered for the event
    registered_users = db.query(User).join(EventRegistration, User.user_id == EventRegistration.user_id).filter(
        EventRegistration.event_id == event_id
    ).all()

    return registered_users

# Route to get all events registered by a specific user
@app.get("/users/{user_id}/registered_events/")
async def get_registered_events(user_id: int, db: SessionLocal = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Query events registered by the user
    registered_events = db.query(Event).join(EventRegistration, Event.event_id == EventRegistration.event_id).filter(
        EventRegistration.user_id == user_id
    ).all()

    return registered_events

#SEND EMAIL INVITATION
def send_invitation_email(to_email, event_name):
    # Create an SMTP server connection
    server = smtplib.SMTP(os.getenv("EMAIL_HOST"), os.getenv("EMAIL_PORT"))

    # Create a MIMEText object for the email body
    message = MIMEMultipart()
    message["From"] = "adarshkoushik@gmail.com"  # Your email address
    message["To"] = to_email
    message["Subject"] = "Invitation to Event"

    # Email body content
    body = f"Hi,\n\nYou are invited to the event: {event_name}\n\nRegards,\nAdarsh"
    message.attach(MIMEText(body, "plain"))

    # Send the email
    server.sendmail("your_email@example.com", to_email, message.as_string())

    # Close the SMTP server connection
    server.quit()

# Route to send invitations to a list of users
@app.post("/send_invitations/")
async def send_invitations(send_email: SendEmail):
    print(send_email)
    emails = send_email.emails
    event_name = send_email.event_name
    for email in emails:
        send_invitation_email(email, event_name)
    return {"message": f"Email sent succesffuly for {emails}"}

