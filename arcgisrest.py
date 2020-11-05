# coding: utf-8
"""Helper which handles requests to ArcGIS Portal, ArcGIS Server, and GeoEvent Server REST
   endpoints, including the admin endpoint.
   Author: David Blanchard - Esri Canada
   Date: October 2020
   Python: 3.8

   Copyright 2020 Esri Canada - All Rights Reserved
   Released under the MIT license. See LICENSE file for details"""


from typing import TypedDict
from urllib.parse import urlsplit

import urllib3

from .connection import Connection

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class WebAdaptors(TypedDict):
	"""Definition of Web Adaptor dictionnary."""
	portal: str
	arcgis: str
	geoevent: str


class ArcgisRest():
	"""Handle connections and requests to various ArcGIS Enterprise endpoints."""

	# Properties
	_server: str = None
	_username: str = None
	_password: str = None
	_use_https: bool = True
	_verify_ssl: bool = True
	_public_host: str = None

	_web_adaptors: dict = {
		'portal': None,
		'arcgis': None,
		'geoevent': None,
	}


	# Connection Handlers
	_portal: Connection = None
	_arcgis: Connection = None
	_geoevent: Connection = None


	# Intialization
	def __init__(self, server: str, username: str = None, password: str = None, web_adaptors: WebAdaptors = None, public_host: str = None, verify_ssl: bool = True):
		"""Handle connections and requests to various ArcGIS Enterprise endpoints.

		Args:
			server (str): The URL to the server, excluding the directories (e.g. https://example.com).
			username (str, optional): The username to use for authentication. Defaults to None.
			password (str, optional): The password for the provided username. Defaults to None.
			web_adaptors (WebAdaptors, optional): The web adaptor/proxy directory names in a dictionnary {'portal': str, 'arcgis': str}. If not specified, uses a direct connection with the default port and endpoint.
			public_host (str, optional): The public host used by the servers (e.g. `example.com`). This is normally the host/domain via which the main Web Adaptors (or reverse proxies) are accesible and the same as the value used for the *WebContextURL* properties. Used for direct connections. Default to None.
			verify_ssl (bool, optional): Whether to verify the SSL certificates and prevent credentials from being sent over un-encrypted connections. Defaults to True.
		"""

		# Store properties
		us = urlsplit(server)
		self._use_https = us.scheme == 'HTTPS'
		self._server = us.netloc

		self._username = username
		self._password = password
		self._verify_ssl = verify_ssl
		self._public_host = public_host

		if web_adaptors is not None:
			self._web_adaptors['portal'] = web_adaptors.get('portal')
			self._web_adaptors['arcgis'] = web_adaptors.get('arcgis')
			self._web_adaptors['geoevent'] = None

		# Initialize the connection handlers
		self._portal = Connection(self, 'portal')
		self._arcgis = Connection(self, 'arcgis')
		self._geoevent = Connection(self, 'geoevent')

		#END


	# Property Accessors
	@property
	def server(self) -> str:
		"""str: The URL to the server, excluding the directories."""
		return self._server


	@property
	def username(self) -> str:
		"""str: The username to use for authentication."""
		return self._username


	@property
	def password(self) -> str:
		"""str: The password for the associated username."""
		return self._password


	def use_https(self) -> bool:
		"""bool: Whether to use a secure HTTPS connection."""
		return self._use_https


	@property
	def verify_ssl(self) -> bool:
		"""bool: Whether to verify the SSL certificates and prevent credentials from being sent over un-encrypted connections."""
		return self._verify_ssl


	@property
	def public_host(self) -> str:
		"""str: The public host for the server to be used for authentication (e.g. example.com)."""
		return self._public_host


	@property
	def web_adaptors(self) -> WebAdaptors:
		"""WedAdaptors dict: The name of the web adaptors used on this server."""
		return self._web_adaptors.copy()


	@property
	def portal(self) -> Connection:
		"""Connection: The ArcGIS Portal connection handler."""
		return self._portal


	@property
	def arcgis(self) -> Connection:
		"""Connection: The ArcGIS Server connection handler."""
		return self._arcgis


	@property
	def geoevent(self) -> Connection:
		"""Connection: The GeoEvent Server connection handler."""
		return self._geoevent
