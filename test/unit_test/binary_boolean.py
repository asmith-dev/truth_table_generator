# This code tests boolean comprehension of 0 and 1

if __name__ == '__main__':
    # Testing false
    if not 0:
        print("0 is False?")
    else:
        print("0 is not False")

    # Testing true
    if 1:
        print("1 is True?")
    """
    else:
        print("1 is not True")
    """
    # ^^^^^ This won't execute because it is unreachable
