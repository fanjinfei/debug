//myCtrl.$inject = ['myService'];
function format(source, params) {
    $.each(params,function (i, n) {
        source = source.replace(new RegExp("\\{" + i + "\\}", "g"), n);
    })
    return source;
};

function myCtrl($scope, $compile, $location, $translate, myService) {
    var _this = this;
    var searchObject = $location.search();
    $scope.q = searchObject.q;
    $scope.total = 0;
    $scope.current_page = 1;
    $scope.page_size = 20;
//        $scope.q= "fan";
    $scope.count= 0;
    
    $scope.pages =[];
    $scope.numPages =10;
    $scope.currentPage=2;
   
    
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

    $scope.get_search = function() {
//        $scope.msg = myService.getStatus() + ' clicked';
//        $scope.msg = myService.getStatus() ;
        _this.ready = false;
        myService.getSearch($scope.q, $scope.current_page, $scope.page_size, $scope.q_lang).then(function($resp) {
            var $mva = $resp.data; //async; it has to be bind later
            _this.ready = true;
            $scope.results = $resp.data ; // this is resolved

            $scope.numPages = 10; //Math.ceil(result.data.Total / result.data.PageSize);
            showResults($scope, $compile, $resp.data)
        });
    }

    $scope.onSelectPage = function (page) {
        $scope.current_page = page;
        $scope.get_search();
    }

    $scope.changeLanguage = function(lang){
          $translate.use(lang); 
    }

    $scope.EnterKeyPressed = function($event){
        var keyCode = $event.which || $event.keyCode;
        if (keyCode === 13) {
            $scope.get_search()
        }
   };    

    if ($scope.q) {
        $scope.get_search();
    }
    $scope.q_lang = getSearchLang();
    $translate.use($scope.q_lang);
};

function myCtrlMenu($scope, $location) {
    $scope.uname= $location.absUrl();
    console.log($location);
};

angular.module('myApp').controller('myCtrl', ['$scope', '$compile', '$location', '$translate', 'myService', myCtrl]);
angular.module('myApp').controller('myCtrlMenu', ['$scope', '$location',myCtrlMenu]);

function getSearchLang(){
    var target = document.getElementById('search_lang');
    return target.getAttribute('lang');
}
function showResults($scope, $compile, $data){
//    console.log($data);
//    var target = document.getElementById('search_results');
    var target = document.getElementById('search_results');
    angular.forEach($data.docs, function($value, key) {
        var url = $value.attr_strurl;
        var title = $value.attr_fldtitle;
        var description = $value.description;
        var release_date = $value.attr_strdate;
//        var newEle = angular.element(format("<res-item ready='myCtl.ready' url='{0}' title='red' description='ef' releasedate='2018-10-10'> </res-item>", [url]));
        var newEle = angular.element("<res-item ready='myCtl.ready' url='"+url+"' title='"+title+"' description='"+description+"' releasedate='"+release_date+"'> </res-item>");
//        var newEle = angular.element(document.createElement('my-results'));
        $compile(newEle)($scope);
        angular.element(target).append(newEle);
        //console.log($value)
    })
}

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

/*
<div ng-app="hello">
    <div ng-controller="pagingCtrl">
        <paging>
            <table class="table table-striped table-bordered table-hover">
                <tr><th>id</th><th>name</th></tr>
                <tr ng-repeat="item in data"><td>{{item.id}}</td><td>{{item.name}}</td></tr>
            </table>
            <ul class="pagination"
                num-pages="tasks.pageCount"
                current-page="tasks.currentPage"
                on-select-page="selectPage(page)">
                <li ng-class="{disabled: noPrevious()}">
                    <a ng-click="selectPrevious()">&laquo;</a>
                </li>
                <li ng-repeat="page in pages"
                    ng-class="{active: isActive(page)}">
                    <a ng-click="selectPage(page)">{{page}}</a>
                </li>
                <li ng-class="{disabled: noNext()}">
                    <a ng-click="selectNext()">&raquo;</a>
                </li>
            </ul>
        </paging>
    </div>
</div>


        $scope.currentPage = 1;
        $scope.numPages = 5;
        $scope.pageSize = 10;
        $scope.pages = [];
        //get first page
        $http.get('url',
                {
                    method: 'GET',
                    params: {
                        'pageNo': $scope.currentPage,
                        'pageSize': $scope.pageSize
                    },
                    responseType: "json"
                }).then(function (result) {
                    $scope.data = result.data.Data;
                    $scope.numPages = Math.ceil(result.data.Total / result.data.PageSize);
                });
                
        $scope.onSelectPage = function (page) {
            //replace your real data
            $http.get('url',
                {
                    method: 'GET',
                    params: {
                        'pageNo': page,
                        'pageSize': $scope.pageSize
                    },
                    responseType: "json"
                }).then(function (result) {
                    $scope.data = result.data.Data;
                    $scope.numPages = Math.ceil(result.data.Total / result.data.PageSize);
                });
        };
    });
    
    myModule.directive('paging', function() {
        return {
            restrict: 'E',
            //scope: {
            //    numPages: '=',
            //    currentPage: '=',
            //    onSelectPage: '&'
            //},
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
    });
*/
