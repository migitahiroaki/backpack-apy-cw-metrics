from typing import Generator

import pytest
import json
from unittest.mock import patch, mock_open
from src.backpack_api import BorrowLendRatesWrapper
from src.types.app_environment import AppEnvironment


@pytest.fixture()
def mock_api() -> Generator:
    """Backpack APIのレスポンスをモック化"""
    with patch("urllib.request.urlopen") as mock_urlopen:
        # モックレスポンス

        # レスポンスデータはencodedなので、dictをjson.dumpsしてからencodeする
        mock_response_data = json.dumps(
            {
                "borrowLend": [
                    {"symbol": "BTC", "borrowRate": "0.03", "lendRate": "0.011"},
                    {"symbol": "ETH", "borrowRate": "0.04", "lendRate": "0.028"},
                    {"symbol": "USDC", "borrowRate": "0.02", "lendRate": "0.015"},
                ]
            }
        ).encode("utf-8")

        mock_response = mock_open(read_data=mock_response_data).return_value
        mock_urlopen.return_value.__enter__.return_value = mock_response
        yield mock_urlopen


def test_fetch_success(mock_api) -> None:
    """APIからのデータ取得とパースが成功するケース"""
    api_rapped_result: BorrowLendRatesWrapper = BorrowLendRatesWrapper(
        AppEnvironment(
            borrow_targets=["USDC"],
            lend_targets=["BTC", "ETH"],
            api_url="http://localhost",  # モック化するので関係ない
            metrics_namespace="dummy",  # ダミー値
        )
    )

    mock_api.assert_called_once()
    # 借入レートの検証
    assert 1 == len(api_rapped_result.borrow_rates())
    assert 0.02 == api_rapped_result.borrow_rates().get("USDC")
    # 貸出レートの検証
    assert 2 == len(api_rapped_result.lend_rates())
    assert 0.011 == api_rapped_result.lend_rates().get("BTC")
    assert 0.028 == api_rapped_result.lend_rates().get("ETH")


def test_fetch_symbols_do_not_match(mock_api) -> None:
    """APIレスポンスに指定したシンボルがないケース"""
    api_rapped_result: BorrowLendRatesWrapper = BorrowLendRatesWrapper(
        AppEnvironment(
            borrow_targets=["DAI"],  # レスポンスにないシンボル
            lend_targets=["XRP"],  # レスポンスにないシンボル
            api_url="http://localhost",  # モック化するので関係ない
            metrics_namespace="dummy",  # ダミー値
        )
    )

    mock_api.assert_called_once()
    # ValueErrorが発生することを検証
    with pytest.raises(ValueError):
        api_rapped_result.borrow_rates()
    with pytest.raises(ValueError):
        api_rapped_result.lend_rates()


def test_fetch_no_symbols_specified(mock_api) -> None:
    """APIレスポンスに指定したシンボルがないケース"""
    api_rapped_result: BorrowLendRatesWrapper = BorrowLendRatesWrapper(
        AppEnvironment(
            borrow_targets=[],  # 指定なし
            lend_targets=[],  # 指定なし
            api_url="http://localhost",  # モック化するので関係ない
            metrics_namespace="dummy",  # ダミー値
        )
    )
    with pytest.raises(ValueError):
        api_rapped_result.borrow_rates()
    with pytest.raises(ValueError):
        api_rapped_result.lend_rates()


def test_fetch_api_error_response(mock_api) -> None:
    """APIからエラーレスポンスが返るケース"""
    # APIがエラーを返すようにモックを設定
    mock_api.return_value.__enter__.return_value.read.return_value = json.dumps(
        {"error": "Internal Server Error"}
    ).encode("utf-8")

    with pytest.raises(ValueError):
        BorrowLendRatesWrapper(
            AppEnvironment(
                borrow_targets=["USDC"],
                lend_targets=["BTC", "ETH"],
                api_url="http://localhost",  # モック化するので関係ない
                metrics_namespace="dummy",  # ダミー値
            )
        )


def test_fetch_api_invalid_json(mock_api) -> None:
    """APIから期待してない構造のJSONが返るケース"""
    # APIが無効なJSONを返すようにモックを設定
    mock_api.return_value.__enter__.return_value.read.return_value = b"invalid json"

    with pytest.raises(json.JSONDecodeError):
        BorrowLendRatesWrapper(
            AppEnvironment(
                borrow_targets=["USDC"],
                lend_targets=["BTC", "ETH"],
                api_url="http://localhost",  # モック化するので関係ない
                metrics_namespace="dummy",  # ダミー値
            )
        )
