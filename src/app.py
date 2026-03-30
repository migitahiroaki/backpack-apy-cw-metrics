import logging
from src.env import Env
from src.backpack_api import BorrowLendRatesWrapper
from src.metrics import MetricsClientWrapper
from src.types.app_environment import AppEnvironment


# ロガーの設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context) -> None:
    """AWS Lambdaのエントリポイント。環境変数の読み込み、APIからのデータ取得、CloudWatchへのメトリクス送信を行う。"""

    # 環境変数の読み込みと検証
    env: AppEnvironment = Env().app_env

    # Backpack APIからデータ取得しインスタンス化
    api_wrapper: BorrowLendRatesWrapper = BorrowLendRatesWrapper(env)
    borrow_rates: dict[str, float] = api_wrapper.borrow_rates()
    lend_rates: dict[str, float] = api_wrapper.lend_rates()

    # CloudWatchにメトリクスを送信
    metrics_client = MetricsClientWrapper(env)
    metrics_client.send_metrics(borrow_rates, lend_rates)
