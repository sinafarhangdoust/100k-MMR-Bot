import os
from typing import List
import json

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

class S3Wrapper:

    def __init__(
        self,
        endpoint: str = "http://localhost:9000"
    ):
        self.s3_client = self.instantiate_s3_client(endpoint=endpoint)

    @staticmethod
    def instantiate_s3_client(
        endpoint: str
    ):
        cfg = Config(
            region_name='eu-west-1',
            s3={"addressing_style": "path"},
            connect_timeout=60,
            read_timeout=60,
            retries={"max_attempts": 5, "mode": "standard"},
            signature_version="s3v4",
        )
        return boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "admin"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "adminadmin"),
            config=cfg,
        )

    def read_object(
        self,
        bucket_name: str,
        key: str
    ):
        loaded_object = self.s3_client.get_object(Bucket=bucket_name, Key=key)["Body"].read()
        if key.endswith(".json"):
            return json.loads(loaded_object.decode("utf-8"))
        else:
            return loaded_object.decode("utf-8")