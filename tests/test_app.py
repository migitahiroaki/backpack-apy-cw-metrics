import pytest
import os
from unittest.mock import patch
from src.app import lambda_handler


class TestLambdaHandler:
    @patch("src.app.send_metrics_to_cloudwatch")
    @patch("src.app.build_metric_data")
    @patch("src.app.fetch_borrow_lend_data")
    @patch("src.app.get_targets")
    def test_lambda_handler_success(
        self, mock_get_targets, mock_fetch, mock_build, mock_send
    ):
        # モック設定
        mock_get_targets.return_value = (["BTC"], ["USDC"])
        mock_fetch.return_value = [
            {"symbol": "BTC", "borrowRate": "0.01", "lendRate": "0.005"}
        ]
        mock_build.return_value = [{"MetricName": "BorrowRate", "Value": 1.0}]
        mock_send.return_value = {"status": "success", "metrics_sent": 1}

        # 環境変数設定
        os.environ["BORROW_SYMBOLS"] = "BTC"
        os.environ["LEND_SYMBOLS"] = "USDC"

        event = {}
        context = {}

        result = lambda_handler(event, context)

        assert result == {"status": "success", "metrics_sent": 1}
        mock_get_targets.assert_called_once()
        mock_fetch.assert_called_once()
        mock_build.assert_called_once_with(
            [{"symbol": "BTC", "borrowRate": "0.01", "lendRate": "0.005"}],
            ["BTC"],
            ["USDC"],
        )
        mock_send.assert_called_once_with([{"MetricName": "BorrowRate", "Value": 1.0}])

    @patch("src.app.get_targets")
    def test_lambda_handler_config_error(self, mock_get_targets):
        mock_get_targets.side_effect = ValueError("Config error")

        os.environ["BORROW_SYMBOLS"] = ""
        os.environ["LEND_SYMBOLS"] = ""

        event = {}
        context = {}

        with pytest.raises(ValueError, match="Config error"):
            lambda_handler(event, context)
