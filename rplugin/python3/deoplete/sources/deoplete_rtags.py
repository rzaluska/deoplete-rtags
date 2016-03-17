import re
import json
from pprint import pprint
from subprocess import Popen, PIPE

from deoplete.sources.base import Base

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
        buf[-1] = buf[-1][0:col-1]
        text = "\n".join(buf)

        command = self.get_rc_command(buf_name, line, col, len(text))
        p = Popen(command, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        stdout_data, stderr_data = p.communicate(input=text.encode("utf-8"))
        stdout_data = stdout_data.decode("utf-8")
        if not stdout_data:
            return []
        completions = []
        for line in stdout_data.split("\n"):
            try:
                json_completion = json.loads(line)
                completion = {'dup': 1}
                if json_completion['k'] == "VarDecl":
                    completion['abbr'] = "[V] " + json_completion['c']
                    completion['word'] = json_completion['c']
                    completion['kind'] = " ".join(json_completion['s'].split(" ")[:-1])
                    completion['menu'] = json_completion['comm']
                elif json_completion['k'] == "ParmDecl":
                    completion['kind'] = " ".join(json_completion['s'].split(" ")[:-1])
                    completion['word'] = json_completion['c']
                    completion['abbr'] = "[P] " + json_completion['c']
                    completion['menu'] = json_completion['comm']
                elif json_completion['k'] == "FieldDecl":
                    completion['kind'] = " ".join(json_completion['s'].split(" ")[:-1])
                    completion['word'] = json_completion['c']
                    completion['abbr'] = "[S] " + json_completion['c']
                    completion['menu'] = json_completion['comm']
                elif json_completion['k'] == "FunctionDecl":
                    completion['kind'] = json_completion['s']
                    completion['word'] = json_completion['c'] + "("
                    completion['abbr'] = "[F] " + json_completion['c'] + "("
                    completion['menu'] = json_completion['comm']
                elif json_completion['k'] == "CXXMethod":
                    completion['kind'] = json_completion['s']
                    completion['word'] = json_completion['c'] + "("
                    completion['abbr'] = "[M] " + json_completion['c'] + "("
                    completion['menu'] = json_completion['comm']
                elif json_completion['k'] == "NotImplemented":
                    completion['word'] = json_completion['c']
                    completion['abbr'] = "[K] " + json_completion['c']
                else:
                    completion['word'] = json_completion['c']
                    completion['menu'] = json_completion['comm']
                    completion['kind'] = json_completion['k']
                completions.append(completion)
            except:
                pass

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
