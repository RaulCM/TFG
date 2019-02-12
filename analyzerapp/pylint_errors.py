class Error:
    def __init__(self, data):
        self.path = data[0].rstrip()
        self.line = int(data[1].rstrip())
        self.code = data[2].rstrip()

def check(error):
    if error.code == 'C0303':
        c0303(error)
        print('C0303')
    elif error.code == 'C0326':
        # c0326(error)
        print("C0326")
    elif error.code == 'C0321':
        c0321(error)
        print("C0321")
    elif error.code == 'W0611':
        # w0611(error)
        print("W0611")
    else:
        print("NO");

def read_file(error):
    fo = open(error.path, "r")
    lines = fo.readlines()
    fo.close()
    return lines

def replace_lines(file, lines):
    fo = open(file, 'w')
    fo.writelines(lines)
    fo.close()

def c0303(error):
    # Trailing whitespace
    lines = read_file(error)
    lines[error.line] = lines[error.line].rstrip() + "\n"
    replace_lines(error.path, lines)

def c0321(error):
    # More than one statement on a single line
    lines = readfile(error)
    first = lines[error.line][:error.column].rstrip()[:-1]
    second = lines[error.line][error.column:]
    lines[error.line] = first + "\n" + second
    replace_lines(error.path, lines)

def c0326(error):
    # %s space %s %s %s\n%s
    fo = open(error.path, "r+")
    line = fo.readlines()[error.line]
    print(line)
    pattern = r'.*[^=!<>+\-*/&|^% ]=[^=!<>+\-*/&|^% ].*'
    new = re.search(pattern, line)
    print(new)
    # TODO Sustituir linea
    fo.close()

def w0611(error):
    # Unused import %s
    lines = read_file(error)
    if ',' not in lines[error.line]:
        del lines[error.line]
        if lines[0] == '\n':
            del lines[0]
        replace_lines(error.path, lines)
