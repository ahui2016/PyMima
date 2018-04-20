class AAA:
    def __init__(self, aaa=None):
        self.aaa = 'aaa'


class BBB(AAA):
    def __init__(self):
        self.bbb = 'bbb'


class CCC(AAA):
    def __init__(self):
        super().__init__()


if __name__ == '__main__':
    c = CCC()
    print(c.aaa)

    b = BBB()
    print(b.aaa)
