import requests

from json import JSONDecodeError
from requests.exceptions import ConnectionError
from ledmatrix_server.config import config
from ledmatrix_server.common import log


def get_entity(entity_id:str) -> dict:
    ha_url = config.hass_url
    ha_token = config.hass_key

    url = f"{ha_url}/api/states/{entity_id}"
    headers = {
        "Authorization": f"Bearer {ha_token}",
        "content-type": "application/json",
    }

    try:
        r = requests.get(url, headers=headers)
    except ConnectionError as e:
        log.error(f"Unable to reach Home Assistant: {url}")
        log.error(e)
        return dict()
    
    try:
        ret = r.json()
    except JSONDecodeError:
        log.debug(f"Unable to decode response for JSON for {url}.")
        log.debug(f"{r = }")
        raise
    except Exception:
        log.debug("Something unexpected went wrong.")
        log.debug(f"{r = }")
        raise
    
    if ret == {'message': 'Entity not found.'}:
        log.error(f"No entity: {entity_id}")
        return dict()
    
    log.debug(f"State for {entity_id} has length of {len(ret)}")
    return ret


def get_state(entity_id:str) -> str|int|float|bool|None:
    try:
        return get_entity(entity_id).get("state", None)
    except (KeyError, TypeError):
        return False
