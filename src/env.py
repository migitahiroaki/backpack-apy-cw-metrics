import os
import logging

from src.types.app_environment import AppEnvironment

logger = logging.getLogger(__name__)


class Env:
    def __init__(self) -> None:
        """環境変数の初期化と検証"""
        # 借入・貸出対象の通貨シンボルを環境変数から取得
        borrow_symbols_raw: str = os.environ.get("BORROW_SYMBOLS", "").strip()
        lend_symbols_raw: str = os.environ.get("LEND_SYMBOLS", "").strip()
        if not borrow_symbols_raw and not lend_symbols_raw:
            msg = "環境変数 'BORROW_SYMBOLS' と 'LEND_SYMBOLS' が両方空です。"
            logger.error(msg)
            raise ValueError(msg)
        # カンマ区切りの文字列をリストに変換し、空要素を除外
        borrow_targets: list[str] = [
            s.strip() for s in borrow_symbols_raw.split(",") if s.strip()
        ]
        lend_targets: list[str] = [
            s.strip() for s in lend_symbols_raw.split(",") if s.strip()
        ]
        if not borrow_targets and not lend_targets:
            msg = f"借入・貸出対象の通貨シンボルが指定されてないか不正です。\n{borrow_targets=}\n{lend_targets=}"
            logger.error(msg)
            raise ValueError(msg)

        # backpack API エンドポイント
        api_url: str = os.environ.get(
            "API_URL", "https://api.backpack.exchange/api/v1/borrowLend/apy"
        )
        if not api_url.startswith("http") and not api_url.startswith("https"):
            msg = f"API_URLが不正です。URLはhttpsまたはhttpで始まる必要があります。{api_url=}"
            logger.error(msg)
            raise ValueError(msg)

        # メトリクス名前空間
        metrics_namespace: str = os.environ.get(
            "CLOUDWATCH_NAMESPACE", "Backpack/Lending"
        )
        if not metrics_namespace:
            msg = f"環境変数 'CLOUDWATCH_NAMESPACE' が不正です。{metrics_namespace=}"
            logger.error(msg)
            raise ValueError(msg)

        self._app_env: AppEnvironment = AppEnvironment(
            borrow_targets=borrow_targets,
            lend_targets=lend_targets,
            api_url=api_url,
            metrics_namespace=metrics_namespace,
        )

    @property
    def app_env(self) -> AppEnvironment:
        """環境変数オブジェクトを取得"""
        return self._app_env
