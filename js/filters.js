angular.module('dashboardFilters', []).filter('linkify', function() {
    var rules = [
        {
            'search': '((?:Bugzilla|bugzilla|bug|Bug) ([0-9]+))',
            'replace': '<a href="https://bugzilla.mozilla.org/show_bug.cgi?id=$2">$1</a>',
        }
    ];

    return function(input) {
        for (rule in rules) {
            var match = input.match(rules[rule]);
            input = input.replace(new RegExp(rules[rule].search), rules[rule].replace);
        }
        return input;
    };
});

angular.module('dashboardFilters').filter('parseUrlFilter', function() {
    var urlPattern = /[^\"|\'](http|ftp|https):\/\/[\w-]+(\.[\w-]+)+([\w.,@?^=%&amp;:\/~+#-]*[\w@?^=%&amp;\/~+#-])?/gi;
    return function(text, target) {
        angular.forEach(text.match(urlPattern), function(url) {
            text = text.replace(url, "<a target=\"" + target + "\" href="+ url + ">" + url +"</a>");
        });
        return text;
    };
});