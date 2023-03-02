import requests
import uuid
from typing import Optional
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse, urljoin
from instagram_basic_display.InstagramBasicDisplayException import InstagramBasicDisplayException


class InstagramBasicDisplay:
    GRAPH_URL = 'https://graph.instagram.com/'

    API_URL = 'https://api.instagram.com/'

    _scopes = ['user_profile', 'user_media']

    _user_fields = 'account_type, id, media_count, username'

    _media_fields = 'caption, id, media_type, media_url, permalink, thumbnail_url, timestamp, username, children{id, media_type, media_url, permalink, thumbnail_url, timestamp, username}'

    _media_children_fields = 'id, media_type, media_url, permalink, thumbnail_url, timestamp, username'

    _access_token = None

    def __init__(self, app_id: str, app_secret: str, redirect_url: str, graph_version: Optional[str] = None):
        self._app_id = app_id
        self._app_secret = app_secret
        self._redirect_url = redirect_url
        self._graph_version = graph_version

    def get_login_url(self, scopes: Optional[list] = None, state: Optional[str] = str(uuid.uuid4())) -> str:
        if scopes is None:
            scopes = ['user_profile', 'user_media']
        if len([item for item in scopes if item not in self._scopes]) > 0:
            raise InstagramBasicDisplayException("Error: get_login_url() - Invalid scope permissions used.")

        url_parts = list(urlparse(urljoin(self.API_URL, 'oauth/authorize')))
        url_parts[4] = urlencode({
            'client_id': self.get_app_id(),
            'redirect_uri': self.get_redirect_url(),
            'scope': ','.join(scopes),
            'response_type': 'code',
            'state': state
        })
        return urlunparse(url_parts)

    def get_user_profile(self, user_id='me'):
        return self._make_call(user_id, {'fields': self._user_fields})

    def get_user_media(self, user_id='me', limit: Optional[int] = None, since: Optional[int] = None, until: Optional[int] = None):
        params = {
            'fields': self._media_fields
        }

        if limit is not None:
            params['limit'] = limit

        if since is not None:
            params['since'] = since

        if until is not None:
            params['until'] = until

        return self._make_call('{}/media'.format(user_id), params)

    def get_media(self, _id: int):
        return self._make_call(str(_id), {'fields': self._media_fields})

    def get_media_children(self, _id: int):
        return self._make_call('{}/children'.format(_id), {'fields': self._media_children_fields})

    def pagination(self, response):
        if isinstance(response, dict) and response.get('paging') is not None:
            if response['paging'].get('next') is None:
                return

            paging_next_parsed = urlparse(response['paging']['next'])

            if not paging_next_parsed.query:
                return

            params = parse_qs(paging_next_parsed.query)
            return self._make_call(paging_next_parsed.path, params)

        raise InstagramBasicDisplayException("Error: pagination() | This method doesn't support pagination.")

    def get_o_auth_token(self, code: str):
        api_data = {
            'client_id': self.get_app_id(),
            'client_secret': self.get_app_secret(),
            'grant_type': 'authorization_code',
            'redirect_uri': self.get_redirect_url(),
            'code': code
        }

        return self._make_o_auth_call(urljoin(self.API_URL, 'oauth/access_token'), api_data)

    def get_long_lived_token(self, token: str):
        api_data = {
            'client_secret': self.get_app_secret(),
            'grant_type': 'ig_exchange_token',
            'access_token': token
        }

        return self._make_o_auth_call(urljoin(self._get_graph_url(), 'access_token'), api_data, 'GET')

    def refresh_token(self, token: str):
        api_data = {
            'grant_type': 'ig_refresh_token',
            'access_token': token
        }

        return self._make_o_auth_call(urljoin(self._get_graph_url(), 'refresh_access_token'), api_data, 'GET')

    def _make_call(self, endpoint: str, params: dict = None, method: str = 'GET'):
        if not self._access_token:
            raise InstagramBasicDisplayException(
                "Error: _make_call() | function - This method requires an authenticated users access token.")

        get_data = {
            'access_token': self.get_access_token(),
        }

        if method == 'GET':
            get_data.update(params)

        request_args = {
            'headers': {'Accept': 'application/json'},
            'params': get_data
        }

        if method == 'POST':
            request_args['json'] = params

        r = requests.request(method.lower(), urljoin(self._get_graph_url(), endpoint), **request_args)
        if r.status_code != 200:
            try:
                json_data = r.json()
                if 'error' in json_data:
                    error = json_data.get('error')
                    raise InstagramBasicDisplayException.from_error_response(error)
                raise InstagramBasicDisplayException('Status code: {}'.format(r.status_code))
            except ValueError:
                raise InstagramBasicDisplayException('Failed to parse error JSON response, HTTP code: {}'.format(r.status_code))

        return r.json()

    def _make_o_auth_call(self, api_host: str, params: Optional[dict] = None, method: Optional[str] = None):

        if not method:
            method = 'POST'

        request_args = {
            'headers': {'Accept': 'application/json'},
        }

        if method == 'POST':
            request_args['data'] = params
        else:
            request_args['params'] = params

        r = requests.request(method.lower(), api_host, **request_args)
        if r.status_code != 200:
            try:
                json_data = r.json()
                if 'error' in json_data:
                    error = json_data.get('error')
                    raise InstagramBasicDisplayException.from_error_response(error)
                raise InstagramBasicDisplayException('Status code: {}'.format(r.status_code))
            except ValueError:
                raise InstagramBasicDisplayException('Failed to parse error JSON response, HTTP code: {}'.format(r.status_code))

        return r.json()

    def _get_graph_url(self) -> str:
        if self._graph_version:
            return urljoin(self.GRAPH_URL, self._graph_version)

        return self.GRAPH_URL

    def set_access_token(self, access_token: str) -> None:
        self._access_token = access_token

    def get_access_token(self) -> str:
        return self._access_token

    def set_app_id(self, app_id: str) -> None:
        self._app_id = app_id

    def get_app_id(self) -> str:
        return self._app_id

    def set_app_secret(self, app_secret: str) -> None:
        self._app_secret = app_secret

    def get_app_secret(self) -> str:
        return self._app_secret

    def set_redirect_url(self, redirect_url: str) -> None:
        self._redirect_url = redirect_url

    def get_redirect_url(self) -> str:
        return self._redirect_url

    def set_user_fields(self, user_fields: str) -> None:
        self._user_fields = user_fields

    def set_media_fields(self, media_fields: str) -> None:
        self._media_fields = media_fields

    def set_media_children_fields(self, media_children_fields: str) -> None:
        self._media_children_fields = media_children_fields

    def set_graph_version(self, graph_version: Optional[str] = None) -> None:
        self._graph_version = graph_version

    def get_graph_version(self) -> Optional[str]:
        return self._graph_version
