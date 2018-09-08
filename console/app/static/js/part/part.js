$(document).ready(function () {
    function Part() {
        AppCommonClass.call(this);
        this.get_part_relation = function (project_id) {
            $.get('/part/number/tree?project_id=' + project_id).done(function (resp) {
                if (resp.success) {
                    var data = resp['data'];
                    var nodedata = data['nodedata'];
                    var linkdata = data['linkdata'];
                    myPartDiagram.model = new go.GraphLinksModel(nodedata, linkdata);
                } else
                    toastr.error(resp.message)
            });
        };


        this.project_thead_part_number_html = function (level) {
            var html = '';
            html += '<tr>';
            html += '<th width="60" style="min-width: 60px"></th>';
            html += '<th width="120" style="min-width: 120px">零件号</th>';
            html += '<th width="120" style="min-width: 120px">Las</th>';
            html += '</tr>';

            html += '<input type="hidden" name="level" value="' + level + '"/>';
            return html
        };

        this.project_tbody_part_number_html = function (data) {
            var add_html = '';
            add_html += '<tr>';
            add_html += '<td colspan="3" style="font-size: 15px">';
            add_html += '<a class="monitor-dialog-add" href="javascript:void(0)">';
            add_html += '<i class="blue-add-icon"></i>';
            add_html += '<span class="td-add-par-number" style="position: relative;top: -1px;">添加</span>';
            add_html += '</a>';
            add_html += '</td>';
            add_html += '</tr>';

            if (!data || !data.length)
                return add_html;

            var html = '';
            data.forEach(function (val) {
                html += '<tr>';
                html += '<td><a href="javascript:void(0);" class="td-remove">移除</a></td>';
                html += '<td><input name="number" class="td-input" required value="' + (val['number'] || '') + '" /></td>';
                html += '<td><input name="las" class="td-input" required value="' + (val['las'] || '') + '" />';
                html += '<a href="javascript:void(0)" class="show-las-modal"  data-value="' + val['number'] + '"><i class="glyphicon glyphicon-edit"></i></a></td>';
                html += '</tr>';
            });
            html += add_html;
            return html
        };

        this.get_part_number = function (project_id, part_id, hide_html) {
            var hide_html = hide_html || false;
            if (hide_html) {
                $('.table-project-data thead').html('');
                $('.table-project-data tbody').html('');
                return
            }
            var _this = this;
            $.get('/project/part/number/get?project_id=' + project_id + '&part_num_relation_id=' + part_id, function (resp) {
                if (resp.success) {
                    var resp_data = resp['data'];
                    var level = resp['level'];
                    $('.table-project-data thead').html(_this.project_thead_part_number_html(level));
                    $('.table-project-data tbody').html(_this.project_tbody_part_number_html(resp_data));
                } else {
                    toastr.error(resp.message)
                }
            });
        };

        this.add_part_number = function () {
            var html_tr2 = '';

            html_tr2 += '<tr>';
            html_tr2 += '<td><a href="javascript:void(0);" class="td-remove">移除</a></td>';
            html_tr2 += '<td><input name="number" class="td-input" required/></td>';
            html_tr2 += '<td><input name="las" class="td-input" required/>';
            html_tr2 += '<a href="javascript:void(0)" class="show-las-modal"  data-value=""><i class="glyphicon glyphicon-edit"></i></a></td>';

            html_tr2 += '</tr>';

            $(document).on('click', '.td-add-par-number', function () {
                $(this).parents('tr').before(html_tr2);
            });
        };

        this.remove_part_number = function () {
            $(document).on('click', '.td-remove', function () {
                $(this).parents('tr').remove();
            });
        }
    }

    Part.prototype = Object.create(AppCommonClass.prototype);
    Part.prototype.constructor = Part;

    var partNumber = new Part();
    $.g_part = new Part();

    // init func
    partNumber.add_part_number();
    partNumber.remove_part_number();


    // show las modal todo
    var btn_las;
    var update_las_modal = $("#update-las-modal");
    $(document).on('click', '.show-las-modal', function () {
        partNumber.show_modal(update_las_modal, $(this));
        if ($(this).data('value'))
            update_las_modal.find('.modal-title').text('零件号【' + $(this).data('value') + '】编辑信息');
        else
            update_las_modal.find('.modal-title').text('零件号Las信息');
    });
    update_las_modal.on('hide.bs.modal', function () {
        $(this).find('input').val('');
        $(this).find('select').val('');
        $(this).find('[name="no_las"]').removeAttr('checked');
        $('.start_rule:not(:first-of-type)').remove();
    });
    var num = 0;
    update_las_modal.on('show.bs.modal', function (event) {
        $(this).find('[name="no_las"]').val('!');
        $.get('/las/get?project_group_id=' + project_group_id).done(function (resp) {
            var data = resp['data'];

            function option_html(data, selected_val) {
                var h = '';
                data.forEach(function (val) {
                    for (var k in val) {
                        if (selected_val == k) {
                            h += '<option selected value="' + k + '">' + k + ' | ' + val[k] + '</option>'
                        } else
                            h += '<option value="' + k + '">' + k + ' | ' + val[k] + '</option>'
                    }
                });
                return h
            }

            btn_las = $(event.relatedTarget);
            var las_name = btn_las.parents('td').find('input').val();
            var first_las_name = las_name[0];
            if (first_las_name === '!') {
                update_las_modal.find('[name="no_las"]').prop('checked', 'checked');
                las_name = las_name.substring(2, las_name.length - 1)
            }
            if ($.inArray(las_name[las_name.length - 1], ['#', '&', '-', '/']) > -1) {
                las_name = las_name.substring(0, las_name.length - 2)
            }

            las_name = String(las_name).replace(/[$]/g, '');
            // console.log(String(aa));

            var las_val = las_name.split(/[/.#+&,-]/);
            var las_f = [];
            las_val.forEach(function (value) {

                try {
                    if (las_name.split(value)[1][0])
                        las_f.push(las_name.split(value)[1][0]);
                } catch (e) {
                    console.log(e);
                }

            });

            var html = '';
            las_val.forEach(function (val, index) {
                num += index;
                html += '<div class="form-group start_rule"><div class="col-sm-6">';
                html += '<select name="las_' + index + '" class="form-control pull-left">' + option_html(data, val) + '</select></div>';
                html += '<div class="col-sm-4"><select class="form-control pull-left las_f" name="las_f_' + index + '">';
                var f = [['', '请选择'], ['#', '#'], ['/', '/'], ['-', '-'], ['&', '&']];
                if (index === las_val.length - 1) {
                    f.forEach(function (value) {
                        html += '<option value="' + value[0] + '">' + value[1] + '</option>';
                    });
                } else {
                    f.forEach(function (value) {
                        if (las_f[index] === value[0]) {
                            html += '<option selected value="' + value[0] + '">' + value[1] + '</option>';
                        } else
                            html += '<option value="' + value[0] + '">' + value[1] + '</option>';
                    });
                }

                html += '</select></div>';
                html += '<div class="col-sm-2">';
                html += '<i style="position: relative;top: 10px;right: 20px;cursor: pointer" class="text-success glyphicon glyphicon glyphicon-plus add_las"></i>';
                if (index !== 0) {
                    html += '<i style="position: relative;top: 10px;cursor: pointer" class="text-danger glyphicon glyphicon-minus remove_las"></i>';
                }
                html += '</div></div>';
            });
            $('.parent_rule').html(html);
        });


    });


    var data = '';
    $.get('/las/get?project_group_id=' + project_group_id).done(function (resp) {
        data = resp['data'];
    });


    function option_html2(data) {
        var h = '';
        data.forEach(function (val) {
            for (var k in val) {
                h += '<option value="' + k + '">' + k + ' | ' + val[k] + '</option>'
            }
        });
        return h
    }

    $(document).on('click', '.remove_las', function () {
        $(this).parents('.start_rule').remove();
    });

    $(document).on('click', '.add_las', function () {
        var sel = $(this).parents('.start_rule').find('.las_f');
        if (!sel.val()) {
            sel.val('#');
        }

        num += 1;
        var rule_html = '';
        rule_html += '<div class="form-group start_rule"><div class="col-sm-6"><select name="las_' + num + '" class="form-control pull-left">' + option_html2(data) + '</select></div>';
        rule_html += '<div class="col-sm-4"><select class="form-control pull-left las_f" name="las_f_' + num + '">';
        var f = [['', '请选择'], ['#', '#'], ['/', '/'], ['-', '-'], ['&', '&']];
        f.forEach(function (value) {
            rule_html += '<option value="' + value[0] + '">' + value[1] + '</option>';
        });
        rule_html += '</select></div>';
        rule_html += '<div class="col-sm-2"><i style="position: relative;top: 10px;right: 20px;cursor: pointer" class="text-success glyphicon glyphicon glyphicon-plus add_las"></i>';
        rule_html += '<i style="position: relative;top: 10px;cursor: pointer" class="text-danger glyphicon glyphicon-minus remove_las"></i>';
        rule_html += '</div></div>';

        $(this).parents('.start_rule').after(rule_html)
    });

    $('.submit_update_las').click(function () {
        var no_las = update_las_modal.find('[name="no_las"]:checked').val();

        // var start_rule_len = $('.start_rule').length;
        var las_name = btn_las.parents('td').find('input');
        var new_las_name = '';
        for (var i = 0; i <= num; i++) {
            if ($('[name="las_' + i + '"]').val())
                new_las_name += $('[name="las_' + i + '"]').val() + $('[name="las_f_' + i + '"]').val()
        }
        if ($.inArray(new_las_name[new_las_name.length - 1], ['#', '&', '-', '/']) > -1) {
            new_las_name = new_las_name.substring(0, new_las_name.length - 1)
        }

        if (no_las) {
            new_las_name = '!(' + new_las_name + ')';
        }
        las_name.val(new_las_name);
        update_las_modal.modal('hide');
    });


    $('.submit-project-part').click(function () {
        var this_form = $('form#project-data-form');
        var params = this_form.serialize();
        var part_num_relation_id = this_form.find('[name="part_num_relation_id"]').val();
        // alert(level)
        $.post('/project/part/number/submit/' + project_id + '?part_num_relation_id=' + part_num_relation_id || '', params, function (resp) {
            if (resp.success) {
                toastr.success(resp.message);
                partNumber.get_part_number(project_id, part_num_relation_id);
            } else
                toastr.error(resp.message);
        })
    });

    // init
    if (project_id)
        partNumber.get_part_relation(project_id);

    // content
    var add_content = $('#add-content');
    add_content.on('hide.bs.modal', function () {
        $(this).find('form')[0].reset();
    });
    $('.submit-content').click(function (e) {
        e.preventDefault();

        var params = add_content.find('form').serialize();
        var parent_id = add_content.find('[name="parent_id"]').val();
        var level = add_content.find('[name="level"]').val();
        params += '&parent_id=' + parent_id + '&level=' + level;

        $.post('/part/number/content/add/' + project_id, params, function (resp) {
            if (resp.success) {
                add_content.modal('hide');
                partNumber.get_part_relation(project_id)
            } else
                toastr.error(resp.message)
        })
    });


    // update name
    var update_name = $('#update-name-modal');
    update_name.on('hide.bs.modal', function () {
        $(this).find('form')[0].reset();
    });

    update_name.find('.submit_update_name').click(function () {
        var params = update_name.find('form').serialize();
        $.post('/part/number/edit/name', params, function (resp) {
            if (resp.success) {
                toastr.success(resp.message);
                partNumber.get_part_relation(project_id);
                update_name.modal('hide');
            } else {
                toastr.error(resp.message)
            }
        })
    });
});
