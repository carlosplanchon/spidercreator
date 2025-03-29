#!/usr/bin/env python3

from planning.rec_filtering import RecordingInterpreter

from planning.plan_tokenizer import PlanningTokenizer


def make_planner_idx_to_recording_idx(
    recordings_itpr: RecordingInterpreter,
    planning_tokenizer: PlanningTokenizer
        ) -> dict[int, int]:

    filtered_rec_keys: list[int] = list(
        recordings_itpr.filtered_recording.keys()
    )

    last_recording_idx: int = 0

    last_matched_url: str | None = None

    PLANNER_IDX_TO_RECORDING_IDX: dict[int, int] = {}

    eof = False
    while eof is False:
        print("*" * 50)
        try:
            planning_tokenizer.advance_planning_until_valid_url()

            print("--> Searching for same URL on planning.")
            print(f"Last recording IDX: {last_recording_idx}")

            recording_idx = last_recording_idx

            matched: bool = False

            while recording_idx < len(
                    recordings_itpr.filtered_recording) and matched is False:
                print("-" * 50)
                print(f"RECORDING I: {recording_idx}")

                planning_url: str =\
                    planning_tokenizer.actual_planning_frame.url

                recording_url = recordings_itpr.filtered_recording[
                    filtered_rec_keys[recording_idx]
                ]["url"]

                print("--> RECORDING URL:")
                print(recording_url)

                print("--> PLANNING URL:")
                print(planning_url)

                if recording_url is not None and planning_url is not None:
                    planning_url = planning_url.rstrip("/")
                    recording_url = recording_url.rstrip("/")

                    if planning_url == recording_url and\
                            planning_url != last_matched_url:
                        print("--> URLs match.")
                        last_matched_url = recording_url

                        last_recording_idx = recording_idx

                        PLANNER_IDX_TO_RECORDING_IDX[
                            planning_tokenizer.planning_idx - 1
                        ] = filtered_rec_keys[recording_idx]

                        matched = True

                recording_idx += 1
        except EOFError:
            eof = True

    return PLANNER_IDX_TO_RECORDING_IDX
