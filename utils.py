from typing import List

from langsmith import Client as LangsmithClient

def get_thread_history_from_langsmith(
    langsmith_client: LangsmithClient,
    thread_id: str,
    project_name: str
) -> List:
  filter_string = f'and(in(metadata_key, ["session_id","conversation_id","thread_id"]), eq(metadata_value, "{thread_id}"))'
  runs = [r for r in langsmith_client.list_runs(project_name=project_name, filter=filter_string, run_type="llm")]

  # Sort by start time to get the most recent interaction
  runs = sorted(runs, key=lambda run: run.start_time, reverse=True)
  # The current state of the conversation
  return runs[0].inputs['messages'] + [runs[0].outputs['choices'][0]['message']]