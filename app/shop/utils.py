# -*- coding: utf-8 -*-
from typing import Any
from urllib.parse import urlsplit

from django.http import HttpRequest


def convert_to_str(data: Any):
    """attempt to convert complex data to a string"""
    if data is not None:
        if isinstance(data, (str, int, float, bool)):
            return data
        if isinstance(data, list):
            return [convert_to_str(d) for d in data]
        if not isinstance(data, dict):
            __type__ = data.__class__.__name__
            data = vars(data)
            data.update({'__type__': __type__})
        return {convert_to_str(k): convert_to_str(v) for k, v in data.items()}
    return data


def get_current_url(request: HttpRequest):
    """build the current url from a Django request"""
    url = f"{request.scheme}://{request.get_host()}{request.path}"
    return [e for e in urlsplit(url)] + ['']
