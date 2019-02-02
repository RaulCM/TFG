class Error:
    def __init__(self, data):
        self.path = data[0].rstrip()
        self.line = int(data[1].rstrip())
        self.code = data[2].rstrip()

def check(error):
    if error.code == 'C0326':
        c0326(error)
    elif error.code == 'R0201':
        print("OK")
    else:
        print("NO");


def c0326(error):
    fo = open(error.path, "r+")
    line = fo.readlines()[error.line]
    print(line)
    # TODO Corregir linea
    # TODO Sustituir linea
    fo.close()





def r0201(arg):
    pass
