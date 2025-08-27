import os

try:
    S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]
except KeyError:
    # Default bucket name
    S3_BUCKET_NAME = "rag-storage"