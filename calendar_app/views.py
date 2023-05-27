from typing import Any
from django.http.response import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import View
import google.oauth2.credentials
import google_auth_oauthlib.flow
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from backend_assessment.settings import BASE_DIR
import json
import os
import traceback

# Create your views here.

# CLIENT_SECRETS_FILE = str(BASE_DIR / "credentials.json")

CLIENT_SECRETS_CONFIG = {
    os.environ.get("CLIENT_TYPE", "web"): {
        "client_id": os.environ.get("client_id"),
        "client_secret": os.environ.get("client_secret"),
        "auth_uri": os.environ.get("auth_uri"),
        "token_uri": os.environ.get("token_uri"),
        "auth_provider_x509_cert_url": os.environ.get("auth_provider_x509_cert_url"),
        "client_x509_cert_url": os.environ.get("client_x509_cert_url"),
        "redirect_uris": [
            # "http://localhost:8000/rest/v1/calendar/redirect",
            # "http://localhost:8000/rest/v1/calendar/redir",
            # "http://localhost:8000",
            "https://convin-task.anuranroy1.repl.co/rest/v1/calendar/redirect",
            "https://convin-task.anuranroy1.repl.co/rest/v1/calendar/redir",
            "https://convin-task.anuranroy1.repl.co",
            "https://92d38d49-f819-4ed6-b134-1692495d4b0d.id.repl.co/rest/v1/calendar/redirect",
            "https://92d38d49-f819-4ed6-b134-1692495d4b0d.id.repl.co/rest/v1/calendar/redir",
            "https://92d38d49-f819-4ed6-b134-1692495d4b0d.id.repl.co",
        ],
        "javascript_origins": [
            # "http://localhost:8000",
            "https://convin-task.anuranroy1.repl.co",
            "https://92d38d49-f819-4ed6-b134-1692495d4b0d.id.repl.co",
        ],
    }
}

SCOPES = ["https://www.googleapis.com/auth/calendar.events.readonly"]


def get_data(creds, event_count=10):
    try:
        service = build("calendar", "v3", credentials=creds, static_discovery=False)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        print(f"Getting the upcoming {event_count} events")
        events_list: list[dict[str, str]] = []
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=event_count,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return []

        # Prints the start and name of the next 10 events
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            # print(event)
            print(start, event["summary"])
            events_list.append(event)

        return events_list
    except HttpError as error:
        print("An error occurred: %s" % error)


class GoogleCalendarInitView(View):
    # def __init__(self, request) -> None:
    #     super(View, self).__init__(request)

    def get(self, request) -> Any:
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            CLIENT_SECRETS_CONFIG, scopes=SCOPES
        )

        # Indicate where the API server will redirect the user after the user completes
        # the authorization flow. The redirect URI is required. The value must exactly
        # match one of the authorized redirect URIs for the OAuth 2.0 client, which you
        # configured in the API Console. If this value doesn't match an authorized URI,
        # you will get a 'redirect_uri_mismatch' error.
        flow.redirect_uri = (
            "https://convin-task.anuranroy1.repl.co/rest/v1/calendar/redirect"
        )

        print("\n\nFlow Dir = \n", dir(flow))
        print("\n\nFlow Dict = \n", flow.__dict__)
        # Generate URL for request to Google's OAuth 2.0 server.
        # Use kwargs to set optional request parameters.
        authorization_url, state = flow.authorization_url(
            # Enable offline access so that you can refresh an access token without
            # re-prompting the user for permission. Recommended for web server apps.
            access_type="offline",
            # Enable incremental authorization. Recommended as a best practice.
            include_granted_scopes="true",
        )

        # print("\n\nFlow Creds Dir = \n", dir(flow.credentials))

        # return redirect(to=authorization_url)
        print("\n\nAuthorization URL = ", authorization_url)
        return HttpResponseRedirect(
            redirect_to=authorization_url,
        )


class GoogleCalendarRedirectView(View):
    # def __init__(self, request, **kwargs: Any) -> None:
    #     super(View, self).__init__(**kwargs)

    def get(self, request) -> Any:
        # super(View, self).get(request, **kwargs)
        try:
            get_dict = request.GET
            print("\n\nQuery Dict received on RedirectView = \n", get_dict)
            state = get_dict.get("state")
            flow = google_auth_oauthlib.flow.Flow.from_client_config(
                CLIENT_SECRETS_CONFIG, scopes=SCOPES, state=state
            )
            flow.redirect_uri = "https://convin-task.anuranroy1.repl.co/rest/v1/calendar/redirect"  # flask.url_for("oauth2callback", _external=True)
            authorization_response = request.build_absolute_uri()
            flow.fetch_token(authorization_response=authorization_response)

            credentials = flow.credentials
            request.session["credentials"] = {
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes,
            }

            print(request.session.__dict__)
            events_list = get_data(creds=credentials)
            if len(events_list) > 0:
                print(json.dumps(events_list[0], indent=4))

            return render(
                request, "templates/render_events.html", context={"events": events_list}
            )
            # return HttpResponse("Redirect done.")
        except Exception as e:
            return HttpResponse(
                f"Couldn't process request. Go to login page and try again. Error message: {traceback.print_exc()}"
            )
