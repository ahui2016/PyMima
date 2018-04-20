class AAA:
    aaa = None

    def __init__(self):
        self.bbb = 'bbb'


class BBB(AAA):
    # aaa = None

    def __init__(self):
        self.bbb = 'ccc'


if __name__ == '__main__':
    AAA.aaa = 'aaa'
    AAA.bbb = 'ddd'
    a = AAA()
    print(a.aaa, a.bbb)

    b = BBB()
    print(b.aaa, b.bbb)
