import logging
import requests

from dataclasses import dataclass, field
from typing import Dict

log = logging.getLogger('root')


@dataclass
class XBRConfig:
    Hostname: str = field(default_factory=lambda: "")
    Username: str = field(default_factory=lambda: "")
    Password: str = field(default_factory=lambda: "")
    Cookies: Dict[str, str] = field(default_factory=lambda: {})

    def logged_in(self, page: requests.Response) -> bool:
        check = f'<span id="hiloc">Hi </span>{self.Username}'
        return check in str(page.content)


def authorized(config: XBRConfig, page: requests.Response) -> bool:
    """Are we authorized???"""
    if config.logged_in(page):
        log.debug("we are authorized")
        return True
    log.debug("we are not authorized")
    return False


def get_page(config: XBRConfig, path: str) -> requests.Response:
    log.debug("get_page: %s", path)
    page = requests.get(f'http://{config.Hostname}/{path}',
                        cookies=config.Cookies)
    page.raise_for_status()
    return page


def login(config: XBRConfig) -> Dict[str, str]:
    """Login to the router and store the cookies for later

    raises:
        RequestException - on any http/networking issue
        ValueError - on invalid username/password
    """
    log.debug("attempting login")
    page = requests.post(f'http://{config.Hostname}/check.jst',
        data={
            'username': config.Username,
            'password': config.Password,
        })
    page.raise_for_status()
    if not authorized(config, page):
        raise ValueError('Invalid username/password')
    return page.cookies


def fetch_network_stats_page(config: XBRConfig) -> bytes:
    """Fetches the network_setup.jst page from the modem.

    config: the router config
    returns: string containing the page
    exceptions:
        Any requests.exceptions.RequestException
        ValueError: incorrect user/password
    """
    log.debug("fetch_network_stats_page")
    page = get_page(config, 'network_setup.jst')
    if not authorized(config, page):
        config.Cookies = login(config)
        page = get_page(config, 'network_setup.jst')
    return page.content
