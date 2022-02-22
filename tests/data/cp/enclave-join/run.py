"""run module."""

from pathlib import Path
from typing import Dict, List

import pandas as pd

from cosmian_lib_sgx import InputData, KeyInfo, OutputData, Side, parse_args

from merge import merge_all


def main() -> int:
    """Entrypoint of your code."""
    root_path: Path = Path(__file__).parent.parent.absolute()
    keys: Dict[Side, List[KeyInfo]] = parse_args()

    input_data: InputData = InputData(
        root_path=root_path,
        keys=keys
    )
    output_data: OutputData = OutputData(
        root_path=root_path,
        keys=keys
    )

    dataframe: pd.DataFrame = merge_all(datas=input_data.read(), on="siren", sep=";")
    result: bytes = dataframe.to_csv(index=False, sep=";").encode("utf-8")
    output_data.write(result)

    return 0


if __name__ == "__main__":
    main()
