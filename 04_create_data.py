import math
from functools import partial

import pandas as pd

df = pd.read_csv("data/users.csv", na_values=["NULL", "null", "NaN", ""])

df.to_json("users.json", orient="records", force_ascii=False, indent=2)

df_work = df.copy()
df_work["signup_date"] = ["2025-09-28", "30/09/2025", "2025.10.01"]
df_work.to_csv("user_work.csv", index=False)

print("created: users.json, user_work.csv")
print(df_work)

# 2
activity_scores = pd.Series(
    data=[0.95, 0.88, 0.60], index=["Alice", "Bob", "Charlie"], name="activity_score"
)

print("created: Custom Series")
print(activity_scores)
print("\nSeries index: ", activity_scores.index)
print("Series values: ", activity_scores.values)

# 3
df_selected = df_work[["name", "age", "active", "salary", "signup_date"]].copy()

print("created: DF with specified columns")
print(df_selected)
print(df_selected.info())

# 4
print("created: Inspect the DF")

print("Data_Types: ")
print(df_selected.dtypes)

print("Head (first 2 rows): ")
print(df_selected.head(2))

print("Tail (last 2 rows): ")
print(df_selected.tail(2))

print("Statistics: ")
print(df_selected.describe(include="all"))

# 5
print("created: Data slicing")

print("Slicing by column name(name, salary): ")
print(df_selected.loc[:1, ["name", "salary"]])  # .loc: label-based indexing

print("Slicing by row position(last 2 rows):")
print(df_selected.iloc[2:])  # .iloc: interger-location based indexing

print("Combined slice (first 2 rows of name + salary")
print(df_selected.loc[:1, ["name", "salary"]])

print("iloc row/col mix (first 2 rows, first 3 cols)")
print(df_selected.iloc[0:2, 0:3])

# 6
print("Boolean & Range Slicing")

print("Boolean filter (active users only): ")
active_users = df_selected[df_selected["active"]]
print(active_users)

print("Range filter (age btw 26 and 80)")
age_filtered = df_selected[(df_selected["age"] >= 26) & (df_selected["age"] <= 80)]
print(age_filtered)
# in pandas, and -> &, or -> |

# 7
print("Data Cleaning: duplicated, nunique, drop_duplicated ")

# duplicate first col
df_with_dup = pd.concat([df_selected, df_selected.iloc[[0]]], ignore_index=True)
print(df_with_dup)

print("duplicated() result: ")
print(df_with_dup.duplicated(keep=False))
# keep=False: represent all duplicates
# keep="frist": Kept the first one among the duplicates.

print("nunique() result: ")  # count unique value of col
print("no dup: ", df_selected.nunique())
print("dup: ", df_with_dup.nunique())

df_no_dup = df_with_dup.drop_duplicates()  # default: keep=first
print("drop_duplicates() result: ")
print(df_no_dup)

# 8
print("Safe Type conversion")

df_selected["salary_converted"] = pd.to_numeric(df_selected["salary"], errors="coerce")
# errors="coerce": Non-convertible values will be set to "NaN"
print("converted salary col: ")
print(df_selected[["salary", "salary_converted"]])

df_selected["signup_converted"] = pd.to_datetime(
    df_selected["signup_date"], errors="coerce", dayfirst=True
)
# errors="coerce": Non-convertible values will be set to "NaT"
# dayfirst=True: interpret dates in European format
print("converted signup_date col: ")

"""_
    #trouble parsing dates if they are in mixed formats
        df_selected["signup_date_cleaned"] = (
            df_selected["signup_date"]
            .str.replace(".", "-", regex=False)     # . → -
            .str.replace("/", "-", regex=False)     # / → -
            .str.replace("년", "-", regex=False)    # delete 연/월/일
            .str.replace("월", "-", regex=False)
            .str.replace("일", "", regex=False)
            .str.strip()
            )

    df_selected["signup_converted"] = pd.to_datetime(
    df_selected["signup_date_cleaned"],
    errors="coerce",
    dayfirst=True)
    print("converted all signup_date col: ")
    print(df_selected[["signup_date", "signup_converted"]])
"""


print("Data types after conversion: ")
print(df_selected.dtypes)

# 9
print("Fill defaults:.apply()")


def fill_salary(x: float | None) -> float:
    # None 이거나 NaN 이면 기본값
    if x is None:
        return 40000.0
    if isinstance(x, float) and math.isnan(x):
        return 40000.0
    # 여기 도달하면 x는 float
    return float(x)


df_selected["salary_filled"] = df_selected["salary_converted"].apply(fill_salary)
print("Salary before/after filling: ")
print(df_selected[["name", "salary", "salary_converted", "salary_filled"]])

# 10
print("Cleaning pipeline: .pipe()")


def normalize_strings(d: pd.DataFrame) -> pd.DataFrame:
    out = d.copy()
    # 날짜 구분자를 통일 (., / -> -)
    out["signup_date"] = (
        out["signup_date"]
        .astype("string")
        .str.replace(".", "-", regex=False)
        .str.replace("/", "-", regex=False)
        .str.strip()
    )
    return out


def to_types(d: pd.DataFrame) -> pd.DataFrame:
    out = d.copy()
    # 숫자형 안전 변환
    out["age_num"] = pd.to_numeric(out["age"], errors="coerce")
    out["salary_num"] = pd.to_numeric(out["salary"], errors="coerce")
    # 날짜형 안전 변환
    out["signup_dt"] = pd.to_datetime(out["signup_date"], errors="coerce", dayfirst=True)
    return out


def report(d: pd.DataFrame) -> pd.DataFrame:
    cols = ["age_num", "salary_num", "signup_dt"]
    print("\n=== dtypes ===")
    print(d[cols].dtypes)
    print("\n=== null counts ===")
    print(d[cols].isna().sum())
    return d


df_piped = (
    df_selected.pipe(normalize_strings)  # 문자열 정규화(날짜 구분자 통일)
    .pipe(to_types)  # 숫자 + 날짜 타입 변환
    .pipe(report)  # dtypes / null counts 출력
)

# 11


def enforce_min_salary(d: pd.DataFrame, threshold: float = 45000.0) -> pd.DataFrame:
    base = d["salary_filled"] if "salary_filled" in d.columns else d["salary_num"]
    return d[base.fillna(0) >= threshold]


min_salary_45k = partial(enforce_min_salary, threshold=45000.0)

df_final = df_piped.pipe(min_salary_45k).drop_duplicates(subset=["name"]).reset_index(drop=True)
print("\n=== Final rows (salary >= 45k) ===")
print(df_final)

df_final.to_csv("data/user_clean_result.csv", index=False)
