from typing import TypedDict


class AppEnvironment(TypedDict):
    """アプリケーションの環境変数をマップ後のオブジェクト"""

    # 借入対象
    borrow_targets: list[str]
    # 貸出対象
    lend_targets: list[str]

    # backpack API エンドポイント
    api_url: str

    # メトリクス名前空間
    metrics_namespace: str
