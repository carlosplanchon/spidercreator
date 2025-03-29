#!/usr/bin/env python3

# ! pip install -U validators

import attrs

from attrs_strict import type_validator

import validators
import tldextract

from enum import StrEnum

from pipeline.xpath_builder_planning import Planning


def validate_url(url: str) -> bool:
    """
    Validates a URL based only on its subdomain, domain, and suffix.

    Returns:
        bool: True if the domain structure is valid, False otherwise.
    """
    extracted = tldextract.extract(url)

    # Ensure there is a valid domain and suffix
    if extracted.domain and extracted.suffix:
        domain_url = f"https://{extracted.subdomain + '.' if extracted.subdomain else ''}{extracted.domain}.{extracted.suffix}"
        return validators.url(domain_url) is True

    return False


class PlanningState(StrEnum):
    INVALID_URL: str = "INVALID_URL"
    VALID_URL: str = "VALID_URL"
    EOF: str = "EOF"


@attrs.define()
class PlanningTokenizer:
    structured_planning: Planning = attrs.field(
        validator=type_validator()
    )

    # Planning:
    planning_idx: int = attrs.field(
        validator=type_validator(),
        default=0
    )

    actual_planning_frame = attrs.field(
        validator=type_validator(),
        init=False
    )

    actual_planning_token: PlanningState = attrs.field(
        validator=type_validator(),
        init=False
    )

    def update_planning_frame_token(self):
        print("--- UPDATE PLANNING FRAME TOKEN ---")
        print(self.actual_planning_frame.url)
        if validate_url(url=self.actual_planning_frame.url) is True:
            return PlanningState.VALID_URL
        return PlanningState.INVALID_URL

    def advance_planning_frame(self):
        if self.planning_idx < len(
                self.structured_planning.in_url_list):
            print(f"PLANNING I: {self.planning_idx}")

            self.actual_planning_frame =\
                self.structured_planning.in_url_list[
                    self.planning_idx
                ]

            self.actual_planning_token: PlanningState =\
                self.update_planning_frame_token()

            self.planning_idx += 1

        else:
            print("EOF")
            self.actual_planning_token =\
                PlanningState.EOF

    def advance_planning_until_valid_url(self):
        print("Advancing planning frames until valid URL...")
        self.advance_planning_frame()
        while self.actual_planning_token != PlanningState.VALID_URL:
            print("--> Invalid URL.")
            self.advance_planning_frame()

            if self.actual_planning_token == PlanningState.EOF:
                print("--> EOF.")
                raise EOFError

        print("--> Valid URL.")
