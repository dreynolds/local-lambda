from lambda_server import convert_response


def test_convert_response():
    BODY = '{}'
    STATUS_CODE = 201
    HEADERS = {'x-test-header': 'abc123'}
    api_gw_resp = {
        'body': BODY,
        'statusCode': STATUS_CODE,
        'headers': HEADERS,
    }
    resp = convert_response(api_gw_resp)

    assert resp.status_code == STATUS_CODE
    assert resp.data.decode('utf-8') == BODY
    for k, v in HEADERS.items():
        assert resp.headers[k] == v
