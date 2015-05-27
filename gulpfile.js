var gulp = require("gulp"),
    useref = require('gulp-useref'),
    gulpif = require("gulp-if"),
    uglify = require('gulp-uglify'),
    minifyCss = require('gulp-minify-css'),
    rev = require("gulp-rev"),
    revReplace = require("gulp-rev-replace")
    minifyInline = require('gulp-minify-inline'),
    debug = require("gulp-debug");

gulp.task('script', function() {
    var assets = useref.assets({searchPath: '.'});
    return gulp.src("static/index.html")
        .pipe(assets)
        .pipe(gulpif("*.js", uglify()))
        .pipe(gulpif("*.js", minifyCss()))
        .pipe(debug({title: "combine"}))
        .pipe(rev())
        .pipe(assets.restore())
        .pipe(useref())
        .pipe(revReplace())
        .pipe(gulp.dest("./dist"))
});
gulp.task("inline_index", function() {
    return gulp.src('static/*.html')
        .pipe(minifyInline())
        .pipe(gulp.dest("static/"))
})
gulp.task("inline_template", function(){
    return gulp.src("static/templates/*.html")
        .pipe(minifyInline())
        .pipe(gulp.dest("static/templates/"))
})
gulp.task("inline", ["inline_index", "inline_template"])
gulp.task("default", ["inline", "script"])
