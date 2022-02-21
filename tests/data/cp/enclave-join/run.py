"""CSV Join with Cosmian Secure Computation."""

from pathlib import Path
from typing import Iterator, Dict, List

import pandas as pd

from cosmian_lib_sgx import InputData, KeyInfo, OutputData, Side, parse_args

from merge import merge_all


def main() -> int:
    root_path: Path = Path(__file__).parent.parent.absolute()
    keys: Dict[Side, List[KeyInfo]] = parse_args()

    input: InputData = InputData(
        root_path=root_path,
        keys=keys,
        debug=False if keys else True
    )
    output: OutputData = OutputData(
        root_path=root_path,
        keys=keys,
        debug=False if keys else True
    )

    df: pd.DataFrame = merge_all(datas=input.read(), on="siren", sep=";")
    output.write(df.to_csv(index=False, sep=";").encode("utf-8"))

    return 0


if __name__ == "__main__":
    main()
