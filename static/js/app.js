var app = angular.module('MobileNews', ['mm.foundation', 'slick', 'ngRoute', 'angular-loading-bar', 'angular-spinkit', 'ngAnimate'])

app.config(["$routeProvider", '$locationProvider', function($routeProvider, $locationProvider){
    $locationProvider.html5Mode(true)
    $routeProvider.when("/", {
        controller: "IndexCtrl",
        templateUrl: '/static/templates/index.html'
    }).when("/p/:id", {
        controller: "PassageCtrl",
        templateUrl: "/static/templates/passage.html"
    }).otherwise({
        controller: "NotFoundCtrl",
        // templateUrl: "/static/template/404.html"
    })
}])

app.filter("table", function(){
    return function(array){
        if (angular.isArray(array)){
            return array.join(" / ")
        }else{
            return ''
        }
    }
})

app.factory('api', ['$http', function($http){
    var api = {};
    api.passage = function(id){
        return $http.get("/api/p/"+ id)
    }
    api.index = function(id){
        return $http.get('/api/index')
    }
    return api;
}])

app.run(["$rootScope", 'api', "$route",  function($rootScope, api, $route){
    api.changeTitle = function(title){
        $rootScope.title = title
    }
    api.loading_finish = function(){
        $rootScope.loading = false;
        console.log('loading finish!')
    }
    $rootScope.title = '新闻中心'
    $rootScope.loading = true
}])

app.controller('IndexCtrl', ['api', '$scope', function(api, $scope){
    console.log("Index!")
    api.changeTitle('新闻中心')
    api.index().then(function(response){
        console.log(response.data)
    })
    var test = JSON.parse('["http://www.new1.uestc.edu.cn/upload/image/c04efff3a64c9674e38adede69a73570.jpg", "http://www.new1.uestc.edu.cn/upload/image/164737f0710abd8934605f6cc36e5ca8.jpg", "http://www.new1.uestc.edu.cn/upload/image/942b9a6be5aa21021a1421aacaffbe79.jpg", "http://www.new1.uestc.edu.cn/upload/image/a36d5c3cc977a2fbfb53640bf8defee7.jpg", "http://www.new1.uestc.edu.cn/upload/image/c11aa96143a77e28bb94bd88f8157b43.jpg"]')
    $scope.slides = [{"dest": "1", "pid": "49922", "img": test[0]},{"dest": "2", "pid": "49922", "img": test[1]},{"dest": "3", "pid": "49922", "img": test[2]}]
    api.loading_finish()
    $scope.menus = [
        {name:"链接一", link:'#'},
        {name:"链接一", link:'#'},
        {name:"链接一", link:'#'},
        {name:"链接一", link:'#'},
        {name:"链接一", link:'#'},
    ]
}])

app.controller('PassageCtrl', ['api', '$scope', '$routeParams', '$sce', function(api, $scope, $routeParams, $sce){
    api.passage($routeParams.id).then(function(result){
        $scope.passage = result;
        $scope.passage.content = $sce.trustAsHtml(result.content)
        api.changeTitle(result.title)
        console.log("loaded passage of ", $routeParams.id)
        api.loading_finish()
    })
}])

app.controller('NotFoundCtrl', ['$route', function($route){
    console.log($route.url())
}])
