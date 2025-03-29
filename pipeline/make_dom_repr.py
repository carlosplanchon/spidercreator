#!/usr/bin/env python3

from betterhtmlchunking import DomRepresentation
from betterhtmlchunking.main import ReprLengthComparisionBy
# from betterhtmlchunking.main import tag_list_to_filter_out


def make_dom_representation(
    website_html: str,
    MAX_NODE_REPR_LENGTH: int
        ) -> DomRepresentation:
    # Create document representation with 20 character chunks.
    dom_repr = DomRepresentation(
        MAX_NODE_REPR_LENGTH=MAX_NODE_REPR_LENGTH,
        website_code=website_html,
        repr_length_compared_by=ReprLengthComparisionBy.HTML_LENGTH,
        # tag_list_to_filter_out=["/head", "/header", "..."]
        # # By default tag_list_to_filter_out is used.
    )
    dom_repr.start()

    return dom_repr
