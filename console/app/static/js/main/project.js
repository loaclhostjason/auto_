$(document).ready(function () {
    function Projects() {
        AppCommonClass.call(this);
        this.get_protect_relation = function (project_id) {
            $.get('/project/tree?project_id=' + project_id).done(function (resp) {
                if (resp.success) {
                    let data = resp['data'];
                    let nodedata = data['nodedata'];
                    let linkdata = data['linkdata'];
                    myDiagram.model = new go.GraphLinksModel(nodedata, linkdata);
                } else
                    toastr.error(resp.message)
            });
        };
    }

    Projects.prototype = Object.create(AppCommonClass.prototype);
    Projects.prototype.constructor = Projects;

    let projects = new Projects();
    let create_project_modal = $('#create_project_modal');
    $('.add-project').click(function () {
        projects.show_modal(create_project_modal, $(this));
    });

    $('.submit_project').click(function () {
        let params = create_project_modal.find('form').serialize();
        $.post('/project/create', params, function (resp) {
            if (resp.success) {
                create_project_modal.modal('hide');
                toastr.success(resp.message);
                window.location.href = '/project/edit/' + resp.project_id;
            } else
                toastr.error(resp.message)
        })
    });

    // init
    if (project_id)
        projects.get_protect_relation(project_id);

    // submit content
    let add_content = $('#add-content');
    $('.submit-content').click(function () {
        let params = add_content.find('form').serialize();
        let parent_id = add_content.find('[name="parent_id"]').val();
        params += '&parent_id=' + parent_id;

        $.post('/project/content/add/' + project_id, params, function (resp) {
            if (resp.success) {
                add_content.modal('hide');
                projects.get_protect_relation(project_id)
            } else
                toastr.error(resp.message)
        })
    })
});