import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from lambda_22128867.canary import canary




import canary
import pytest
from unittest.mock import patch, MagicMock

def test_check_page_load_success():
    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_urlopen.return_value = mock_response

        status_code, page_loaded, tti = canary.check_page_load("https://www.bbc.com/")
        assert status_code == 200
        assert page_loaded == 1
        assert tti >= 0

def test_check_page_load_failure():
    with patch('urllib.request.urlopen', side_effect=Exception("Network error")):
        status_code, page_loaded, tti = canary.check_page_load("https://www.bbc.com/")
        assert status_code == 0
        assert page_loaded == 0
        assert tti == 0

@patch('canary.cloudwatch.put_metric_data')
def test_put_metrics_success(mock_put_metric_data):
    canary.put_metrics("https://www.bbc.com/", latency=0.1, page_loaded=1, tti=0.05)
    mock_put_metric_data.assert_called_once()

@patch('canary.sns.publish')
def test_send_alert_success(mock_sns_publish):
    canary.send_alert("arn:aws:sns:region:123456789012:topic", "https://www.bbc.com/")
    mock_sns_publish.assert_called_once()

@patch('canary.check_page_load', return_value=(200, 1, 0.1))
@patch('canary.put_metrics')
@patch('canary.send_alert')
def test_lambda_handler_success(mock_send_alert, mock_put_metrics, mock_check_page_load):
    event = {}
    context = {}
    response = canary.lambda_handler(event, context)
    assert response['statusCode'] == 200
    assert response['page_loaded'] == 1
    mock_put_metrics.assert_called_once()
    mock_send_alert.assert_not_called()

@patch('canary.check_page_load', return_value=(0, 0, 0))
@patch('canary.put_metrics')
@patch('canary.send_alert')
def test_lambda_handler_failure(mock_send_alert, mock_put_metrics, mock_check_page_load):
    event = {}
    context = {}
    with pytest.raises(Exception):
        canary.lambda_handler(event, context)
    mock_put_metrics.assert_called_once()
    mock_send_alert.assert_called_once()
