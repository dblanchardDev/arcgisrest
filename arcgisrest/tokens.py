# coding: utf-8
"""Retrieve a token for an ArcGIS endpoint and store for later re-use.
   Author: David Blanchard - Esri Canada
   Date: October 2020
   Python: 3.8

   https://github.com/dblanchardDev/arcgisrest

   Copyright 2020 Esri Canada - All Rights Reserved
   Released under the MIT license. See LICENSE file for details"""

from datetime import datetime
from urllib.parse import urlsplit

import requests

from .utils import deriveBaseUrl, deriveRefererUrl, readEsriJson

#region HANDLE STORED TOKENS ——————————————————————————————————————————————————————————————————————

_stored_tokens = {}


def getStoredToken(url: str) -> dict:
	"""Get an non-expired token that has been stored for re-use (if available).

	Args:
		url (str): The URL for which the token is required.

	Returns:
		dict: The token data dictionary {token, expires, ssl}, or None if not found/expired.
	"""

	base_url = deriveBaseUrl(url)
	if base_url in _stored_tokens:
		token = _stored_tokens[base_url]

		ten_minutes_ago = datetime.now().timestamp() * 1000 - 600000
		if token['expires'] > ten_minutes_ago:
			return token

	return None


def setStoredToken(url: str, token_data: dict):
	"""Store or update a token for re-use.

	Args:
		url (str): The URL for which the token was generated.
		token_data (dict): The token data dictionary {token, expires, ssl}.
	"""

	base_url = deriveBaseUrl(url)
	_stored_tokens[base_url] = token_data

	return

#endregion


#region TOKEN ACQUISITION —————————————————————————————————————————————————————————————————————————

def getServerInfo(endpoint_type: str, url: str, public_host: str = None, verify_ssl: bool = True) -> dict:
	"""Retrieve ArcGIS Enterprise's rest information.

	Args:
		endpoint_type (str): The endpoint type as chosen from ['portal', 'arcgis', 'geoevent'].
		url (str): The URL for which the info is required.
		public_host (str, optional): The public host or domain of the server if it differs from the url. Defaults to None.
		verify_ssl (bool, optional): Whether to verify the SSL Certificate. Defaults to True.

	Returns:
		dict: The /rest/info data from the server as a JSON dictionnary.
	"""
	if endpoint_type not in ['portal', 'arcgis', 'geoevent']:
		raise ValueError('Endpoint type must be one of ["portal", "arcgis", "geoevent"].')

	# Derive the info URL
	server_base = deriveBaseUrl(url)
	info_url = server_base

	if endpoint_type == 'portal':
		info_url += '/sharing/rest/info'
	elif endpoint_type == 'arcgis':
		info_url += '/rest/info'

	# If the public host is specified, use it to obtain the correct info
	headers = {}
	if public_host:
		headers['Host'] = public_host

	# Retrieve the info
	info_resp = requests.get(info_url, params={'f': 'json'}, timeout=4, verify=verify_ssl, headers=headers)
	info = readEsriJson(info_resp, 'getting ArcGIS Server info')

	return info


def _generateToken(token_url: str, username: str, password: str, referer: str = None, verify_ssl: bool = True) -> dict:
	"""Send a request for a token to an ArcGIS Enterprise get token endpoint.

	Args:
		token_url (str): The get token URL.
		username (str): The username used for authentication.
		password (str): The password for the provided username.
		referer (str, optional): The referer used to generate the token.
		                         If not specified, will generate a request IP token.
		verify_ssl (bool, optional): Whether to verify the SSL certificates. Defaults to True.

	Returns:
		dict: The JSON dictionnary token return from the server.
	"""

	# Ensure secure connection (if verify SSL)
	if verify_ssl and not token_url.startswith('https://'):
		raise requests.exceptions.SSLError('Not authorized to send credentials over an unencrypted connection. Either use an encrypted connection or set verify_ssl to False.')

	response = requests.post(token_url, data={
		'f': 'json',
		'expiration': 60,
		'username': username,
		'password': password,
		'client': 'requestip' if referer is None else 'referer',
		'referer': referer or '',
	}, timeout=4, verify=verify_ssl)

	token_data = readEsriJson(response, 'getting a token')

	return token_data


def _swapPortalForServerToken(token_url: str, url: str, token: str, verify_ssl: bool = True) -> dict:
	"""Send a request for a referer token to an ArcGIS Enterprise get token endpoint.

	Args:
		token_url (str): The get token URL.
		url (str): The URL of the request for which a token is required.
		token (str): Portal token that is being upgraded.
		verify_ssl (bool, optional): Whether to verify the SSL certificates. Defaults to True.

	Returns:
		dict: The JSON dictionnary token return from the server.
	"""

	response = requests.post(token_url, data={
		'f': 'json',
		'expiration': 60,
		'serverURL': url,
		'token': token,
	}, timeout=4, verify=verify_ssl)

	token_data = readEsriJson(response, 'swapping portal token for server token')

	return token_data


def getToken(endpoint_type: str, url: str, username: str, password: str, public_host: str = None, verify_ssl: bool = True) -> dict:
	"""Get an ArcGIS token for a URL. Will re-use previous tokens if they have 10 or more minutes until expiration.

	Args:
		endpoint_type (str): The endpoint type as chosen from ['portal', 'arcgis', 'geoevent'].
		url (str): The URL for which a token is required.
		username (str): The username with which to authenticate.
		password (str): The password corresponding to the provided username.
		public_host (str, optional): The public host or domain of the server if it differs from the url. Defaults to None.
		verify_ssl (bool, optional): Whether to verify the SSL certificate. Defaults to True.

	Raises:
		NotImplementedError: Authentications other than token based are not implemented.

	Returns:
		dict: The token data dictionary {token, expires, ssl}.
	"""

	# Portal & ArcGIS follow a standard flow for tokens
	if endpoint_type in ['portal', 'arcgis']:

		token_data = getStoredToken(url)
		if token_data is None:

			# Get the server information & validate it's data
			info = getServerInfo(endpoint_type, url, public_host, verify_ssl)

			if not info['authInfo']['isTokenBasedSecurity']:
				raise NotImplementedError('ArcGISREST does not support non token based securities.')

			token_url = info['authInfo']['tokenServicesUrl']

			if token_url == '':
				raise Exception('The server rest info retrieved for {} does not contain a token service URL. Unable to authenticate. Try specifying a public host.'.format(url))

			# Get the token
			token_data = getStoredToken(token_url)

			if token_data is None:
				token_data = _generateToken(token_url, username, password, deriveRefererUrl(url), verify_ssl)
				setStoredToken(token_url, token_data)

			# If federated server, swap Portal token for server token
			if endpoint_type == 'arcgis' and 'owningSystemUrl' in info:
				token_data = _swapPortalForServerToken(token_url, url, token_data['token'], verify_ssl)
				setStoredToken(url, token_data)

	# GeoEvent requires that we go up to it's associated ArcGIS Server instance
	elif endpoint_type == 'geoevent':

		# Derive ArcGIS Server's URL
		us = urlsplit(url)
		port = 6080 if us.scheme == 'http' else '6443'
		arcgis_url = '{}://{}:{}/arcgis'.format(us.scheme, us.hostname, port)

		# Get token for ArcGIS Server
		token_data = getToken('arcgis', arcgis_url, username, password, public_host, verify_ssl)
		setStoredToken(url, token_data)

	# Un-recognized endpoint
	else:
		raise ValueError('Endpoint type must be one of ["portal", "arcgis", "geoevent"].')

	return token_data

#endregion
