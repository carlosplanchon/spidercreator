#!/usr/bin/env python3

from ctxexec.cand_sp_exec import CandSpiderExecutor


def execute_cand_spiders(
    CAND_SPIDER_CREATION_RESULTS,
    recordings_data,
    max_exec_instances: int = 20
        ):
    CAND_SPIDER_EXEC_RESULTS: dict[int, CandSpiderExecutor] = {}

    port_offset: int = 0

    actual_exec_instance: int = 0

    for key, chunk in CAND_SPIDER_CREATION_RESULTS.items():
        if chunk is not False:
            print(f"{'-' * 50}", key)
            print(f"ACTUAL EXEC INSTANCE: {actual_exec_instance}")
            if chunk is not None and chunk.spider_code is not None:
                print("--- EXPLANATION ---")
                print(chunk.explanation)
                print(chunk.spider_code)

                print("--- PORT OFFSET ---")
                print(port_offset)

                # Recordings data is used in
                # map_url_to_exec_context.
                # So the search for the website HTML is internal.
                # This can be better made external.
                # I mean, provide URL -> HTMLs
                # from outside of this function. Idk
                # remains to be evaluated.
                # ANOTHER WAY MAY BE TO GIVE THE
                # RELEVANT SEGMENT OF RECORDINGS ONLY.
                print("--- CAND SPIDER EXECUTION ---")
                cand_spider_executor = CandSpiderExecutor(
                    spider_code=chunk.spider_code,
                    recordings_data=recordings_data,
                    port_offset=port_offset
                )
                cand_spider_executor.start()

                port_offset = cand_spider_executor.port_offset

                print(cand_spider_executor.spider_code_output_with_local_addresses)

                CAND_SPIDER_EXEC_RESULTS[key] = cand_spider_executor

                actual_exec_instance += 1

                if actual_exec_instance >= max_exec_instances:
                    break

    return CAND_SPIDER_EXEC_RESULTS
