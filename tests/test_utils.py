from utils import request_to_event


def test_request_to_event():
    path = "/"
    method = "POST"
    qs = {}
    body = "BODY"
    headers = {'Host': "example.org", "Connection": "keep-alive"}
    event = request_to_event(path, method, qs, body, headers)
    assert event == {
        'body': body,
        'resource': "/{proxy+}",
        'path': path,
        'httpMethod': method,
        'isBase64Encoded': False,
        'headers': headers,
        'queryStringParameters': qs,
    }
