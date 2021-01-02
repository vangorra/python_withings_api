#!/usr/bin/env python3
"""Integration test."""
import argparse
import os
from os import path
import pickle
from typing import cast
from urllib import parse

import arrow
from oauthlib.oauth2.rfc6749.errors import MissingTokenError
from typing_extensions import Final
from withings_api import AuthScope, WithingsApi, WithingsAuth
from withings_api.common import CredentialsType, GetSleepField, GetSleepSummaryField

CREDENTIALS_FILE: Final = path.abspath(
    path.join(path.dirname(path.abspath(__file__)), "../.credentials")
)


def save_credentials(credentials: CredentialsType) -> None:
    """Save credentials to a file."""
    print("Saving credentials in:", CREDENTIALS_FILE)
    with open(CREDENTIALS_FILE, "wb") as file_handle:
        pickle.dump(credentials, file_handle)


def load_credentials() -> CredentialsType:
    """Load credentials from a file."""
    print("Using credentials saved in:", CREDENTIALS_FILE)
    with open(CREDENTIALS_FILE, "rb") as file_handle:
        return cast(CredentialsType, pickle.load(file_handle))


def main() -> None:
    """Run main function."""
    parser: Final = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument(
        "--client-id",
        dest="client_id",
        help="Client id provided by withings.",
        required=True,
    )
    parser.add_argument(
        "--consumer-secret",
        dest="consumer_secret",
        help="Consumer secret provided by withings.",
        required=True,
    )
    parser.add_argument(
        "--callback-uri",
        dest="callback_uri",
        help="Callback URI configured for withings application.",
        required=True,
    )
    parser.add_argument(
        "--live-data",
        dest="live_data",
        action="store_true",
        help="Should we run against live data? (Removal of .credentials file is required before running)",
    )

    args: Final = parser.parse_args()

    if path.isfile(CREDENTIALS_FILE):
        print("Attempting to load credentials from:", CREDENTIALS_FILE)
        api = WithingsApi(load_credentials(), refresh_cb=save_credentials)
        try:
            api.user_get_device()
        except MissingTokenError:
            os.remove(CREDENTIALS_FILE)
            print("Credentials in file are expired. Re-starting auth procedure...")

    if not path.isfile(CREDENTIALS_FILE):
        print("Attempting to get credentials...")
        auth: Final = WithingsAuth(
            client_id=args.client_id,
            consumer_secret=args.consumer_secret,
            callback_uri=args.callback_uri,
            mode=None if args.live_data else "demo",
            scope=(
                AuthScope.USER_ACTIVITY,
                AuthScope.USER_METRICS,
                AuthScope.USER_INFO,
                AuthScope.USER_SLEEP_EVENTS,
            ),
        )

        authorize_url: Final = auth.get_authorize_url()
        print("Goto this URL in your browser and authorize:", authorize_url)
        print(
            "Once you are redirected, copy and paste the whole url"
            "(including code) here."
        )
        redirected_uri: Final = input("Provide the entire redirect uri: ")
        redirected_uri_params: Final = dict(
            parse.parse_qsl(parse.urlsplit(redirected_uri).query)
        )
        auth_code: Final = redirected_uri_params["code"]

        print("Getting credentials with auth code", auth_code)
        save_credentials(auth.get_credentials(auth_code))

        api = WithingsApi(load_credentials(), refresh_cb=save_credentials)

    # This only tests the refresh token. Token refresh is handled automatically by the api so you should not
    # need to use this method so long as your code regularly (every 3 hours or so) requests data from withings.
    orig_access_token = api.get_credentials().access_token
    print("Refreshing token...")
    api.refresh_token()
    assert orig_access_token != api.get_credentials().access_token

    print("Getting devices...")
    assert api.user_get_device() is not None

    print("Getting measures...")
    assert (
        api.measure_get_meas(
            startdate=arrow.utcnow().shift(days=-21), enddate=arrow.utcnow()
        )
        is not None
    )

    print("Getting activity...")
    assert (
        api.measure_get_activity(
            startdateymd=arrow.utcnow().shift(days=-21), enddateymd=arrow.utcnow()
        )
        is not None
    )

    print("Getting sleep...")
    assert (
        api.sleep_get(
            data_fields=GetSleepField,
            startdate=arrow.utcnow().shift(days=-2),
            enddate=arrow.utcnow(),
        )
        is not None
    )

    print("Getting sleep summary...")
    assert (
        api.sleep_get_summary(
            data_fields=GetSleepSummaryField,
            startdateymd=arrow.utcnow().shift(days=-2),
            enddateymd=arrow.utcnow(),
        )
        is not None
    )

    print("Getting subscriptions...")
    assert api.notify_list() is not None

    print("Successfully finished.")


if __name__ == "__main__":
    main()
