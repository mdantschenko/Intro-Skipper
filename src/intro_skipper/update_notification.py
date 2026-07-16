import json
from importlib import metadata
from typing import Any, Callable

import requests

from intro_skipper.helpers.constants import UpdateCheckConstants


def _read_installed_commit_id() -> str | None:
    try:
        direct_url_text = metadata.distribution(
            UpdateCheckConstants.DISTRIBUTION_NAME
        ).read_text("direct_url.json")
    except metadata.PackageNotFoundError:
        return None
    if direct_url_text is None:
        return None
    direct_url_description: dict[str, Any] = json.loads(direct_url_text)
    return direct_url_description.get("vcs_info", {}).get("commit_id")


def _fetch_latest_commit_id() -> str | None:
    try:
        response = requests.get(
            UpdateCheckConstants.LATEST_COMMIT_URL,
            timeout=UpdateCheckConstants.REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.RequestException:
        return None
    commit_description: dict[str, Any] = response.json()
    return commit_description.get("sha")


def build_update_notification(
    read_installed_commit_id: Callable[[], str | None] = _read_installed_commit_id,
    fetch_latest_commit_id: Callable[[], str | None] = _fetch_latest_commit_id,
) -> str | None:
    installed_commit_id = read_installed_commit_id()
    if installed_commit_id is None:
        return None
    latest_commit_id = fetch_latest_commit_id()
    if latest_commit_id is None or latest_commit_id == installed_commit_id:
        return None
    return (
        "A newer version of Intro Skipper is available. Update it with: "
        + UpdateCheckConstants.UPDATE_COMMAND
    )
