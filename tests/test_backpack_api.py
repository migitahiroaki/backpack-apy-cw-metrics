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
                    {
                        "borrowRate": "0.0247598127681745707458618837",
                        "lendRate": "0.0091190938836865249343561863",
                        "symbol": "ETH",
                    },
                    {
                        "borrowRate": "0.0235064381205238674430117829",
                        "lendRate": "0.0082192204175710125387631955",
                        "symbol": "SOL",
                    },
                    {
                        "borrowRate": "0.0274873778949264731378605522",
                        "lendRate": "0.0064222255200771863327465163",
                        "symbol": "DOGE",
                    },
                    {
                        "borrowRate": "0.050280184674322377107839855",
                        "lendRate": "0.0153491601803669172872381915",
                        "symbol": "SUI",
                    },
                    {
                        "borrowRate": "0.0332512249491371022806041114",
                        "lendRate": "0.0093979736652540003662562596",
                        "symbol": "APT",
                    },
                    {
                        "borrowRate": "0.0017841724130169212726058632",
                        "lendRate": "0.0000473511590906380246302222",
                        "symbol": "BTC",
                    },
                    {
                        "borrowRate": "0.0318802345448612641913056069",
                        "lendRate": "0.008638969514400606722656216",
                        "symbol": "SEI",
                    },
                    {
                        "borrowRate": "0.0071447095301617889474294842",
                        "lendRate": "0.0004338984312982698732375402",
                        "symbol": "XRP",
                    },
                    {
                        "borrowRate": "0.0014740893971417280573973555",
                        "lendRate": "0.000015831416727006975197149",
                        "symbol": "XPL",
                    },
                    {
                        "borrowRate": "0.0181905068019192608852231107",
                        "lendRate": "0.0028126035705407026191529355",
                        "symbol": "BNB",
                    },
                    {
                        "borrowRate": "0.009716202191201484418155475",
                        "lendRate": "0.0006878048337193906979623998",
                        "symbol": "MON",
                    },
                    {
                        "borrowRate": "0.0147795059937032217109988889",
                        "lendRate": "0.0024500479378542939102090899",
                        "symbol": "USDC",
                    },
                    {
                        "borrowRate": "0.0247982963071636642533806285",
                        "lendRate": "0.0079626205291676812835899496",
                        "symbol": "USDT",
                    },
                    {
                        "borrowRate": "0.0017090875897074934855080617",
                        "lendRate": "0.0000248283333089834415342177",
                        "symbol": "HYPE",
                    },
                ],
                "staking": [
                    {
                        "dilutionFactor": "0.2086672",
                        "stakingRate": "0.03355914",
                        "symbol": "MON",
                    },
                    {
                        "dilutionFactor": "0.68390682",
                        "stakingRate": "0.0440436",
                        "symbol": "SOL",
                    },
                    {
                        "dilutionFactor": "0.94669436",
                        "stakingRate": "0.03786777",
                        "symbol": "USDC",
                    },
                ],
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
    assert 0.0147795059937032217109988889 == api_rapped_result.borrow_rates().get(
        "USDC"
    )
    # 貸出レートの検証
    assert 2 == len(api_rapped_result.lend_rates())
    assert 0.0000473511590906380246302222 == api_rapped_result.lend_rates().get("BTC")
    assert 0.0091190938836865249343561863 == api_rapped_result.lend_rates().get("ETH")


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
