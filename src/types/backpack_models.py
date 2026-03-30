from dataclasses import dataclass
from typing import Any


@dataclass
class BorrowLendData:
    """backpack API の借入・貸出金利データの構造"""

    symbol: str
    """通貨シンボル"""
    borrow_rate: float
    """借入金利"""
    lend_rate: float
    """貸出金利"""

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "BorrowLendData":
        """生レスポンスから BorrowLendRatesResponse オブジェクトをへ変換"""
        # 数値チェックをして安全にfloatに変換する
        if (borrow_rate := data.get("borrowRate", "")).isdecimal():
            raise ValueError(f"borrowRate is missing in {data=}")
        if (lend_rate := data.get("lendRate", "")).isdecimal():
            raise ValueError(f"lendRate is missing in {data=}")
        return cls(
            symbol=data["symbol"],
            borrow_rate=float(borrow_rate),
            lend_rate=float(lend_rate),
        )


@dataclass
class BorrowLendRatesResponse:
    """backpack API の借入・貸出金利データのレスポンス構造"""

    borrow_lend: list[BorrowLendData]
    """借入・貸出金利のリスト"""
    # staking は使用しないため省略

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BorrowLendRatesResponse":
        """生レスポンスから BorrowLendRatesResponse オブジェクトをへ変換"""

        # borrowLend がlist[dict]になっていて、かつ要素が１つ以上あることをチェック

        if isinstance(borrow_lend := data.get("borrowLend"), list) and len(borrow_lend):
            return cls(
                borrow_lend=[
                    BorrowLendData.from_dict(item)
                    for item in borrow_lend
                    if isinstance(item, dict)  # ここでフィルタリング兼型確定
                ]
            )

        else:
            raise ValueError(f"borrowLendの中身が不正です。 {borrow_lend=}")

    def lend_rates(self, symbols: list[str]) -> dict[str, float]:
        """シンボル -> 貸出金利"""
        symbol_to_rate: dict[str, float] = {}
        for item in self.borrow_lend:
            if item.symbol in symbols:
                symbol_to_rate[item.symbol] = item.lend_rate

        if not symbol_to_rate:
            raise ValueError(
                f"指定したシンボルと一致する貸出レートが取得できませんでした。{symbols=}"
            )
        return symbol_to_rate

    def borrow_rates(self, symbols: list[str]) -> dict[str, float]:
        """シンボル -> 借入金利"""
        symbol_to_rate: dict[str, float] = {}
        for item in self.borrow_lend:
            if item.symbol in symbols:
                symbol_to_rate[item.symbol] = item.borrow_rate

        if not symbol_to_rate:
            raise ValueError(
                f"指定したシンボルと一致する借入レートが取得できませんでした。{symbols=}"
            )
        return symbol_to_rate
