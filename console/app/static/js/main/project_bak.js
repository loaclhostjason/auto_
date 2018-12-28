$(document).ready(function () {
    function ProjectsBak() {
        AppCommonClass.call(this);
    }

    ProjectsBak.prototype = Object.create(AppCommonClass.prototype);
    ProjectsBak.prototype.constructor = ProjectsBak;

    var projects_bak = new ProjectsBak();


    var btn_las;
    var las_modal = $("#update-las-modal-bak");
    $(document).on('click', '.show-las-modal-bak', function () {
        projects_bak.show_modal(las_modal, $(this));
        las_modal.find('.modal-title').text('Las【' + $(this).data('value') + '】编辑信息');
    });
    las_modal.on('hide.bs.modal', function () {
        $(this).find('textarea').val('');
    });

    las_modal.on('show.bs.modal', function (event) {
        btn_las = $(event.relatedTarget);

        var las_val = btn_las.parents('td').find('input').val();
        las_modal.find('[name="las_value"]').val(las_val || '');
    });

    $('.submit_update_las_bak').click(function () {
        var las_value = las_modal.find('[name="las_value"]').val();
        var las_name = btn_las.parents('td').find('input');
        las_name.val(las_value);
        las_modal.modal('hide');
    });

});