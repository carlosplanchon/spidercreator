#!/usr/bin/env python3

import argparse
import os
from pathlib import Path
import prettyprinter
import pyhtml2md

prettyprinter.install_extras()

# -------------------------------------------------------------------
# Importing your existing modules/functions
# (Adjust these imports to match your actual project structure)
# -------------------------------------------------------------------
from utils.recordings import load_recordings
from utils.utils import b64_to_png

from planning.rec_filtering import RecordingInterpreter
from pipeline.mindmap import make_mermaid_mindmap
from pipeline.spider_draft import make_scrapy_spider_draft
from pipeline.xpath_builder_planning import make_non_structured_planning
from pipeline.xpath_builder_planning import make_structured_planning
from pipeline.xpath_builder_planning import Planning
from planning.plan_tokenizer import PlanningTokenizer
from planning.planner_to_rec import make_planner_idx_to_recording_idx
from pipeline.make_dom_repr import make_dom_representation
from betterhtmlchunking import DomRepresentation
from pipeline.roiclf_spcandmkr import classify_roi_html_create_cand_spider
from ctxexec.pipeline import execute_cand_spiders
from pipeline.verify_sp_execution import verify_spider_exec_result
from pipeline.verify_sp_execution import XPathExecutionVerificationResult
from pipeline.verification_pipeline import get_verification_criteria
from pipeline.verification_pipeline import run_verification_on_cand_spider_exec_results
from pipeline.sp_combination import get_spider_combination


def main():
    """
    Main entry point. Parses --task_id from the command line,
    then uses that to decide where to read recordings from
    and where to save results.
    """
    # Store the original working directory.
    # We'll return to it before writing results.
    original_cwd = os.getcwd()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--task_id",
        required=True,
        help="Task ID for reading from 'recordings/{task_id}' and saving results to 'results/{task_id}'"
    )
    args = parser.parse_args()

    # -------------------------------------------------
    # 1) Prepare Folders
    # -------------------------------------------------
    task_id = args.task_id

    # Read from: recordings/{task_id}/
    recordings_folder = Path("recordings") / task_id
    # Write results to: results/{task_id}/
    results_folder = Path("results") / task_id
    results_folder.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------
    # 2) Load the Recordings
    # -------------------------------------------------
    recordings_data = load_recordings(directory=str(recordings_folder))

    # -------------------------------------------------
    # 3) Existing Logic (Slightly Adapted)
    # -------------------------------------------------

    recordings_itpr = RecordingInterpreter(recordings=recordings_data)
    recordings_itpr.start()

    prettyprinter.cpprint(recordings_itpr.filtered_recording)

    # '''
    # --- Mindmap ---
    mermaid_code: str = make_mermaid_mindmap(
        recordings=recordings_itpr.get_filtered_recordings_list()
    )
    print("\n--- MERMAID WORK MINDMAP ---")
    print(mermaid_code)

    # --- Spider Draft ---
    scrapy_spider_draft: str = make_scrapy_spider_draft(
        recordings=recordings_itpr.get_filtered_recordings_list(),
        mermaid_code=mermaid_code
    )
    print("\n--- SCRAPY SPIDER DRAFT ---")
    print(scrapy_spider_draft)

    # --- XPATH Builder Planning (Non-structured) ---
    xpath_builder_non_structured_planning = make_non_structured_planning(
        mermaid_code=mermaid_code,
        scrapy_spider=scrapy_spider_draft
    )
    print("\n--- XPATH BUILDER NON-STRUCTURED PLANNING ---")
    print(xpath_builder_non_structured_planning)

    # --- XPATH Builder Planning (Structured) ---
    xpath_builder_structured_planning: Planning = make_structured_planning(
        mermaid_code=mermaid_code,
        scrapy_spider_draft=scrapy_spider_draft
    )
    print("\n--- XPATH BUILDER STRUCTURED PLANNING ---")
    print("--> In URLs:")
    for recording in xpath_builder_structured_planning.in_url_list:
        print("-" * 50)
        prettyprinter.cpprint(recording.model_dump())
    print("--> Summary:")
    prettyprinter.cpprint(xpath_builder_structured_planning.summary)

    planning_tokenizer = PlanningTokenizer(
        structured_planning=xpath_builder_structured_planning
    )

    PLANNER_IDX_TO_RECORDING_IDX = make_planner_idx_to_recording_idx(
        recordings_itpr=recordings_itpr,
        planning_tokenizer=planning_tokenizer
    )

    print("\n--- PLANNER IDX TO RECORDING IDX ---")
    prettyprinter.cpprint(PLANNER_IDX_TO_RECORDING_IDX)

    # -------------------------------------------------
    # 4) Execute the Plan
    # -------------------------------------------------
    PLANNER_IDX_TO_RESULT: dict = {}

    for planner_idx, recording_idx in PLANNER_IDX_TO_RECORDING_IDX.items():
        print("\n", "-" * 50)
        print(f"PLANNER IDX: {planner_idx}")
        print(f"RECORDING IDX: {recording_idx}")

        plan = xpath_builder_structured_planning.in_url_list[planner_idx]
        SELECTED_RECORDING = recordings_itpr.recordings[recording_idx]

        website_html: str = SELECTED_RECORDING["website_html"]
        markdown = pyhtml2md.convert(website_html)  # Example usage
        website_url: str = SELECTED_RECORDING["url"]
        extracted_content_on_rec: str = SELECTED_RECORDING["extracted_content"]
        website_screenshot = SELECTED_RECORDING["website_screenshot"]

        print("\n--- WEBSITE URL ON RECORDING ---")
        print(website_url)
        print("--- PLAN ---")
        prettyprinter.cpprint(plan.model_dump())

        # Example usage: b64_to_png(website_screenshot, f"output_{recording_idx}.png")

        # Make DOM representation
        dom_repr: DomRepresentation = make_dom_representation(
            website_html=website_html,
            MAX_NODE_REPR_LENGTH=32768  # 16384*2
        )
        roi_amt: int = len(dom_repr.tree_regions_system.sorted_roi_by_pos_xpath)
        print(f"Regions of interest amount: {roi_amt}")

        # Print minimal ROI info
        for idx_roi in dom_repr.tree_regions_system.sorted_roi_by_pos_xpath:
            print("-" * 50)
            print(f"ROI IDX: {idx_roi}")
            print(
                dom_repr.render_system.get_roi_text_render_with_pos_xpath(
                    roi_idx=idx_roi
                )
            )

        plan_json = plan.model_dump()
        prettyprinter.cpprint(plan_json)

        # Classification + Candidate Spider Generation
        CAND_SPIDER_CREATION_RESULTS = classify_roi_html_create_cand_spider(
            dom_repr=dom_repr,
            extracted_content_on_rec=extracted_content_on_rec,
            planning=plan_json,
            max_exec_amt=75
        )

        # Print quick summary
        for key, chunk in CAND_SPIDER_CREATION_RESULTS.items():
            if chunk not in [False, None]:
                print(f"\n{'-' * 50} {key}")
                print(f"Have desired content?: {chunk.result}\n")
                if chunk.spider_code is not None:
                    print(chunk.spider_code)
                print("--- EXPLANATION ---")
                print(chunk.explanation)

        # Execute Candidate Spiders
        CAND_SPIDER_EXEC_RESULTS = execute_cand_spiders(
            CAND_SPIDER_CREATION_RESULTS=CAND_SPIDER_CREATION_RESULTS,
            recordings_data=recordings_data
        )

        # Print the results
        for key, cand_spider_exec_obj in CAND_SPIDER_EXEC_RESULTS.items():
            print("\n" + "*" * 80)
            print(f"Key: {key}")
            print(cand_spider_exec_obj.spider_code)
            print("Result:")
            print(cand_spider_exec_obj.spider_code_output_with_local_addresses[:5000])

        # Verification
        verification_criteria: str = get_verification_criteria(
            plan_json=plan_json)
        print("\n--- VERIFICATION CRITERIA ---")
        print(verification_criteria)

        CAND_SPIDER_EXEC_EVAL_RESULT = run_verification_on_cand_spider_exec_results(
            CAND_SPIDER_EXEC_RESULTS=CAND_SPIDER_EXEC_RESULTS,
            extracted_content_on_rec=extracted_content_on_rec,
            verification_criteria=verification_criteria
        )

        for key, xpath_verification_result in CAND_SPIDER_EXEC_EVAL_RESULT.items():
            print("\n" + "*" * 80)
            print(f"Key: {key}")
            sp_exec_ver_res = xpath_verification_result.model_dump()
            prettyprinter.cpprint(sp_exec_ver_res)

        if CAND_SPIDER_EXEC_EVAL_RESULT:
            selected_key: int = list(CAND_SPIDER_EXEC_EVAL_RESULT.keys())[0]
            spider_code_runnable: str = CAND_SPIDER_EXEC_RESULTS[selected_key].spider_code_runnable
            spider_output: str = CAND_SPIDER_EXEC_RESULTS[selected_key].spider_code_output_with_local_addresses
        else:
            spider_code_runnable, spider_output = "", ""

        print("\n--- SPIDER CODE RUNNABLE ---")
        print(spider_code_runnable)
        print("--- SPIDER OUTPUT ---")
        print(spider_output)

        PLANNER_IDX_TO_RESULT[planner_idx] = {
            "spider_code_runnable": spider_code_runnable,
            "spider_output": spider_output
        }

    print("\n--- PLANNER IDX TO RESULT ---")
    prettyprinter.cpprint(PLANNER_IDX_TO_RESULT)

    # Combine final spider code
    spider_code: str = get_spider_combination(
        PLANNER_IDX_TO_RESULT=PLANNER_IDX_TO_RESULT,
        xpath_builder_structured_planning=xpath_builder_structured_planning
    )

    print("\n--- SPIDER COMBINATION ---")
    print(spider_code)
    # '''

    # spider_code = SPIDER_COMBINATION
    os.chdir(original_cwd)

    # -------------------------------------------------
    # 5) Write the Final Spider Code to results/<task_id>/
    # -------------------------------------------------
    # Write spider code to results/{task_id}/spider_code.py
    spider_code_path = results_folder / "spider_code.py"
    # Ensure the folder exists
    results_folder.mkdir(parents=True, exist_ok=True)
    with open(spider_code_path, "w", encoding="utf-8") as f:
        f.write(spider_code)

    print(f"\n[INFO] Final spider code has been saved to: {spider_code_path}")
    print("[INFO] Done.")


if __name__ == "__main__":
    main()
