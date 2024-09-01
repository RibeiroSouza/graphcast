import logging
import os
from datetime import datetime

import requests
import yaml
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


RCFILE_PATH = "~/.cdsapirc"


def save_cds_rcfile(cds_key, cds_url):
    """Save the CDS RC file with the given key and URL.

    Args:
        cds_key (str): The CDS key.
        cds_url (str): The CDS URL.
    """
    save_cds_file(cds_key, cds_url, RCFILE_PATH)


def save_cds_file(cds_key, cds_url, filename):
    """Save the CDS file with the given key, URL, and filename.

    Args:
        cds_key (str): The CDS key.
        cds_url (str): The CDS URL.
        filename (str): The filename to save the CDS file.

    """
    expanded_filename = os.path.expanduser(filename)
    with open(expanded_filename, "w") as f:
        data = {
            "key": cds_key,
            "url": cds_url
        }
        yaml.dump(data, f)


def get_latest_available_date(api_url="https://cds.climate.copernicus.eu/api/v2.ui/resources/reanalysis-era5-single-levels", retries=3, timeout=5):
    """Get the latest available date from the CDS API.

    Args:
        api_url (str): The URL of the CDS API.
        retries (int): The number of retries in case of request failure.
        timeout (int): The timeout for each request.

    Returns:
        datetime: The latest available date.

    Raises:
        Exception: If the maximum number of retries is reached.
    """
    for attempt in range(retries):
        try:
            result = requests.get(api_url, timeout=timeout)
            result.raise_for_status()

            data = result.json()

            date_range = data.get("structured_data", {}).get("temporalCoverage", "")
            if not date_range:
                raise ValueError("Temporal coverage not found in data")

            final_date = date_range.split("/")[1]

            return datetime.strptime(final_date, "%Y-%m-%d")

        except RequestException as e:
            logger.error(f"CDS most recent date request failed: {e}")
            if attempt == retries - 1:
                raise
        except ValueError as e:
            logger.error(f"cds most recent date data parsing error: {e}")
            raise

    raise Exception("Maximum retries reached")
