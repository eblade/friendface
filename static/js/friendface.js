angular.module('friendface', [])

.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.headers.common["X-Requested-With"] = 'XMLHttpRequest';
}])

.controller('Main', function ($scope, $http) {
    $scope.state = Object();

    $scope.get_messages = function () {
        $http.get('/m').then(
            function (r) {
                $scope.state.messages = r.data.messages;
            },
            function () { alert('Could not get messages!'); }
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

    $scope.create_message = function () {
        $http.post('/m', $scope.state.message_text).then(
            function (r) {
            },
            function () { alert('Could not create message :(') }
        );
    };

    $scope.get_messages();
});
