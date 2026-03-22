from importlib.resources import files

from ledmatrix_server.common import log

_INDICES: dict[str, dict[str, str]] = dict()

def _walk(base):
    for item in base.iterdir():
        if item.is_file():
            yield item
        elif item.is_dir():
            yield from _walk(item)


def _build_index(base_dir: str) -> dict:
    base = files(base_dir)
    index = {}

    for path in _walk(base):
        index[path.name] = path

    return index


def _get_generic(index_name:str, base_dir:str, name:str):
    global _INDICES

    if _INDICES.get(index_name) is None:
        _INDICES[index_name] = _build_index(base_dir)
    
    index:dict = _INDICES[index_name]
    
    try:
        return index[name]
    except KeyError:
        log.error(f"No resource '{name}' in index '{index_name}' (base dir: {base_dir})")
        raise
    


def get_image(name: str):
    return _get_generic("images", "ledmatrix_server.resources.images", name)


def get_font(name: str):
    return _get_generic("fonts", "ledmatrix_server.resources.fonts", name)
