"""CSV Join with Cosmian Confidential Microservice."""

from io import BytesIO
from pathlib import Path
from typing import Iterator

import pandas as pd

from cosmian_lib.sgx import KeyInfo, InputData, OutputData, parse_args


def merge_all(datas: Iterator[BytesIO], on: str, sep: str = ";") -> pd.DataFrame:
    content: BytesIO = next(files)
    dataframe: pd.DataFrame = pd.read_csv(content, sep=sep)

    for data in datas:  # type: BytesIO
        df: pd.DataFrame = pd.read_csv(data, sep=sep)

        dataframe: pd.DataFrame = pd.merge(
            dataframe,
            df,
            how="inner",
            on=on
        )

    return dataframe


def main() -> int:
    root_path: Path = Path(__file__).parent.absolute()
    keys: Dict[Side, List[KeyInfo]] = parse_args()

    input: InputData = InputData(
        root_path=root_path,
        keys=keys
    )
    output: OutputData = OutputData(
        root_path=root_path,
        keys=keys
    )

    df: pd.DataFrame = merge_all(datas=input.read(), on="siren", sep=";")
    output.write(df.to_csv(index=False, sep=";").encode("utf-8"))

    return 0


if __name__ == "__main__":
    main()
