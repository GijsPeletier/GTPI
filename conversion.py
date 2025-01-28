import re
# an example script provided to me (this project was a respond to a question on gui's)
# Purpose of this script: replace \bra[\Big]{ ... } by \Big( ... \Big)


def gobble_brace_pair(s):
    """
    parse a string of the form {arg}b into arg and b, with brace matching
    """
    arg = ""  # will contain the expression between braces
    s = s[1:]  # gobble opening brace
    level = 1
    while level > 0:
        if s[0] == "{":
            level += 1
        elif s[0] == "}":
            level -= 1
        arg += s[0]
        s = s[1:]
    return arg[:-1], s


# convert mathtools braces of the form \bra[\Big]{ ... }
def convert_braces(s):
    match = re.search(r"\\bra\[(\\\w+)\]", s)
    if match is not None:
        arg, rest = gobble_brace_pair(s[match.end() :])
        s = (
            s[: match.start()]
            + match.group(1)
            + "("
            + arg
            + match.group(1)
            + ")"
            + rest
        )
        convert_braces(s)
    return s


def converter(latex_content):
    latex_content = convert_braces(latex_content)
    return latex_content


def inverter(converted_string: str) -> str:
    raise NotImplementedError()
