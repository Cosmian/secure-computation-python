from io import BytesIO
from typing import Iterator

import pandas as pd


def merge_all(datas: Iterator[BytesIO], on: str, sep: str = ";") -> pd.DataFrame:
    try:
        content: BytesIO = next(datas)
        dataframe: pd.DataFrame = pd.read_csv(content, sep=sep)
    except StopIteration:
        raise Exception("No input data!")

    for data in datas:  # type: BytesIO
        df: pd.DataFrame = pd.read_csv(data, sep=sep)

        dataframe: pd.DataFrame = pd.merge(
            dataframe,
            df,
            how="inner",
            on=on
        )

    return dataframe
