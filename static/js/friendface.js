angular.module('friendface', [])

.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.headers.common["X-Requested-With"] = 'XMLHttpRequest';
}])

.controller('Main', function ($scope, $http) {
    $scope.state = Object();

    $scope.get_threads = function () {
        $http.get('/thread').then(
            function (r) {
                $scope.state.threads = r.data.threads;
                $scope.load_thread($scope.state.threads[0]);
            },
            function () { alert('Could not get threads!'); }
        );
    };

    $scope.create_thread = function () {
        $http.post('/thread').then(
            function (r) {},
            function () { alert('Could not create thread!'); }
        );
    };

    $scope.load_thread = function (thread_id) {
        $http.get('/thread/' + thread_id).then(
            function (r) {
                $scope.state.current_thread = r.data;
            },
            function () { alert('Could not load thread ' + thread_id); }
        );
    };

    $scope.create_message = function (thread_id) {
        $http.post('/thread/' + thread_id, $scope.state.message_text).then(
            function (r) {
            },
            function () { alert('Could not create message :(') }
        );
    };

    $scope.get_threads();
});
