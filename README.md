## arcgisrest

Helper which handles requests to ArcGIS Portal, ArcGIS Server, and GeoEvent Server REST endpoints, including the admin endpoint.

Simply provide the server’s basic information and the arcgisrest helper takes care of the rest, including deriving URLs for each endpoint, token authentication, and parsing out ArcGIS errors. Will work with federated and un-federated servers.

Underneath the hood, this module makes use of the [Requests package](https://requests.readthedocs.io/) and exposes many of the same methods, wrapped to work with ArcGIS Enterprise.

📝 *This helper is meant for onsite deployments of ArcGIS Enterprise and is not compatible with ArcGIS Online.*

&nbsp;
# Getting Started

This helper was written with Python 3.8, but should work with most if not all 3.x versions of Python.

You will first need to install the [Requests package](https://requests.readthedocs.io/en/master/user/install/#install) in your Python environment. You will then need to drop the *arcgis* folder in your project.

Next, import the module and make your first request as follows:

```python
from arcgisrest import ArcgisRest

# Establish the instance of ArcgisRest for the server
arcgisrest = ArcgisRest('https://myserver.com', 'user_name', 'P@ssw0rd')

# Get the listing of the Utilities directory
utilities_resp = arcgisrest.arcgis.get('Utilties')

# Update a user's email address in Portal
update_results = arcgisrest.portal.post('community/users/a_username/update', data={
	'email': 'a_username@example.com',
	'clearEmptyFields': False,
})

# Get a listing of Portal's Web Adaptors (from admin endpoint)
wa_resp = arcgisrest.portal.get('system/webadaptors', admin=True)
```

&nbsp;
# Connecting to a Server

Each instance of the *ArcgisRest* class is used to send requests to all software components (Portal, ArcGIS Server, and GeoEvent) on the same server. If the components are on multiple servers, multiple instances of the *ArcgisRest* class will be required.


`arcgisrest.`**`ArcgisRest`**`(server: str, username: str = None, password: str = None, web_adaptors: dict = None, public_host: str = None, verify_ssl: bool = True)`

The choice of parameters used at initialization varies depending on whether you will be connecting through Web Adaptors (or reverse proxies), or connecting directly to the server.

However, both scenarios share the following parameters:

 * **server** – The URL to the server, excluding the directories (e.g. `https://example.com`).

 * **username** (optional) – The username to use for authentication. Will use an anonymous connection if not specified.

 * **password** (optional) – The password for the provided username. Will use an anomymous connection if not specified.

 * **verify_ssl** (optional) – Whether to verify the SSL certificates and prevent credentials from being sent over un-encrypted connections. Defaults to True.

&nbsp;
## Connections via Web Adaptors (or Reverse Proxies)
A connection via Web Adaptors (or Reverse Proxies) is one where the connection to all ArcGIS Enteprise components is established through the same common web server.

📝 *If you are using ports other than 80/443, include the port in the **server** parameter (e.g. `https://example.com:3001`).*

📝 *Connection to the GeoEvent endpoints are not supported in this mode.*

 * **web_adaptors** (optional) – A dictionnary of the Web Adaptor (or reverse proxy) directory names in the format `{'portal': str, 'arcgis': str}`. Only specify the directories that are installed. If not specified, a direct connection will be used.

&nbsp;
## Direct Connections
A direct connection is one that connects directly to the server hosting the ArcGIS Enterprise software. In this mode, the appropriate port and directory will automatically be derived.

 * **public_host** (optional) – The public host used by the servers (e.g. `example.com`). This is normally the host/domain via which the main Web Adaptors (or reverse proxies) are accesible and the same as the value used for the *WebContextURL* properties.


&nbsp;
# ArcgisRest

From the instance of *ArcgisRest*, you can access several properties, along with the connection handlers for each ArcGIS Enterprise component (Portal, ArcGIS Server, and GeoEvent Server).

If multiple components of ArcGIS Enterprise are installed on the same server, you may re-use the same instance of *ArcgisRest*.

📝 *No actual connection is made to the server until the first request is sent.*

 * `arcgisrest.`**`portal`**`:Connection` – The ArcGIS Portal connection handler. Use this sub-class to send requests to Portal.

 * `arcgisrest.`**`arcgis`**`:Connection` – The ArcGIS Server connection handler. Use this sub-class to send requests to ArcGIS Server.

 * `arcgisrest.`**`geoevent`**`:Connection` – The GeoEvent Server connection handler. Use this sub-class to send requests to GeoEvent Server.

 * `arcgisrest.`**`server`**`:str` (readonly) – The URL to the server, excluding the directories.

 * `arcgisrest.`**`username`**`:str` (readonly) – The username to use for authentication.

 * `arcgisrest.`**`password`**`:str` (readonly) – The password for the associated username.

 * `arcgisrest.`**`use_https`**`:bool` (readonly) – Whether to use a secure HTTPS connection as determined from the initial server URL.

 * `arcgisrest.`**`verify_ssl`**`:bool` (readonly) – Whether to verify the SSL certificates and prevent credentials from being sent over un-encrypted connections.

 * `arcgisrest.`**`public_host`**`:str` (readonly) – The public host for the server to be used for authentication.

 * `arcgisrest.`**`web_adaptors`**`:dict` (readonly) – The name of the web adaptors used on this server.


&nbsp;
# Connection Handler

Used to send requests to the corresponding software component on the server. URL derivation and the authentication is automatically handled.

This class is not created directy but instead accessed via the `.portal`, `.arcgis`, and `.geoevent` properties of the *ArcgisRest* class.

 * `connection.`**`get`**`(path: str, params: dict = None, admin: bool = False) -> requests.Response` – Send a GET request to the corresponding server component.

 * `connection.`**`post`**`(path: str, data: dict = None, json: dict = None, files: dict = None, admin: bool = False) -> requests.Response` – Send a POST request to the corresponding server component.

 * `connection.`**`put`**`(path: str, data: dict = None, json: dict = None, files: dict = None, admin: bool = False) -> requests.Response` – Send a PUT request to the corresponding server component.

 * `connection.`**`patch`**`(path: str, data: dict = None, json: dict = None, files: dict = None, admin: bool = False) -> requests.Response` – Send a PATCH request to the corresponding server component.

 * `connection.`**`delete`**`(path: str, admin: bool = False) -> requests.Response` – Send a DELETE request to the corresponding server component.

 * `connection.`**`head`**`(path: str, admin: bool = False) -> requests.Response` – Send a HEAD request to the corresponding server component.

## Parameters

 * **path** – Path to which to send the request, relative to the endpoints root directory (e.g. what comes after `https://example.com/arcgis/rest`).

 * **admin** – Whether to connect to the admin endpoint. Defaults to False.

 * **params** – Dictionary to send in the query string for the request.

 * **data** – Dictionary to send in the body of the request.

 * **json** – A JSON serializable Python object to send in the body of the request.

 * **files** – Dictionary of 'name': file-like-objects (or {'name': file-tuple}) for multipart encoding upload. file-tuple can be a 2-tuple ('filename', fileobj), 3-tuple ('filename', fileobj, 'content_type') or a 4-tuple ('filename', fileobj, 'content_type', custom_headers), where 'content-type' is a string defining the content type of the given file and custom_headers a dict-like object containing additional headers to add for the file.

## Response
All requests return an instance of the *requests.Response* class from the Requests package. The following are commonly used properties and methods of this class:

 * `response.`**`ok`**`:bool` – Whether the request was successful.

 * `response.`**`status_code`**`:int` – The HTTP response code.

 * `response.`**`reasons`**`:str` – The text reason behind the status code.

 * `response.`**`json`**`() -> any` – Returns the JSON-encoded body of the response if any.

See the [Requests package documentation](https://requests.readthedocs.io/en/master/user/quickstart/#response-content) for details.


## Exceptions

 * **requests.exceptions.HTTPError** – An non-successful value is received from the HTTP server.
 * **arcgisrest.utils.ArcGISError** – ArcGIS Enteprise reported that the request was not successful.
 * **NotImplementedError** – Sending a GeoEvent request via Web Adaptor isn't supported.

## Sessions
A session allow for connection-pooling, which improves performance when making several consecutive requests to the same host.

Sessions are started using context managers on the Connection Manager:
```python
with arcgisrest.portal as portal:
	com_resp = portal.get('community')
	self_resp = portal.get('portals/self')
```

&nbsp;
# Utilities
A few utilities are available from the *utils* sub-package.

📝 *You do not normally need to access these methods as URL derivation, referrers, and request parsing is handled by default by the request methods.*

`arcgisrest.utils.`**`deriveBaseUrl`**`(url: str) -> str` – Derive the base URL to an ArcGIS Server endpoint from a more complex URL.

 * Parameters:
   * **url** – The full URL from which to derive the base URL.

 * Exception:
   * **ValueError** – URL is missing the scheme, domain, or path to the root directory of the server endpoint.

 * Returns: The base URL to the server endpoint.

&nbsp;

`arcgisrest.utils.`**`deriveRefererUrl`**`(url: str) -> str` – Derive the referer URL for tokens.

 * Parameters:
   * **url** – The full URL from which to derive the referer URL.

 * Exception:
   * **ValueError** – URL is missing the scheme, or domain.

 * Returns: The referer URL to use for tokens.

&nbsp;

`arcgisrest.utils.`**`readEsriJson`**`(response: requests.Response, action: str) -> dict` – Read the JSON from a request to an Esri server, raising an error for HTTP errors and ArcGIS errors.

 * Parameters:
   * **response** – The response object to parse.
   * **action** – A short description of the action being taken by the request.

 * Exception:
   * **requests.exceptions.HTTPError** – An non-successful value is received from the HTTP server.
   * **arcgisrest.utils.ArcGISError** – ArcGIS Enteprise reported that the request was not successful.

 * Returns: The JSON dictionary from the response.
