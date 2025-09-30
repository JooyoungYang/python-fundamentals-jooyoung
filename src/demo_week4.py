from __future__ import annotations

import os
from collections import namedtuple
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import Any, ParamSpec, TypedDict, TypeVar

import numpy as np
import pandas as pd
import yaml
from pydantic import BaseModel, Field
from yaml_env_tag import construct_env_tag


# -------------------------------------------------
# (A) Four User data structures
# -------------------------------------------------
class UserTD(TypedDict, total=False):
    # TypedDict: acts like python's dict, but the key and value types are specified as type hints.
    id: int
    name: str
    email: str
    age: int
    is_active: bool
    preferences: dict[str, Any]


UserNT = namedtuple("UserNT", ["id", "name", "email", "age", "is_active", "preferences"])
# namedtuple: kind of tuple. accessable to field's name


@dataclass
# dataclass: automatically creates boilerplate methods for data containers
class UserDC:
    id: int
    name: str
    email: str
    age: int
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    preferences: dict[str, Any] | None = None


class UserModel(BaseModel):
    # Pydantic Basemodel: Runtime data validation and conversion
    id: int = Field(..., gt=0)
    name: str
    email: str
    age: int
    is_active: bool = True
    preferences: dict[str, Any] | None = None


# -------------------------------------------------
# (B) Execution time measurement decorator
# -------------------------------------------------
P = ParamSpec("P")
R = TypeVar("R")


def timeit(func: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        t0 = perf_counter()
        result: R = func(*args, **kwargs)
        dt = (perf_counter() - t0) * 1000.0
        print(f"[timeit] {func.__name__}: {dt:.2f} ms")
        return result

    return wrapper


# -------------------------------------------------
# (C) Performance comparison: Python list vs NumPy array
# -------------------------------------------------
@timeit
def list_scalar_mul(lst: list[float], a: float) -> list[float]:
    return [a * x for x in lst]


@timeit
def numpy_scalar_mul(arr: np.ndarray, a: float) -> np.ndarray:
    return a * arr


def main() -> None:
    base_path = Path(__file__).resolve().parent.parent / "data"

    # 1) creat list & numpy array
    n = 200_000
    py_list = [float(i) for i in range(n)]
    np_arr = np.arange(n, dtype=np.float64)

    # 2) Performance comparison activate
    _ = list_scalar_mul(py_list, 3.14)
    _ = numpy_scalar_mul(np_arr, 3.14)

    # 3) CSV → pandas DataFrame
    df = pd.read_csv(base_path / "users.csv", na_values=["NULL"])
    print("\n[CSV → Pandas]")
    print(df.to_string(index=False))

    # 4) JSON load
    import json

    with open(base_path / "users.json", encoding="utf-8") as f:
        users_json = json.load(f)
    print("\n[JSON] Loaded users:", users_json)

    # 5) YAML load (environment variable substitution)
    config_path = base_path / "config.yaml"

    os.environ["DB_PASSWORD"] = "super_secret_pw"
    print("DBG ENV:", os.getenv("DB_PASSWORD"))

    raw = config_path.read_text(encoding="utf-8")
    print("DBG RAW:", raw.encode("unicode_escape"))

    yaml.SafeLoader.add_constructor("!ENV", construct_env_tag)
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # password가 None이면 fallback 처리
    if config["database"]["credentials"]["password"] is None:
        print("DBG: fallback substitution")
        raw = config_path.read_text(encoding="utf-8")
        expanded = os.path.expandvars(raw.replace("!ENV ", ""))  # !ENV 제거하고 치환
        config = yaml.safe_load(expanded)

    print("\n[YAML] Loaded config:", config)

    # 6) XML load
    import xml.etree.ElementTree as ET

    tree = ET.parse(base_path / "users.xml")
    root = tree.getroot()
    print("\n[XML] Users:")
    for user in root.findall("user"):
        print(
            {
                "id": user.get("id"),
                "active": user.get("active"),
                "name": user.findtext("name"),
                "email": user.findtext("email"),
            }
        )

    # 7) Examples of four User data structures
    user_td: UserTD = {
        "id": 1,
        "name": "Alice",
        "email": "alice@example.com",
        "age": 30,
        "is_active": True,
    }
    user_nt: UserNT = UserNT(2, "Bob", "bob@example.com", 25, False, None)
    user_dc = UserDC(3, "Carol", "carol@example.com", 28)
    user_pd = UserModel(id=4, name="Dan", email="dan@example.com", age=32)

    print("\n[TypedDict] ", user_td)
    print("[namedtuple]", user_nt)
    print("[dataclass ]", user_dc)
    print("[pydantic ] ", user_pd.model_dump())


if __name__ == "__main__":
    main()
