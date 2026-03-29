import json
import urllib.request
import boto3
import os
import logging

# ロガーの設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# クライアントの初期化(毎回キャッシュはしないようにhandler外で初期化)
cw = boto3.client("cloudwatch")


def lambda_handler(event, context):
    # 1. 環境変数の取得とバリデーション
    borrow_raw = os.environ.get("BORROW_SYMBOLS", "").strip()
    lend_raw = os.environ.get("LEND_SYMBOLS", "").strip()

    if not borrow_raw and not lend_raw:
        msg = "環境変数 'BORROW_SYMBOLS' と 'LEND_SYMBOLS' が両方空です。"
        logger.error(msg)
        raise ValueError(msg)

    borrow_targets = [s.strip() for s in borrow_raw.split(",") if s.strip()]
    lend_targets = [s.strip() for s in lend_raw.split(",") if s.strip()]

    url = "https://api.backpack.exchange/api/v1/borrowLend/apy"

    try:
        logger.info(f"Fetching data from {url}")

        # 2. API実行 (ブロッキング)
        with urllib.request.urlopen(url) as res:
            data = json.loads(res.read().decode())

        borrow_lend_data = data.get("borrowLend", [])
        metric_data = []

        # 3. メトリクスの組み立て
        for item in borrow_lend_data:
            symbol = item["symbol"]

            # 借入金利 (Borrow Rate)
            if symbol in borrow_targets:
                val = float(item["borrowRate"]) * 100
                logger.info(f"Target Found (Borrow): {symbol} = {val}%")
                metric_data.append(
                    {
                        "MetricName": "BorrowRate",
                        "Dimensions": [{"Name": "Currency", "Value": symbol}],
                        "Value": val,
                        "Unit": "Percent",
                    }
                )

            # 貸出金利 (Lend Rate)
            if symbol in lend_targets:
                val = float(item["lendRate"]) * 100
                logger.info(f"Target Found (Lend): {symbol} = {val}%")
                metric_data.append(
                    {
                        "MetricName": "LendRate",
                        "Dimensions": [{"Name": "Currency", "Value": symbol}],
                        "Value": val,
                        "Unit": "Percent",
                    }
                )

        # 4. CloudWatchへ送信
        if metric_data:
            logger.info(f"Sending {len(metric_data)} metrics to CloudWatch...")
            cw.put_metric_data(Namespace="Backpack/Lending", MetricData=metric_data)
            return {"status": "success", "metrics_sent": len(metric_data)}

        logger.warning("No matching symbols found in the API response.")
        return {"status": "no_match"}

    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        raise e
