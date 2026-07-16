import argparse
from dataclasses import dataclass
from typing import Sequence

from intro_skipper.helpers.constants import ApplicationConstants
from intro_skipper.services.streaming_service import StreamingService
from intro_skipper.services.streaming_service_catalog import (
    build_all_streaming_services,
)


@dataclass(frozen=True)
class CommandLineOptions:
    streaming_services: tuple[StreamingService, ...]
    write_log_file: bool


def parse_command_line_options(argument_list: Sequence[str]) -> CommandLineOptions:
    parser = _build_argument_parser()
    parsed_arguments = parser.parse_args(list(argument_list))
    try:
        streaming_services = _resolve_streaming_service_names(
            parsed_arguments.streaming_services
        )
    except ValueError as error:
        parser.error(str(error))
    return CommandLineOptions(
        streaming_services=streaming_services,
        write_log_file=parsed_arguments.write_log_file,
    )


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Skips intros, recaps and credits in streaming tabs and can open "
            "streaming services on startup."
        )
    )
    parser.add_argument(
        "streaming_services",
        nargs="*",
        metavar="streaming_service",
        help=f"services to open on startup: {_describe_valid_names()}",
    )
    parser.add_argument(
        "--log",
        action="store_true",
        dest="write_log_file",
        help="additionally save a log file of this run",
    )
    return parser


def _resolve_streaming_service_names(
    requested_names: list[str],
) -> tuple[StreamingService, ...]:
    all_streaming_services = build_all_streaming_services()
    normalized_names = [name.lower() for name in requested_names]
    if ApplicationConstants.COMMAND_LINE_NAME_FOR_ALL_SERVICES in normalized_names:
        return all_streaming_services
    resolved_services: list[StreamingService] = []
    for name in normalized_names:
        streaming_service = _find_streaming_service_by_alias(
            name, all_streaming_services
        )
        if streaming_service not in resolved_services:
            resolved_services.append(streaming_service)
    return tuple(resolved_services)


def _find_streaming_service_by_alias(
    alias: str, all_streaming_services: tuple[StreamingService, ...]
) -> StreamingService:
    for streaming_service in all_streaming_services:
        if alias in streaming_service.command_line_aliases:
            return streaming_service
    raise ValueError(
        f"unknown streaming service '{alias}', valid names: {_describe_valid_names()}"
    )


def _describe_valid_names() -> str:
    aliases = [
        alias
        for streaming_service in build_all_streaming_services()
        for alias in streaming_service.command_line_aliases
    ]
    aliases.append(ApplicationConstants.COMMAND_LINE_NAME_FOR_ALL_SERVICES)
    return ", ".join(aliases)
