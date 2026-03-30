import json
import logging
import urllib.request

from src.types.app_environment import AppEnvironment
from src.types.backpack_models import BorrowLendRatesResponse


logger = logging.getLogger(__name__)


class BorrowLendRatesWrapper:
    def __init__(self, env: AppEnvironment):
        """Backpack APIから借入・貸出データを取得してオブジェクトに変換"""
        self._env: AppEnvironment = env
        self._data: BorrowLendRatesResponse | None = None
        with urllib.request.urlopen(self._env["api_url"]) as res:
            response_body = res.read().decode()
            logger.info("Backpack API response body: %s", response_body)
            raw_data = json.loads(response_body)
            self._data = BorrowLendRatesResponse.from_dict(raw_data)

    def lend_rates(self) -> dict[str, float]:
        """シンボル から 貸出金利 を索引する dictを返す。 例: {"BTC": 0.01, "ETH": 0.02}"""

        targets: list[str] = self._env["lend_targets"]

        if self._data is None:
            raise ValueError("APIからのデータが初期化されていません。")

        symbol_to_rate: dict[str, float] = {}
        for item in self._data.borrow_lend:
            if item.symbol in targets:
                symbol_to_rate[item.symbol] = item.lend_rate

        # ターゲットが指定されてるのに該当するレートが取得できない場合はエラーにする
        if len(targets) > 0 and not symbol_to_rate:
            raise ValueError(
                f"指定したシンボル {targets} と一致する貸出レートが取得できませんでした。"
            )
        return symbol_to_rate

    def borrow_rates(self) -> dict[str, float]:
        """シンボルから 借入金利 を索引する dictを返す 例: {"USDC": 0.02, "USDT": 0.03}"""

        targets: list[str] = self._env["borrow_targets"]

        if self._data is None:
            raise ValueError("APIからのデータが初期化されていません。")

        symbol_to_rate: dict[str, float] = {}
        for item in self._data.borrow_lend:
            if item.symbol in targets:
                symbol_to_rate[item.symbol] = item.borrow_rate

        # ターゲットが指定されてるのに該当するレートが取得できない場合はエラーにする
        if len(targets) > 0 and not symbol_to_rate:
            raise ValueError(
                f"指定したシンボル {targets} と一致する借入レートが取得できませんでした。"
            )
        return symbol_to_rate
