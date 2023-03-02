# Instagram Basic Display Python API

A simple Python library for the Instagram Basic Display API. Based on the [instagram-basic-display-php](https://github.com/espresso-dev/instagram-basic-display-php) by [espresso.dev](https://github.com/espresso-dev)

> [PyPI](#installation) package available.

## Requirements

- Python3.6 or better
- python-requests
- Facebook Developer Account
- Facebook App

## Get started

To use the [Instagram Basic Display API](https://developers.facebook.com/docs/instagram-basic-display-api), you will need to register a Facebook app and configure Instagram Basic Display. Follow the [getting started guide](https://developers.facebook.com/docs/instagram-basic-display-api/getting-started).

### Installation

I strongly advice using [PyPI](https://pypi.org/) to keep updates as smooth as possible.

```
$ pip3 install instagram-basic-display
```

### Initialize the library

```python
from instagram_basic_display.InstagramBasicDisplay import InstagramBasicDisplay

instagram_basic_display = InstagramBasicDisplay(app_id='YOUR_APP_ID', app_secret='YOUR_APP_SECRET', redirect_url='YOUR_APP_REDIRECT_URI')

# Optionally you can force graph version using optional parameter `graph_version`:
# instagram_basic_display = InstagramBasicDisplay(app_id='YOUR_APP_ID', app_secret='YOUR_APP_SECRET', redirect_url='YOUR_APP_REDIRECT_URI', graph_version='v16.0')


print(instagram_basic_display.get_login_url()) # Returns login URL you need to follow

```

### Authenticate user (OAuth2)

```python
# Get the OAuth callback code
code = request.args.get('code')

# Get the short lived access token (valid for 1 hour)
short_lived_token = instagram_basic_display.get_o_auth_token(code)

# Exchange this token for a long lived token (valid for 60 days)
long_lived_token = instagram_basic_display.get_long_lived_token(short_lived_token.get('access_token'))

print('Your token is: {}' .format(long_lived_token.access_token))
```

### Get user profile

```python
# Set user access token
instagram_basic_display.set_access_token(long_lived_token.access_token)

# Get the users profile
profile = instagram_basic_display.get_user_profile()

print(profile)
```

## Available methods

### Setup Instagram

`Instagram(app_id: str, app_secret: str, redirect_url: str)`


### Get login URL

`get_login_url(scopes: list=None)`


### Get OAuth token (Short lived valid for 1 hour)

`get_o_auth_token(code: str)`

### Exchange the OAuth token for a Long lived token (valid for 60 days)

`get_long_lived_token(access_token)`

### Refresh access token for another 60 days before it expires

`refresh_token(access_token)`

### Set / Get access token

- Set the access token, for further method calls: `set_access_token($token)`
- Get the access token, if you want to store it for later usage: `get_access_token()`

### User methods

**Authenticated methods**

- `get_user_profile()`
- `get_user_media(user_id='me', limit: int = None, before: int = None, after: int = None)`
    - if an `user_id` isn't defined or equals `'me'`, it returns the media of the logged in user

### Media methods

**Authenticated methods**

- `get_media(_id: int)`
- `get_media_children(_id: int)`


## Pagination

The `get_user_media` endpoint has a maximum range of results, so increasing the `limit` parameter above the limit of 99 won't help.You can use pagination to return more results for this endpoint.

Pass an object into the `pagination()` method and receive your next dataset:

```python
media = instagram_basic_display.get_user_media()

more_media = instagram_basic_display.pagination(media)
```
