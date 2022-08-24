import re

indent = r'^\s*'
sep = r'\s+'

ident = r'([a-z][a-z0-9_]*)'

sub_stmt = indent + r'subroutine' + sep + ident

sub_match = re.compile(sub_stmt,flags=re.IGNORECASE)

module_stmt = indent + r'module' + sep + ident

module_match = re.compile(module_stmt,flags=re.IGNORECASE)

end_module_stmt = indent + r'end' + sep + r'module'

end_module_match = re.compile(end_module_stmt,flags=re.IGNORECASE)


def parse_fortran_line(line):
    """Lightweight parsing of necessary fortran statements"""

    stmt_parsers = [('subroutine',sub_match),
                    ('module',module_match),
                    ('end module',end_module_match)]

    for parser in stmt_parsers:

        match = parser[1].match(line)

        if match:

            return  parser[0], match.groups()
    
    return None, None


def parse_fortran_file(file):
    """Extract necessary information from Fortran file"""

    modules = {}

    if isinstance(file,str) or isinstance(file,unicode):

        fh = open(file,'r')

    else:

        fh = file

    cur_mod = None

    while True:

        line = fh.readline()

        if not line:

            break

        parser, matches = parse_fortran_line(line)

        if parser == 'module':

            mod_name = matches[0].lower()

            modules[mod_name] = {'subroutines':[]}

            cur_mod = mod_name
            
        elif cur_mod and parser == 'end module':

            cur_mod = None
            
        elif cur_mod and parser == 'subroutine':

            sub_name = matches[0].lower()
            modules[mod_name]['subroutines'].append(sub_name)

    return modules