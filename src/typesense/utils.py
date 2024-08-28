from urllib.parse import quote


def encodeURIComponent(string):
    return quote(string, safe="~()*!'")
