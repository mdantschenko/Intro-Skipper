from intro_skipper.update_notification import build_update_notification


def fail_because_network_must_not_be_contacted() -> str | None:
    raise AssertionError("the network must not be contacted")


def test_update_notice_names_the_upgrade_command() -> None:
    notification = build_update_notification(
        read_installed_commit_id=lambda: "installed-commit",
        fetch_latest_commit_id=lambda: "newer-commit",
    )
    assert notification is not None
    assert "uv tool upgrade intro-skipper" in notification


def test_no_notice_when_the_installed_version_is_current() -> None:
    notification = build_update_notification(
        read_installed_commit_id=lambda: "same-commit",
        fetch_latest_commit_id=lambda: "same-commit",
    )
    assert notification is None


def test_development_installs_skip_the_check_without_network_access() -> None:
    notification = build_update_notification(
        read_installed_commit_id=lambda: None,
        fetch_latest_commit_id=fail_because_network_must_not_be_contacted,
    )
    assert notification is None


def test_no_notice_when_github_is_unreachable() -> None:
    notification = build_update_notification(
        read_installed_commit_id=lambda: "installed-commit",
        fetch_latest_commit_id=lambda: None,
    )
    assert notification is None
