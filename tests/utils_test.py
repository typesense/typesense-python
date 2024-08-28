from src.typesense.utils import encodeURIComponent


def test_encode_URI():
    encoded = encodeURIComponent("abc123:/ ?&+=_-|#$@^*()~")
    assert encoded == "abc123%3A%2F%20%3F%26%2B%3D_-%7C%23%24%40%5E*()~"
