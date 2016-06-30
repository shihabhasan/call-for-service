import os
from compressor.filters import FilterBase


def escape(a_string):
    escaped = a_string.translate(str.maketrans({"\"": r"\"", "\n": r"\n"}))
    return escaped


class JSTemplateFilter(FilterBase):
    def __init__(self, content, params=None, *args, **kwargs):
        super().__init__(content, *args, **kwargs)

    def input(self, **kwargs):
        content = escape(self.content)

        retval = "if (!window.templates) { window.templates = {}; }\n"
        retval += "window.templates['{}'] = ".format(
            os.path.basename(self.filename))
        retval += '"{}";'.format(content)

        return retval