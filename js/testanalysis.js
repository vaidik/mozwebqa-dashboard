app.controller('testanalysis', function($scope, $http) {
    $scope.parse_data = {};

    $scope.init = function() {
        $http.get('config.json').success(function(data) {
            for (var repo in data.repos) {
                repo = data.repos[repo].split('/');
                repo = repo[repo.length - 1];
                
                (function(repo_name) {
                    $http.get('dumps/' + repo_name + '.json').success(function(data) {
                        $scope.parse_data[repo_name] = data;
                        Hyphenator.run();
                    });
                }) (repo);
            }
        });
    }
});