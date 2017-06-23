(function(){
    var app = angular.module('MobileNews', ['mm.foundation', 'slick', 'ngRoute', 'angular-loading-bar', 'angular-spinkit', 'ngAnimate'])

    //http://stackoverflow.com/questions/901115/how-can-i-get-query-string-values-in-javascript
    function getParameterByName(name, url) {
        name = name.replace(/[\[\]]/g, "\\$&");
        var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
            results = regex.exec(url);
        if (!results) return null;
        if (!results[2]) return '';
        return decodeURIComponent(results[2].replace(/\+/g, " "));
    }

    function parseLink(link) {
      if (/ArticlePage/.test(link) && getParameterByName("Id", link)){
        return '/post/' + getParameterByName("Id", link)
      }
      if (/Category/.test(link) && getParameterByName("CatId", link)) {
        return '/category/' + getParameterByName("CatId", link)
      }
    }
    function buildLink(params) {
      return "http://www.new1.uestc.edu.cn/?n=UestcNews.Front.Document.ArticlePage&Id=" + params.id
    }

    app.config(["$routeProvider", '$locationProvider', function($routeProvider, $locationProvider){
        $locationProvider.html5Mode(true)
        $routeProvider.when("/", {
            controller: "IndexCtrl",
            templateUrl: '/static/templates/index.html'
        }).when("/post/:id", {
            controller: "PassageCtrl",
            templateUrl: "/static/templates/passage.html"
        }).when('/category/annoucement', {
            controller: "annoucementCtrl",
            templateUrl: "/static/templates/annoucement.html"
        }).when("/category/:column",{
            controller: "ColumnCtrl",
            templateUrl: "/static/templates/column.html"
        }).otherwise({
            controller: "NotFoundCtrl",
            template: "您的页面没有找到……"
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
        // var prefix = "/mobile"
        var prefix = ""
        api.passage = function(id){
            return $http.get(prefix+"/api/p/"+ id)
        }
        api.index = function(id){
            return $http.get(prefix+'/api/index')
        }
        api.column = function(column, page){
            var url = page == undefined ? "/api/column/"+column : "/api/column/" + column + "?page="+page
            return $http.get(prefix+url)
        }
        return api;
    }])

    app.run(["$rootScope", 'api', "$route", "$location", "$log", function($rootScope, api, $route, $location, $log){
        api.changeTitle = function(title){
            $rootScope.title = title
            document.title = title
        }
        api.loading_finish = function(){
            $rootScope.loading = false;
            console.log('loading finish!')
        }
        $rootScope.title = '新闻中心'
        $rootScope.loading = true
        if(/UC/.test(navigator.userAgent) || !window.CSS || !window.CSS.supports || !window.CSS.supports("width", "100vw")){
          document.body.className = "unsupport";
          $log.log("unsupported browser detected");
        }
    }])

    app.controller('IndexCtrl', ['api', '$scope', '$routeParams', '$location', function(api, $scope, $routeParams, $location){
        api.changeTitle('新闻中心')
        if ($routeParams['d98a07f84921b24ee30f86fd8cd85c3c']) {
          var link = parseLink($routeParams['d98a07f84921b24ee30f86fd8cd85c3c'])
          $location.url(link ? link : '/')
        } else {
          api.index().then(function(response){
              console.log(response.data)
              $scope.news = response.data.news.map(function(x){
                  x.img = x.img ? x.img[0] : null
                  return x
              });
              $scope.info = response.data.info;
              $scope.slides = response.data.slide;
              api.loading_finish()
          }, function(){
              alert("载入失败了，刷新试试？")
          })
        }
    }])

    app.controller('PassageCtrl', ['api', '$scope', '$routeParams', '$sce', function(api, $scope, $routeParams, $sce){

        api.passage($routeParams.id).then(function(result){
            $scope.passage = result.data;
            $scope.passage.content = $sce.trustAsHtml(result.data.content)
            $scope.passage.pc_link = buildLink($routeParams)
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
            {name:"首页", link: "/"},
            {name:"焦点新闻", link:'/category/42'},
            {name:"校园时讯", link:'/category/50'},
            {name:"教育教学", link:"/category/43"},
            {name:"科研学术", link:"/category/44"},
            {name:"合作交流", link:'/category/45'},
            {name:"信息公告", link:'/category/annoucement'},
        ]
    }])

    app.controller("MenuCtrl", ['$scope', "$location", function($scope, $location){
        $scope.menus = [
            {name:"焦点新闻", link:'/category/42'},
            {name:"校园时讯", link:'/category/50'},
            {name:"教育教学", link:"/category/43"},
            {name:"科研学术", link:"/category/44"},
            {name:"合作交流", link:'/category/45'},
            {name:"信息公告", link:'/category/annoucement'},
        ]
        $scope.location = $location
    }])

    app.controller('annoucementCtrl', ['api', '$scope', '$q', function(api, $scope, $q){

        $scope.types = [{name:"学术", id:66}, {name:"文化",id:67}, {name:"公告",id:68}]

        $scope.switch = function(id){
            $scope.id = id
            $scope.page = 1
            api.column(id).then(function(response){
                console.log(response.data)
                $scope.lists = response.data
                api.loading_finish()
            })
        }

        $scope.load = function(){
            $scope.page += 1;
            api.column($scope.id, $scope.page).then(function(response){
                $scope.lists.push.apply($scope.lists, response.data)
                api.loading_finish()
            })
        }
        $scope.switch(66)
    }])
})()
