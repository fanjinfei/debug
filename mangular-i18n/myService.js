
//myService.$inject = ['$http'];
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
    _this.getSearch = function getSearch($q, $current_page, $page_size, $q_lang) {
        return $http({
            method: 'get',
            url: 'http://localhost:8001/api/en/ws2019?q='+$q+'&start='+$current_page+'&rows='+$page_size+'&lang='+$q_lang,
        });
    }    
}

angular.module('myApp').service('myService', ['$http', myService]);

function appendTransform(defaults, transform) {
  defaults = angular.isArray(defaults) ? defaults : [defaults];
  return defaults.concat(transform);
}

//module.exports = myService;
