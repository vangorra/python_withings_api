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
from withings_api import AuthScope, Credentials, MeasureType, WithingsApi, WithingsAuth

CREDENTIALS_FILE: Final = path.abspath(
    path.join(path.dirname(path.abspath(__file__)), "../.credentials")
)


def save_credentials(credentials: Credentials) -> None:
    """Save credentials to a file."""
    print("# Saving credentials in:", CREDENTIALS_FILE)
    with open(CREDENTIALS_FILE, "wb") as file_handle:
        pickle.dump(credentials, file_handle)


def load_credentials() -> Credentials:
    """Load credentials from a file."""
    print("# Using credentials saved in:", CREDENTIALS_FILE)
    with open(CREDENTIALS_FILE, "rb") as file_handle:
        return cast(Credentials, pickle.load(file_handle))


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
        print("# Attempting to load credentials from:", CREDENTIALS_FILE)
        api = WithingsApi(load_credentials(), refresh_cb=save_credentials)
        try:
            api.user_get_device()
        except MissingTokenError:
            os.remove(CREDENTIALS_FILE)
            print("# Credentials in file are expired. Re-starting auth procedure...")

    if not path.isfile(CREDENTIALS_FILE):
        print("# Attempting to get credentials...")
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
        print("# Goto this URL in your browser and authorize:", authorize_url)
        print(
            "# Once you are redirected, copy and paste the whole url"
            "# (including code) here."
        )
        redirected_uri: Final = input("# Provide the entire redirect uri: ")
        redirected_uri_params: Final = dict(
            parse.parse_qsl(parse.urlsplit(redirected_uri).query)
        )
        auth_code: Final = redirected_uri_params["code"]

        print("# Getting credentials with auth code", auth_code)
        save_credentials(auth.get_credentials(auth_code))

        api = WithingsApi(load_credentials(), refresh_cb=save_credentials)

    # This only tests the refresh token. Token refresh is handled automatically by the api so you should not
    # need to use this method so long as your code regularly (every 3 hours or so) requests data from withings.
    orig_access_token = api.get_credentials().access_token
    print("# Refreshing token...")
    api.refresh_token()
    assert orig_access_token != api.get_credentials().access_token

    print("#" + "*" * 80 + "\n# Getting devices...\n#" + "*" * 80 + "\n")
    api.user_get_device().yamldump()  # type: ignore
    #   import pdb; pdb.set_trace()
    #   api.user_get_device().yamldump()  # type: ignore

    print("#" + "*" * 80 + "\n# Getting measures...\n#" + "*" * 80 + "\n")
    api.measure_get_meas(
        meastype=MeasureType.SPO2,
        startdate=arrow.utcnow().shift(days=-2),
        enddate=arrow.utcnow(),
    ).yamldump()  # type: ignore

    print("#" + "*" * 80 + "\n# Getting activity...\n#" + "*" * 80 + "\n")
    api.measure_get_activity(
        startdate=arrow.utcnow().shift(days=-2), enddate=arrow.utcnow()
    ).yamldump()  # type: ignore

    print("#" + "*" * 80 + "\n# Getting sleep...\n#" + "*" * 80 + "\n")
    api.sleep_get(
        startdate=arrow.utcnow().shift(days=-2), enddate=arrow.utcnow()
    ).yamldump()  # type: ignore

    print("#" + "*" * 80 + "\n# Getting sleep summary...\n#" + "*" * 80 + "\n")
    api.sleep_get_summary(
        startdate=arrow.utcnow().shift(days=-2), enddate=arrow.utcnow()
    ).yamldump()  # type: ignore

    heart_list = api.heart_list(
        startdate=arrow.utcnow().shift(days=-2), enddate=arrow.utcnow()
    )

    for series in heart_list.series:
        if series.ecg:
            signalid = series.ecg.signalid

            print("#" + "*" * 80 + "\n# Getting heart ecg...\n#" + "*" * 80 + "\n")
            series.ecgvalues = api.heart_get(signalid)
            series.yamldump(default_flow_style=True, width=200, indent=2)

    print("#" + "*" * 80 + "\n# Getting subscriptions...\n#" + "*" * 80 + "\n")
    api.notify_list().yamldump()  # type: ignore

    print("# Successfully finished.")


if __name__ == "__main__":
    main()
