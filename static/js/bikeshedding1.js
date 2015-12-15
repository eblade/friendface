angular.module('bikeshedding', [])

.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.headers.common["X-Requested-With"] = 'XMLHttpRequest';
}])

.controller('Main', function ($scope, $http) {
    $scope.test = "Hello World";
});
