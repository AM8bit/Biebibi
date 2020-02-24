const gulp = require('gulp')
const concat = require("gulp-concat");
const uglify = require('gulp-uglify')
const jshint = require('gulp-jshint');
const cleanCSS = require('gulp-clean-css');
const inject = require('gulp-inject');

function clean(cb) {
    // body omitted
    cb();
}


function build(cb) {
    gulp.src(['./web/index.html', './web/daemon.py'])
        .pipe(gulp.dest('./docker/src/'));
    gulp.src(['./web/cgi-bin/*'])
        .pipe(gulp.dest('./docker/src/cgi-bin/'));
    gulp.src(['./web/js/common/*.js', '!./web/js/common/eruda.js'])
        .pipe(uglify())
        .pipe(jshint())
        .pipe(concat('all.js'))
        .pipe(gulp.dest('./docker/src/dist/'));
    gulp.src(['./web/css/common/ui.css', './web/css/common/plyr.css'])
        .pipe(cleanCSS())
        .pipe(concat('styles.css'))
        .pipe(gulp.dest('./docker/src/dist/'));
    cb();
}

gulp.task('make', function () {
    var target = gulp.src('./docker/src/index.html');
    var sources = gulp.src(['./docker/src/dist/*.js', './docker/src/dist/*.css'], {read: false});
    return target.pipe(inject(sources, {relative: true}))
        .pipe(gulp.dest('./docker/src/'));
})

exports.default = build