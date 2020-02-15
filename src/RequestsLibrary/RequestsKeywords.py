import json
import sys

from requests.models import Response
from requests.sessions import merge_setting
from requests.cookies import merge_cookies

import robot
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from robot.utils.asserts import assert_equal

from RequestsLibrary import utils, log
from RequestsLibrary.SessionWrapper import SessionWrapper
from RequestsLibrary.compat import httplib, PY3
from RequestsLibrary.exceptions import InvalidResponse


class WritableObject:
    """ HTTP stream handler """

    def __init__(self):
        self.content = []

    def write(self, string):
        self.content.append(string)


class RequestsKeywords(SessionWrapper):
    ROBOT_LIBRARY_SCOPE = 'Global'

    def __init__(self):
        self._cache = robot.utils.ConnectionCache('No sessions created')
        self.builtin = BuiltIn()
        self.debug = 0

    def delete_all_sessions(self):
        """ Removes all the session objects """
        logger.info('Delete All Sessions')

        self._cache.empty_cache()

    def update_session(self, alias, headers=None, cookies=None):
        """Update Session Headers: update a HTTP Session Headers

        ``alias`` Robot Framework alias to identify the session

        ``headers`` Dictionary of headers merge into session
        """
        session = self._cache.switch(alias)
        session.headers = merge_setting(headers, session.headers)
        session.cookies = merge_cookies(session.cookies, cookies)

    def to_json(self, content, pretty_print=False):
        """ Convert a string to a JSON object

        ``content`` String content to convert into JSON

        ``pretty_print`` If defined, will output JSON is pretty print format
        """
        if PY3:
            if isinstance(content, bytes):
                content = content.decode(encoding='utf-8')
        if pretty_print:
            json_ = utils.json_pretty_print(content)
        else:
            json_ = json.loads(content)
        logger.info('To JSON using : content=%s ' % (content))
        logger.info('To JSON using : pretty_print=%s ' % (pretty_print))

        return json_

    def get_request(
            self,
            alias,
            uri,
            headers=None,
            data=None,
            json=None,
            params=None,
            allow_redirects=None,
            timeout=None):
        """ Send a GET request on the session object found using the
        given `alias`

        ``alias`` that will be used to identify the Session object in the cache

        ``uri`` to send the GET request to

        ``params`` url parameters to append to the uri

        ``headers`` a dictionary of headers to use with the request

        ``data`` a dictionary of key-value pairs that will be urlencoded
               and sent as GET data
               or binary data that is sent as the raw body content

        ``json`` a value that will be json encoded
               and sent as GET data if data is not specified

        ``allow_redirects`` Boolean. Set to True if POST/PUT/DELETE redirect following is allowed.

        ``timeout`` connection timeout
        """
        session = self._cache.switch(alias)
        redir = True if allow_redirects is None else allow_redirects

        response = self._common_request(
            "get",
            session,
            uri,
            params=params,
            headers=headers,
            data=data,
            json=json,
            allow_redirects=redir,
            timeout=timeout)

        return response

    def post_request(
            self,
            alias,
            uri,
            data=None,
            json=None,
            params=None,
            headers=None,
            files=None,
            allow_redirects=None,
            timeout=None):
        """ Send a POST request on the session object found using the
        given `alias`

        ``alias`` that will be used to identify the Session object in the cache

        ``uri`` to send the POST request to

        ``data`` a dictionary of key-value pairs that will be urlencoded
               and sent as POST data
               or binary data that is sent as the raw body content
               or passed as such for multipart form data if ``files`` is also
                  defined

        ``json`` a value that will be json encoded
               and sent as POST data if files or data is not specified

        ``params`` url parameters to append to the uri

        ``headers`` a dictionary of headers to use with the request

        ``files`` a dictionary of file names containing file data to POST to the server

        ``allow_redirects`` Boolean. Set to True if POST/PUT/DELETE redirect following is allowed.

        ``timeout`` connection timeout
        """
        session = self._cache.switch(alias)
        if not files:
            data = utils.format_data_according_to_header(session, data, headers)
        redir = True if allow_redirects is None else allow_redirects

        response = self._common_request(
            "post",
            session,
            uri,
            data=data,
            json=json,
            params=params,
            files=files,
            headers=headers,
            allow_redirects=redir,
            timeout=timeout)
        return response

    def patch_request(
            self,
            alias,
            uri,
            data=None,
            json=None,
            params=None,
            headers=None,
            files=None,
            allow_redirects=None,
            timeout=None):
        """ Send a PATCH request on the session object found using the
        given `alias`

        ``alias`` that will be used to identify the Session object in the cache

        ``uri`` to send the PATCH request to

        ``data`` a dictionary of key-value pairs that will be urlencoded
               and sent as PATCH data
               or binary data that is sent as the raw body content

        ``json`` a value that will be json encoded
               and sent as PATCH data if data is not specified

        ``headers`` a dictionary of headers to use with the request

        ``files`` a dictionary of file names containing file data to PATCH to the server

        ``allow_redirects`` Boolean. Set to True if POST/PUT/DELETE redirect following is allowed.

        ``params`` url parameters to append to the uri

        ``timeout`` connection timeout
        """
        session = self._cache.switch(alias)
        data = utils.format_data_according_to_header(session, data, headers)
        redir = True if allow_redirects is None else allow_redirects

        response = self._common_request(
            "patch",
            session,
            uri,
            data=data,
            json=json,
            params=params,
            files=files,
            headers=headers,
            allow_redirects=redir,
            timeout=timeout)

        return response

    def put_request(
            self,
            alias,
            uri,
            data=None,
            json=None,
            params=None,
            files=None,
            headers=None,
            allow_redirects=None,
            timeout=None):
        """ Send a PUT request on the session object found using the
        given `alias`

        ``alias`` that will be used to identify the Session object in the cache

        ``uri`` to send the PUT request to

        ``data`` a dictionary of key-value pairs that will be urlencoded
               and sent as PUT data
               or binary data that is sent as the raw body content

        ``json`` a value that will be json encoded
               and sent as PUT data if data is not specified

        ``headers`` a dictionary of headers to use with the request

        ``allow_redirects`` Boolean. Set to True if POST/PUT/DELETE redirect following is allowed.

        ``params`` url parameters to append to the uri

        ``timeout`` connection timeout
        """
        session = self._cache.switch(alias)
        data = utils.format_data_according_to_header(session, data, headers)
        redir = True if allow_redirects is None else allow_redirects

        response = self._common_request(
            "put",
            session,
            uri,
            data=data,
            json=json,
            params=params,
            files=files,
            headers=headers,
            allow_redirects=redir,
            timeout=timeout)

        return response

    def delete_request(
            self,
            alias,
            uri,
            data=None,
            json=None,
            params=None,
            headers=None,
            allow_redirects=None,
            timeout=None):
        """ Send a DELETE request on the session object found using the
        given `alias`

        ``alias`` that will be used to identify the Session object in the cache

        ``uri`` to send the DELETE request to

        ``json`` a value that will be json encoded
               and sent as request data if data is not specified

        ``headers`` a dictionary of headers to use with the request

        ``allow_redirects`` Boolean. Set to True if POST/PUT/DELETE redirect following is allowed.

        ``timeout`` connection timeout
        """
        session = self._cache.switch(alias)
        data = utils.format_data_according_to_header(session, data, headers)
        redir = True if allow_redirects is None else allow_redirects

        response = self._common_request(
            "delete",
            session,
            uri,
            data=data,
            json=json,
            params=params,
            headers=headers,
            allow_redirects=redir,
            timeout=timeout)

        return response

    def head_request(
            self,
            alias,
            uri,
            headers=None,
            allow_redirects=None,
            timeout=None):
        """ Send a HEAD request on the session object found using the
        given `alias`

        ``alias`` that will be used to identify the Session object in the cache

        ``uri`` to send the HEAD request to

        ``allow_redirects`` Boolean. Set to True if POST/PUT/DELETE redirect following is allowed.

        ``headers`` a dictionary of headers to use with the request

        ``timeout`` connection timeout
        """
        session = self._cache.switch(alias)
        redir = False if allow_redirects is None else allow_redirects
        response = self._common_request(
            "head",
            session,
            uri,
            headers=headers,
            allow_redirects=redir,
            timeout=timeout)

        return response

    def options_request(
            self,
            alias,
            uri,
            headers=None,
            allow_redirects=None,
            timeout=None):
        """ Send an OPTIONS request on the session object found using the
        given `alias`

        ``alias`` that will be used to identify the Session object in the cache

        ``uri`` to send the OPTIONS request to

        ``allow_redirects`` Boolean. Set to True if POST/PUT/DELETE redirect following is allowed.

        ``headers`` a dictionary of headers to use with the request

        ``timeout`` connection timeout
        """
        session = self._cache.switch(alias)
        redir = True if allow_redirects is None else allow_redirects
        response = self._common_request(
            "options",
            session,
            uri,
            headers=headers,
            allow_redirects=redir,
            timeout=timeout)

        return response

    def status_should_be(self, expected_status, response, msg=None):
        """
        Fails if response status code is different than the expected.

        ``expected_status`` could be the code number as an integer or as string.
        But it could also be a named status code like 'ok', 'created', 'accepted' or
        'bad request', 'not found' etc.

        The ``response`` is the output of other requests keywords like ``Get Request``.

        A custom message ``msg`` can be added to work like built in keywords.
        """
        self._check_status(expected_status, response, msg)

    def request_should_be_successful(self, response):
        """
        Fails if response status code is a client or server error (4xx, 5xx).

        The ``response`` is the output of other requests keywords like ``Get Request``.

        In case of failure an HTTPError will be automatically raised.
        """
        self._check_status(None, response, msg=None)

    def _common_request(
            self,
            method,
            session,
            uri,
            **kwargs):

        log.log_request(method, session, uri, **kwargs)
        method_function = getattr(session, method)

        self._capture_output()
        resp = method_function(
            self._get_url(session, uri),
            params=utils.utf8_urlencode(kwargs.pop('params', None)),
            timeout=self._get_timeout(kwargs.pop('timeout', None)),
            cookies=self.cookies,
            verify=self.verify,
            **kwargs)
        self._print_debug()

        session.last_resp = resp
        log.log_response(method, resp)

        return resp

    @staticmethod
    def _check_status(expected_status, resp, msg=None):
        """
        Helper method to check HTTP status
        """
        if not isinstance(resp, Response):
            raise InvalidResponse(resp)
        if expected_status is None:
            resp.raise_for_status()
        else:
            try:
                expected_status = int(expected_status)
            except ValueError:

                expected_status = utils.parse_named_status(expected_status)
            msg = '' if msg is None else '{} '.format(msg)
            msg = "{}Url: {} Expected status".format(msg, resp.url)
            assert_equal(resp.status_code, expected_status, msg)

    @staticmethod
    def  _get_url(session, uri):
        """
        Helper method to get the full url
        """
        url = session.url
        if uri:
            slash = '' if uri.startswith('/') else '/'
            url = "%s%s%s" % (session.url, slash, uri)
        return url

    def _get_timeout(self, timeout):
        return float(timeout) if timeout is not None else self.timeout

    def _capture_output(self):
        if self.debug >= 1:
            self.http_log = WritableObject()
            sys.stdout = self.http_log

    def _print_debug(self):
        if self.debug >= 1:
            sys.stdout = sys.__stdout__  # Restore stdout
            if PY3:
                debug_info = ''.join(
                    self.http_log.content).replace(
                    '\\r',
                    '').replace(
                    '\'',
                    '')
            else:
                debug_info = ''.join(
                    self.http_log.content).replace(
                    '\\r',
                    '').decode('string_escape').replace(
                    '\'',
                    '')

            # Remove empty lines
            debug_info = "\n".join(
                [ll.rstrip() for ll in debug_info.splitlines() if ll.strip()])
            logger.debug(debug_info)
