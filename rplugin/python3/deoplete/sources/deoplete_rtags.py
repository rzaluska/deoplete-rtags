import re
import json
from pprint import pprint
from subprocess import Popen, PIPE

from deoplete.source.base import Base

current = __file__


class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)
        self.name = 'rtags'
        self.mark = '[rtags]'
        self.filetypes = ['c', 'cpp', 'objc', 'objcpp']
        self.rank = 500
        self.is_bytepos = True
        self.min_pattern_length = 1
        self.input_pattern = (r'[^. \t0-9]\.\w*|'
                              r'[^. \t0-9]->\w*|'
                              r'[a-zA-Z_]\w*::\w*')

    def get_complete_position(self, context):
        m = re.search(r'\w*$', context['input'])
        return m.start() if m else -1

    def gather_candidates(self, context):
        line = context['position'][1]
        col = (context['complete_position'] + 1)
        buf = self.vim.current.buffer
        buf_name = buf.name
        buf = buf[0:line]
        buf[-1] = buf[-1][0:col]
        text = "\n".join(buf)

        command = self.get_rc_command(buf_name, line, col, len(text))
        p = Popen(command, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        stdout_data, stderr_data = p.communicate(input=text.encode("utf-8"))
        if stdout_data.decode("utf-8") == "":
            return []
        completions_json = json.loads(stdout_data.decode("utf-8"))
        completions = []
        for raw_completion in completions_json:
            completion = {'dup': 1}
            if raw_completion['k'] == "VarDecl":
                completion['abbr'] = "[V] " + raw_completion['c']
                completion['word'] = raw_completion['c']
                completion['kind'] = raw_completion['k']
                completion['menu'] = raw_completion['comm']
            elif raw_completion['k'] == "ParmDecl":
                completion['kind'] = " ".join(raw_completion['s'].split(" ")[:-1])
                completion['word'] = raw_completion['c']
                completion['abbr'] = "[P] " + raw_completion['c']
                completion['menu'] = raw_completion['comm']
            elif raw_completion['k'] == "FieldDecl":
                completion['kind'] = " ".join(raw_completion['s'].split(" ")[:-1])
                completion['word'] = raw_completion['c']
                completion['abbr'] = "[S] " + raw_completion['c']
                completion['menu'] = raw_completion['comm']
            elif raw_completion['k'] == "FunctionDecl":
                completion['kind'] = raw_completion['s']
                completion['word'] = raw_completion['c'] + "("
                completion['abbr'] = "[F] " + raw_completion['c'] + "("
                completion['menu'] = raw_completion['comm']
            elif raw_completion['k'] == "CXXMethod":
                completion['kind'] = raw_completion['s']
                completion['word'] = raw_completion['c'] + "("
                completion['abbr'] = "[M] " + raw_completion['c'] + "("
                completion['menu'] = raw_completion['comm']
            elif raw_completion['k'] == "NotImplemented":
                completion['word'] = raw_completion['c']
                completion['abbr'] = "[K] " + raw_completion['c']
            else:
                completion['word'] = raw_completion['c']
                completion['menu'] = raw_completion['comm']
                completion['kind'] = raw_completion['k']
            completions.append(completion)

        return completions

    def get_rc_command(self, file_name, line, column, offset):
        # TODO change string to table
        command = "rc --absolute-path --synchronous-completions"
        command += " --json-completions"
        command += " -l {filename}:{line}:{column}"
        command += " --unsaved-file={filename}:{offset}"
        formated_command = command.format(filename=file_name,
                                          line=line,
                                          column=column,
                                          offset=offset)
        return formated_command.split(" ")
