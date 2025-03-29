#!/usr/bin/env python3

import time

from pipeline.verify_sp_execution import verify_spider_exec_result
from pipeline.verify_sp_execution import XPathExecutionVerificationResult

from typing import Any


def get_verification_criteria(plan_json: dict[str, Any]) -> str:
    verification_criteria: str = "\n".join(
        [
            action["verify"] for action in plan_json["action_list"]
        ]
    )
    return verification_criteria


def sort_spider_eval_results(
    spider_eval_results: dict[int, XPathExecutionVerificationResult]
        ) -> dict[int, XPathExecutionVerificationResult]:
    """
    Sorts the CAND_SPIDER_EXEC_EVAL_RESULT dictionary
    by key in descending order.

    :param spider_eval_results: Dictionary of spider execution evaluations.
    :return: Sorted dictionary with the highest key first.
    """
    sorted_eval_results: dict[int, XPathExecutionVerificationResult] = dict(
        sorted(
            spider_eval_results.items(),
            key=lambda item: item[1].score,
            reverse=True
        )
    )

    return sorted_eval_results


def run_verification_on_cand_spider_exec_results(
    CAND_SPIDER_EXEC_RESULTS: dict[int, Any],
    extracted_content_on_rec: str,
    verification_criteria: str
        ):
    CAND_SPIDER_EXEC_EVAL_RESULT: dict[
        int, XPathExecutionVerificationResult] = {}

    for key, cand_spider_executor in CAND_SPIDER_EXEC_RESULTS.items():
        time.sleep(5)
        print(f"Key: {key}")
        spider_code_runnable: str = cand_spider_executor.spider_code_runnable
        spider_output: str =\
            cand_spider_executor.spider_code_output_with_local_addresses

        if spider_output.strip() != "":
            xpath_verification_result = verify_spider_exec_result(
                spider_code_runnable=spider_code_runnable,
                verification_criteria=verification_criteria,
                extracted_content_on_rec=extracted_content_on_rec,
                spider_output=spider_output
            )

            CAND_SPIDER_EXEC_EVAL_RESULT[key] = xpath_verification_result

    CAND_SPIDER_EXEC_EVAL_RESULT: dict[
        int, XPathExecutionVerificationResult] = sort_spider_eval_results(
            spider_eval_results=CAND_SPIDER_EXEC_EVAL_RESULT
        )

    return CAND_SPIDER_EXEC_EVAL_RESULT
