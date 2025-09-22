import argparse

from src import utils


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Age Group Analyzer (CLI)")
    parser.add_argument(
        "--ages",
        default="15,22,35",  # 기본값 제공
        help="Comma-separated ages, e.g. 15,22,35 (default: 15,22,35)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # 공백 제거 + 빈 값 방지
    ages: list[int] = [int(x.strip()) for x in args.ages.split(",") if x.strip()]

    title = "Age Group Analyzer"
    people_count = len(ages)
    info = {"title": title, "count": people_count}
    print(info)

    for idx, age in enumerate(ages):
        if age < 20:
            print(f"Person {idx}: Teenager")
        elif age < 30:
            print(f"Person {idx}: Twenties")
        else:
            print(f"Person {idx}: Older")

    count = 0
    while count < 3:
        print("While loop:", count)
        count += 1

    age_range: tuple[int, int] = (0, 100)
    print("Age range tuple:", age_range)

    print("Numbers from 0 to 4:", list(range(5)))
    print("ID of ages list:", id(ages))

    s: str = "28"
    age_from_str: int = int(s)
    print("Casted age:", age_from_str)
    if age_from_str < 20:
        print("Teenager (from string)")
    elif age_from_str < 30:
        print("Twenties (from string)")
    else:
        print("Older (from string)")

    print("Age after 5 years:", utils.add_years(22, 5))


if __name__ == "__main__":
    main()
