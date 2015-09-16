(function(){
    var app = angular.module('MobileNews', ['mm.foundation', 'slick', 'ngRoute', 'angular-loading-bar', 'angular-spinkit', 'ngAnimate'])

    function LinkTranslate(link){
        if (/Category/.test(link)){
            return "#/category/"+link.match(/\d+/)
        }else if(/Document\.ArticlePage/.test(link)){
            return "#/post/"+link.match(/\d+/)
        }else{
            console.warn("Unknow url", link)
            return link
        }
    }

    var CATEGORYS = {
        focus: 42,
    }
    app.config(["$routeProvider", '$locationProvider', function($routeProvider, $locationProvider){
        $routeProvider.when("/", {
            controller: "IndexCtrl",
            templateUrl: '/static/templates/index.html'
        }).when("/post/:id", {
            controller: "PassageCtrl",
            templateUrl: "/static/templates/passage.html"
        }).when("/category/:column",{
            controller: "ColumnCtrl",
            templateUrl: "/static/templates/column.html"
        }).otherwise({
            controller: "NotFoundCtrl",
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
        api.column = function(column, page){
            var url = page == undefined ? "/api/column/"+column: "/api/column/"+column + "?page="+page
            return $http.get(url)
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

    app.controller('IndexCtrl', ['api', '$scope', '$q', function(api, $scope, $q){
        console.log("Index!")
        api.changeTitle('新闻中心')
        api.index().then(function(response){
            console.log(response.data)
            $scope.top = response.data.general;
            $scope.slides = response.data.slides;
            api.loading_finsih()
        }, function(){
            alert("载入失败了，刷新试试？")
        })
        // var q1 = api.index().then(function(response){
        //     console.log(response.data)
        //     $scope.top = response.data.general.map(function(x){
        //         x.img = x.img.length ? x.img[0] : undefined;
        //         return x
        //     }).slice(5)
        // })

        // var q2 = api.column(CATEGORYS.focus).then(function(response){
        //     console.log(response.data)
        //     $scope.slides = response.data.slice(5)
        // })

        // var q = $q.all([q1, q2]).then(function(){
        //     api.loading_finish()
        // }, function(){
        //     alert('啊咧！载入失败了，刷新试试？')
        // })

    }])

    app.controller('PassageCtrl', ['api', '$scope', '$routeParams', '$sce', function(api, $scope, $routeParams, $sce){
        api.passage($routeParams.id).then(function(result){
            $scope.passage = result.data;
            $scope.passage.content = $sce.trustAsHtml(result.data.content)
            api.changeTitle(result.data.title)
            console.log("loaded passage of ", $routeParams.id)
            api.loading_finish()
        })
    }])

    app.controller("ColumnCtrl", ["api", "$scope", "$routeParams", function(api, $scope, $routeParams){
        api.column($routeParams.column).then(function(response){
            $scope.items = response.data
        })
        api.loading_finish()
        $scope.page = 1
        $scope.load = function(){
            api.column($routeParams.column, $scope.page + 1).then(function(response){
                $scope.items.push.apply($scope.items, response.data)
                $scope.page += 1;
            })
        }
    }])

    app.controller('NotFoundCtrl', ['$route', function($route){
        console.log($route.url())
    }])

    app.controller("SideCtrl", ['$scope', function($scope){
        $scope.columns = [
            {name: "首页", link: "#/"},
            {name: "焦点新闻", link: "#/column/top"},
        ]
    }])

    app.controller("MenuCtrl", ['$scope', function($scope){
        $scope.menus = [
            {name:"焦点新闻", link:'#/category/42'},
            {name:"校园时讯", link:'#/category/50'},
            {name:"合作交流", link:'#/category/45'},
            {name:"成电人物", link:'#/category/48'},
        ]
    }])
})()