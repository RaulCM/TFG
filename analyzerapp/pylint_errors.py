import re

class Error:
    def __init__(self, data):
        self.path = data[0].rstrip()
        self.line = int(data[1].rstrip()) - 1
        self.column = int(data[2].rstrip())
        self.code = data[3].rstrip()

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
        w0611(error)
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

def check_placeholders(file):
    fo = open(file, "r")
    lines = fo.readlines()
    fo.close()
    i = 0
    total = len(lines)
    while i < total:
        print(lines[i])
        if lines[i].startswith("#DEL"):
            del lines[i]
            total = total - 1
        elif lines[i].startswith("#SPLIT"):
            aux = lines[i].split("#SPLIT")
            column = int(aux[1])
            lines[i] = aux[2]
            if lines[i][column - 1] == ";" or lines[i][column -2:column - 1] ==";":
                first = lines[i][:column].rstrip()[:-1]
                second = first[:-len(first.lstrip())] + lines[i][column:]
                lines[i] = first + "\n" + second
            # TODO if y sentencia en la misma linea
            # elif lines[i][column -2:column - 1] == ":":
            #     first = lines[i][:column].rstrip()[:-1]
            #     second = lines[i][column:]
            #     lines[i] = first + ":\n    " + second
        else:
            i = i + 1
    replace_lines(file, lines)

def c0303(error):
    # Trailing whitespace
    lines = read_file(error)
    lines[error.line] = lines[error.line].rstrip() + "\n"
    replace_lines(error.path, lines)

def c0321(error):
    # More than one statement on a single line
    lines = read_file(error)
    lines[error.line] = "#SPLIT" + str(error.column) + "#SPLIT" + lines[error.line]
    print(lines[error.line])
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
    if ',' not in lines[error.line] and ';' not in lines[error.line]:
        lines[error.line] = "#DEL" + lines[error.line]
        print(lines[error.line])
        replace_lines(error.path, lines)
