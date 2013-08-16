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
        previous = None
        defs = []

        start_regex = '^ +(def |@).*'

        for i in xrange(len(lines)):
            line = lines[i]
            if found == 1:
                matches = re.search(start_regex, line)
                if matches:
                    if previous is not None:
                        defs[len(defs)-1] += '\n' + line
                        previous = matches.groups()[0].strip()
                    else:
                        found = 0
                elif re.search(' +#.*', line):
                    defs[len(defs)-1] += '\n' + line
                elif re.search(' +class', line):
                    found = 0
                    previous = None
                else:
                    defs[len(defs)-1] += '\n' + line
                    if previous == 'def':
                        previous = None

            matches = re.search(start_regex, line)
            if matches and found == 0:
                start_line = {
                    'line': i,
                    'line_content': line,
                }
                found = 1
                previous = matches.groups()[0].strip()
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
        def merge_dicts(x, y):
            x.update(y)
            return x

        files = self.walk()

        for d in files.keys():
            for f in files[d]:
                test_file = open('%s/%s' % (d, f))
                test_contents = test_file.read()
                test_file.close()

                methods = self._get_methods(test_contents)
                results = map(self._apply_rules_on_methods, methods)

                results.append({})
                results.append({})
                files[d][f] = reduce(merge_dicts, results)

        return files

    @staticmethod
    def clean_result(parsed_data):
        ret_val = {}

        for dir, dir_contents in parsed_data.iteritems():
            for f, f_contents in dir_contents.iteritems():
                for method, results in f_contents.iteritems():
                    if len(results.keys()) != 0:
                        ret_val.update({
                            '%s:%s:%s' % (dir, f, method): {
                                'dir': dir,
                                'file': f,
                                'method': method,
                                'results': results,
                            }
                        })

        return ret_val


if __name__ == '__main__':
    rules = {
        'skip_or_xfail': '(skip|xfail|skipif)\((?:reason=)?(.*)\)',
    }

    if len(sys.argv) < 2:
        raise ValueError('Provide directory name to parse.')

    parser = TestsParser(sys.argv[1], rules)
    print json.dumps(TestsParser.clean_result(parser.parse()), indent=4)
