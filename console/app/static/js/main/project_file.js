$(document).ready(function () {
    function ProjectFile() {
        AppCommonClass.call(this);

        this.get_file_option = function (data) {
            let project_select_html = '';
            if (!data || !data.length) {
                return project_select_html;
            }

            data.forEach(function (val) {
                project_select_html += '<option value="' + val + '">' + val + '</option>';
            });
            return project_select_html;
        }
    }

    ProjectFile.prototype = Object.create(AppCommonClass.prototype);
    ProjectFile.prototype.constructor = ProjectFile;

    let project_file = new ProjectFile();
    let create_project_file_modal = $('#create_project_file_modal');
    $('.add-project-file').click(function () {
        project_file.show_modal(create_project_file_modal, $(this));
    });

    create_project_file_modal.on('show.bs.modal', function () {
        let modal = $(this);
        $.get('/project/user/' + user_id, function (resp) {
            let data = resp['data'];
            let project_select = modal.find('[name="project_name"]');
            console.log(data);
            let project_select_html = project_file.get_file_option(data);
            project_select.html(project_select_html);
        })
    });
    create_project_file_modal.on('hide.bs.modal', function () {
        $(this).find('form')[0].reset();
    });


    $('.submit_project_file').click(function () {
        let params = create_project_file_modal.find('form').serialize();
        $.post('/project/create', params, function (resp) {
            if (resp.success) {
                create_project_file_modal.modal('hide');
                toastr.success(resp.message);
                window.location.href = '/project/edit/' + resp['project_id'];
            } else
                toastr.error(resp.message)
        })
    });
});