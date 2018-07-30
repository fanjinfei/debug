
function myResults() {
    return {
        template : "<h1>my results</h1> {{fname}} <button ng-click='go()'>Click Me!</button> {{ msg }} {{count}} \
         <a ng-href='#here'> here </a> <br>\
         \
        "
    };
};

function result_item() {
    return {
        restrict:'E',
        scope: {
            title: '@',
            url: '@',
            description: '@',
            releasedate: '@',
        },
/*        template: 
'<li class="mrgn-bttm-md"> \
    <span class="results_title">1. \
      <a href="{{ url }}">  {{ title }}      </a> \
       </span> \
          <span class="results_description" tabindex="0" style="display: none;"> \
            <span data-name="summary" style="display: none;"> {{ description }}   </span> \
            <span class="wb-inv">Release date</span>  \
            <span data-name="docdate" style="display: none;" class="text-muted">  {{ releasedate }}  </span> \
         </span> \
       <hr class="drk-grey" style="display: none;"> \
</li>' */
        template: 
'<li > \
    <span class="results_title">1. \
      <a href="{{ url }}">  {{ title }}      </a> <br>\
       </span> \
          <span class="results_description" tabindex="0" "> \
            <span data-name="summary"> {{ description }}   </span> \
            <span>Release date</span>  \
            <span >  {{ releasedate }}  </span> \
         </span> \
       <hr class="drk-grey" style="display: none;"> \
</li>'

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

function PagingDirective() {
    return {
            restrict: 'E',
            //scope: {
            //    numPages: '=',
            //    currentPage: '=',
            //    onSelectPage: '&'
            //},
/*            scope: {
                numPages: '=',
                currentPage: '=',
                onSelectPage: '&'
            },*/
            template: '',
            replace: true,
            link: function(scope, element, attrs) {
                scope.$watch('numPages', function(value) {
                    scope.pages = [];
                    for (var i = 1; i <= value; i++) {
                        scope.pages.push(i);
                    }
                    alert(scope.currentPage )
                    if (scope.currentPage > value) {
                        scope.selectPage(value);
                    }
                });
                scope.isActive = function(page) {
                    return scope.currentPage === page;
                };
                scope.selectPage = function(page) {
                    if (!scope.isActive(page)) {
                        scope.currentPage = page;
                        scope.onSelectPage(page);
                    }
                };
                scope.selectPrevious = function() {
                    if (!scope.noPrevious()) {
                        scope.selectPage(scope.currentPage - 1);
                    }
                };
                scope.selectNext = function() {
                    if (!scope.noNext()) {
                        scope.selectPage(scope.currentPage + 1);
                    }
                };
                scope.noPrevious = function() {
                    return scope.currentPage == 1;
                };
                scope.noNext = function() {
                    return scope.currentPage == scope.numPages;
                };

            }
        };
}
angular.module('myApp').directive('yepNope', YepNopeDirective);
angular.module('myApp').directive('myResults', myResults);
angular.module('myApp').directive('resItem', result_item);
angular.module('myApp').directive('paging', PagingDirective);

