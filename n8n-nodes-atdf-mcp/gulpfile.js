const { src, dest } = require('gulp');

function buildIcons() {
  return src('nodes/**/*.{png,svg}')
    .pipe(dest('dist/'));
}

exports.build = buildIcons;
exports['build:icons'] = buildIcons;