# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os


class JSScriptException(Exception):
    pass


class JSScript(object):

    def __init__(self, filename):
        self._filename = os.path.join(os.path.dirname(__file__), filename)
        with open(self._filename) as f:
            self._file = f.read()

    def get_script(self, script_name):
        in_script = False
        end_found = False
        out = ''
        for line in self._file.splitlines(True):
            if in_script:
                if line == "// END SCRIPT\n":
                    end_found = True
                    break
                elif line.startswith("// SCRIPT"):
                    break
                out += line
            elif line == "// SCRIPT {}\n".format(script_name):
                in_script = True
        if not in_script:
            raise JSScriptException(
                "Script '{}' not found in '{}'".format(
                    script_name, self._filename))
        elif not end_found:
            raise JSScriptException(
                "End of script '{}' not found in '{}'".format(
                    script_name, self._filename))
        return out


external_javascript = JSScript('scripts.js')

__all__ = [external_javascript]
