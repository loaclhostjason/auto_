$(document).ready(function () {
    function ProjectGroups() {
        AppCommonClass.call(this);
    }

    ProjectGroups.prototype = Object.create(AppCommonClass.prototype);
    ProjectGroups.prototype.constructor = ProjectGroups;

    var project_group = new ProjectGroups();

    var project_group_modal = $("#project-group-modal");
    var btn;
    project_group_modal.on('hide.bs.modal', function () {
        $(this).find('form')[0].reset();
    });
    project_group_modal.on('show.bs.modal', function (event) {
        btn = $(event.relatedTarget);
    });

    $('.create-project-group').click(function () {
        project_group.show_modal(project_group_modal, $(this));
        project_group_modal.find('.modal-title').text('添加项目');
    });
    var group_id = '';
    $('.edit-project-group').click(function () {
        project_group.show_modal(project_group_modal, $(this));
        project_group_modal.find('.modal-title').text('编辑项目【' + $(this).data('name') + '】');

        var tds = $(this).parents('tr').children('td');
        var name = tds.eq(0).text();
        project_group_modal.find('[name="name"]').val(name);
        group_id = $(this).data('id')
    });


    $('.submit-group').click(function () {
        var params = project_group_modal.find('form').serialize();
        var action = btn.data('action');
        params = params + '&action=' + action + '&id=' + group_id;
        $.post('/manage/project/group?action=' + action, params, function (resp) {
            if (resp.success) {
                sessionStorage.setItem('success', resp.message);
                window.location.reload();
            } else {
                toastr.error(resp.message)
            }
        })
    });

    $('.delete-project-group').click(function () {
        var id = $(this).data('id');
        $.update_info_reload('是否删除', '/project/group/delete/' + id, '');
    })
});