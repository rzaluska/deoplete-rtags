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
        self.input_pattern = (r'[^. \t0-9]\.\w*|'
                              r'[^. \t0-9]->\w*|'
                              r'[a-zA-Z_]\w*::\w*')

    def get_complete_position(self, context):
        m = re.search(r'\w*$', context['input'])
        return m.start() if m else -1

    def gather_candidates(self, context):
        f = open("/tmp/deoplete-rtags.log", "a")
        f.write("GatherCandidates\n")
        f.write(str(context) + "\n")
        line = context['position'][1]
        f.write("Line: " + str(line) + "\n")
        col = (context['complete_position'] + 1)
        f.write("Col: " + str(col) + "\n")
        buf = self.vim.current.buffer
        f.write("Buf: " + str(buf.name) + "\n")
        text = "\n".join(buf[0:line])
        f.write("Text:\n" + str(text) + "\n")
        offset = len(text.encode("utf-8"))
        f.write("Offset: " + str(offset) + "\n")

        command = self.get_rc_command(buf.name, line, col, len(text))
        p = Popen(command, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        stdout_data, stderr_data = p.communicate(input=text.encode("utf-8"))
        f.write("Answer: " + str(stdout_data) + "\n")
        re_compiled = re.compile(r".*CDATA\[ (.*?)\]\]><\/completions>",
                                 re.DOTALL)
        re_result = re.search(re_compiled, stdout_data)
        if not re_result:
            return []
        clean_answear = re_result.group(1).strip()
        completions = []
        for line in clean_answear.split("\n"):
            line_split = line.strip().split(" ")
            f.write("Answer: " + str(line_split) + "\n")
            if len(line_split) < 6:
                continue
            completion = {'dup': 1}
            completion['kind'] = "[" + line_split[-3] + "]"
            if completion['kind'] == "[CXXMethod]":
                if line_split[-4] == "const":
                    completion['word'] = " ".join(line_split[2:-4])
                else:
                    completion['word'] = " ".join(line_split[2:-3])
            else:
                completion['word'] = line_split[0]
            completions.append(completion)

        f.close()
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
