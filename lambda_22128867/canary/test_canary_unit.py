import sys
import types
import pytest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError


if sys.platform == "win32":
    fake_resource = types.SimpleNamespace()
    fake_resource.RUSAGE_SELF = 0

    def fake_getrusage(who):
        return types.SimpleNamespace(ru_maxrss=123456)

    fake_resource.getrusage = fake_getrusage
    sys.modules['resource'] = fake_resource


import canary

TEST_URLS = [
    "https://www.smh.com.au/",
    "https://www.bbc.com/",
    "https://www.nytimes.com/"
]

@pytest.mark.parametrize("url", TEST_URLS)
@patch("canary.urllib.request.urlopen")
def test_check_page_load_success(mock_urlopen, url):
    mock_response = MagicMock()
    mock_response.getcode.return_value = 200
    mock_urlopen.return_value = mock_response

    code, loaded, tti = canary.check_page_load(url)
    assert code == 200
    assert loaded == 1
    assert tti >= 0  


@pytest.mark.parametrize("url", TEST_URLS)
@patch("canary.urllib.request.urlopen", side_effect=Exception("Timeout"))
def test_check_page_load_failure(mock_urlopen, url):
    code, loaded, tti = canary.check_page_load(url)
    assert code == 0
    assert loaded == 0
    assert tti == 0


@patch("canary.cloudwatch.put_metric_data")
def test_put_metrics_success(mock_put):

    canary.put_metrics(TEST_URLS[0], 0.5, 1, 0.2, 123.4, 0.3)
    mock_put.assert_called_once()


@patch("canary.cloudwatch.put_metric_data", side_effect=ClientError(
    error_response={'Error': {'Code': '500', 'Message': 'CW Error'}},
    operation_name='PutMetricData'
))
def test_put_metrics_failure(mock_put):
  
    canary.put_metrics(TEST_URLS[1], 0.5, 1, 0.2, 123.4, 0.3)


@patch("canary.sns.publish")
def test_send_alert_success(mock_publish):
    canary.send_alert("arn:aws:sns:ap-southeast-2:123456789012:test", TEST_URLS[2])
    mock_publish.assert_called_once()


@patch("canary.sns.publish", side_effect=ClientError(
    error_response={'Error': {'Code': '500', 'Message': 'SNS Error'}},
    operation_name='Publish'
))
def test_send_alert_failure(mock_publish):
    canary.send_alert("arn:aws:sns:ap-southeast-2:123456789012:test", TEST_URLS[2])
