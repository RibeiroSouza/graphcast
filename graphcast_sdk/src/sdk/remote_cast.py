import json
import logging
import time

import boto3
import runpod
from gcutils.constants import AWS_ACCESS_KEY_ID, AWS_BUCKET, AWS_SECRET_ACCESS_KEY, CAST_ID, CDS_KEY, CDS_URL, FORCAST_LIST
from gcutils.inpututils import generate_cast_id, get_completion_path, validate_forcast_list

logger = logging.getLogger(__name__)


class UploadMonitor():
    def __init__(self, pod, aws_access_key_id,
                 aws_secret_access_key, aws_bucket, cast_id) -> None:
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key)
        self.pod = pod
        self.cast_id = cast_id
        self.aws_bucket = aws_bucket

    def is_complete(self):
        """Check if the upload is complete.

        Returns:
            bool: True if the upload is complete, False otherwise.
        """
        pod = runpod.get_pod(self.pod["id"])

        if not pod:
            raise Exception(
                f"runpod pod {self.pod} was terminated prematurely, output of runpod.get_pod is: {pod}")

        try:
            self.s3_client.head_object(
                Bucket=self.aws_bucket,
                Key=get_completion_path(
                    self.cast_id))
            return True
        except Exception as e:
            if hasattr(e, "response") and e.response["Error"].get("Code") == "404":  # type: ignore
                logger.debug(f"upload not complete, expected_s3_error {e}")
                return False
            else:
                raise e

    def upload_location(self):
        """Return the upload location of the file."""
        return f"s3://{self.aws_bucket}/{self.cast_id}/"


def cast_from_parameters(param_file=None, **kwargs):
    """Cast from parameters.

    Args:
        param_file (str, optional): Path to the parameter file. Defaults to None.
        **kwargs: Additional keyword arguments.

    """
    if param_file is not None:
        assert param_file.endswith(".json"), "param_file must be a json file"

        with open(param_file) as f:
            parameters = json.load(f)
        kwargs = parameters

    remote_cast(**kwargs)


def validate_gpu_type_id(gpu_type_id):
    """Validate the GPU type ID.

    Args:
        gpu_type_id (str): The GPU type ID to validate.

    """
    if gpu_type_id == "NVIDIA A100 80GB PCIe":
        logger.warn(f"{gpu_type_id} is known to crash on runpod around 50% of the time when used in combination with the remote graphcast docker image. We suggest using NVIDIA A100-SXM4-80GB instead")


def validate(gpu_type_id, forcast_list, strict_start_times):
    """Validate the GPU type ID, forcast list, and strict start times.

    Args:
        gpu_type_id (str): The GPU type ID to validate.
        forcast_list (list): The list of forecasts to validate.
        strict_start_times (bool): Flag indicating whether strict start times should be enforced.

    """
    validate_gpu_type_id(gpu_type_id)
    validate_forcast_list(forcast_list, strict_start_times)


def remote_cast(
    aws_access_key_id,
    aws_secret_access_key,
    aws_bucket,
    cds_url,
    cds_key,
    forcast_list,
    runpod_key,
    cast_id=None,
    gpu_type_id="NVIDIA A100-SXM4-80GB",  # graphcast needs at least 61GB GPU ram
    container_disk_in_gb=50,
    strict_start_times=True
):
    """Perform a remote cast.

    Args:
        aws_access_key_id (str): The AWS access key ID.
        aws_secret_access_key (str): The AWS secret access key.
        aws_bucket (str): The AWS bucket.
        cds_url (str): The CDS URL.
        cds_key (str): The CDS key.
        forcast_list (list): The list of forecasts.
        runpod_key (str): The runpod key.
        cast_id (str, optional): The cast ID. Defaults to None.
        gpu_type_id (str, optional): The GPU type ID. Defaults to "NVIDIA A100-SXM4-80GB".
        container_disk_in_gb (int, optional): The container disk size in GB. Defaults to 50.
        strict_start_times (bool, optional): Flag indicating whether strict start times should be enforced. Defaults to True.

    Returns:
        str: The upload location of the file.
    """
    if cast_id is None:
        cast_id = generate_cast_id()
        logger.info(f"cast_id generated {cast_id}")

    logger.info("validating input")
    validate(gpu_type_id, forcast_list, strict_start_times)
    runpod.api_key = runpod_key

    pod = runpod.create_pod(
        cloud_type="SECURE",
        # or else someone might snoop your session and steal your AWS/CDS
        # credentials
        name=f"easy-graphcast-{cast_id}",
        image_name="lewingtonpitsos/easy-graphcast:latest",
        gpu_type_id=gpu_type_id,
        container_disk_in_gb=container_disk_in_gb,
        env={
            AWS_ACCESS_KEY_ID: aws_access_key_id,
            AWS_SECRET_ACCESS_KEY: aws_secret_access_key,
            AWS_BUCKET: aws_bucket,
            CDS_KEY: cds_key,
            CDS_URL: cds_url,
            FORCAST_LIST: forcast_list,
            CAST_ID: cast_id
        }
    )

    logger.info(
        f"forecasting pod created, id: {pod['id']}, machineId: {pod['machineId']}, machine: {pod['machine']}")
    monitor = UploadMonitor(
        pod,
        aws_access_key_id,
        aws_secret_access_key,
        aws_bucket,
        cast_id)

    while not monitor.is_complete():
        logger.info(
            "checking runpod and s3 for forcast status: all systems green")
        time.sleep(60)

    logger.info(
        f"easy-graphcast forcast is complete saved to, {monitor.upload_location()}")

    runpod.terminate_pod(pod["id"])

    logger.info("pod terminated")

    return monitor.upload_location()
