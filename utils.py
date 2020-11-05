# coding: utf-8
"""Utilities for working with ArcGIS REST endpoints.
   Author: David Blanchard - Esri Canada
   Date: October 2020
   Python: 3.8

   Copyright 2020 Esri Canada - All Rights Reserved
   Released under the MIT license. See LICENSE file for details"""

import json
from urllib.parse import urlsplit, urlunsplit

import requests


#region URL HELPERS ———————————————————————————————————————————————————————————————————————————————

def deriveBaseUrl(url: str) -> str:
	"""Derive the base URL to an ArcGIS Server endpoint (e.g. https://domain.com/arcgis).

	Args:
		url (str): The full URL from which to derive the base URL.

	Raises:
		ValueError: URL is missing the scheme, domain, or path to the root directory of the server endpoint.

	Returns:
		str: The base URL to the server endpoint.
	"""

	us = urlsplit(url)

	if us.scheme is None or us.netloc is None or us.path is None:
		raise ValueError('The URL "{}" is missing either its scheme, domain, or path.'.format(url))

	path_split = us.path.split('/')
	if len(path_split) < 2:
		raise ValueError('The URL "{}" must contain the endpoint root directory.'.format(url))

	base = urlunsplit((us.scheme, us.netloc, path_split[1], None, None))

	return base


def deriveRefererUrl(url: str) -> str:
	"""Derive the referer URL for tokens (e.g. https://domain.com).

	Args:
		url (str): The full URL from which to derive the referer URL.

	Raises:
		ValueError: URL is missing the scheme, or domain.

	Returns:
		str: The referer URL to use for tokens.
	"""

	us = urlsplit(url)

	if us.scheme is None or us.netloc is None:
		raise ValueError('The URL "{}" is missing either its scheme, or domain.'.format(url))

	referer = urlunsplit((us.scheme, us.netloc, '', None, None))

	return referer

#endregion


#region REQUESTS HELPERS ——————————————————————————————————————————————————————————————————————————

def readEsriJson(response: requests.Response, action: str) -> dict:
	"""Read the JSON from a request to an Esri server, raising an error for HTTP errors and ArcGIS errors.

	Args:
		response (requests.Response): The response object to parse.
		action (str): A short description of the action being taken by the request.

	Raises:
		requests.exceptions.HTTPError: An error was either found in the response code or the Esri content.

	Returns:
		dict: The JSON dictionary from the response.
	"""

	# Check for standard HTTP errors
	try:
		response.raise_for_status()
	except requests.HTTPError as e:
		message = 'ArcgisRest encountered an HTTP error while {} at URL "{}" >> {}'.format(action, response.url, e)
		raise HTTPError(response, message)

	# Read the content
	try:
		data = response.json()
	except json.decoder.JSONDecodeError:
		raise requests.exceptions.RequestException('Unable to read the JSON for {}'.format(response.url))

	# Check for Esri errors
	if 'error' in data:
		error = data['error']
		code = error['code'] if 'code' in error else 'X'
		msg = error['message'] if 'message' in error else 'No Message'
		dtls = '; '.join(error['details']) if 'details' in error and error['details'] is not None else 'No Details'

		message = 'ArcgisRest encoutered an ArcGIS error while {} at URL "{}" >> {}: {} - {}'.format(action, response.url, code, msg, dtls)
		raise ArcGISError(response, message)

	elif 'success' in data and not data['success']:
		message = 'ArcgisRest encoutered an unsuccessful response from ArcGIS while {} at URL "{}" >> {}'.format(action, response.url, response.json())
		raise ArcGISError(response, message)

	return data


class HTTPError(Exception):
	"""A non successful status code was returned."""

	def __init__(self, response: requests.Response, message: str):
		"""A non-successful status code was returned.

		Args:
			response (requests.Reponse): Response from the request.
			message (str): Explenation of the error.
		"""
		self._response = response
		self._message = message
		super().__init__(self.message)


	@property
	def response(self):
		"""requests.Response: Response from the request from which the error originated."""
		return self._response


	@property
	def message(self):
		"""str: Explenation of the error."""
		return self._message


	@message.setter
	def message(self, value: str):
		"""str: Explenation of the error."""
		self._message = value



class ArcGISError(HTTPError):
	"""ArcGIS Enterprise reported an error within its response body."""

#endregion
