import pytest

from intro_skipper.command_line_arguments import parse_command_line_options


def parse_service_names(argument_list: list[str]) -> list[str]:
    return [
        streaming_service.name
        for streaming_service in parse_command_line_options(
            argument_list
        ).streaming_services
    ]


def test_no_arguments_open_no_service() -> None:
    assert parse_service_names([]) == []


def test_a_single_service_is_opened_by_name() -> None:
    assert parse_service_names(["netflix"]) == ["Netflix"]


def test_service_names_are_case_insensitive() -> None:
    assert parse_service_names(["Netflix"]) == ["Netflix"]


def test_two_services_can_be_combined() -> None:
    assert parse_service_names(["netflix", "disney"]) == ["Netflix", "Disney+"]


def test_amazon_prime_is_reachable_under_both_names() -> None:
    assert parse_service_names(["amazon"]) == ["Amazon Prime Video"]
    assert parse_service_names(["prime"]) == ["Amazon Prime Video"]


def test_duplicate_names_open_a_service_only_once() -> None:
    assert parse_service_names(["amazon", "prime"]) == ["Amazon Prime Video"]


def test_all_opens_every_service() -> None:
    assert parse_service_names(["all"]) == [
        "Netflix",
        "Disney+",
        "Amazon Prime Video",
    ]


def test_an_unknown_name_is_rejected_with_an_error() -> None:
    with pytest.raises(SystemExit):
        parse_command_line_options(["youtube"])


def test_log_files_are_disabled_by_default() -> None:
    assert parse_command_line_options([]).write_log_file is False


def test_the_log_flag_enables_log_files() -> None:
    assert parse_command_line_options(["--log"]).write_log_file is True


def test_the_log_flag_can_be_combined_with_services() -> None:
    command_line_options = parse_command_line_options(["netflix", "--log"])
    assert command_line_options.write_log_file is True
    assert [
        streaming_service.name
        for streaming_service in command_line_options.streaming_services
    ] == ["Netflix"]
