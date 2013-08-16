var app = angular.module('dashboard', []);

app.factory('parseImpUrl', function() {
    var rules = [
        {
            'search': '((?:Bugzilla|bugzilla|bug|Bug) ([0-9]+))',
            'replace': '<a href="https://bugzilla.mozilla.org/show_bug.cgi?id=$2">$1</a>',
        },
        {
            'function': function(text) {
                var ret_val = {};
                var urlPattern = /[^\"|\'](http|ftp|https):\/\/[\w-]+(\.[\w-]+)+([\w.,@?^=%&amp;:\/~+#-]*[\w@?^=%&amp;\/~+#-])?/gi;
                angular.forEach(text.match(urlPattern), function(url) {
                    ret_val.match = url;
                    ret_val.replace = url.replace(url, "<a href="+ url + ">" + url +"</a>");
                    //text = text.replace(url, "<a href="+ url + ">" + url +"</a>");
                });
                return ret_val;
            },
        },
    ];

    return function(text) {
        var ret_val = {
            matches: [],
            replaces: [],
        };
        angular.forEach(rules, function(element, index, arr) {
            if ('search' in element) {
                var regex = new RegExp(element.search);
                var match = text.match(regex);
                if (match) {
                    ret_val.matches.push(match[0]);
                    ret_val.replaces.push(match[0].replace(regex, element.replace));
                }
            } else if ('function' in element) {
                var match_dict = element.function(text);
                ret_val.matches.push(match_dict.match);
                ret_val.replaces.push(match_dict.replace);
            }
        });

        return ret_val;
    };


    var urlPattern = /[^\"|\'](http|ftp|https):\/\/[\w-]+(\.[\w-]+)+([\w.,@?^=%&amp;:\/~+#-]*[\w@?^=%&amp;\/~+#-])?/gi;

    return function(text) {
        var urls = [];
        angular.forEach(text.match(urlPattern), function(url) {
            urls.push(url);
        });
        return urls;
    };
});

var TestAnalysisCtrl = function($scope, $http, parseImpUrlService) {
    var parseImpUrl = parseImpUrlService;
    $scope.parse_data = {};

    $scope.init = function() {
        $http.get('config.json').success(function(data) {
            for (var repo in data.repos) {
                repo = data.repos[repo].split('/');
                repo = repo[repo.length - 1];
                
                (function(repo_name) {
                    $http.get('dumps/' + repo_name + '.json?t=' + new Date().getTime()).success(function(data) {
                        $scope.parse_data[repo_name] = data;

                        var reason;
                        angular.forEach($scope.parse_data[repo_name], function(val, key) {
                            reason = val.results.skip_or_xfail[1];
                            $scope.parse_data[repo_name][key].results.skip_or_xfail.push(parseImpUrl(reason));
                        });
                        Hyphenator.run();
                    });
                }) (repo);
            }
        });
    }
};
TestAnalysisCtrl.$inject = ['$scope', '$http', 'parseImpUrl'];

var linkify = function() {
    var rules = [
        {
            'search': '((?:Bugzilla|bugzilla|bug|Bug) ([0-9]+))',
            'replace': '<a href="https://bugzilla.mozilla.org/show_bug.cgi?id=$2">$1</a>',
        },
        {
            'function': function(text) {
                var urlPattern = /[^\"|\'](http|ftp|https):\/\/[\w-]+(\.[\w-]+)+([\w.,@?^=%&amp;:\/~+#-]*[\w@?^=%&amp;\/~+#-])?/gi;
                angular.forEach(text.match(urlPattern), function(url) {
                    text = text.replace(url, "<a href="+ url + ">" + url +"</a>");
                });
                return text;
            },
        },
    ];

    return function(input) {
        angular.forEach(rules, function(element, index, arr) {
            if ('search' in element) {
                input = input.replace(new RegExp(element.search), element.replace);
            } else if ('function' in element) {
                input = element.function(input);
            }
        });

        return input;
    };
};
linkify.$inject = [];
app.filter('linkify', linkify);
