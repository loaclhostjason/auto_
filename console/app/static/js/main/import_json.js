$(document).ready(function () {
    function ImportJson() {
        AppCommonClass.call(this);

        this.get_file_option = function (data) {
            var project_select_html = '';
            if (!data || !data.length) {
                return project_select_html;
            }

            data.forEach(function (val) {
                project_select_html += '<option value="' + val[0] + '">' + val[1] + '</option>';
            });
            return project_select_html;
        }
    }

    ImportJson.prototype = Object.create(AppCommonClass.prototype);
    ImportJson.prototype.constructor = ImportJson;

    function init_upload_file(upload_file, url) {
        var upload_file = $('#' + upload_file);
        upload_file.fileinput({
            language: 'zh',
            uploadUrl: url, //上传的地址
            allowedFileExtensions: ['json'],//接收的文件后缀,
            maxFileCount: 10,
            enctype: 'multipart/form-data',
            showUpload: true, //是否显示上传按钮
            showCaption: true,//是否显示标题
            showPreview: false,//是否显示标题
            browseClass: "btn btn-primary", //按钮样式
            previewFileIcon: "<i class='glyphicon glyphicon-king'></i>",
            msgFilesTooMany: "选择上传的文件数量({n}) 超过允许的最大数值{m}！",
            uploadExtraData: function (previewId, index) {   //额外参数的关键点
                var obj = {};
                obj.project_group = import_modal.find('[name="project_group"]').val() || '';
                return obj;
            },
            slugCallback: function (filename) {
                return filename;
            }
        });
        return upload_file;
    }


    var import_json = new ImportJson();
    var import_modal = $('#import_json_file');
    $('.import-json-file').click(function () {
        import_json.show_modal(import_modal, $(this));
    });
    import_modal.on('hide.bs.modal', function () {
        $(this).find('form')[0].reset();
    });
    import_modal.on('show.bs.modal', function () {
        var modal = $(this);
        $.get('/project/group/pm?user_id=' + user_id, function (resp) {
            var data = resp['data'];
            var project_select = modal.find('[name="project_group"]');
            var project_select_html = import_json.get_file_option(data);
            project_select.html(project_select_html);
        }).done(function () {
            var init_upload = init_upload_file('upload-file', '/import/json');

            init_upload.on("fileuploaded", function (event, data, previewId, index) {
                data = data['response'];
                if (data.success) {
                    toastr.success(data.message);
                    sessionStorage.setItem("success", data.message);
                    window.location.href = '/project/edit/' + data['project_id'];

                } else {
                    toastr.error(data.message)
                }
            });
        })
    });


});