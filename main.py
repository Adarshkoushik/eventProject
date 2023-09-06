from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from databases import Database
from pydantic import BaseModel
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# FastAPI app
app = FastAPI()

# Database setup
DATABASE_URL = "postgresql://postgres:adarsh@localhost/mydb"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
database = Database(DATABASE_URL)

# SQLAlchemy models
Base = declarative_base()

class Event(Base):
    __tablename__ = "events"

    event_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    event_title = Column(String, index=True)
    event_description = Column(String)
    event_date = Column(DateTime, server_default=text("(now() at time zone 'UTC')"))
    event_location = Column(String)

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String, unique=True, index=True)
    lastname = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    address = Column(String)

class EventRegistration(Base):
    __tablename__ = "eventregistrations"

    registration_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    event_id = Column(Integer, index=True)
    registration_date = Column(DateTime, server_default=text("(now() at time zone 'UTC')"))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic model for input validation
class EventCreate(BaseModel):
    event_title: str
    event_description: str
    event_location: str

class UserCreate(BaseModel):
    firstname: str
    lastname: str
    email: str
    address: str

class EventRegistrationCreate(BaseModel):
    user_id: int
    event_id: int
    

# Route to create a new event
@app.post("/events/")
# async def create_event(event: EventCreate, db: SessionLocal = Depends(database.transaction())):
async def create_event(event: EventCreate, db: SessionLocal = Depends(get_db)):
    event_db = Event(**event.dict(),event_date=datetime.utcnow())
    db.add(event_db)
    db.commit()
    db.refresh(event_db)
    return event

# Register a new user
@app.post("/users/")
async def create_user(user: UserCreate, db: SessionLocal = Depends(get_db)):
    user_db = User(**user.dict())
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return user_db

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

# Configure MailHog SMTP server settings
EMAIL_HOST = "localhost"  # MailHog SMTP server hostname
EMAIL_PORT = 1025         # MailHog SMTP server port
EMAIL_USE_TLS = False

# Function to send an invitation email
def send_invitation_email(to_email, event_name):
    # Create an SMTP server connection
    server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)

    # Create a MIMEText object for the email body
    message = MIMEMultipart()
    message["From"] = "your_email@example.com"  # Your email address
    message["To"] = to_email
    message["Subject"] = "Invitation to Event"

    # Email body content
    body = f"Hi,\n\nYou are invited to the event: {event_name}\n\nRegards,\nAdarsh"
    message.attach(MIMEText(body, "plain"))

    # Send the email
    server.sendmail("your_email@example.com", to_email, message.as_string())

    # Close the SMTP server connection
    server.quit()

class SendEmail(BaseModel):
    email: list
    event_name: str


# Route to send invitations to a list of users
@app.post("/send_invitations/")
async def send_invitations(send_email: SendEmail):
    print(send_email)
    email = send_email.email
    event_name = send_email.event_name
    for emails in email:
        send_invitation_email(emails, event_name)
    return {"message": f"Email sent succesffuly for {email}"}

