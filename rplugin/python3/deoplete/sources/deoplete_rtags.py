import re
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
        self.debug("Plugin Started")

    def get_complete_position(self, context):
        m = re.search(r'\w*$', context['input'])
        return m.start() if m else -1

    def gather_candidates(self, context):
        self.debug("GatherCandidates\n")
        line = context['position'][1]
        self.debug("Line: " + str(line) + "\n")
        col = (context['complete_position'] + 1)
        self.debug("Col: " + str(col) + "\n")
        buf = self.vim.current.buffer
        self.debug("Buf: " + str(buf.name) + "\n")
        text = "\n".join(buf[0:line])
        self.debug("Text:\n" + str(text) + "\n")
        offset = len(text.encode("utf-8"))
        self.debug("Offset: " + str(offset) + "\n")

        command = self.get_rc_command(buf.name, line, col, len(text))
        p = Popen(command, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        stdout_data, stderr_data = p.communicate(input=text.encode("utf-8"))
        stdout_data = stdout_data.decode("utf-8")
        re_compiled = re.compile(r".*CDATA\[ (.*?)\]\]><\/completions>",
                                 re.DOTALL)
        re_result = re.search(re_compiled, stdout_data)
        if not re_result:
            return []
        clean_answear = re_result.group(1).strip()
        completions = []
        for line in clean_answear.split("\n"):
            line_split = line.strip().split(" ")
            if len(line_split) < 6:
                continue
            completion = {'dup': 1}
            completion['kind'] = "[" + line_split[-3] + "]"
            if completion['kind'] == "[CXXMethod]":
                self.debug("Answer: " + str(line_split) + "\n")
                if line_split[-4] == "const":
                    if line_split[2] == "*":
                        completion['word'] = " ".join(line_split[3:-4])
                    else:
                        completion['word'] = " ".join(line_split[2:-4])
                else:
                    if line_split[2] == "*":
                        completion['word'] = " ".join(line_split[3:-3])
                    else:
                        completion['word'] = " ".join(line_split[2:-3])
                completion['menu'] = line_split[1]
            else:
                completion['word'] = line_split[0]
            completions.append(completion)

        return completions

    def get_rc_command(self, file_name, line, column, offset):
        command = "rc --absolute-path --synchronous-completions"
        command += " -l {filename}:{line}:{column}"
        command += " --unsaved-file={filename}:{offset}"
        formated_command = command.format(filename=file_name,
                                          line=line,
                                          column=column,
                                          offset=offset)
        return formated_command.split(" ")
