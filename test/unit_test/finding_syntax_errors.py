# This program is a utility for figuring out the invalid token pairs in a truth statement

"""
LP = Left Parenthesis
RP = Right Parenthesis
A  = Alphabetic
O  = Operator
N  = Not
B  = Binary
"""


class Entry:
    def __init__(self, first: str, second: str, reason=""):
        self.first = first
        self.second = second
        self.reason = reason


class Good:
    def __init__(self):
        self.entries: list[Entry] = []

    def __str__(self):
        print("Good list:")
        for i in self.entries:
            print(f"\t{i.first} {i.second}")

        return ""


class Bad:
    def __init__(self):
        self.entries: list[Entry] = []

    def __str__(self):
        print("Bad list:")
        for i in self.entries:
            print(f"\t{i.first} {i.second} is bad because {i.reason}")

        return ""


def not_yes_no(inp: str) -> bool:
    return inp != "y" and inp != "n"


if __name__ == '__main__':
    tokens = ["LP", "RP", "A", "O", "N", "B"]
    example = {"LP": "(", "RP": ")", "A": "name", "O": "++", "N": "!", "B": "true"}
    good = Good()
    bad = Bad()

    for f in tokens:
        for s in tokens:
            print(f"Is this okay?  ->  {f} {s}  ->  Ex. {example[f]} {example[s]}")
            response = input("Answer: ")

            while not_yes_no(response):
                response = input("Answer must be 'y' or 'n'.\nAnswer: ")

            if response == "y":
                good.entries.append(Entry(f, s))
            elif response == "n":
                response = input("Describe why: ")
                bad.entries.append(Entry(f, s, response))

            print()

    print(good)
    print(bad)
