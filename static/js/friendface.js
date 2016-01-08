angular.module('friendface', ['btford.markdown', 'ngDialog'])

.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.headers.common["X-Requested-With"] = 'XMLHttpRequest';
}])

.controller('Main', function ($scope, $http, ngDialog) {
    $scope.state = Object();
    $scope.branches = Array();
    $scope.branch = Object();
    $scope.root = Object();

    $scope.get_branches = function () {
        $http.get('/b').then(
            function (r) {
                $scope.branches = r.data.branches;
            },
            function () { alert('Could not get branches!'); }
        );
    };

    $scope.get_branch = function (key) {
        $http.get('/b/' + key).then(
            function (r) {
                $scope.branch = r.data;
                $scope.root = [$scope.branch.root];
            },
            function () { alert('Could not get branch ' + key + '!'); }
        );
    };

    $scope.load_message = function (message_id) {
        $http.get('/m' + message_id).then(
            function (r) {
                $scope.state.current_data = r.data;
            },
            function () { alert('Could not load message ' + message_id); }
        );
    };


    $scope.get_message_url = function (key) {
        return '/m/' + key;
    };

    $scope.reply = function (message) {
        ngDialog.open({
            template: 'message_form.html',
            data: {
                message: message,
            },
            controller: ['$scope', '$http', function ($scope, $http) {
                $scope.create_message = function (data, in_reply_to) {
                    $http({
                        method: 'POST',
                        url: '/m',
                        headers: {
                            'Content-Type': 'text/markdown',
                            'In-Reply-To': in_reply_to.key,
                        },
                        data: data,
                    }).then(
                        function (r) {
                            $scope.closeThisDialog();
                            in_reply_to.replies.push({
                                key: r.headers('Key'),
                                replies: Array(),
                            });
                        },
                        function () { alert('Could not create message :(') }
                    );
                };
            }],
        });
    };

    $scope.get_branches();
});
