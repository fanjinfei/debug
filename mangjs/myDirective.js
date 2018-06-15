
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
    }
  }
}

angular.module('myApp').directive('yepNope', YepNopeDirective);
angular.module('myApp').directive('myResults', myResults);

