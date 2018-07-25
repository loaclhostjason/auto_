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
                    let bit_position = resp['bit_position'];
                    let byte_position = resp['byte_position'];
                    $('.table-project-data thead').html(_this.project_thead_html(did_len, bit_position, byte_position));
                    $('.table-project-data tbody').html(_this.project_data_html(result, project_data, did_len, byte_position));
                } else {
                    toastr.error(resp.message)
                }
            });
        };

        this.project_data_html = function (result, project_data, did_len, byte_position) {
            if (!result || !result.length) return '';


            let html = '';
            result.forEach(function (data) {
                let prid = data['level_4_id'];
                let data_info = project_data[data['level_4_id']] || {};
                let content = data_info['content'] || {};

                html += '<tr class="data-class">';
                html += '<input type="hidden" name="project_relation_id" value="' + data['level_4_id'] + '">';
                html += '<input type="hidden" name="name" value="' + data['level_4'] + '">';

                html += '<td class="text-center"><a href="javascript:void(0)" class="del-project-func text-danger pull-left" data-id="' + data['level_4_id'] + '"><i class="glyphicon glyphicon-trash"></i></a>' + data['level_4'] + '</td>';
                html += '<td class="text-center"><div style="display: inline-flex"><div style="float: left"><input name="las" class="tc-search-words" value="' + (data_info['las'] || '') + '"></div>';
                html += '<div style="float: right; padding:5px 0 0 10px"><a href="javascript:void(0)" class="show-las-modal"  data-value="' + data['level_4'] + '"><i class="glyphicon glyphicon-edit"></i></a></div></div>';
                html += '</td>';


                let bet_number = [];
                if (did_len) {
                    for (let i = 0; i < did_len; i++) {
                        bet_number.push(i);
                    }
                }
                bet_number.forEach(function (num) {
                    html += '<td colspan="8">';
                    html += '<div class="col-xs-12"><div class="row">';
                    if (content['byte' + num]) {
                        html += '<input type="text" class="tc-search-words col-xs-12" name="' + prid + '_byte' + num + '" value="' + (content['byte' + num] || '') + '">';
                    } else {
                        if (num == byte_position) {
                            html += '<input type="text" class="tc-search-words col-xs-12" name="' + prid + '_byte' + num + '" value="">';
                        } else
                            html += '<input type="text" class="tc-search-words col-xs-12" name="' + prid + '_byte' + num + '" value="" disabled>';
                    }

                    html += '</div></div></td>';
                });


                html += '</tr>'
            });

            return html
        };

        this.project_thead_html = function (did_len, bit_position, byte_position) {
            let html = '';
            html += '<tr>';
            html += '<th width="100" style="vertical-align: middle; min-width: 100px"></th>';
            html += '<th width="120" style="vertical-align: middle; min-width: 120px">LAS</th>';

            if (did_len) {
                for (let i = 0; i < did_len; i++) {
                    html += '<th colspan="8"><div class="text-center with-bottom-border"><span>BYTE' + i + '</span></div>';
                    html += '<div style="width: 172px">';
                    let a = '';
                    for (let j = 7; j >= 0; j--) {
                        if ($.inArray(j, bit_position) > -1 && byte_position == i) {
                            a += '<div style="width: 12.5%; float: left;background: #090; color: #fff; text-align: center"><span>' + j + '</span>';
                        } else {
                            a += '<div style="width: 12.5%; float: left;text-align: center"><span>' + j + '</span>';
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
                projects.get_project_data(project_id, $('[name="project_relation_id"]').val());
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
                projects.get_project_data(project_id, $.g_parent_id);
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
        $(this).find('[name="no_las"]').removeAttr('checked');
        $('.start_rule:not(:first-of-type)').remove();
    });
    update_las_modal.on('show.bs.modal', function (event) {
        $(this).find('[name="no_las"]').val('!');
        $.get('/las/get').done(function (resp) {
            let data = resp['data'];

            function option_html(data, selected_val) {
                let h = '';
                data.forEach(function (val) {
                    for (let k in val) {
                        if (selected_val == k) {
                            h += '<option selected value="' + k + '">' + k + ' | ' + val[k] + '</option>'
                        } else
                            h += '<option value="' + k + '">' + k + ' | ' + val[k] + '</option>'
                    }
                });
                return h
            }

            btn_las = $(event.relatedTarget);
            let las_name = btn_las.parents('td').find('input').val();
            let first_las_name = las_name[0];
            if (first_las_name === '!') {
                update_las_modal.find('[name="no_las"]').prop('checked', 'checked');
                las_name = las_name.substring(2, las_name.length - 1)
            }

            las_name = String(las_name).replace(/[$]/g, '');
            // console.log(String(aa));

            las_val = las_name.split(/[/.#+&,-]/);
            las_f = [];
            las_val.forEach(function (value) {

                try {
                    if (las_name.split(value)[1][0])
                        las_f.push(las_name.split(value)[1][0]);
                } catch (e) {
                    console.log(e);
                }

            });

            let html = '';
            las_val.forEach(function (val, index) {
                html += '<div class="form-group start_rule"><div class="col-sm-6">';
                html += '<select name="las_' + index + '" class="form-control pull-left">' + option_html(data, val) + '</select></div>';
                html += '<div class="col-sm-6"><select class="form-control pull-left las_f" name="las_f_' + index + '">';
                let f = [['', '请选择'], ['#', '#'], ['/', '/'], ['-', '-'], ['&', '&']];
                f.forEach(function (value) {
                    if (las_f[index] === value[0]) {
                        html += '<option selected value="' + value[0] + '">' + value[1] + '</option>';
                    } else
                        html += '<option value="' + value[0] + '">' + value[1] + '</option>';
                });
                html += '</select></div></div>';
            });
            $('.parent_rule').html(html);
        });


    });

    let data = '';
    $.get('/las/get').done(function (resp) {
        data = resp['data'];
    });

    function option_html2(data) {
        let h = '';
        data.forEach(function (val) {
            for (let k in val) {
                h += '<option value="' + k + '">' + k + ' | ' + val[k] + '</option>'
            }
        });
        return h
    }

    $(document).on('change', '.las_f', function () {
        let this_val = $(this).val();

        let start_rule_len = $('.start_rule').length;
        let rule_html = '';
        rule_html += '<div class="form-group start_rule"><div class="col-sm-6"><select name="las_' + start_rule_len + '" class="form-control pull-left">' + option_html2(data) + '</select></div>';
        rule_html += '<div class="col-sm-6"><select class="form-control pull-left las_f" name="las_f_' + start_rule_len + '">';
        let f = [['', '请选择'], ['#', '#'], ['/', '/'], ['-', '-'], ['&', '&']];
        f.forEach(function (value) {
            rule_html += '<option value="' + value[0] + '">' + value[1] + '</option>';
        });
        rule_html += '</select></div></div>';


        if (this_val) {
            $(this).parents('.start_rule').after(rule_html)
        } else {
            $(this).parents('.start_rule').nextAll().remove();
        }
    });
    $('.submit_update_las').click(function () {
        let no_las = update_las_modal.find('[name="no_las"]:checked').val();

        let start_rule_len = $('.start_rule').length;
        let las_name = btn_las.parents('td').find('input');
        let new_las_name = '';
        for (let i = 0; i < start_rule_len; i++) {
            new_las_name += '$' + $('[name="las_' + i + '"]').val() + $('[name="las_f_' + i + '"]').val()
        }
        if (no_las) {
            new_las_name = '!(' + new_las_name + ')';
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

// extra config
$(document).ready(function () {
    $('.add-extra-config').click(function () {
        let level = $(this).attr('level');
        let name = $(this).attr('name');
        window.location.href = '/project/edit/' + project_id + '/extra?level=' + (level || 0) + '&name=' + name || '';
    })
});