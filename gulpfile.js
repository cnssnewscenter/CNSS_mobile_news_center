var gulp = require("gulp"),
    useref = require('gulp-useref'),
    gulpif = require("gulp-if"),
    uglify = require('gulp-uglify'),
    minifyCss = require('gulp-minify-css'),
    rev = require("gulp-rev"),
    revReplace = require("gulp-rev-replace"),
    debug = require("gulp-debug"),
    rename = require("gulp-rename")
    concat = require('gulp-concat'),
    angularTemplates = require('gulp-angular-templates');
 
var option = {
    empty: true,
    quotes: true,
    spare: true
}

gulp.task('script', function() {
    var assets = useref.assets({searchPath: '.'});
    return gulp.src("static/index.html")
        .pipe(assets)
        .pipe(gulpif("*.css", minifyCss()))
        .pipe(gulpif("*.js", uglify()))
        //.pipe(rev())
        .pipe(debug({title: "combined"}))
        .pipe(rename(function(f){
            f.dirname = ""
        }))
        .pipe(assets.restore())
        .pipe(useref())
        .pipe(debug({title: "Changed"}))
        //.pipe(revReplace())
        //.pipe(gulpif("*.html",minifyInline()))
        //.pipe(gulpif("*.html",minifyHTML(option)))
        //.pipe(gulpif("*.html",entities('decode')))
        .pipe(gulp.dest("./dist"))
});
gulp.task('copy', function(){
    return gulp.src("static/logo.png")
        .pipe(gulp.dest('dist/'))
})
gulp.task("inline_template", function(){
    return gulp.src("static/templates/*.html")
        .pipe(angularTemplates({module: "MobileNews"}))
        .pipe(concat("template.js"))
        .pipe(gulp.dest("dist/"))
})
gulp.task("default", ["script","inline_template", "copy"])
