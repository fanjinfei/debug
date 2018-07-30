
var angular = require('angular');
var ngRoute = require('angular-route');
var ngTranslate = require('angular-translate');

//import angular from 'angular';
//import 'angular-route';
'use strict';

console.log('app started');


//var app = angular.module('myApp', [ngRoute]);

var app = angular.module('myApp', ['ngRoute','pascalprecht.translate']).config(['$sceDelegateProvider', function($sceDelegateProvider) {
 $sceDelegateProvider.resourceUrlWhitelist([
   // Allow same origin resource loads.
   'self',
   'http://localhost:8001/**',
   // Allow loading from our assets domain.  Notice the difference between * and **.
   'https://*.github.com/api/**']);
 }]);

app.config(['$routeProvider', function($routeProvider) {
    $routeProvider
    .when("/", {
//        templateUrl : "js/main.html"
        template: require("./main.html")
//        template: "<p>welcome</p>"
    }).when("/red", {
//        template : require("/home/jffan/src/debug/mangjs-pack/red.html"),
        template: "<p>welcome</p>"
//        controller: "myCtrl"
    });
    
}]);

app.config(['$locationProvider', function($locationProvider) {
        $locationProvider.hashPrefix('');
        // use the HTML5 History API
    }]);

app.config(['$translateProvider', function($translateProvider) {
  $translateProvider.translations('en', {
    SEARCH: 'Search',
    SEARCH_PLACEHOLDER: 'Please input search term',
    TITLE: 'Login Form',
    USERNAME: 'Username',
    PASSWORD: 'Password',
    LOGIN: 'Login'
  });
 
  $translateProvider.translations('fr', {
    SEARCH: 'Recherche',
    SEARCH_PLACEHOLDER: 'Recherche S.V.P term',
    TITLE: 'Formulaire de login',
    USERNAME: 'Identifiant',
    PASSWORD: 'Mot de passe',
    LOGIN: 'Connexion'
  });
  $translateProvider.useSanitizeValueStrategy(null);
//  $translateProvider.determinePreferredLanguage();
}]);
 
/*
function myCtrl($scope, myService) {
    var _this = this;
    $scope.firstName= "John";
    $scope.lastName= "Doe";
    $scope.fname= "fan";
    $scope.count= 0;
    
    $scope.go = function() {
//        $scope.msg = myService.getStatus() + ' clicked';
//        $scope.msg = myService.getStatus() ;
        _this.ready = false;
        myService.getStatus().then(function(resp) {
            var $mva = resp.data; //async; it has to be bind later
            _this.ready = true;
            $scope.msg = resp.data + ' clicked'; // this is resolved
            $scope.count = addElement($scope.count)
        });
        $scope.count += 1;
    }

    $scope.EnterKeyPressed = function($event){
        var keyCode = $event.which || $event.keyCode;
        if (keyCode === 13) {
            $scope.go()
        }
   };    

};

function myCtrlMenu($scope, $location) {
    $scope.uname= $location.absUrl();
    console.log($location);
};

function addElement($count){
    var newEle = angular.element("<div class='red'> text</div>");
    var target = document.getElementById('res1');
    if ($count <10) {
        angular.element(target).append(newEle);
    } else {
        angular.element(target).html('');
        $count = 0
    }
    return $count;
};



function myResults() {
    return {
        template : "<h1>my results</h1> {{fname}} <button ng-click='go()'>Click Me!</button> {{ msg }} {{count}} \
         <a ng-href='#here'> here </a> <br>\
         \
        "
    };
};

function YepNopeDirective() {
  return {
    restrict: 'E',
    link: function (scope, element, attrs) {
      scope.$watch(attrs.check, function (val) {
        var words = val ? 'Yep' : 'Nope';
        element.text(words);
      });
    },
  }
}

function myService($http) {
    var _this = this;
    _this.getStatus = function getStatus() {
        return $http({
            method: 'jsonp',
//            url: 'https://status.github.com/api/status.json?callback=JSON_CALLBACK',
            url: 'https://status.github.com/api/status.json',
            transformResponse: appendTransform($http.defaults.transformResponse, function(value) {
                //console.log( value.status);
                return value.status;
//                return (value.status === 'good');
            })
        });
    }
    _this.getResults = function getResults() {
        return $http({
            method: 'jsonp',
            url: 'https://status.github.com/api/status.json?callback=JSON_CALLBACK',
            transformResponse: appendTransform($http.defaults.transformResponse, function(value) {
                return (value.status === 'good');
            })
        });
    }
}

function appendTransform(defaults, transform) {
  defaults = angular.isArray(defaults) ? defaults : [defaults];
  return defaults.concat(transform);
}


app.controller('myCtrl', ['$scope', 'myService', myCtrl]);
app.controller('myCtrlMenu', ['$scope', '$location',myCtrlMenu]);
app.directive('yepNope', YepNopeDirective);
app.directive('myResults', myResults);
app.service('myService', ['$http', myService]);
*/
require('./myDirective');
require('./myService');
require('./myCtrl');

//export default "myApp";


