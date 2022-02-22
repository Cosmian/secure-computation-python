"""merge module."""

from io import BytesIO
from typing import Iterator

import pandas as pd


def merge_all(datas: Iterator[BytesIO], on: str, sep: str = ";") -> pd.DataFrame:
    """Inner join of CSV files in `datas`."""
    try:
        content: BytesIO = next(datas)
        dataframe: pd.DataFrame = pd.read_csv(content, sep=sep)
    except StopIteration as exc:
        raise Exception("No input data!") from exc

    for data in datas:  # type: BytesIO
        df: pd.DataFrame = pd.read_csv(data, sep=sep)

        dataframe: pd.DataFrame = pd.merge(
            dataframe,
            df,
            how="inner",
            on=on
        )

    return dataframe
