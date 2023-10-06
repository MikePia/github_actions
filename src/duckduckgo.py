# Original attribution here - http://pypi.python.org/pypi/duckduckgo2/0.2

import urllib
from urllib.request import urlopen
from urllib.parse import urlencode
import json as j
import sys

__version__ = 0.2


def query(
    query,
    useragent="python-duckduckgo " + str(__version__),
    safesearch=True,
    html=False,
    **kwargs
):
    """
    Query DuckDuckGo, returning a Results object.

    Here's a query that's unlikely to change:

    >>> result = query('1 + 1')
    >>> result.type
    'nothing'
    >>> result.answer.text
    '1 + 1 = 2'
    >>> result.answer.type
    'calc'

    Keword arguments:
    useragent: UserAgent to use while querying. Default: "python-duckduckgo %d" (str)
    safesearch: True for on, False for off. Default: True (bool)
    html: True to allow HTML in output. Default: False (bool)
    Any other keyword arguments are passed directly to DuckDuckGo as URL params.
    """ % __version__

    safesearch = "1" if safesearch else "-1"
    html = "0" if html else "1"
    params = {
        "q": query,
        "o": "json",
        "kp": safesearch,
        "no_redirect": "1",
        "no_html": html,
    }
    params.update(kwargs)
    encparams = urlencode(params)
    url = "http://duckduckgo.com/?" + encparams

    request = urllib.request.Request(url, headers={"User-Agent": useragent})
    response = urlopen(request)
    encoding = response.headers.get_content_charset()
    response_body = response.readall().decode(encoding)
    json = j.loads(response_body)
    response.close()

    return Results(json)


class Results(object):
    def __init__(self, json):
        self.type = {
            "A": "answer",
            "D": "disambiguation",
            "C": "category",
            "N": "name",
            "E": "exclusive",
            "": "nothing",
        }[json.get("Type", "")]

        self.json = json
        self.api_version = None  # compat

        self.heading = json.get("Heading", "")

        self.results = [Result(elem) for elem in json.get("Results", [])]
        self.related = [Result(elem) for elem in json.get("RelatedTopics", [])]

        self.abstract = Abstract(json)
        self.redirect = Redirect(json)
        self.definition = Definition(json)
        self.answer = Answer(json)

        self.image = Image({"Result": json.get("Image", "")})


class Abstract(object):
    def __init__(self, json):
        self.html = json.get("Abstract", "")
        self.text = json.get("AbstractText", "")
        self.url = json.get("AbstractURL", "")
        self.source = json.get("AbstractSource")


class Redirect(object):
    def __init__(self, json):
        self.url = json.get("Redirect", "")


class Result(object):
    def __init__(self, json):
        self.topics = json.get("Topics", [])
        if self.topics:
            self.topics = [Result(t) for t in self.topics]
            return
        self.html = json.get("Result")
        self.text = json.get("Text")
        self.url = json.get("FirstURL")

        icon_json = json.get("Icon")
        if icon_json is not None:
            self.icon = Image(icon_json)
        else:
            self.icon = None


class Image(object):
    def __init__(self, json):
        self.url = json.get("Result")
        self.height = json.get("Height", None)
        self.width = json.get("Width", None)


class Answer(object):
    def __init__(self, json):
        self.text = json.get("Answer")
        self.type = json.get("AnswerType", "")


class Definition(object):
    def __init__(self, json):
        self.text = json.get("Definition", "")
        self.url = json.get("DefinitionURL")
        self.source = json.get("DefinitionSource")


def main():
    if len(sys.argv) > 1:
        q = query(" ".join(sys.argv[1:]))
        keys = q.json.keys()
        keys.sort()
        for key in keys:
            sys.stdout.write(key)
            if type(q.json[key]) in [str, unicode]:
                print(":", q.json[key])
            else:
                sys.stdout.write("\n")
                for i in q.json[key]:
                    print("\t", i)
    else:
        print("Usage: %s [query]" % sys.argv[0])
