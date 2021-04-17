class Error:
    def __init__(self, data):
        self.path = data[0].rstrip()
        self.line = int(data[1].rstrip()) - 1
        self.column = int(data[2].rstrip())
        self.code = data[3].rstrip()
        self.msg = data[4].rstrip()

def check(error):
    lines = read_file(error.path)
    if error.code == 'C0303':
        c0303(lines, error.line)
        print('C0303')
        fixable = True
    elif error.code == 'C0304':
        c0304(lines)
        print("C0304")
        fixable = True
    elif error.code == 'C0321':
        c0321(lines, error.line, error.column)
        print("C0321")
        fixable = True
    elif error.code == 'C0326':
        c0326(lines, error.line, error.msg)
        print("C0326")
        fixable = True
    elif error.code == 'W0404':
        w0404(lines, error.line)
        print("W0404")
        fixable = True
    elif error.code == 'C0410':
        c0410(lines, error.line)
        print("C0410")
        fixable = True
    elif error.code == 'C0411':
        c0411(lines, error.line, error.msg)
        print("C0411")
        fixable = True
    elif error.code == 'C0413':
        c0413(lines, error.line)
        print("C0413")
        fixable = True
    elif error.code == 'W0611':
        w0611(lines, error.line)
        print("W0611")
    else:
        fixable = False
        print("NO")
    replace_lines(error.path, lines)
    return fixable

def check1(error):
    lines = read_file(error.path)
    if error.code == 'C0303':
        c0303(lines, error.line)
        print('C0303')
    elif error.code == 'C0304':
        c0304(lines)
        print("C0304")
    elif error.code == 'C0321':
        c0321(lines, error.line, error.column)
        print("C0321")
    elif error.code == 'C0326':
        c0326(lines, error.line, error.msg)
        print("C0326")
    elif error.code == 'W0404':
        w0404(lines, error.line)
        print("W0404")
    elif error.code == 'C0410':
        c0410(lines, error.line)
        print("C0410")
    elif error.code == 'C0411':
        c0411(lines, error.line, error.msg)
        print("C0411")
    elif error.code == 'C0413':
        c0413(lines, error.line)
        print("C0413")
    elif error.code == 'W0611':
        w0611(lines, error.line)
        print("W0611")
    else:
        print("NO")
    replace_lines(error.path, lines)

def check2(error):
    lines = read_file(error.path)
    if error.code == 'C0303':
        c0303(lines, error.line)
        print('C0303')
    elif error.code == 'C0304':
        c0304(lines)
        print("C0304")
    elif error.code == 'C0321':
        c0321(lines, error.line, error.column)
        print("C0321")
    elif error.code == 'C0326':
        c0326(lines, error.line, error.msg)
        print("C0326")
    elif error.code == 'W0404':
        w0404(lines, error.line)
        print("W0404")
    elif error.code == 'C0410':
        c0410(lines, error.line)
        print("C0410")
    elif error.code == 'C0411':
        c0411(lines, error.line, error.msg)
        print("C0411")
    elif error.code == 'C0413':
        c0413(lines, error.line)
        print("C0413")
    elif error.code == 'W0611':
        w0611(lines, error.line)
        print("W0611")
    else:
        print("NO")
    replace_lines(error.path, lines)

def read_file(path):
    fo = open(path, "r")
    lines = fo.readlines()
    fo.close()
    return lines

def replace_lines(file, lines):
    fo = open(file, "w")
    fo.writelines(lines)
    fo.close()

def indent(line):
    indentation = line[:-len(line.lstrip())]
    return indentation

def placeholder_external(lines, line_number):
    aux = lines[line_number].split("#EXT")
    target_line = int(aux[1])
    line = [aux[2]]
    del lines[line_number]
    new_lines = lines[:target_line] + line + lines[target_line:]
    return new_lines

def placeholder_split(line):
    aux = line.split("#SPLIT")
    column = int(aux[1])
    line = aux[2]
    if line[column - 1] == ";" or line[column -2:column - 1] == ";":
        first = line[:column].rstrip()[:-1]
        second = indent(first) + line[column:]
        line = first + "\n" + second
    # TODO if y sentencia en la misma linea
    # elif lines[i][column -2:column - 1] == ":":
    #     first = lines[i][:column].rstrip()[:-1]
    #     second = lines[i][column:]
    #     lines[i] = first + ":\n    " + second
    return line

def placeholder_top(lines, line_number):
    top_line = lines[line_number][4:].lstrip()
    del lines[line_number]
    lines.insert(0, top_line)
    return lines

def placeholder_importsplit(line):
    line = line.split("#IMPORTSPLIT")[1]
    imports = line.split(",")
    indentation = indent(imports[0])
    new_lines = indentation + imports[0].strip() + "\n"
    j = 1
    while j < len(imports):
        new_lines = (new_lines + indentation + "import " +
                     imports[j].strip() + "\n")
        j = j + 1
    return new_lines

def check_placeholders(file):
    fo = open(file, "r")
    lines = fo.readlines()
    fo.close()
    i = 0
    total = len(lines)
    while i < total:
        if lines[i].startswith("#EXT"):
            lines = placeholder_external(lines, i)
        else:
            i = i + 1
    i = 0
    total = len(lines)
    while i < total:
        if lines[i].startswith("#DEL"):
            del lines[i]
            total = total - 1
        elif lines[i].startswith("#SPLIT"):
            lines[i] = placeholder_split(lines[i])
        elif lines[i].startswith("#TOP"):
            lines = placeholder_top(lines, i)
        elif lines[i].startswith("#IMPORTSPLIT"):
            lines[i] = placeholder_importsplit(lines[i])
        else:
            i = i + 1
    i = 0
    total = len(lines)
    while i < total:
        if lines[i].startswith("#DEL"):
            del lines[i]
            total = total - 1
        elif lines[i].startswith("#SPLIT"):
            lines[i] = placeholder_split(lines[i])
        elif lines[i].startswith("#TOP"):
            lines = placeholder_top(lines, i)
        elif lines[i].startswith("#IMPORTSPLIT"):
            lines[i] = placeholder_importsplit(lines[i])
        else:
            i = i + 1
    replace_lines(file, lines)

def c0303(lines, line_number):
    # Trailing whitespace
    lines[line_number] = lines[line_number].rstrip() + "\n"
    return lines

def c0304(lines):
    # Final newline missing
    lines.append("\n")
    return lines

def c0321(lines, line_number, column):
    # More than one statement on a single line
    lines[line_number] = "#SPLIT" + str(column) + "#SPLIT" + lines[line_number]
    return lines

def replace_comma(line, old, new):
    line = line.split(old)
    new_line = line[0].rstrip()
    i = 1
    while i < len(line):
        new_line = new_line + new + line[i].strip()
        i = i + 1
    new_line = new_line + "\n"
    return new_line

def replace_bracket1(line, old, new):
    new_line = line
    line = line.split(old, 1)
    if len(line) > 1:
        new_line = line[0] + new + line[1].strip() + "\n"
    return new_line

def replace_bracket2(line, old, new):
    new_line = line
    line = line.split(old, 1)
    if len(line) > 1:
        new_line = line[0].rstrip() + new + line[1].rstrip() + "\n"
    return new_line

def c0326(lines, line_number, msg):
    # %s space %s %s %s\n%s
    line = lines[line_number]
    if (msg == "Exactly one space required around assignment" or
            msg == "Exactly one space required after assignment" or
            msg == "Exactly one space required before assignment"):
        line = line.split("=", 1)
        lines[line_number] = line[0].rstrip() + " = " + line[1].lstrip()
    elif (msg == "Exactly one space required around comparison" or
          msg == "Exactly one space required after comparison" or
          msg == "Exactly one space required before comparison"):
        comparators = [">>=", "<<=", "//=", "**=", "==", "!=", "<>", "<=",
                       ">=", "+=", "-=", "*=", "/=", "&=", "|=", "^=", "%=",
                       "<", ">", "="]
        for comparator in comparators:
            tokens = line.split(comparator, 1)
            if len(tokens) == 2:
                break
        line = tokens[0].rstrip() + " " + comparator + " " + tokens[1].lstrip()
        lines[line_number] = line
    elif (msg == "Exactly one space required after comma" or
          msg == "No space allowed before comma"):
        lines[line_number] = replace_comma(line, ",", ", ")
    elif msg == "No space allowed after bracket":
        line = replace_bracket1(line, "( ", "(")
        line = replace_bracket1(line, "[ ", "[")
        line = replace_bracket1(line, "{ ", "{")
        lines[line_number] = line
    elif msg == "No space allowed before bracket":
        line = replace_bracket2(line, " )", ")")
        line = replace_bracket2(line, " ]", "]")
        line = replace_bracket2(line, " }", "}")
        lines[line_number] = line
    elif msg == "No space allowed before :":
        line = line.split(":", 1)
        lines[line_number] = line[0].rstrip() + ":" + line[1]
    return lines

def c0410(lines, line_number):
    # Multiple imports on one line (%s)
    lines[line_number] = "#IMPORTSPLIT" + lines[line_number]
    return lines

def c0411(lines, line_number, msg):
    # %s comes before %s
    if msg.startswith("standard"):
        if not lines[line_number].startswith("#TOP"):
            lines[line_number] = "#TOP" + lines[line_number]
    elif msg.startswith("external"):
        if not lines[line_number].startswith("#"):
            split_msg = msg.split("\"")
            import2 = split_msg[3] + "\n"
            i = 0
            total = len(lines)
            while i < total:
                if lines[i] == import2:
                    break
                else:
                    i = i + 1
            lines[line_number] = "#EXT" + str(i) + "#EXT" + lines[line_number]
    return lines

def c0413(lines, line_number):
    # Import "%s" should be placed at the top of the module
    if not lines[line_number].startswith("#TOP"):
        lines[line_number] = "#TOP" + lines[line_number]
    return lines

def w0404(lines, line_number):
    # Reimport %r (imported line %s)
    if ',' not in lines[line_number] and ';' not in lines[line_number]:
        lines[line_number] = "#DEL" + lines[line_number]
        return lines

def w0611(lines, line_number):
    # Unused import %s
    if ',' not in lines[line_number] and ';' not in lines[line_number]:
        lines[line_number] = "#DEL" + lines[line_number]
    return lines
