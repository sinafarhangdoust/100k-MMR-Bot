import argparse
import os

import boto3
from aiohttp import ClientError

from utils import instantiate_s3_client

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

def index_on_s3(
    s3_client: boto3.client,
    file_path: str,
    bucket_name: str,
    s3_key: str
):
    try:
        with open(file_path, "rb") as file:
            s3_client.put_object(
                Body=file,
                Bucket=bucket_name,
                Key=s3_key,
            )
    except ClientError as err:
        pass
        # TODO: handle error

def index_files(
    s3_client: boto3.client,
    dir_path: str,
    base_s3_dir: str
):
    for item in os.listdir(dir_path):
        if os.path.isfile(os.path.join(dir_path, item)):
            index_on_s3(
                s3_client=s3_client,
                file_path=os.path.join(dir_path, item),
                bucket_name=S3_BUCKET_NAME,
                s3_key=str(os.path.join(base_s3_dir, item)).lower()
            )
        else:
            index_files(
                s3_client=s3_client,
                dir_path=os.path.join(dir_path, item),
                base_s3_dir=str(os.path.join(base_s3_dir, item)).lower()
            )


def main(args):

    if not args.heroes_dir and not args.items_dir and not args.mechanics_dir:
        raise ValueError("Either --heroes-dir or --items-dir or --mechanics-dir must be specified")

    s3_client = instantiate_s3_client(endpoint="http://localhost:4567")

    if args.heroes_dir:
        index_files(
            s3_client=s3_client,
            dir_path=args.heroes_dir,
            base_s3_dir="heroes"
        )

    if args.items_dir:
        index_files(
            s3_client=s3_client,
            dir_path=args.items_dir,
            base_s3_dir="items"
        )

    if args.mechanics_dir:
        index_files(
            s3_client=s3_client,
            dir_path=args.mechanics_dir,
            base_s3_dir="mechanics"
        )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="S3 index script")
    parser.add_argument("--heroes-dir",
                        dest="heroes_dir",
                        type=str,
                        help="Path to heroes directory",
                        required=False)
    parser.add_argument("--items-dir",
                        dest="items_dir",
                        type=str,
                        help="Path to items directory",
                        required=False)
    parser.add_argument("--mechanics-dir",
                        dest="mechanics_dir",
                        type=str,
                        help="Path to mechanics directory",
                        required=False)
    args = parser.parse_args()
    main(args=args)