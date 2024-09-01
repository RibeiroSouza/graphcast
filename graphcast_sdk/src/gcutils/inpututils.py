import json
import logging
import os
import random
from datetime import datetime, timedelta

from gcutils.cdsutils import get_latest_available_date

logger = logging.getLogger(__name__)


def generate_cast_id():
    """Generate a unique cast ID based on the current time and random adjectives and nouns.

    Returns:
        str: The generated cast ID.
    """
    adj = [
        "whispering", "forgotten", "sublime", "phantom", "mystic",
        "cosmic", "dazzling", "spectral", "fleeting", "shimmering",
        "invisible", "echoing", "intangible", "melodic", "transient",
        "prismatic", "noctilucent", "aurora", "enigmatic", "ephemeral",
        "stellar", "mythic", "azure", "crystalline", "mystifying",
        "radiant", "lucent", "polar", "celestial", "timeless",
        "cobalt", "harmonic", "infinite", "nautical", "primal",
        "solar", "wandering", "auroral", "floral", "lucent",
        "maritime", "opaline", "stellar", "twinkling", "zodiacal",
        "botanic", "coral", "dreamlike", "glacial", "harmonic",
        "ethereal", "arcane", "sylvan", "emerald", "golden",
        "silver", "moonlit", "sunlit", "twilight", "midnight",
        "dawn", "dusk", "summer", "winter", "autumn",
        "spring", "ancient", "modern", "timeless", "endless",
        "boundless", "ageless", "eternal", "everlasting", "perpetual",
        "unending", "infinite", "limitless", "unbounded", "unfathomable"
    ]
    nouns = [
        "cosmos", "phantasm", "stardust", "galaxy", "oasis",
        "tempest", "artifact", "cascade", "maelstrom", "saga",
        "reverie", "illusion", "odyssey", "riddle", "miracle",
        "cosmic", "haven", "mirage", "oracle", "tapestry",
        "atlantis", "harmony", "nebulae", "pinnacle", "relic",
        "zenith", "borealis", "inferno", "oceanus", "pulsar",
        "saga", "allegory", "clarity", "expanse", "fable",
        "lagoon", "narrative", "pastoral", "rhapsody", "sonnet",
        "tundra", "cascade", "echo", "infinity", "monolith",
        "oasis", "panorama", "sphere", "torrent", "wilderness",
        "abyss", "beacon", "chronicle", "dimension", "eclipse",
        "fjord", "glacier", "horizon", "island", "jungle",
        "kaleidoscope", "labyrinth", "meadow", "nirvana", "ocean",
        "paradise", "quasar", "rainforest", "sanctuary", "tide",
        "universe", "vortex", "waterfall", "xanadu", "yonder",
        "zenith", "arcadia", "bazaar", "citadel", "dome",
        "enclave", "fortress", "grove", "hamlet", "isle"
    ]

    present = datetime.now()
    time_string = present.strftime("%Y-%m-%d_%H-%M-%S")

    return f"{time_string}_{random.choice(adj)}_{random.choice(nouns)}"


def confirm_start_time_exists(start_point, c):
    """Check if the start time exists and retrieve the corresponding data file.

    Args:
        start_point (dict): The start point information.
        c: The CDS API client.

    Returns:
        None
    """
    start_datetime = datetime.strptime(start_point["start_date"], "%Y%m%d")

    c.retrieve(
        "reanalysis-era5-single-levels",
        {
            "product_type": "reanalysis",
            "format": "netcdf",
            "day": start_datetime.day,
            "year": start_datetime.year,
            "month": start_datetime.month,
            "time": start_point["start_time"],
            "variable": "2m_temperature",
            "area": [1, -1, -1, 1,],
        },
        "file.nc"
    )

    os.remove("file.nc")


def parse_forcast_list(forcast_list):
    """Parse the forecast list and convert it to regular JSON.

    Args:
        forcast_list (str): The forecast list.

    Returns:
        list: The parsed forecast list.
    """
    # the runpod API cannot handle double quotes so forcast_list is single quoted
    # we need to convert it to regular JSON
    forcast_list = json.loads(forcast_list.replace("'", '"'))

    for start in forcast_list:
        start["start_time"] = int(start["start"][-2:])
        start["start_date"] = start["start"][:-2]

    return forcast_list


def get_completion_path(cast_id):
    """Get the completion path for a given cast ID.

    Args:
        cast_id (str): The cast ID.

    Returns:
        str: The completion path.
    """
    return f"{cast_id}/.easy_graphcast_complete"


def validate_forcast_list(forcast_list, strict_start_times=True):
    """Validate the forecast list and perform checks on the start times.

    Args:
        forcast_list (str): The forecast list.
        strict_start_times (bool, optional): Whether to enforce strict start times. Defaults to True.

    Raises:
        ValueError: If the forecast list contains double quotes.
        ValueError: If the start times are not 0600 or 1800.

    Returns:
        None
    """
    # the runpod API cannot handle double quotes so forcast_list is single
    # quoted
    latest_available_date = None
    latest_available_date = None
    if '"' in forcast_list:
        raise ValueError(
            "forcast_list cannot contain double quotes (this is a limitation of the runpod API) replace with single quotes.")

    forcast_list = parse_forcast_list(forcast_list)

    if strict_start_times:
        for start in forcast_list:
            if start["start_time"] not in [6, 18]:
                raise ValueError(
                    """you must start all graphcast forecasts at either 0600 or 1800
                    (see https://youtu.be/PD1v5PCJs_o?t=1915 for more information).
                    You can disable this check by setting strict_start_times=False""")
    try:
        latest_available_date = get_latest_available_date()
        got_date = True
    except Exception as e:
        logger.info(
            f"could not get the latest available date due to error: {e}")
        got_date = False

    if got_date:
        for start in forcast_list:
            start_date = datetime.strptime(start["start"], "%Y%m%d%H")
            if latest_available_date is not None and latest_available_date < start_date:
                raise ValueError(
                    f"""there is no public ERA5 data for the start date {start['start']}
                    so you cannot start a forcast from that date. The latest available date is {latest_available_date}""")
    else:
        latest_available_date = datetime.now() - timedelta(days=5)
        for start in forcast_list:
            start_date = datetime.strptime(start["start"], "%Y%m%d%H")
            if latest_available_date < start_date:
                logger.warning(
                    f"the forcast start date {start_date} is more recent than 5 days ago, the data may not exist yet. Monitor the runpod instance closely")

    logger.info("input passed validation")
