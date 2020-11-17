## arcgisrest

Helper which handles requests to ArcGIS Portal, ArcGIS Server, and GeoEvent Server REST endpoints, including the admin endpoint.

Simply provide the server’s basic information and the arcgisrest helper takes care of the rest, including deriving URLs for each endpoint, token authentication, and parsing out ArcGIS errors. Will work with federated and un-federated servers.

Underneath the hood, this module makes use of the [Requests package](https://requests.readthedocs.io/) and exposes many of the same methods, wrapped to work with ArcGIS Enterprise.

📝 *This helper is meant for onsite deployments of ArcGIS Enterprise and is not compatible with ArcGIS Online.*

&nbsp;
# Getting Started

This helper was written with Python 3.8 but should work with most if not all 3.x versions of Python.

You will first need to install the [Requests package](https://requests.readthedocs.io/en/master/user/install/#install) in your Python environment. You will then need to copy the *arcgis* folder from this repository into your project.

You would then import the module and make your first request as follows:

```python
import arcgisrest

# Establish the instance of ArcgisRest for the server
server = arcgisrest.ArcgisRest('https://myserver.com', 'user_name', 'P@ssw0rd')

# Get the listing of the Utilities directory
utilities_resp = server.arcgis.get('Utilties')

# Update a user's email address in Portal
update_results = server.portal.post('community/users/a_username/update', data={
	'email': 'a_username@example.com',
	'clearEmptyFields': False,
})

# Get a listing of Portal's Web Adaptors (from admin endpoint)
wa_resp = server.portal.get('system/webadaptors', admin=True)
```

&nbsp;
# Connecting to a Server

Each instance of the *ArcgisRest* class is used to send requests to all software components (Portal, ArcGIS Server, and GeoEvent) on the same server. If the components are on multiple servers, multiple instances of the *ArcgisRest* class will be required.


<code>arcgisrest.<b>ArcgisRest</b>(<b>server</b>: str, <b>username</b>: str = None, <b>password</b>: str = None, <b>web_adaptors</b>: dict = None, <b>public_host</b>: str = None, <b>verify_ssl</b>: bool = True, <b>timeout</b>: Union[float, tuple] = 3.05)</code>

The choice of parameters used at initialization varies depending on whether you will be connecting through Web Adaptors (or reverse proxies) or connecting directly to the server.

However, both scenarios share the following parameters:

 * **server** – The URL to the server (e.g. `https://example.com`). If passing a URL with directories, they will automatically be stripped out.

 * **username** (optional) – The username to use for authentication. Will use an anonymous connection if not specified.

 * **password** (optional) – The password for the provided username. Will use an anonymous connection if not specified.

 * **verify_ssl** (optional) – Whether to verify the SSL certificates and prevent credentials from being sent over un-encrypted connections. Defaults to True.

 * **timeout** (optional) – How many seconds to wait for the server to send data before giving up, as a float, or a (connect timeout, read timeout) tuple. To wait forever, pass a None value. Defaults to 3.05 seconds.

&nbsp;
## Connections via Web Adaptors (or Reverse Proxies)
A connection via Web Adaptors (or Reverse Proxies) is one where the connection to all ArcGIS Enterprise components is established through the same common web server.

📝 *If you are using ports other than 80/443, include the port in the **server** parameter (e.g. `https://example.com:3001`).*

📝 *Connection to the GeoEvent endpoints are not supported in this mode.*

 * **web_adaptors** (optional) – A dictionary of the Web Adaptor (or reverse proxy) directory names in the format `{'portal': str, 'arcgis': str}`. Only specify the directories that are installed. If not specified, a direct connection will be used.

```python
import arcgisrest

server = arcgisrest.ArcgisRest('https://example.com', 'user_name', 'P@ssw0rd', web_adaptors={'portal': 'portal', 'arcgis': 'arcgis'})
```

&nbsp;
## Direct Connections
A direct connection is one that connects directly to the server hosting the ArcGIS Enterprise software. In this mode, the appropriate port and directory will automatically be derived.

 * **public_host** (optional) – The public host used by the servers (e.g. `example.com`). This is normally the host/domain via which the main Web Adaptors (or reverse proxies) are accessible and the same as the value used for the *WebContextURL* properties.

```python
import arcgisrest

server = arcgisrest.ArcgisRest('https://server.domain', 'user_name', 'P@ssw0rd', public_host='example.com', verify_ssl=False)
```


&nbsp;
# ArcgisRest

From the instance of *ArcgisRest*, you can access several properties, along with the connection handlers for each ArcGIS Enterprise component (Portal, ArcGIS Server, and GeoEvent Server).

If multiple components of ArcGIS Enterprise are accessible on/from the same server, you may re-use the same instance of *ArcgisRest*.

📝 *No actual connection is made to the server until the first request is sent.*

 * <code>ArcgisRest.<b>portal</b>:Connection</code> – The ArcGIS Portal connection handler. Use this sub-class to send requests to Portal.

 * <code>ArcgisRest.<b>arcgis</b>:Connection</code> – The ArcGIS Server connection handler. Use this sub-class to send requests to ArcGIS Server.

 * <code>ArcgisRest.<b>geoevent</b>:Connection</code> – The GeoEvent Server connection handler. Use this sub-class to send requests to GeoEvent Server.

 * <code>ArcgisRest.<b>server</b>:str</code> (readonly) – The URL to the server, excluding the directories.

 * <code>ArcgisRest.<b>username</b>:str</code> (readonly) – The username to use for authentication.

 * <code>ArcgisRest.<b>password</b>:str</code> (readonly) – The password for the associated username.

 * <code>ArcgisRest.<b>use_https</b>:bool</code> (readonly) – Whether to use a secure HTTPS connection as determined from the initial server URL.

 * <code>ArcgisRest.<b>verify_ssl</b>:bool</code> (readonly) – Whether to verify the SSL certificates and prevent credentials from being sent over un-encrypted connections.

 * <code>ArcgisRest.<b>public_host</b>:str</code> (readonly) – The public host for the server to be used for authentication.

 * <code>ArcgisRest.<b>web_adaptors</b>:dict</code> (readonly) – The name of the web adaptors used on this server as a dictionary (`{'portal': str, 'arcgis': str}`).

 * <code>ArcgisRest.<b>timeout</b>:Union[float, tuple]</code> (readonly) – How many seconds to wait for the server to send data before giving up. If a tuple then (connect timeout, read timeout), if None then wait forever.


&nbsp;
# Connection Handler

Used to send requests to the corresponding software component on the server. URL derivation and authentication are automatically handled.

This class is not created directly but instead accessed via the `.portal`, `.arcgis`, and `.geoevent` properties of the *ArcgisRest* class.

 * <code>Connection.<b>get</b>(<b>path</b>: str, <b>params</b>: dict = None, <b>admin</b>: bool = False) -> requests.Response</code> – Send a GET request to the corresponding server component.

 * <code>Connection.<b>post</b>(<b>path</b>: str, <b>data</b>: dict = None, <b>json</b>: dict = None, <b>files</b>: dict = None, <b>admin</b>: bool = False) -> requests.Response</code> – Send a POST request to the corresponding server component.

 * <code>Connection.<b>put</b>(<b>path</b>: str, <b>data</b>: dict = None, <b>json</b>: dict = None, <b>files</b>: dict = None, <b>admin</b>: bool = False) -> requests.Response</code> – Send a PUT request to the corresponding server component.

 * <code>Connection.<b>patch</b>(<b>path</b>: str, <b>data</b>: dict = None, <b>json</b>: dict = None, <b>files</b>: dict = None, <b>admin</b>: bool = False) -> requests.Response</code> – Send a PATCH request to the corresponding server component.

 * <code>Connection.<b>delete</b>(<b>path</b>: str, <b>admin</b>: bool = False) -> requests.Response</code> – Send a DELETE request to the corresponding server component.

 * <code>Connection.<b>head</b>(<b>path</b>: str, <b>admin</b>: bool = False) -> requests.Response</code> – Send a HEAD request to the corresponding server component.

 * <code>Connection.<b>arcgisrest</b>:ArcgisRest</code> (readonly) – A pointer back to the source ArcgisRest instance.

 * <code>Connection.<b>endpoint_type</b>:str</code> (readonly) – The endpoint type for this connection handler ('portal', 'arcgis', or 'geoevent').

## Parameters

 * **path** – Path to which to send the request, relative to the endpoints root directory (e.g. what comes after `https://example.com/arcgis/rest`).

 * **admin** – Whether to connect to the admin endpoint. Defaults to False.

 * **params** – Dictionary to send in the query string for the request.

 * **data** – Dictionary to send in the body of the request.

 * **json** – A JSON serializable Python object to send in the body of the request.

 * **files** – Dictionary of 'name': file-like-objects (or {'name': file-tuple}) for multipart encoding upload. file-tuple can be a 2-tuple ('filename', fileobj), 3-tuple ('filename', fileobj, 'content_type') or a 4-tuple ('filename', fileobj, 'content_type', custom_headers), where 'content-type' is a string defining the content type of the given file and custom_headers a dict-like object containing additional headers to add for the file.

## Response
All requests return an instance of the *requests.Response* class from the Requests package. The following are commonly used properties and methods of this class:

 * <code>requests.response.<b>ok</b>:bool</code> – Whether the request was successful.

 * <code>requests.response.<b>status_code</b>:int</code> – The HTTP response code.

 * <code>requests.response.<b>reasons</b>:str</code> – The text reason behind the status code.

 * <code>requests.response.<b>json</b>() -> any</code> – Returns the JSON-encoded body of the response if any.

See the [Requests package documentation](https://requests.readthedocs.io/en/master/user/quickstart/#response-content) for details.


## Exceptions

 * **arcgisrest.utils.ArcgisRestException** – Not raised directly, serves as the parent for the *HTTPError* and the *ArcGISError* exceptions. Has the following properties (beyond those provided by the core Python exception):
    * _**message**_ – Explanation of the error.
    * _**response**_ – A copy of the original *requests.Response* object from which the exception originated.

 * **arcgisrest.utils.HTTPError** – A non successful status code was returned (400+). Inherits from *ArcgisRestException*.

 * **arcgisrest.utils.ArcGISError** – The request status was successful (200 to 299) but ArcGIS Enterprise reported an error in the response body. Inherits from *ArcgisRestException*.

 * **NotImplementedError** – Sending a GeoEvent request via Web Adaptor isn't supported.

## Sessions
A session allows for connection-pooling, which improves performance when making several consecutive requests to the same host.

Sessions are started using context managers on the Connection Manager:
```python
import arcgisrest
server = arcgisrest.ArcgisRest('https://example', 'user_name', 'P@ssw0rd', web_adaptors={'portal': 'portal'})

with server.portal as portal:
	com_resp = portal.get('community')
	self_resp = portal.get('portals/self')
```

&nbsp;
# Tokens
A few methods related to tokens are exposed for convenience.

📝 *You should not normally need to call these methods as their operations are already handled for you when making a request.*

<code>arcgisrest.tokens.<b>getServerInfo</b>(<b>endpoint_type</b>: str, <b>url</b>: str, <b>public_host</b>: str = None, <b>verify_ssl</b>: bool = True, <b>timeout</b>: Union[float, tuple] = 3.05) -> dict</code> – Get the server's info endpoint (not available for GeoEvent Server).

 * Parameters:
   * **endpoint_type** – The endpoint type as chosen from ['portal', 'arcgis'].

   * **url** – The full URL for which the info is required.

   * **public_host** – Same as ArcgisRest.

   * **verify_ssl** – Same as ArcgisRest.

   * **timeout** (optional) – How many seconds to wait for the server to send data before giving up, as a float, or a (connect timeout, read timeout) tuple. To wait forever, pass a None value. Defaults to 3.05 seconds.

 * Returns:

   * The _/rest/info_ JSON data from the server as a dictionnary.


<code>arcgisrest.tokens.<b>getToken</b>(<b>endpoint_type</b>: str, <b>url</b>: str, <b>username</b>: str, <b>password</b>: str, <b>public_host</b>: str = None, <b>verify_ssl</b>: bool = True, <b>timeout</b>: Union[float, tuple] = 3.05) -> dict</code> – Get an ArcGIS token for a URL. Will re-use previous tokens if they have 10 or more minutes until expiration.

 * Parameters:
   * **endpoint_type** – The endpoint type as chosen from ['portal', 'arcgis', 'geoevent'].

   * **url** – The full URL for which a token is required.

   * **username** – The username with which to authenticate.

   * **password** – The password corresponding to the provided username.

   * **public_host** – The public host or domain of the server if it differs from the url. Defaults to None.

   * **verify_ssl** – Whether to verify the SSL certificate. Defaults to True.

   * **timeout** (optional) – How many seconds to wait for the server to send data before giving up, as a float, or a (connect timeout, read timeout) tuple. To wait forever, pass a None value. Defaults to 3.05 seconds.

 * Raises:
   * **NotImplementedError** – Authentications other than token based are not implemented.

 * Returns: The token data dictionary (`{token: str, expires: int, ssl: bool}`).

&nbsp;
# Utilities
A few utilities are available from the *utils* sub-package.

📝 *You should not normally need to call these methods as their operations are already handled for you when making a request.*

<code>arcgisrest.utils.<b>deriveBaseUrl</b>(<b>url</b>: str) -> str</code> – Derive the base URL to an ArcGIS Server endpoint from a more complex URL.

 * Parameters:
   * **url** – The full URL from which to derive the base URL.

 * Exception:
   * **ValueError** – URL is missing the scheme, domain, or path to the root directory of the server endpoint.

 * Returns: The base URL to the server endpoint.

&nbsp;

<code>arcgisrest.utils.<b>deriveRefererUrl</b>(<b>url</b>: str) -> str</code> – Derive the referrer URL for tokens.

 * Parameters:
   * **url** – The full URL from which to derive the referrer URL.

 * Exception:
   * **ValueError** – URL is missing the scheme, or domain.

 * Returns: The referrer URL to use for tokens.

&nbsp;

<code>arcgisrest.utils.<b>readEsriJson</b>(<b>response</b>: requests.Response, <b>action</b>: str) -> dict</code> – Read the JSON returned by a request to an Esri server, raising an exception for HTTP errors and ArcGIS errors (within the body of the response).

 * Parameters:
   * **response** – The response object to parse.
   * **action** – A short description of the action being taken by the request.

 * Exception:
   * **requests.exceptions.HTTPError** – An non-successful value is received from the HTTP server.
   * **arcgisrest.utils.ArcGISError** – The request status was successful (200 to 299) but ArcGIS Enterprise reported an error in the response body.

 * Returns: The JSON dictionary from the response.

&nbsp;

<code>arcgisrest.utils.<b>logDebug</b>()</code> – Activate the logging of debug messages for the requests and urllib3 packages.

---

## Issues
Found a bug? Please let me know by submitting an issue.

## Contributing
Contributions are welcomed on this open source project. Please see our [guidelines in the repository](https://github.com/dblanchardDev/arcgisrest/blob/master/Contributing.md) before contributing.

## Licensing
Copyright 2020 Esri Canada – All Rights Reserved

Licensed under the MIT License (the "License"); you may not use these files except in compliance with the License. You may obtain a copy of the License at:

https://github.com/dblanchardDev/arcgisrest/blob/main/LICENSE

Unless required by applicable law or agreed to in writing, software and code distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

## Support
This tool is distributed "AS IS" and is not supported nor certified by Esri Inc. or any of its international distributors.
