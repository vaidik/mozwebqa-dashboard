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
                match = {
                    rule_name: {
                        'reason': match.groups()[0]
                    }
                }
                result[method_name].update(match)

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
    def parse_result(result):
        rules = {
            'github': {
                'search': (r'((http:|https:)//[^ \<]*github\.com'
                           r'([^ \<]*[^ \<\.\"\']))'),
                'replace': r'https://api.github.com/repos\3',
            },
            'bugzilla': {
                'search': r'((?:Bugzilla|bugzilla|bug|Bug) ([0-9]+))',
                'replace': (r'https://api-dev.bugzilla.mozilla.org/'
                            r'latest/bug/\2'),
            },
        }

        links = []

        for rule_name, rule in rules.iteritems():
            for result_type in result.keys():
                reason = result[result_type]['reason']
                try:
                    if isinstance(rule, dict):
                        match = re.search(rule['search'], reason)
                        url = match.groups()[0]
                        if rule.get('replace', None):
                            url = re.sub(rule['search'], rule['replace'], url)
                    elif isinstance(rule, str):
                        match = re.search(rule, reason)
                        url = match.groups()[0]
                    string = match.groups()[0]

                    links.append({'url': url,
                                  'status': 'Getting status...',
                                  'raw': string})

                    if 'github' in string and 'issues' in string:
                        url_split = url.split('/')
                        to_use = '%s/%s-#%s' % (url_split[4], url_split[5],
                                                url_split[7])
                    else:
                        to_use = string
                    links[len(links)-1].update(to_use=to_use)

                except AttributeError:
                    pass

        return links

    @staticmethod
    def clean_result(parsed_data):
        ret_val = []

        for dir, dir_contents in parsed_data.iteritems():
            for f, f_contents in dir_contents.iteritems():
                for method, results in f_contents.iteritems():
                    for result_type in results.keys():
                        if len(results.keys()) != 0:
                            links = TestsParser.parse_result(results)
                            results[result_type]['links'] = links

                            # Strip quotes
                            results[result_type]['reason'] = results[
                                result_type]['reason'].strip('\'').strip('\"')

                            ret_val.append({
                                'dir': dir,
                                'file': f,
                                'method': method,
                                'results': results,
                            })

        return ret_val

if __name__ == '__main__':
    rules = {
        'skip': 'skip\((?:reason=)?(.*)\)',
        'skipif': 'skipif\((?:reason=)?(.*)\)',
        'xfail': 'xfail\((?:reason=)?(.*)\)',
    }

    if len(sys.argv) < 2:
        raise ValueError('Provide directory name to parse.')

    parser = TestsParser(sys.argv[1], rules)
    print json.dumps({
        'response': TestsParser.clean_result(parser.parse()),
    }, indent=2)
