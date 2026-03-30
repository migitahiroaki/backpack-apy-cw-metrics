from typing import Generator

import boto3
from mypy_boto3_cloudwatch import CloudWatchClient
import pytest
from moto import mock_aws
from src.metrics import MetricsClientWrapper
from src.types.app_environment import AppEnvironment


@pytest.fixture(scope="module", autouse=True)
def mocked_client():
    with mock_aws():
        client: CloudWatchClient = boto3.client("cloudwatch")
        yield client


@pytest.fixture()
def env() -> Generator:
    yield AppEnvironment(
        borrow_targets=["BTC", "SOL"],
        lend_targets=["USDC"],
        api_url="http://localhost",  # ダミー値
        metrics_namespace="TestNamespace",
    )


def test_send_metrics_to_cloudwatch(mocked_client, env) -> None:
    """CloudWatchにメトリクスデータが送信されることを検証"""
    metrics_client = MetricsClientWrapper(env)
    borrow_rates = {"BTC": 0.01, "SOL": 0.02}
    lend_rates = {"USDC": 0.005}

    # CloudWatchにメトリクスデータを送信
    metrics_client.send_metrics(borrow_rates, lend_rates)

    # モックされたCloudWatchクライアントから送信されたデータを検証
    response = mocked_client.list_metrics(Namespace=env["metrics_namespace"])
    metrics = response.get("Metrics", [])

    # BorrowRateとLendRateの両方のメトリクスが送信されていることを検証
    assert any(
        metric["MetricName"] == "BorrowRate"  # type: ignore
        and metric["Dimensions"][0]["Value"] == "BTC"  # type: ignore
        for metric in metrics
    )
    assert any(
        metric["MetricName"] == "BorrowRate"  # type: ignore
        and metric["Dimensions"][0]["Value"] == "SOL"  # type: ignore
        for metric in metrics
    )
    assert any(
        metric["MetricName"] == "LendRate"  # type: ignore
        and metric["Dimensions"][0]["Value"] == "USDC"  # type: ignore
        for metric in metrics
    )
