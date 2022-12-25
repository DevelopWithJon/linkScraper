"""requests utils."""

from dataclasses import dataclass
import logging
from collections import deque
import time
import asyncio
from typing import Any
from abc import ABCMeta, abstractmethod

import requests
import aiohttp
import sentry_sdk


log = logging.getLogger(__name__)


class APIRateLimiter:
    """
    API rate limiter
    """

    def __init__(self, rate_limit, rate_second_delta):
        self._rate_limit = rate_limit
        self._rate_second_delta = rate_second_delta
        self._request_times = deque()

    def limit(self) -> None:
        """
        Returns when the next rate limited API call can be made
        """
        if self._rate_limit and self._rate_second_delta:
            while True:
                now = time.time()
                while self._request_times:
                    if now - self._request_times[0] > self._rate_second_delta:
                        self._request_times.popleft()
                    else:
                        break

                if len(self._request_times) < self._rate_limit:
                    break

                time.sleep(0.00001)

            self._request_times.append(time.time())

    async def async_limit(self) -> None:
        """
        Returns when the next rate limited API call can be made
        """
        if self._rate_limit and self._rate_second_delta:
            while True:
                now = time.time()
                while self._request_times:
                    if now - self._request_times[0] > self._rate_second_delta:
                        self._request_times.popleft()
                    else:
                        break

                if len(self._request_times) < self._rate_limit:
                    break

                asyncio.sleep(0.00001)

            self._request_times.append(time.time())

    def __enter__(self) -> None:
        """
        Context manager entry

        api_rate_limiter = APIRateLimiter(1, 1)
        for _ in range(1000):
            with api_rate_limiter:
                request.get('https://api.io)
        """
        return self.limit()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Context manager exit
        """

    async def __aenter__(self) -> None:
        """
        Async context manager enter
        """
        await self.async_limit()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Async context manager exit
        """


class APIClient(metaclass=ABCMeta):
    """
    API client
    """

    RATE_LIMIT = None
    RATE_SECOND_DELTA = None
    BASE_URL = None
    SERVICE = None

    # @abstractmethod
    # def RATE_LIMIT(self):
    #     """
    #     Required rate period
    #     """

    # @abstractmethod
    # def RATE_LIMIT(self):
    #     """
    #     Required rate limit
    #     """

    @classmethod
    def service_url(cls, service):
        """
        Service URL generator
        """
        return f"{cls.BASE_URL}{service}"

    def __init__(self, service=None):
        """
        Set up the sync rate limiter and async rate limited HTTP session
        """
        # Rate limiter for sync calls
        self.rate_limiter = APIRateLimiter(
            rate_limit=self.RATE_LIMIT,
            rate_second_delta=self.RATE_SECOND_DELTA,
        )

    @property
    def async_http_session(self):
        """
        Set up a rate limited async HTTP session
        Lazy set up because APIClient used for sync only calls will crash with AsyncHTTPSession set up without closing
        """
        return AsyncHTTPSession(
            rate_limit=self.RATE_LIMIT,
            rate_second_delta=self.RATE_SECOND_DELTA,
        )

    def post(self, url, body=None, headers=None, params=None, data=None):
        """
        HTTP POST request
        """
        return post(url, body, headers, params, data, self.rate_limiter)

    def get(self, url, body=None, headers=None, params=None, data=None):
        """
        HTTP GET request
        """
        return get(url, body, headers, params, data, self.rate_limiter)

    def put(self, url, body=None, headers=None, params=None, data=None):
        """
        HTTP PUT request
        """
        return put(url, body, headers, params, data, self.rate_limiter)

    def patch(self, url, body=None, headers=None, params=None, data=None):
        """
        HTTP PATCH request
        """
        return patch(url, body, headers, params, data, self.rate_limiter)

    def delete(self, url, body=None, headers=None, params=None, data=None):
        """
        HTTP DELETE request
        """
        return delete(url, body, headers, params, data, self.rate_limiter)

    async def async_post(
        self,
        url,
        body=None,
        headers=None,
        params=None,
        data=None,
        async_http_session=None,
    ):
        """
        Async HTTP POST request
        """
        # Allow optional async_http_session because async calls are faster with one http session passed around
        async_http_session = (
            async_http_session if async_http_session else self.async_http_session
        )

        return await async_post(async_http_session, url, body, headers, params, data)

    async def async_get(
        self,
        url,
        body=None,
        headers=None,
        params=None,
        data=None,
        async_http_session=None,
    ):
        """
        Async HTTP GET request
        """
        async_http_session = (
            async_http_session if async_http_session else self.async_http_session
        )

        return await async_get(async_http_session, url, body, headers, params, data)

    async def async_put(
        self,
        url,
        body=None,
        headers=None,
        params=None,
        data=None,
        async_http_session=None,
    ):
        """
        Async HTTP PUT request
        """
        async_http_session = (
            async_http_session if async_http_session else self.async_http_session
        )

        return await async_put(async_http_session, url, body, headers, params, data)

    async def async_patch(
        self,
        url,
        body=None,
        headers=None,
        params=None,
        data=None,
        async_http_session=None,
    ):
        """
        Async HTTP PATCH request
        """
        async_http_session = (
            async_http_session if async_http_session else self.async_http_session
        )

        return await async_patch(async_http_session, url, body, headers, params, data)

    async def async_delete(
        self,
        url,
        body=None,
        headers=None,
        params=None,
        data=None,
        async_http_session=None,
    ):
        """
        Async HTTP DELETE request
        """
        async_http_session = (
            async_http_session if async_http_session else self.async_http_session
        )

        return await async_delete(async_http_session, url, body, headers, params, data)


@dataclass
class HTTPResponse:
    """
    HTTP response
    """

    response: Any = None
    headers: dict = None
    text: str = None
    status_code: int = None
    ok: Any = None
    json: dict = None
    request_url: str = None
    request_method: str = None
    request_body: dict = None
    request_headers: dict = None
    content: bytes = None
    duration: int = None


class APIException:
    """
    APIException
    """


class AsyncHTTPSession(aiohttp.ClientSession):
    """
    AIOHTTP client
    """

    def __init__(
        self,
        default_headers=None,
        timeout=30,
        rate_limiter=None,
        rate_limit=None,
        rate_second_delta=None,
        service=None,
    ):
        if rate_limit and rate_second_delta:
            rate_limiter = APIRateLimiter(
                rate_limit=rate_limit,
                rate_second_delta=rate_second_delta,
                service=service,
            )

        self.rate_limiter = rate_limiter
        if not default_headers:
            default_headers = dict()

        # Infinite concurrent connections
        connector = aiohttp.TCPConnector(limit=None)
        timeout = aiohttp.ClientTimeout(timeout)
        super().__init__(connector=connector, timeout=timeout, headers=default_headers)

    async def _request(self, method, url, **kwargs):
        """
        Base class override to rate limit
        """
        if self.rate_limiter:
            async with self.rate_limiter:
                return await super()._request(method, url, **kwargs)
        else:
            return await super()._request(method, url, **kwargs)


async def async_request(
    http_session, url, method, body=None, headers=None, params=None, data=None
):
    """
    Makes an async HTTP request
    """
    log.debug(
        f"HTTP call to {url} with method {method} and body {body if body else data} and params {params}"
    )
    start_time = time.time()
    response = HTTPResponse(
        request_url=url,
        request_method=method,
        request_body=body,
        request_headers=headers,
        ok=False,
    )
    try:
        async with http_session as open_http_session, getattr(
            open_http_session, method
        )(url, json=body, headers=headers, params=params, data=data) as async_response:
            response = HTTPResponse(
                request_url=url,
                request_method=method,
                request_body=body,
                request_headers=headers,
                response=async_response,
                text=await async_response.text(),
                ok=async_response.ok,
                status_code=async_response.status,
                duration=round((time.time() - start_time), 3),
            )
            response.response = async_response
            response.text = await async_response.text()
            response.ok = async_response.ok
            response.status_code = async_response.status
            response.duration = round((time.time() - start_time), 3)
            try:
                response.json = await async_response.json()
            except:
                response.json = {}

            if not response.ok:
                log.error(
                    f"""
                        HTTP {method} request to {url} returned status code {response.status_code} and body {response.text}
                    """
                )
                sentry_sdk.capture_message(
                    f"""
                        HTTP {method} request to {url} returned status code {response.status_code} and body {response.text}
                    """
                )
    except Exception as e:
        log.error(
            f"""
                HTTP {method} request to {url} failed with {e}
            """
        )
        sentry_sdk.capture_message(
            f"""
                HTTP {method} request to {url} failed with {e}
            """
        )

    return response


async def async_get(http_session, url, body=None, headers=None, params=None, data=None):
    """
    Makes an async HTTP GET request
    """
    return await async_request(http_session, url, "get", body, headers, params, data)


async def async_post(
    http_session, url, body=None, headers=None, params=None, data=None
):
    """
    Makes an async HTTP POST request
    """
    return await async_request(http_session, url, "post", body, headers, params, data)


async def async_put(http_session, url, body=None, headers=None, params=None, data=None):
    """
    Makes an async HTTP PUT request
    """
    return await async_request(http_session, url, "put", body, headers, params, data)


async def async_patch(
    http_session, url, body=None, headers=None, params=None, data=None
):
    """
    Makes an async HTTP PATCH request
    """
    return await async_request(http_session, url, "patch", body, headers, params, data)


async def async_delete(
    http_session, url, body=None, headers=None, params=None, data=None
):
    """
    Makes an async HTTP DELETE request
    """
    return await async_request(http_session, url, "delete", body, headers, params, data)


def request(
    url, method, body=None, headers=None, params=None, data=None, rate_limiter=None, proxies=None, timeout=None
):
    """
    Makes a HTTP request
    """
    log.debug(
        f"HTTP call to {url} with method {method} and body {body if body else data} and params {params}"
    )
    if rate_limiter:
        with rate_limiter:
            response = getattr(requests, method)(
                url, json=body, headers=headers, params=params, data=data, proxies=proxies, timeout=timeout
            )
    else:
        response = getattr(requests, method)(
            url, json=body, headers=headers, params=params, data=data, proxies=proxies, timeout=timeout
        )

    if not response.ok:
        log.error(
            f"""
                HTTP {method} request to {url} returned status code {response.status_code} and body {response.text}
            """
        )
        sentry_sdk.capture_message(
            f"""
                HTTP {method} request to {url} returned status code {response.status_code} and body {response.text}
            """
        )

    return response


def get(url, body=None, headers=None, params=None, data=None, rate_limiter=None, proxies=None, timeout=None):
    """
    Makes a HTTP GET request
    """
    return request(url, "get", body, headers, params, data, rate_limiter, proxies, timeout)


def post(url, body=None, headers=None, params=None, data=None, rate_limiter=None):
    """
    Makes a HTTP POST request
    """
    return request(url, "post", body, headers, params, data, rate_limiter)


def put(url, body=None, headers=None, params=None, data=None, rate_limiter=None):
    """
    Makes a HTTP PUT request
    """
    return request(url, "put", body, headers, params, data, rate_limiter)


def patch(url, body=None, headers=None, params=None, data=None, rate_limiter=None):
    """
    Makes a HTTP PATCH request
    """
    return request(url, "patch", body, headers, params, data, rate_limiter)


def delete(url, body=None, headers=None, params=None, data=None, rate_limiter=None):
    """
    Makes a HTTP DELETE request
    """
    return request(url, "delete", body, headers, params, data, rate_limiter)


def flatten_dictionary(in_dict, dict_out=None, parent_key=None, separator="_"):
    if dict_out is None:
        dict_out = {}

    for k, v in in_dict.items():
        k = f"{parent_key}{separator}{k}" if parent_key else k
        if isinstance(v, dict):
            flatten_dictionary(in_dict=v, dict_out=dict_out, parent_key=k)

        elif isinstance(v, list):
            k = f"{parent_key}{separator}{k}" if parent_key else k
            for i, r in enumerate(v):
                if i <= 1:
                    flatten_dictionary(in_dict=r, dict_out=dict_out, parent_key=k)
                else:
                    flatten_dictionary(
                        in_dict=r, dict_out=dict_out, parent_key=f"{k}_{i}"
                    )

        dict_out[k] = v

    return dict_out

