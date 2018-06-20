//myCtrl.$inject = ['myService'];
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

angular.module('myApp').controller('myCtrl', ['$scope', 'myService', myCtrl]);
angular.module('myApp').controller('myCtrlMenu', ['$scope', '$location',myCtrlMenu]);

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
