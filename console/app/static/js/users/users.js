$(document).ready(function () {
    function Users() {
        AppCommonClass.call(this);
    }

    Users.prototype = Object.create(AppCommonClass.prototype);
    Users.prototype.constructor = Users;

    let users = new Users();

    let user_modal = $('#user_modal');
    $('.create_user').click(function () {
        users.show_modal(user_modal, $(this));
    });

    user_modal.on('hide.bs.modal', function () {
        users.hide_modal($(this));
    });

    laydate.render({
        elem: '#expiry_time',
        min: moment().format('YYYY-MM-DD'),
        calendar: true,
        value: new Date()
    });

    user_modal.find('input').bind('input propertychange', function () {
        let submit_user = $('.submit_user');
        let user_name = $('[name="username"]').val();
        let upw = $('[name="upw"]').val();
        let upw2 = $('[name="upw2"]').val();
        user_name && upw && upw2 ? submit_user.removeAttr('disabled') : submit_user.attr('disabled', true);
    });

    $('.submit_user').click(function () {
        let params = user_modal.find('form').serialize();
        console.log(params);
        $.post('/users/create', params, function (resp) {
            if (resp.success) {
                sessionStorage.setItem("success", resp.message);
                window.location.reload();
            } else {
                toastr.error(resp.message);
            }
        })
    });

    $('.delete-user').click(function () {
        $.update_info_reload('是否删除用户', '/users/delete/' + $(this).data('id'), '');
    });

    // edit user info
    laydate.render({
        elem: '#edit_expiry_time',
        min: moment().format('YYYY-MM-DD'),
        calendar: true,
        value: new Date()
    });
    let edit_user_modal = $('#edit_user_modal');
    edit_user_modal.on('hide.bs.modal', function () {
        users.hide_modal($(this));
    });
    $('.edit_user').click(function () {
        users.show_modal(edit_user_modal, $(this));
        edit_user_modal.find('.modal-title').text('编辑【' + $(this).data('username') + '】基本信息');
    });

    let edit_btn;
    edit_user_modal.on('show.bs.modal', function (event) {
        edit_btn = $(event.relatedTarget);
        let user_id = edit_btn.data('id');
        let modal = $(this);
        if (user_id) {
            $.get('/users/info/' + user_id, function (resp) {
                if (!resp.success) {
                    toastr.error(resp.message);
                    return false;
                }
                let data = resp.data;
                for (let key in data) {
                    modal.find('[name="' + key + '"]').val(data[key]);
                }
            })
        }
    });
    $('.submit_edit_user').click(function () {
        let user_id = edit_btn.data('id');
        let params = edit_user_modal.find('form').serialize();
        $.post('/users/edit/' + user_id, params, function (resp) {
            if (resp.success) {
                sessionStorage.setItem("success", resp.message);
                window.location.reload();
            } else {
                toastr.error(resp.message);
            }
        })
    });

    // update_password

    let update_password_modal = $('#update_password_modal');
    update_password_modal.on('hide.bs.modal', function () {
        users.hide_modal($(this));
    });
    $('.update_password').click(function () {
        users.show_modal(update_password_modal, $(this));
        update_password_modal.find('.modal-title').text('更换【' + $(this).data('username') + '】密码');
    });
    let update_pwd_btn;
    update_password_modal.on('show.bs.modal', function (event) {
        update_pwd_btn = $(event.relatedTarget);
    });
    $('.submit_update_password').click(function () {
        let user_id = update_pwd_btn.data('id');
        let params = update_password_modal.find('form').serialize();
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