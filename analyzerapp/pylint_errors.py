class Error:
    def __init__(self, data):
        self.path = data[0].rstrip()
        self.line = int(data[1].rstrip())
        self.code = data[2].rstrip()

def check(error):
    if error.code == 'C0303':
        c0303(error)
        print('C0303')
    # elif error.code == 'C0326':
    #     c0326(error)
    elif error.code == 'R0201':
        print("OK")
    else:
        print("NO");

def replace_lines(file, lines):
    fo = open(file, 'w')
    fo.writelines(lines)
    fo.close()

def c0303(error):
    # Trailing whitespace
    fo = open(error.path, "r")
    lines = fo.readlines()
    fo.close()
    lines[error.line] = lines[error.line].rstrip() + "\n"
    replace_lines(error.path, lines)

def c0326(error):
    fo = open(error.path, "r+")
    line = fo.readlines()[error.line]
    print(line)
    # TODO Corregir linea
    # TODO Sustituir linea
    fo.close()





def r0201(arg):
    pass
