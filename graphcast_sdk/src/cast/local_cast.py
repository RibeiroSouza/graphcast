import json

from gcutils.constants import AWS_ACCESS_KEY_ID, AWS_BUCKET, AWS_SECRET_ACCESS_KEY, CDS_KEY, CDS_URL
from gcutils.inpututils import generate_cast_id

from .cast import cast_all

with open("credentials.json") as f:
    credentials = json.load(f)

cast_all(
    aws_access_key_id=credentials[AWS_ACCESS_KEY_ID],
    aws_secret_access_key=credentials[AWS_SECRET_ACCESS_KEY],
    aws_bucket=credentials[AWS_BUCKET],
    cds_url=credentials[CDS_URL],
    cds_key=credentials[CDS_KEY],
    forcast_list="[{'start': '2023122518', 'hours_to_forcast': 48}]",
    cast_id=f"test_{generate_cast_id()}"
)
