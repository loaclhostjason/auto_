from flask_assets import Environment, Bundle

assets_env = Environment()

common_css = Bundle(
    'vendor/nprogress/nprogress.css',
    'vendor/toastr/toastr.min.css',
    'vendor/font-awesome/css/font-awesome.min.css',
    'vendor/bootstrap-fileinput/fileinput.min.css',
    'vendor/bootstrap-select/css/bootstrap-multiselect.css',
    'vendor/bootstrap3-editable/css/bootstrap-editable.css',
    'css/app.css',
    'css/comment/base.css',
    'css/comment/btn.css',
    'css/comment/error.css',
    'css/comment/form.css',
    'css/comment/panel.css',
    'css/comment/table.css',
    'css/layout/aside.css',
    'css/layout/common.css',
    'css/layout/header.css',
    'css/layout/main.css',
    filters='cssmin',
    output='public/css/common.css',
)

common_js = Bundle(
    'vendor/nprogress/nprogress.js',
    'vendor/toastr/toastr.min.js',
    'vendor/jquery-ui.min.js',
    'vendor/bootstrap-fileinput/fileinput.min.js',
    'vendor/bootstrap-fileinput/locales/zh.js',
    'vendor/bootstrap-select/js/bootstrap-multiselect.js',
    'vendor/bootstrap3-editable/js/bootstrap-editable.min.js',
    'js/update_password.js',
    'js/class.js',
    'js/app.js',
    filters='jsmin',
    output='public/js/common.js',
)

go_js = Bundle(
    'js/gojs/other/Arrowheads.js',
    'js/gojs/other/BalloonLink.js',
    'js/gojs/other/NonRealtimeDraggingTool.js',
    filters='jsmin',
    output='public/js/go_js',
)

bundles = {
    'common_css': common_css,
    'common_js': common_js,
    'go_js': go_js,
}
