# Tests to see if a class can change the values of a separate class
# Conclusion: yes it can

# The master class whose variables are trying to be changed
class A:
    def __init__(self):
        self.num = 0
        self.list = []
        self.dict = {}

    def __str__(self):
        return f"Num: {self.num}\nList: {self.list}\nDict: {self.dict}"


# First changing class
class B:
    def __init__(self, aa: A):
        self.a = aa

        self.a.num += 1
        self.a.list.append("changed by B")
        self.a.dict["B"] = True


# Second changing class
class C:
    def __init__(self, aa: A):
        self.a = aa

        self.a.num += 1
        self.a.list.append("changed by C")
        self.a.dict["C"] = True


if __name__ == '__main__':
    # Use of master class
    a = A()

    # Inputting the master class into the changing classes
    b = B(a)
    c = C(a)

    # Checking to see if the changing classes changed the master class
    print(a)
