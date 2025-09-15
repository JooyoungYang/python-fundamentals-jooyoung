import argparse
import utils

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ages", type=str, help="Comma separated ages")
    args = parser.parse_args()

    ages = [int(x) for x in args.ages.split(",")]
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

    age_range = (0, 100)
    print("Age range tuple:", age_range)

    print("Numbers from 0 to 4:", list(range(5)))
    print("ID of ages list:", id(ages))

    s = "28"
    age_from_str = int(s)
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
