$(document).ready(function () {
    var users = new AppCommonClass();

    var update_password_modal = $('#update_password_modal');
    update_password_modal.on('hide.bs.modal', function () {
        users.hide_modal($(this));
    });
    $('.update_password').click(function () {
        users.show_modal(update_password_modal, $(this));
        update_password_modal.find('.modal-title').text('更换【' + $(this).data('username') + '】密码');
    });
    var update_pwd_btn;
    update_password_modal.on('show.bs.modal', function (event) {
        update_pwd_btn = $(event.relatedTarget);
    });
    $('.submit_update_password').click(function () {
        var user_id = update_pwd_btn.data('id');
        var params = update_password_modal.find('form').serialize();
        $.post('/users/edit/' + user_id + '?type=update_pwd', params, function (resp) {
            if (resp.success) {
                sessionStorage.setItem("success", resp.message);
                window.location.reload();
            } else {
                toastr.error(resp.message);
            }
        })
    });
});