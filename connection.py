# coding: utf-8
"""Connection handler for a single endpoint server (i.e. portal, arcgis, or geoevent).
   Author: David Blanchard - Esri Canada
   Date: October 2020
   Python: 3.8

   Copyright 2020 Esri Canada - All Rights Reserved
   Released under the MIT license. See LICENSE file for details"""

import requests

from .tokens import getToken
from .utils import readEsriJson

#region CONSTANTS —————————————————————————————————————————————————————————————————————————————————

ENDPOINT_PROPERTIES = {
	'portal': {
		'port_http': 7080,
		'port_https': 7443,
		'directory': '/arcgis',
		'rest': '/sharing/rest',
		'admin': '/portaladmin',
	},
	'arcgis': {
		'port_http': 6080,
		'port_https': 6443,
		'directory': '/arcgis',
		'rest': '/rest',
		'admin': '/admin',
	},
	'geoevent': {
		'port_http': 6180,
		'port_https': 6143,
		'directory': '/geoevent',
		'rest': '/rest',
		'admin': '/admin',
	}
}

#endregion


class Connection():
	"""Connection handler for a single endpoint server (i.e. portal, arcgis, or geoevent)."""

	#region INTITIALIZATION AND CORE PROPERTIES ———————————————————————————————————————————————————

	_arcgisrest = None
	_endpoint_type: str = None


	def __init__(self, arcgisrest, endpoint_type: str):
		"""Connection handler for a single endpoint server (i.e. portal, arcgis, or geoevent).

		Args:
			arcgisrest (ArcgisRest): The outer ArcgisRest class instance to call up to.
			endpoint_type (str): The endpoint type as chosen from ['portal', 'arcgis', 'geoevent'].

		Raises:
			ValueError: Incorect value passed for endpoint type.
		"""

		# Store the values as properties
		self._arcgisrest = arcgisrest

		if endpoint_type not in ['portal', 'arcgis', 'geoevent']:
			raise ValueError('Endpoint type must be one of ["portal", "arcgis", "geoevent"].')
		self._endpoint_type = endpoint_type

		#END


	@property
	def arcgisrest(self):
		"""ArcgisRest: The outer ArcgisRest instance."""
		return self._arcgisrest


	@property
	def endpoint_type(self) -> str:
		"""str: The endpoint type as chosen from ['portal', 'arcgis', 'geoevent']."""
		return self._endpoint_type

	#endregion


	#region REQUESTS ——————————————————————————————————————————————————————————————————————————————

	def _request(self, method: str, path: str, params: dict = None, data: dict = None, json: dict = None, files: dict = None, admin: bool = False) -> requests.Response:
		"""Send a request of any method type, adjusting the body and headers to handle tokens and format. Will also check for errors reported by the ArcGIS Server.

		Args:
			method (str): method for the new Request object: GET, OPTIONS, HEAD, POST, PUT, PATCH, or DELETE.
			path (str): Path to which to send the request, after the endpoints rest directory.
			params (dict, optional): Dictionary to send in the query string for the Request (for GET). Defaults to None.
			data (dict, optional): Dictionary, to send in the body of the Request (POST, PUT, PATCH). Defaults to None.
			json (dict, optional): json data to send in the body of the Request (POST, PUT, PATCH). Defaults to None.
			files (dict, optional): [description]. Dictionary of files to send (see requests library for details). Defaults to None.
			admin (bool, optional): Whether to connect to the admin endpoint. Defaults to False.

		Raises:
			ValueError: If incorrect method passed.
			NotImplementedError: Sending a GeoEvent request via Web Adaptor isn't supported.
			requests.exceptions.HTTPError: An non-successful value is received from the server (either from the web server, or from within the ArcGIS response).

		Returns:
			requests.Response: The response from the requests module.
		"""

		# Check method is valid
		if method not in ['GET', 'OPTIONS', 'HEAD', 'POST', 'PUT', 'PATCH', 'DELETE']:
			raise ValueError('The request method must be GET, OPTIONS, HEAD, POST, PUT, PATCH, or DELETE.')

		# GeoEvent using web apators not support
		if self.endpoint_type == 'geoevent' and self.arcgisrest.web_adaptors['arcgis'] is not None:
			raise NotImplementedError('Sending a GeoEvent request via a proxied (or web adaptor) endpoint is not supported. Please use a direct connection.')

		# Derive the full URL
		web_adaptor = self.arcgisrest.web_adaptors[self.endpoint_type]
		url = self._deriveUrl(path, web_adaptor, admin)

		# Append token and format to the request
		headers = {}

		if method not in ['HEAD', 'OPTIONS']:
			# Obtain a token
			token = None
			if self.arcgisrest.username and self.arcgisrest.password:
				token_data = getToken(self.endpoint_type, url, self.arcgisrest.username, self.arcgisrest.password, self.arcgisrest.public_host, self.arcgisrest.verify_ssl)
				token = token_data['token']

			# Generate the requires params and headers
			if method == 'GET' and params is None:
				params = {}
			elif method in ['POST', 'PUT', 'PATCH'] and data is None and json is None:
				data = {}

			params, data, json = self._mixinBodies([params, data, json], token)
			headers = self._getHeaders(token)

		# Send the request (and parse for errors)
		req = self._session or requests

		response = req.request(method, url, params=params, data=data, json=json, files=files, headers=headers, timeout=4, verify=self.arcgisrest.verify_ssl)

		if method not in ['HEAD', 'OPTIONS']:
			readEsriJson(response, 'executing a {} request'.format(method.lower()))
		else:
			response.raise_for_status()

		return response


	def head(self, path: str, admin: bool = False) -> requests.Response:
		"""Sends a HEAD request, automatically handling the URL derivation and the authentication.

		Args:
			path (str): Path to which to send the request, after the endpoints rest directory (e.g. what comes after https://example.com/arcgis/rest).
			admin (bool, optional): Whether to connect to the admin endpoint. Defaults to False.

		Raises:
			ValueError: If incorrect method passed.
			NotImplementedError: Sending a GeoEvent request via Web Adaptor isn't supported.
			requests.exceptions.HTTPError: An non-successful value is received from the server (either from the web server, or from within the ArcGIS response).

		Returns:
			requests.Response: The response from the requests module.
		"""
		response = self._request('HEAD', path, admin=admin)

		return response


	def get(self, path: str, params: dict = None, admin: bool = False) -> requests.Response:
		"""Sends a GET request, automatically handling the URL derivation and the authentication.

		Args:
			path (str): Path to which to send the request, after the endpoints rest directory (e.g. what comes after https://example.com/arcgis/rest).
			params (dict): URL parameters of the request. Defaults to None.
			admin (bool, optional): Whether to connect to the admin endpoint. Defaults to False.

		Raises:
			ValueError: If incorrect method passed.
			NotImplementedError: Sending a GeoEvent request via Web Adaptor isn't supported.
			requests.exceptions.HTTPError: An non-successful value is received from the server (either from the web server, or from within the ArcGIS response).

		Returns:
			requests.Response: The response from the requests module, after having been checked for ArcGIS errors.
		"""
		response = self._request('GET', path, params=params, admin=admin)

		return response


	def post(self, path: str, data: dict = None, json: dict = None, files: dict = None, admin: bool = False) -> requests.Response:
		"""Sends a POST request, automatically handling the URL derivation and the authentication.

		Args:
			path (str): Path to which to send the request, after the endpoints rest directory (e.g. what comes after https://example.com/arcgis/rest).
			data (dict): Body of the request. Defaults to None.
			json (dict): Body of the request to be sent as JSON. Defaults to None.
			files (dict, optional): [description]. Dictionary of files to send (see requests library for details). Defaults to None.
			admin (bool, optional): Whether to connect to the admin endpoint. Defaults to False.

		Raises:
			ValueError: If incorrect method passed.
			NotImplementedError: Sending a GeoEvent request via Web Adaptor isn't supported.
			requests.exceptions.HTTPError: An non-successful value is received from the server (either from the web server, or from within the ArcGIS response).

		Returns:
			requests.Response: The response from the requests module, after having been checked for ArcGIS errors.
		"""
		response = self._request('POST', path, data=data, json=json, files=files, admin=admin)

		return response


	def put(self, path: str, data: dict = None, json: dict = None, files: dict = None, admin: bool = False) -> requests.Response:
		"""Sends a PUT request, automatically handling the URL derivation and the authentication.

		Args:
			path (str): Path to which to send the request, after the endpoints rest directory (e.g. what comes after https://example.com/arcgis/rest).
			data (dict): Body of the request. Defaults to None.
			json (dict): Body of the request to be sent as JSON. Defaults to None.
			files (dict, optional): [description]. Dictionary of files to send (see requests library for details). Defaults to None.
			admin (bool, optional): Whether to connect to the admin endpoint. Defaults to False.

		Raises:
			ValueError: If incorrect method passed.
			NotImplementedError: Sending a GeoEvent request via Web Adaptor isn't supported.
			requests.exceptions.HTTPError: An non-successful value is received from the server (either from the web server, or from within the ArcGIS response).

		Returns:
			requests.Response: The response from the requests module, after having been checked for ArcGIS errors.
		"""
		response = self._request('PUT', path, data=data, json=json, files=files, admin=admin)

		return response


	def patch(self, path: str, data: dict = None, json: dict = None, files: dict = None, admin: bool = False) -> requests.Response:
		"""Sends a PATCH request, automatically handling the URL derivation and the authentication.

		Args:
			path (str): Path to which to send the request, after the endpoints rest directory (e.g. what comes after https://example.com/arcgis/rest).
			data (dict): Body of the request. Defaults to None.
			json (dict): Body of the request to be sent as JSON. Defaults to None.
			files (dict, optional): [description]. Dictionary of files to send (see requests library for details). Defaults to None.
			admin (bool, optional): Whether to connect to the admin endpoint. Defaults to False.

		Raises:
			ValueError: If incorrect method passed.
			NotImplementedError: Sending a GeoEvent request via Web Adaptor isn't supported.
			requests.exceptions.HTTPError: An non-successful value is received from the server (either from the web server, or from within the ArcGIS response).

		Returns:
			requests.Response: The response from the requests module, after having been checked for ArcGIS errors.
		"""
		response = self._request('PATCH', path, data=data, json=json, files=files, admin=admin)

		return response


	def delete(self, path: str, admin: bool = False) -> requests.Response:
		"""Sends a DELETE request, automatically handling the URL derivation and the authentication.

		Args:
			path (str): Path to which to send the request, after the endpoints rest directory (e.g. what comes after https://example.com/arcgis/rest).
			admin (bool, optional): Whether to connect to the admin endpoint. Defaults to False.

		Raises:
			ValueError: If incorrect method passed.
			NotImplementedError: Sending a GeoEvent request via Web Adaptor isn't supported.
			requests.exceptions.HTTPError: An non-successful value is received from the server (either from the web server, or from within the ArcGIS response).

		Returns:
			requests.Response: The response from the requests module, after having been checked for ArcGIS errors.
		"""
		response = self._request('DELETE', path, admin=admin)

		return response

	#endregion


	#region SESSION MANAGERS ——————————————————————————————————————————————————————————————————————

	_session: requests.Session = None

	def __enter__(self):
		"""Start a request session, enabling connection-pooling. Improves performance when making several consecutive requests to the same host."""
		self._session = requests.Session()

		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		"""Terminate the request session."""
		self._session.close()
		self._session = None

		#END

	#endregion


	#region HELPERS ———————————————————————————————————————————————————————————————————————————————

	def _deriveUrl(self, path: str, web_adaptor: str = None, admin: bool = False) -> str:
		"""Derive the full URL from existing properties and those provided to the request method.

		Args:
			path (str): Path to which to send the request, after the endpoints rest directory
			            (e.g. what comes after https://example.com/arcgis/rest).
			web_adaptor (str, optional): The web adaptor directory name. Defaults to using a direct
			                             connection, using the default port and endpoint.
			admin (bool, optional): Whether to connect to the admin endpoint. Defaults to False.

		Returns:
			str: The complete URL to the resource.
		"""

		ep = ENDPOINT_PROPERTIES[self.endpoint_type]

		# Scheme (http/https)
		scheme = "https" if self.arcgisrest.use_https else "http"

		# Server (domain + port)
		server = self.arcgisrest.server

		if ':' not in server and web_adaptor is None:
			port = ep['port_https'] if self.arcgisrest.use_https else ep['port_http']
			server += ':{}'.format(port)

		# Root Directory
		directory = web_adaptor if web_adaptor is not None else ep['directory']
		if not directory.startswith(('/', '\\')):
			directory = '/' + directory

		# Rest Directory
		rest = ep['admin'] if admin else ep['rest']

		# Path
		if not path.startswith(('/', '\\')):
			path = '/' + path

		# Assemble
		assembled = '{}://{}{}{}{}'.format(scheme, server, directory, rest, path)

		return assembled


	def _mixinBodies(self, bodies: list, token: str = None) -> list:
		"""Mixin required parameters or body data/json according to the endpoint type.

		Args:
			bodies (list): A list of body elements to augment, from highest priority to lowest.
			token (str, optional): The token used to login to the server. Defaults to None.

		Returns:
			list: The updated bodies in the same order as was passed in.
		"""

		# ArcGIS ∴ add f=json and token=xyz
		if self.endpoint_type in ['portal', 'arcgis']:
			mixin = {'f': 'json'}

			if token is not None:
				mixin['token'] = token

			for idx, data in enumerate(bodies):
				if data is not None:
					bodies[idx] = {**data, **mixin}
					break

		return bodies


	def _getHeaders(self, token: str = None) -> dict:
		"""Create the base headers for the request, passing the accepted format (JSON) and token where required.

		token (str, optional): The token used to login to the server. Defaults to None.

		Returns:
			dict: A set of header names and values.
		"""

		# Required to get JSON from GeoEvent endpoints (ignored by others)
		headers = {
			'Accept': 'application/json'
		}

		# Tokens
		if token is not None:
			# GeoEvent
			if self.endpoint_type == 'geoevent':
				headers['Cookie'] = 'adminToken={}'.format(token)

		return headers


	#endregion
