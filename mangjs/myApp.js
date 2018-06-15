
var app = angular.module('myApp', ['ngRoute']).config(function($sceDelegateProvider) {
 $sceDelegateProvider.resourceUrlWhitelist([
   // Allow same origin resource loads.
   'self',
   // Allow loading from our assets domain.  Notice the difference between * and **.
   'https://*.github.com/api/**']);
 });
app.config(function($routeProvider) {
    $routeProvider
    .when("/", {
        templateUrl : "main.html"
    }).when("/red", {
        templateUrl : "red.html"
    });
    
});
app.config(['$locationProvider', function($locationProvider) {
        $locationProvider.hashPrefix('');
        // use the HTML5 History API
    }]);
 


