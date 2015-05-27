var gulp = require("gulp"),
    useref = require('gulp-useref'),
    gulpif = require("gulp-if"),
    uglify = require('gulp-uglify'),
    minifyCss = require('gulp-minify-css'),
    rev = require("gulp-rev"),
    revReplace = require("gulp-rev-replace")
    minifyInline = require('gulp-minify-inline'),
    debug = require("gulp-debug"),
    entities = require("gulp-html-entities"),
    minifyHTML = require('gulp-minify-html');

var option = {
    empty: true,
    // conditionals: false,
    quotes: true,
    spare: true
}

gulp.task('script', function() {
    var assets = useref.assets({searchPath: '.'});
    return gulp.src("static/index.html")
        .pipe(assets)
        // .pipe(gulpif("*.js", uglify()))
        .pipe(gulpif("*.css", minifyCss()))
        .pipe(rev())
        .pipe(debug({title: "combined"}))
        .pipe(assets.restore())
        // .pipe(minifyInline())
        .pipe(useref())
        .pipe(revReplace())
        .pipe(entities('decode'))
        // .pipe(minifyHTML(option))
        .pipe(gulp.dest("./dist"))
});
gulp.task("inline_template", function(){
    return gulp.src("static/templates/*.html")
        .pipe(minifyInline())
        .pipe(entities('decode'))
        .pipe(minifyHTML(option))
        .pipe(gulp.dest("dist/templates/"))
})
gulp.task("default", ["script","inline_template"])
