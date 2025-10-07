import os
import sys
import types
import boto3
import pytest
from moto import mock_sns
from unittest.mock import patch

if sys.platform == "win32":
    fake_resource = types.SimpleNamespace()
    fake_resource.RUSAGE_SELF = 0

    def fake_getrusage(who):
        return types.SimpleNamespace(ru_maxrss=123456) 
    fake_resource.getrusage = fake_getrusage
    sys.modules['resource'] = fake_resource


import canary

REGION = "ap-southeast-2"

@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = REGION


@pytest.fixture(scope="function")
def sns_client(aws_credentials):
    with mock_sns():
        client = boto3.client("sns", region_name=REGION)
        yield client


@pytest.fixture(scope="function")
def sns_topic(sns_client):
    response = sns_client.create_topic(Name="test-topic")
    return response["TopicArn"]


@pytest.fixture(autouse=True)
def set_env_vars(sns_topic):
    os.environ["ALERT_TOPIC_ARN"] = sns_topic
    os.environ["TARGET_URL"] = "https://www.bbc.com/"
    canary.ALERT_TOPIC_ARN = sns_topic
    canary.TARGET_URL = "https://www.bbc.com/"
    yield
    del os.environ["ALERT_TOPIC_ARN"]
    del os.environ["TARGET_URL"]


@patch("canary.cloudwatch.put_metric_data")
def test_lambda_handler_success(mock_put_metric):
    event = {}
    context = {}

    with mock_sns():
        response = canary.lambda_handler(event, context)

    assert response["page_loaded"] == 1
    assert "latency" in response
    assert "time_to_interactive" in response
    mock_put_metric.assert_called_once()


@patch("canary.cloudwatch.put_metric_data")
@patch("canary.sns.publish")
def test_lambda_handler_failure_triggers_alert(mock_sns_publish, mock_put_metric):
    def fail_load(url, timeout=10):
        return 0, 0, 0  

    with mock_sns():
        with patch("canary.check_page_load", side_effect=fail_load):
            with pytest.raises(Exception) as exc_info:
                canary.lambda_handler({}, {})

    assert "Page load failed" in str(exc_info.value)
    mock_put_metric.assert_called_once()
    mock_sns_publish.assert_called_once()

    args, kwargs = mock_sns_publish.call_args
    assert kwargs["TopicArn"] == canary.ALERT_TOPIC_ARN
    assert "could NOT be loaded" in kwargs["Message"]
