import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from databases import Database

from models import Base, Event
from main import app, get_db

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:adarsh@localhost/test_db"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def test_client():

    # Create a test FastAPI app

    with TestClient(app) as client:
        yield client

event_data = {
        "event_title": "Test Event",
        "event_description": "This is a test event",
        "event_location": "Test Location",
        "event_date": "2023-06-10T11:40:00"
    }

updated_event_data = {
        "event_title": "Updated Event",
        "event_description": "Updated Description",
        "event_location": "Updated Location",
        "event_date": "2023-06-10T11:40:00"
    }

user_data = {
        "firstname": "Akshay",
        "lastname": "Joy",
        "email": "akshay@example.com",
        "address": "New city"
    }

updated_user_data = {
        "firstname": "Updated First Name",
        "lastname": "Updated Last Name",
        "email": "updated@example.com",
        "address": "Updated Address"
    }


def test_create_event(test_client):

    # Send a POST request to create the event
    response = test_client.post("/events/", json=event_data)

    # Check if the response status code is 200 (Created)
    assert response.status_code == 200

    
def test_create_event_title_missing(test_client):
    # Define event data for testing
    del event_data["event_title"]

    # Send a POST request to create the event
    response = test_client.post("/events/", json=event_data)

    # Check if the response status code is 422
    assert response.status_code == 422

def test_create_event_date_missing(test_client):
    # Define event data for testing
    del event_data["event_date"]

    # Send a POST request to create the event
    response = test_client.post("/events/", json=event_data)

    # Check if the response status code is 422
    assert response.status_code == 422


def test_update_event_success(test_client):
    # Send a PUT request to update the event
    response = test_client.put(f"/events/6/",json=updated_event_data)

    # Check if the response status code is 200 (OK)
    assert response.status_code == 200

def test_update_event_id_not_present(test_client):
    # Send a PUT request to update the event
    response = test_client.put(f"/events/1/",json=updated_event_data)

    # Check if the response status code is 404
    assert response.status_code == 404

def test_update_event_title_missing(test_client):
    del updated_event_data["event_title"]
    # Send a PUT request to update the event
    response = test_client.put(f"/events/38/",json=updated_event_data)

    # Check if the response status code is 422
    assert response.status_code == 422

def test_update_event_date_missing(test_client):
    del updated_event_data["event_date"]
    # Send a PUT request to update the event
    response = test_client.put(f"/events/38/",json=updated_event_data)

    # Check if the response status code is 422
    assert response.status_code == 422

def test_delete_event_success(test_client):
    # Send a DELETE request to delete the event
    response = test_client.delete(f"/events/9/")

    # Check if the response status code is 200 (OK)
    assert response.status_code == 200

def test_delete_event_failure(test_client):
    # Send a DELETE request to delete the event
    response = test_client.delete(f"/events/1/")

    # Check if the response status code is 404
    assert response.status_code == 404

def test_create_user_success(test_client):
    # Send a POST request to create the user
    response = test_client.post("/users/", json=user_data)

    # Check if the response status code is 200
    assert response.status_code == 200


def test_create_user_fname_missing(test_client):
    del user_data["firstname"]
    # Send a POST request to create the user
    response = test_client.post("/users/", json=user_data)

    # Check if the response status code is 422
    assert response.status_code == 422

def test_create_user_lname_missing(test_client):
    del user_data["lastname"]
    # Send a POST request to create the user
    response = test_client.post("/users/", json=user_data)

    # Check if the response status code is 422
    assert response.status_code == 422

def test_create_user_email_missing(test_client):
    del user_data["email"]

    # Send a POST request to create the user
    response = test_client.post("/users/", json=user_data)

    # Check if the response status code is 422
    assert response.status_code == 422

def test_create_user_address_missing(test_client):
    del user_data["address"]

    # Send a POST request to create the user
    response = test_client.post("/users/", json=user_data)

    # Check if the response status code is 422
    assert response.status_code == 422

# Pytest test case to update a user
def test_update_user(test_client):

    # Send a PUT request to update the user
    response = test_client.put(f"/users/28/", json=updated_user_data)

    # Check if the response status code is 200 (OK)
    assert response.status_code == 200

def test_update_user_not_present(test_client):
  
    # Send a PUT request to update the user
    response = test_client.put(f"/users/1/", json=updated_user_data)

    # Check if the response status code is 404
    assert response.status_code == 404

def test_update_user_fname_missing(test_client):
    del updated_user_data["firstname"]

    # Send a PUT request to update the user
    response = test_client.put(f"/users/23/", json=updated_user_data)

    # Check if the response status code is 422
    assert response.status_code == 422

def test_update_user_lname_missing(test_client):
    del updated_user_data["lastname"]

    # Send a PUT request to update the user
    response = test_client.put(f"/users/23/", json=updated_user_data)

    # Check if the response status code is 422
    assert response.status_code == 422

def test_update_user_email_missing(test_client):
    del updated_user_data["email"]

    # Send a PUT request to update the user
    response = test_client.put(f"/users/23/", json=updated_user_data)

    # Check if the response status code is 422
    assert response.status_code == 422

def test_update_user_address_missing(test_client):
    del updated_user_data["address"]

    # Send a PUT request to update the user
    response = test_client.put(f"/users/28/", json=updated_user_data)

    # Check if the response status code is 422
    assert response.status_code == 422


def test_delete_user(test_client):
    # Send a DELETE request to delete the user
    response = test_client.delete(f"/users/28/")

    # Check if the response status code is 200 (OK)
    assert response.status_code == 200

def test_delete_user_not_present(test_client):
    # Send a DELETE request to delete the user
    response = test_client.delete(f"/users/1/")

    # Check if the response status code is 404
    assert response.status_code == 404

def test_register_user_for_event(test_client):
     
    # Send a POST request to register the user for the event
    response = test_client.post("/events/register/", json=registration_data)

    # Check if the response status code is 200
    assert response.status_code == 200

def test_register_user_for_event_id_not_present(test_client):
    registration_data = {
        "user_id": 28 ,
        "event_id": 10
    }

    # Send a POST request to register the user for the event
    response = test_client.post("/events/register/", json=registration_data)

    # Check if the response status code is 404
    assert response.status_code == 404

def test_register_user_for_event_user_not_present(test_client):
    registration_data = {
        "user_id": 28 ,
        "event_id": 10
    }
    # Send a POST request to register the user for the event
    response = test_client.post("/events/register/", json=registration_data)

    # Check if the response status code is 404
    assert response.status_code == 404

def test_register_user_already_registered(test_client):
    registration_data = {
        "user_id": 28 ,
        "event_id": 10
    }
    # Send a POST request to register the user for the event
    response = test_client.post("/events/register/", json=registration_data)

    # Check if the response status code is 400
    assert response.status_code == 422


# Pytest test case to fetch registered users for an event
def test_fetch_registered_users_for_event(test_client):

    # Send a GET request to fetch registered users for the event
    response = test_client.get(f"/events/8/registered_users/")

    # Check if the response status code is 200 (OK)
    assert response.status_code == 200

def test_fetch_registered_users_for_event_not_present(test_client):

    # Send a GET request to fetch registered users for the event
    response = test_client.get(f"/events/5/registered_users/")

    # Check if the response status code is 404
    assert response.status_code == 422

# Pytest test case to fetch events registered by a user
def test_fetch_events_registered_by_user(test_client):
    # Send a GET request to fetch events registered by the user
    response = test_client.get(f"/users/28/registered_events/")

    # Check if the response status code is 200 (OK)
    assert response.status_code == 200

def test_fetch_events_registered_by_user_not_present(test_client):
    # Send a GET request to fetch events registered by the user
    response = test_client.get(f"/users/1/registered_events/")

    # Check if the response status code is 404
    assert response.status_code == 404

# Pytest test case to send invitations to a list of users
def test_send_invitations(test_client):

    # Define invitation data with a list of user emails
    invitation_data = {
        "emails": ["testuser@example.com"],
        "event_name": "Test Event"
    }

    # Send a POST request to send invitations
    response = test_client.post("/send_invitations/", json=invitation_data)

    # Check if the response status code is 200 (OK)
    assert response.status_code == 200

def test_send_invitations_missing_email_id(test_client):

    # Define invitation data with a list of user emails
    invitation_data = {
        #"emails": ["testuser@example.com"],
        "event_name": "Test Event"
    }

    # Send a POST request to send invitations
    response = test_client.post("/send_invitations/", json=invitation_data)

    # Check if the response status code 422
    assert response.status_code == 422

def test_send_invitations_missing_event_name(test_client):

    # Define invitation data with a list of user emails
    invitation_data = {
        "emails": ["testuser@example.com"],
        #"event_name": "Test Event"
    }

    # Send a POST request to send invitations
    response = test_client.post("/send_invitations/", json=invitation_data)

    # Check if the response status code 422
    assert response.status_code == 422


    


