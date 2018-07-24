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
    user_modal.on('show.bs.modal', function (event) {
        laydate.render({
            elem: '#expiry_time',
            min: moment().format('YYYY-MM-DD'),
            calendar: true,
            value: new Date()
        });
    });

    laydate.render({
        elem: '#expiry_time',
        min: moment().format('YYYY-MM-DD'),
        calendar: true,
        value: new Date()
    });

    $('.submit_user').click(function () {
        let params = user_modal.find('form').serialize();
        params += '&role=user';
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

    // create com user
    $('.create_com_user').click(function () {
        users.show_modal(user_modal, $(this));
        user_modal.find('.modal-title').text('项目管理员【' + $(this).data('username') + '】，分配普通用户');
    });


});

$(document).ready(function () {
    let selection_summary = $('.selection-summary');
    selection_summary.click(function () {
        $(this).toggleClass('open');
        let loop = $(this).data('loop');
        let elm = $(this).parents('tbody').find('.selection-info');
        if ($(this).is('.open') && elm.data('loop') === loop) {
            elm.show()
        } else {
            elm.hide();
        }
    });
});


$(document).ready(function () {
    function PM() {
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

    PM.prototype = Object.create(AppCommonClass.prototype);
    PM.prototype.constructor = PM;

    let pm = new PM();
    let pm_modal = $('#fp-pm-modal');

    let uid = 0;
    pm_modal.on('hide.bs.modal', function () {
        pm.hide_modal($(this));
    });
    pm_modal.on('show.bs.modal', function (event) {
        let btn = $(event.relatedTarget);
        uid = btn.data('uid');

        let modal = $(this);
        $.get('/project/user/' + g_user_id, function (resp) {
            let data = resp['data'];
            let project_select = modal.find('[name="project_name"]');
            console.log(data);
            let project_select_html = pm.get_file_option(data);
            project_select.html(project_select_html);
        })
    });

    $('.fp_pm').click(function () {
        pm.show_modal(pm_modal, $(this));

        let user = $(this).data('user');
        pm_modal.find('.modal-title').text('分配【' + user + '】项目')
    });

    $('.submit_pm').click(function () {
        let params = pm_modal.find('form').serialize();
        $.post('/users/fp_pm?user_id=' + uid, params, function (resp) {
            if (resp.success) {
                pm_modal.modal('hide');
                sessionStorage.setItem('success', resp.message);
                window.location.reload();
            } else
                toastr.error(resp.message)
        })
    })
});