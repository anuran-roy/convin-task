import os
import google_auth_oauthlib.flow
from googleapiclient.discovery import build

# Set up the OAuth 2.0 flow
scopes = ["https://www.googleapis.com/auth/calendar.events.readonly"]
client_secrets_file = "credentials.json"  # Path to your client secrets JSON file
token_file = "token.json"  # Path to store the generated token

# Initialize the flow
flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    client_secrets_file, scopes=scopes
)

# Redirect URI where the user will be redirected after completing the authorization
redirect_uri = "http://localhost:8000/rest/v1/calendar/redirect/"
authorization_url, state = flow.authorization_url(
    redirect_uri=redirect_uri, access_type="offline"
)

# Print the authorization URL and instruct the user to visit it
print(
    f"Please visit the following URL to authorize the application: {authorization_url}"
)

# After authorization, Google will redirect the user to the redirect_uri
# with an authorization code in the query parameters

# Obtain the authorization code from the user
authorization_code = input("Enter the authorization code: ")

# Exchange the authorization code for a token
flow.fetch_token(authorization_response=authorization_code)

# Save the token to a file for future use
token = flow.credentials.to_json()
with open(token_file, "w") as f:
    f.write(token)
print("Token saved to", token_file)

# Create a service object for interacting with the Google API
service = build("calendar", "v3", credentials=flow.credentials)

# Now you can use the `service` object to make API requests
# For example, let's list the user's next 10 events from their calendar
events = service.events().list(calendarId="primary", maxResults=10).execute()
for event in events["items"]:
    print(event["summary"])
