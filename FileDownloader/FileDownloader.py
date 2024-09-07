import os
import logging
import subprocess

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def download_file(
    url: str,
    output_dir: str,
    file_name: str
) -> None:
    """
    Downloads the file from the given url
    :param url: The url to download the file from
    :param output_dir: The output directory to save the downloaded file
    :param file_name: The name to save the downloaded file
    :return: None
    """
    output_path = os.path.join(output_dir, file_name)
    # if the file exists, skip downloading and exit
    if os.path.exists(output_path):
        logger.info("File %s already exists at the path %s", file_name, output_dir)
        return
    # create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    try:
        subprocess.run(["curl", "-L", url, "-o", output_path], check=True)
        logger.info(f"The file successfully downloaded to {output_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to download the file: {e}")
    except Exception as e:
        logger.error(f"An error occurred while downloading the file: {e}")



