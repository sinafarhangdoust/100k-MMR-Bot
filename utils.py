from typing import List

from langsmith import Client as LangsmithClient
import boto3
from botocore.config import Config

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

def instantiate_s3_client():
    cfg = Config(
      region_name='eu-west-1',
      connect_timeout=60,
      read_timeout=60,
      retries={"max_attempts": 10, "mode": "standard"},
      signature_version="s3v4",
    )
    return boto3.client(
      "s3",
      endpoint_url="http://localhost:4566",
      aws_access_key_id="test",
      aws_secret_access_key="test",
      aws_session_token="test",
      config=cfg,
    )