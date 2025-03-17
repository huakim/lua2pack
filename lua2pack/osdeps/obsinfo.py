import random
import string
import time
from requests.adapters import BaseAdapter
from requests import Response, codes
import locale
import re
from io import BytesIO


def generate_random_hex(length=40):
    """
    Generate a random hex string of the specified length.

    Args:
        length (int): The desired length of the hex string. Default is 40.

    Returns:
        str: A random hex string of the specified length.
    """
    # Define the characters to use for the hex string
    hex_chars = string.hexdigits

    # Generate a list of random hex characters
    random_chars = [random.choice(hex_chars) for _ in range(length)]

    # Join the random characters into a string
    random_hex = "".join(random_chars)

    return random_hex.lower()


def lua_code(args):
    st = ("""
filename = package .. '.obsinfo'
""" if args.template == "obs.obsinfo" else "" )
    return st + """
mtime = __get_current_timestamp()
commit = __random_hex_numbers()
"""


ObsInfoAdapterRegex = re.compile(r"(^[A-Za-z][A-Za-z0-9]*)\s*:\s*(.*)")


class ObsInfoAdapter(BaseAdapter):
    def __init__(self, adapter, set_content_length=True):
        super(ObsInfoAdapter, self).__init__()
        self.adapter = adapter
        self._set_content_length = set_content_length

    @staticmethod
    def convert_to_rockspec(text):
        text_pieces = []
        for i in text.split("\n"):
            if i and not i.isspace():
                match = ObsInfoAdapterRegex.match(i)
                if not match:
                    return text
                text_pieces.append(match)
        text = ""
        for i in text_pieces:
            text = text + i.group(1) + "=" + repr(i.group(2).strip()) + "\n"
        return text

    def send(self, request, **kwargs):
        """Wraps a file, described in request, in a Response object.

        :param request: The PreparedRequest` being "sent".
        :returns: a Response object containing the file
        """
        adapter = self.adapter
        # Check that the method makes sense. Only support GET
        if request.method not in ("GET", "HEAD"):
            raise ValueError("Invalid request method %s" % request.method)
        url = request.url
        e = url[(url.find("://") + 3) :]
        e = adapter.read_rockspec_file(e)
        e = ObsInfoAdapter.convert_to_rockspec(e)
        resp = Response()
        resp.request = request
        resp_str = str(e).encode(locale.getpreferredencoding(False))
        raw = BytesIO(resp_str)
        resp.raw = raw
        if self._set_content_length:
            resp.headers["Content-Length"] = len(resp_str)

        # Add release_conn to the BytesIO object
        raw.release_conn = raw.close
        resp.status_code = codes.ok
        resp.url = url

        return resp

    def close(self):
        pass


def mount_adapter(adapter):
    adapter.session.mount("obsinfo://", ObsInfoAdapter(adapter))


def generate_timestamp():
    return int(time.time())


def update_globals():
    return {
        "__random_hex_numbers": generate_random_hex,
        "__get_current_timestamp": generate_timestamp,
    }
