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

        this.get_attr_input = function (project_id, level, id) {
            $.get('/attr/content?project_id=' + project_id + '&level=' + level + '&project_relation_id=' + id, function (resp) {
                if (resp.success) {
                    let data = resp['data'];
                    let content = resp['content'];
                    attr_html(data, content, id, level);
                } else {
                    toastr.error(resp.message)
                }


            });
        };

        this.get_project_data = function (project_id, parent_id) {
            let _this = this;
            $.get('/project/data/get?project_id=' + project_id + '&project_relation_id=' + parent_id, function (resp) {
                if (resp.success) {
                    let result = resp['result'];
                    let project_data = resp['project_data'];
                    let did_len = resp['did_len'];
                    $('.table-project-data thead').html(_this.project_thead_html(did_len));
                    $('.table-project-data tbody').html(_this.project_data_html(result, project_data, did_len));
                } else {
                    toastr.error(resp.message)
                }
            });
        };

        this.project_data_html = function (result, project_data, did_len) {
            if (!result || !result.length) return '';


            let html = '';
            result.forEach(function (data, index) {
                let prid = data['level_4_id'];
                let data_info = project_data[data['level_4_id']] || {};
                let content = data_info['content'] || {};
                let number = [7, 6, 5, 4, 3, 2, 1, 0];

                html += '<tr class="data-class">';
                html += '<input type="hidden" name="project_relation_id" value="' + data['level_4_id'] + '">';
                html += '<input type="hidden" name="name" value="' + data['level_4'] + '">';

                if (index === 0) {
                    html += '<td class="text-center" rowspan="' + result.length + '">' + data['level_1'] + '</td>';
                }
                html += '<td class="text-center">' + data['level_2'] + '</td>';
                html += '<td class="text-center">' + data['level_3'] + '</td>';
                html += '<td class="text-center">' + data['level_4'] + '</td>';
                html += '<td class="text-center"><input name="las" class="tc-search-words" value="' + (data_info['las'] || '') + '">';
                html += '<a href="javascript:void(0)" class="show-las-modal pull-right" style="padding-left: 10px" data-value="' + data['level_4'] + '"><i class="glyphicon glyphicon-edit"></i></a>';
                html += '<a href="javascript:void(0)" class="del-project-func text-danger pull-right" data-id="' + data['level_4_id'] + '"><i class="glyphicon glyphicon-trash"></i></a></td>';


                let bet_number = [];
                if (did_len){
                    for (let i=0;i<did_len; i++) {
                        bet_number.push(i);
                    }
                }
                bet_number.forEach(function (num) {
                    html += '<td colspan="8"><div class="col-xs-12"><div class="row">';
                    number.forEach(function (value) {
                        html += '<div style="width: 12.5%; float: left">';
                        html += '<input type="checkbox" name="' + prid + '_bit' + num + '_' + value + '" value="y"' + (content['bit' + num + '_' + value] === 'y' ? 'checked' : '') + '>';
                        html += '</div>';
                    });
                    html += '</div></div><div class="bline col-xs-12" style="margin:  10px 0"></div>';
                    html += '<div class="col-xs-12"><div class="row">';
                    html += '<input type="text" class="tc-search-words col-xs-12" name="' + prid + '_byte' + num + '" value="' + (content['byte' + num] || '') + '">';
                    html += '</div></div></td>';
                });


                html += '</tr>'
            });

            return html
        };

        this.project_thead_html = function (did_len) {
            let html = '';
            html += '<tr>';
            html += '<th width="160" style="vertical-align: middle; min-width: 160px">项目名称</th>';
            html += '<th width="100" style="vertical-align: middle; min-width: 100px">地址</th>';
            html += '<th width="100" style="vertical-align: middle; min-width: 100px"></th>';
            html += '<th width="100" style="vertical-align: middle; min-width: 100px"></th>';
            html += '<th width="120" style="vertical-align: middle; min-width: 120px">LAS</th>';

            if (did_len) {
                for (let i = 0; i < did_len; i++) {
                    html += '<th colspan="8"><div class="text-center with-bottom-border"><span>BYTE' + i + '</span></div>';
                    html += '<div style="width: 172px">';
                    let a = '';
                    for (let j = 7; j >= 0; j--) {
                        a += '<div style="width: 12.5%; float: left"><span>' + j + '</span>';
                        if (j !== 0) {
                            a += '<i class="resize-line-icon"></i>';
                        }
                        a += '</div>';
                    }
                    html += a;
                    html += '</div></th>';
                }
            }
            html += '</tr>';
            return html;
        }
    }

    Projects.prototype = Object.create(AppCommonClass.prototype);
    Projects.prototype.constructor = Projects;

    let projects = new Projects();
    $.g_projects = new Projects();

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
    $('.submit-content').click(function (e) {
        e.preventDefault();

        let params = add_content.find('form').serialize();
        let parent_id = add_content.find('[name="parent_id"]').val();
        let level = add_content.find('[name="level"]').val();
        params += '&parent_id=' + parent_id + '&level=' + level;

        $.post('/project/content/add/' + project_id, params, function (resp) {
            if (resp.success) {
                add_content.modal('hide');
                if (level >= 4)
                    projects.get_project_data(project_id, parent_id);
                projects.get_protect_relation(project_id)
            } else
                toastr.error(resp.message)
        })
    });


    // submit attr
    $(document).on('click', '.submit-add-attr', function () {
        let form_data = $('form#attr-form').serialize();
        $.post('/manage/attr/content/add?project_id=' + project_id, form_data, function (resp) {
            if (resp.success) {
                toastr.success(resp['message'])
            } else
                toastr.error(resp['message'])
        })
    });

    // update username
    let update_name = $('#update-name-modal');
    update_name.on('hide.bs.modal', function () {
        $(this).find('form')[0].reset();
    });

    update_name.find('.submit_update_name').click(function () {
        let params = update_name.find('form').serialize();
        $.post('/project/edit/name', params, function (resp) {
            if (resp.success) {
                toastr.success(resp.message);
                projects.get_protect_relation(project_id);

                update_name.modal('hide');
            } else {
                toastr.error(resp.message)
            }
        })
    });


    // submit project data
    $('.submit-project-data').click(function () {
        let params = $('form#project-data-form').serialize();
        $.post('/project/data/submit/' + project_id, params, function (resp) {
            if (resp.success) {
                toastr.success(resp.message);
            } else
                toastr.error(resp.message);
        })
    });

    // show las modal
    let btn_las;
    let update_las_modal = $("#update-las-modal");
    $(document).on('click', '.show-las-modal', function () {
        projects.show_modal(update_las_modal, $(this));
        update_las_modal.find('.modal-title').text('Las【' + $(this).data('value') + '】编辑信息');
    });
    update_las_modal.on('hide.bs.modal', function () {
        $(this).find('input').val('');
        $(this).find('select').val('');
    });
    update_las_modal.on('show.bs.modal', function (event) {
        btn_las = $(event.relatedTarget);
    });

    $(document).on('change', '.las_f', function () {
        let this_val = $(this).val();

        let start_rule_len = $('.start_rule').length;
        let rule_html = '';
        rule_html += '<div class="form-group start_rule"><div class="col-sm-6"><input name="las_' + start_rule_len + '" class="form-control pull-left" required></div>';
        rule_html += '<div class="col-sm-6"><select class="form-control pull-left las_f" name="las_f_' + start_rule_len + '"><option value="">请选择</option> <option value="|">|</option><option value="-">-</option><option value="+">+</option><option value="&">&</option> </select></div></div>';


        if (this_val) {
            $(this).parents('.start_rule').after(rule_html)
        } else {
            $(this).parents('.start_rule').nextAll().remove();
        }
    });
    $('.submit_update_las').click(function () {
        let start_rule_len = $('.start_rule').length;
        let las_name = btn_las.parents('td').find('input');
        let new_las_name = '';
        for (let i = 0; i < start_rule_len; i++) {
            new_las_name += '$' + $('[name="las_' + i + '"]').val() + $('[name="las_f_' + i + '"]').val()
        }
        las_name.val(new_las_name);
        update_las_modal.modal('hide');
    });

    $(document).on('click', '.del-project-func', function () {
        let id = $(this).data('id');
        let _this = $(this);
        Modal.confirm({
            msg: '是否删除？'
        }).on(function (e) {
            if (e) {
                $.post('/project/tree/delete/' + id, '', function (data) {
                    if (data.success) {
                        toastr.success(data.message);
                        _this.parents('.data-class').remove();
                    } else {
                        toastr.error(data.message);
                    }
                })
            }
        })
    })
});