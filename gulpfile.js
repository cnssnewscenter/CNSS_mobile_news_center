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
    hash_src = require("gulp-hash-src");
    angularTemplates = require('gulp-angular-templates');
 
var option = {
    empty: true,
    quotes: true,
    spare: true
}
if(process.version.slice(1, 2) == "6"){
    console.error("Cannot build in node6")
    process.exit()
}
gulp.task('script',function() {
    var assets = useref.assets({searchPath: '.'});
    return gulp.src("static/index.html")
        .pipe(assets)
        .pipe(gulpif("*.css", minifyCss()))
        .pipe(gulpif(/.*\/app\.js/, uglify()))
        //.pipe(gulpif("*.js", uglify()))
        .pipe(debug({title: "combined"}))
        .pipe(rename(function(f){
            f.dirname = ""
        }))
        .pipe(assets.restore())
        .pipe(useref())
        .pipe(debug({title: "Changed"}))
        .pipe(hash_src({
            build_dir: "./",
            src_path: "./",
            verbose: true,
            exts: [".js", ".css"],
            destination_path: function(build_dir, link){
                console.log(build_dir, link)
                return build_dir + link.replace(/^static/, "")
            }
        }))
        //.pipe(gulpif("*.html",minifyInline()))
        //.pipe(gulpif("*.html",minifyHTML(option)))
        //.pipe(gulpif("*.html",entities('decode')))
        .pipe(gulp.dest("./dist"))
});
gulp.task('append', ['script', 'inline_template'], function(){
    return  gulp.src(['dist/app.js', 'dist/template.js'])
        .pipe(concat("app.js"))
        .pipe(gulp.dest("dist"))
})
gulp.task('copy', function(){
    return gulp.src("static/logo.png")
        .pipe(gulp.dest('dist/'))
})
gulp.task("inline_template", function(){
    return gulp.src("static/templates/*.html")
        .pipe(angularTemplates({module: "MobileNews", basePath: "/static/templates/"}))
        .pipe(concat("template.js"))
        .pipe(uglify())
        .pipe(gulp.dest("dist/"))
})
gulp.task("default", ["script","inline_template", "copy", 'append'])
