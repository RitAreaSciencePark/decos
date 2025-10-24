"""Client utilities for interacting with the EPIRO REST API.

The module mirrors the structure used by other API helpers in the project
and exposes the minimal set of read-only endpoints currently required by
the webapp.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, Optional, Union

import requests


class EPIROAPI:
    """Simple EPIRO REST client encapsulating the common read operations."""

    INSTRUMENT_DUMP_ENDPOINT = "api/v2/decos/instrument_dump"
    PROPOSALS_ENDPOINT = "/api/v2/decos/proposal"
    TOKEN_URL = "https://auth.pathogen-ri.eu/auth/realms/EPIRO-PRP/protocol/openid-connect/token"

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        *,
        timeout: int = 30,
        extra_headers: Optional[Dict[str, str]] = None,
        session: Optional[requests.Session] = None,
        client_id: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        self.api_key = api_key
        self.extra_headers = extra_headers or {}
        self.client_id = client_id
        self.username = username
        self.password = password
        self.logger = logging.getLogger(self.__class__.__name__)

    def _get_token(self) -> str:
        if not all([self.client_id, self.username, self.password]):
            raise RuntimeError("Client ID, username, and password must be provided for token retrieval.")
        data = {
            "grant_type": "password",
            "client_id": self.client_id,
            "username": self.username,
            "password": self.password,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        try:
            response = self.session.post(self.TOKEN_URL, data=data, headers=headers, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            self.logger.error("Failed to retrieve token from Keycloak", exc_info=exc)
            raise RuntimeError("Failed to retrieve token from Keycloak") from exc
        token_data = response.json()
        access_token = token_data.get("access_token")
        if not access_token:
            self.logger.error("No access token found in token response")
            raise RuntimeError("No access token found in token response")
        return access_token

    def retrieve_instrument_dump(self, *, params: Optional[Dict[str, Any]] = None) -> Any:
        """Return the full instrument dump from EPIRO."""

        return self._request("GET", self.INSTRUMENT_DUMP_ENDPOINT, params=params)

    def retrieve_proposal_list(self, *, params: Optional[Dict[str, Any]] = None) -> Any:
        """Return the list of proposals available to the caller."""

        return self._request("GET", self.PROPOSALS_ENDPOINT, params=params)

    def retrieve_proposals(
        self,
        proposal_list: Optional[Union[str, int, Iterable[Union[str, int]]]] = None,
        proposal_ids: Optional[Union[str, int, Iterable[Union[str, int]]]] = None,
        *,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Retrieve one or more proposals.

        When ``proposal_ids`` is ``None`` the method mirrors
        :meth:`retrieve_proposal_list`. Passing a single identifier returns the
        detailed payload for that proposal, while an iterable of identifiers
        yields a list of individual responses.
        """

        if proposal_ids is None:
            print("no proposal ids")
            proposal_ids = []
            if proposal_list is None:
                print("proposal list empty")
                return self.retrieve_proposal_list(params=params)
            else:
                for proposal in proposal_list:
                    print(proposal)
                    proposal_ids.append(proposal['id'])
        
        if isinstance(proposal_ids, (str, int)):
            endpoint = f"{self.PROPOSALS_ENDPOINT}/{proposal_ids}"
            return self._request("GET", endpoint, params=params)

        results = []
        for proposal_id in proposal_ids:
            endpoint = f"{self.PROPOSALS_ENDPOINT}/{proposal_id}"
            results.append(self._request("GET", endpoint, params=params))
        print(f"{results} +++")
        return results

    # Internal helpers -------------------------------------------------
    def _build_url(self, endpoint: str) -> str:
        endpoint = endpoint.lstrip("/")
        return f"{self.base_url}/{endpoint}" if endpoint else self.base_url

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Any:
        url = self._build_url(endpoint)
        print(url)
        token = self._get_token()
        headers: Dict[str, str] = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {token}"
        if self.extra_headers:
            headers.update(self.extra_headers)
        try:
            print(url)
            print(params)
            response = self.session.request(
                method,
                url,
                params=params,
                json=json_body,
                headers=headers,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            self.logger.error("EPIRO request failure", exc_info=exc)
            raise RuntimeError(f"Failed to call EPIRO endpoint {url}") from exc

        self._check_response(response)

        if response.status_code == 204:
            return None

        return response.json()

    def _check_response(self, response: requests.Response) -> None:
        if 200 <= response.status_code < 300:
            return

        try:
            payload = response.json()
        except ValueError:
            payload = {"detail": response.text}

        message = payload.get("message") or payload.get("detail") or "Unknown error"
        self.logger.error(
            "EPIRO API error %s: %s", response.status_code, message
        )
        raise RuntimeError(
            f"EPIRO API request failed with status {response.status_code}: {message}"
        )
