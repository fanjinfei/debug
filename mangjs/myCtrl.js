
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

angular.module('myApp').controller('myCtrl', ['$scope', 'myService', myCtrl]);
