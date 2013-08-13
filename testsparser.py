#!/bin/python

import json
import os
import re
import sys


class TestsParser(object):

    def __init__(self, tests_dir, rules):
        self.dir = tests_dir
        self.rules = rules

    def walk(self):
        result = {}

        for entry in os.walk(self.dir):
            if not re.search('.git', entry[0]):
                result.update({entry[0]: {}})
                for f in entry[2]:
                    if re.search('.py', f):
                        result[entry[0]].update({f: {}})

        return result

    def _get_methods(self, test_contents):
        lines = test_contents.split('\n')
        found = 0
        defs = []

        start_regex = ' def| @.*'

        for i in xrange(len(lines)):
            line = lines[i]
            if found == 1:
                if not re.search(start_regex, line):
                    defs[len(defs)-1] += '\n' + line
                else:
                    if i-start_line['line'] <= 3:
                        defs[len(defs)-1] += '\n' + line
                    else:
                        found = 0

            if re.search(start_regex, line) and found == 0:
                start_line = {
                    'line': i,
                    'line_content': line,
                }
                found = 1
                defs.append(line)

        return defs

    def _apply_rules_on_methods(self, method):
        result = {}

        method_name = re.search('def (.*) *\(', method).groups()[0]
        result.update({method_name: {}})

        for rule_name, rule in self.rules.iteritems():
            match = re.search(rule, method)
            if match:
                result[method_name].update({rule_name: list(match.groups())})

        return result

    def parse(self):
        files = self.walk()

        for d in files.keys():
            for f in files[d]:
                test_file = open('%s/%s' % (d, f))
                test_contents = test_file.read()
                test_file.close()

                methods = self._get_methods(test_contents)
                files[d][f] = map(self._apply_rules_on_methods, methods)

        return files


if __name__ == '__main__':
    rules = {
        'skip_or_xfail': '(skip|xfail).*\((.*)\)',
    }

    if len(sys.argv) < 2:
        raise ValueError('Provide directory name to parse.')

    parser = TestsParser(sys.argv[1], rules)
    print json.dumps(parser.parse(), indent=4)
