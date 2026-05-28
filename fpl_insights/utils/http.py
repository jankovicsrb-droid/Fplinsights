import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_TIMEOUT = 30
DEFAULT_RETRIES = 3


def create_session(retries: int = DEFAULT_RETRIES) -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=retries,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session
