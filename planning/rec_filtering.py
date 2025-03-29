#!/usr/bin/env python3


import attrs

from attrs_strict import type_validator

import copy

from typing import Any

from enum import StrEnum


class TokenType(StrEnum):
    KEEP_GOING: str = "keep_going"
    EOF: str = "end"


@attrs.define()
class RecordingInterpreter:
    recordings: list[dict[str, Any]] = attrs.field(
        validator=type_validator()
    )

    i: int = attrs.field(
        validator=type_validator(),
        default=0
    )

    actual_token: TokenType = attrs.field(
        validator=type_validator(),
        init=False
    )

    actual_frame: dict[str, Any] = attrs.field(
        validator=type_validator(),
        init=False
    )

    filtered_recording: dict[int, dict[str, Any]] = attrs.field(
        validator=type_validator(),
        init=False
    )

    def __attrs_post_init__(self):
        self.filtered_recording = {}

    def advance_frame(self):
        if self.i < len(self.recordings):
            print(f"I: {self.i}")
            self.actual_token = TokenType.KEEP_GOING

            self.actual_frame = self.recordings[self.i].copy()
            self.i += 1
        else:
            self.actual_token = TokenType.EOF

    def advance(self):
        self.advance_frame()
        while self.actual_frame["url"] == "about:blank":
            self.advance_frame()

    def get_filtered_recordings_list(self):
        return list(self.filtered_recording.values())

    def start(self):
        print("--- START ---")

        self.actual_token = TokenType.KEEP_GOING

        while self.actual_token != TokenType.EOF:
            print("*" * 50)
            self.advance()
            # prettyprinter.cpprint(self.actual_frame)

            # Make a deep copy so as not to mutate the original
            record = copy.deepcopy(self.actual_frame)

            filtered_frame = {
                "url": record["url"],
                "model_thoughts": record["model_thoughts"],
                # "model_outputs": record["model_outputs"],
                "model_actions": record["model_actions"],
                "extracted_content": record["extracted_content"]
            }

            self.filtered_recording[self.i - 1] = filtered_frame

        print("--- END ---")
