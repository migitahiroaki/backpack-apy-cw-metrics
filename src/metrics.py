from typing import Any

import boto3
import logging

from src.types.app_environment import AppEnvironment


logger = logging.getLogger(__name__)


class MetricsClientWrapper:
    """CloudWatchメトリクスの構築と送信を担当するAWS SDK ラッパークラス"""

    def __init__(self, env: AppEnvironment):
        """借入・貸出データからCloudWatchメトリクスデータを構築"""
        self._env = env
        self._client = boto3.client("cloudwatch")

    def send_metrics(
        self, borrow_rates: dict[str, float], lend_rates: dict[str, float]
    ):
        """CloudWatchにメトリクスデータを送信"""

        # キーが重複する可能性があるので、シンボルごとにBorrowRateとLendRateを分けてメトリクスデータを構築
        metrics_data: list = []
        for symbol, rate in borrow_rates.items():
            metrics_data.append(
                {
                    "MetricName": "BorrowRate",
                    "Dimensions": [{"Name": "Currency", "Value": symbol}],
                    "Value": rate * 100,  # パーセント表記に変換
                    "Unit": "Percent",
                }
            )
        for symbol, rate in lend_rates.items():
            metrics_data.append(
                {
                    "MetricName": "LendRate",
                    "Dimensions": [{"Name": "Currency", "Value": symbol}],
                    "Value": rate * 100,  # パーセント表記に変換
                    "Unit": "Percent",
                }
            )

        # CloudWatchにメトリクスデータを送信
        logger.info("CloudWatchにメトリクスを送信します。")
        return self._client.put_metric_data(
            Namespace=self._env["metrics_namespace"], MetricData=metrics_data
        )
