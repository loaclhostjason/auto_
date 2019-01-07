// document.write("undefinedundefined<script language=javascript src='../regexp/check.js'></script>");

function remove(arr) {
    var newarr = [];
    for (var i = 0; i < arr.length - 1; i++) {
        newarr.push(arr[i]);
    }
    return newarr;
}


function calcByteBit(byteStart, bitPos, bitLength, leftMargin,charWidth)
{
	var retValue = []
	if(bitPos)
	{
		for(i = 0; i < byteStart; i++)
			retValue[i] = [0, leftMargin]

		for(i = byteStart, length = bitPos + bitLength; length > 0; length = length - 8, i++)
		{
			if(i == byteStart)
				if(length <= 8)
					retValue[i] = [bitLength, (8 - length) * charWidth + leftMargin]
				else
					retValue[i] = [8 - bitPos, leftMargin]
			else if(length > 8)
				retValue[i] = [8, leftMargin]
			else
				retValue[i] = [length, (8 - length) * charWidth + leftMargin]
		}
		
		length = byteStart * 8 + bitPos + bitLength
		//toastr.info(byteStart)
		//toastr.info(length)
		length = (((length % 8) > 0) ? Math.floor((length + 8) / 8) : length / 8)
		//toastr.info(length)
		for(i = length; i < 3; i++)
			retValue[i] = [0, leftMargin]	
	}
	else
	{
		for(i = 0; i < 3; i++)
			retValue[i] = [0, 0]	
	}
	return retValue
}

$(document).ready(function () {
    function Projects() {
        AppCommonClass.call(this);
        this.get_protect_relation = function (project_id) {
            $.get('/project/tree?project_id=' + project_id).done(function (resp) {
                if (resp.success) {
                    var data = resp['data'];
                    var nodedata = data['nodedata'];
                    var linkdata = data['linkdata'];
                    myDiagram.model = new go.GraphLinksModel(nodedata, linkdata);
                } else
                    toastr.error(resp.message)
            });
        };

        this.get_attr_input = function (project_id, level, id, default_name) {
            var _default_name = default_name || null;
            $.get('/attr/content?project_id=' + project_id + '&level=' + level + '&project_relation_id=' + id, function (resp) {
                if (resp.success) {
                    var data = resp['data'];
                    var content = resp['content'];
                    attr_html(data, content, id, level, _default_name);
                } else {
                    toastr.error(resp.message)
                }


            });
        };

        this.get_project_data = function (project_id, parent_id) {
            var _this = this;
            $.get('/project/data/get?project_id=' + project_id + '&project_relation_id=' + parent_id, function (resp) {
                if (resp.success) {
                    var result = resp['result'];
                    var project_data = resp['project_data'];
                    var did_len = resp['did_len'];
                    var bit_position = resp['bit_position'];
                    var byte_position = resp['byte_position'];
                    var default_conf = resp['default_conf'];
                    var ext_bitPosition = resp['ext_bitPosition'];

                    if (resp['level'] && resp['level'] === 3) {
                        if(did_len > 0) {
                            $('.ui-table thead').html(_this.project_fixthead_html());
                            $('.table-project-data thead').html(_this.project_thead_html(did_len, bit_position, byte_position, ext_bitPosition));
                            if(result.length > 0) {  
                                $('.ui-table tbody').html(_this.project_fixdata_html(result, project_data, did_len, byte_position, default_conf, bit_position));						
                                $('.table-project-data tbody').html(_this.project_data_html(result, project_data, did_len, byte_position, default_conf, bit_position));
                            }
                        } else {
                            $('.ui-table tbody').html('');
                            $('.table-project-data tbody').html('');
                        }
                        init_editTable();
                    } else {
                        $('.ui-table thead').html('');
                        $('.ui-table tbody').html('');
                        $('.table-project-data thead').html('');
                        $('.table-project-data tbody').html('');
                    }

                } else {
                    toastr.error(resp.message)
                }
            });
        };

        this.project_fixdata_html = function (result, project_data, did_len, byte_position, default_conf, bit_position) {
            if (!result || !result.length) return '';
            var html = '';

            var _new_byte_position = [];
            if (bit_position) {
                var start_bit = bit_position[0];
                var bit_len = start_bit + bit_position.length;
                var new_byte_position = Math.ceil(bit_len / 8) - 1 + Number(byte_position);
                var dif_did_len = new_byte_position - byte_position;

                if (dif_did_len) {
                    for (var i = 1; i <= dif_did_len; i++) {
                        _new_byte_position.push(Number(byte_position) + i);
                    }					
                }
            }
			
            var idIndex = 0
            result.forEach(function (data) {
                var prid = data['level_4_id'];
                var data_info = project_data[data['level_4_id']] || {};
                var content = data_info['content'] || {};

                html += '<tr class="data-class" las-id="' + idIndex + '">';
                idIndex = idIndex + 1
                html += '<input type="hidden" name="project_relation_id" value="' + data['level_4_id'] + '">';
                html += '<input type="hidden" name="name" value="' + data['level_4'] + '">';

                // show las change name
                console.log(data['level_4']);
                html += '<td height="60" class="text-center"><a href="javascript:void(0)" class="del-project-func text-danger pull-left" data-id="' + data['level_4_id'] + '"><i class="glyphicon glyphicon-trash"></i></a>';
                html += '<a href="javascript:void (0)" class="display_name" data-pk="' + data['level_4_id'] + '">' + data['level_4'] + '</a></td>';

                html += '<td height="60" class="text-center"><div style="display: inline-flex"><div style="float: left"><input name="las" required class="tc-search-words" value="' + (data_info['las'] || '') + '"></div>';
                html += '<div style="float: right; padding:5px 0 0 10px"><a href="javascript:void(0)" class="show-las-modal-bak"  data-value="' + data['level_4'] + '"><i class="glyphicon glyphicon-edit"></i></a></div></div>';
                html += '</td>';

                html += '</div></div></td>';
            });


            html += '</tr>'
            if (result) {
                html += '<tr class="default-v"><td height="60" colspan="2"><div class="col-xs-4"><span style="position: relative; top: 5px;">默认值：</span></div>';
                html += '<div class="col-xs-8"><input name="default_conf" value="' + (default_conf || '') + '"  class="tc-search-words"/></div></td></tr>';
            }

			return html
		}
        this.project_data_html = function (result, project_data, did_len, byte_position, default_conf, bit_position) {
            if (!result || !result.length) return '';


            var html = '';

            var _new_byte_position = [];
            if (bit_position) {
                var start_bit = bit_position[0];
                var bit_len = start_bit + bit_position.length;
                var new_byte_position = Math.ceil(bit_len / 8) - 1 + Number(byte_position);
                var dif_did_len = new_byte_position - byte_position;

                if (dif_did_len) {
                    for (var i = 1; i <= dif_did_len; i++) {
                        _new_byte_position.push(Number(byte_position) + i);
                    }
                }
            }

			var idIndex = 0
            result.forEach(function (data) {
                var prid = data['level_4_id'];
                var data_info = project_data[data['level_4_id']] || {};
                var content = data_info['content'] || {};

                html += '<tr class="data-class" id="bit' + idIndex + '">';
				idIndex = idIndex + 1
                //html += '<input type="hidden" name="project_relation_id" value="' + data['level_4_id'] + '">';
                //html += '<input type="hidden" name="name" value="' + data['level_4'] + '">';

                // show las change name
                console.log(data['level_4']);
                /*html += '<td class="text-center"><a href="javascript:void(0)" class="del-project-func text-danger pull-left" data-id="' + data['level_4_id'] + '"><i class="glyphicon glyphicon-trash"></i></a>';
                html += '<a href="javascript:void (0)" class="display_name" data-pk="' + data['level_4_id'] + '">' + data['level_4'] + '</a></td>';

                html += '<td class="text-center"><div style="display: inline-flex"><div style="float: left"><input name="las" required class="tc-search-words" value="' + (data_info['las'] || '') + '"></div>';
                html += '<div style="float: right; padding:5px 0 0 10px"><a href="javascript:void(0)" class="show-las-modal-bak"  data-value="' + data['level_4'] + '"><i class="glyphicon glyphicon-edit"></i></a></div></div>';
                html += '</td>';*/

				var fmInput = null
				if(bit_position)
					fmInput = calcByteBit(byte_position, bit_position[0], bit_position.length, 5, 19.5)
				else
					fmInput = calcByteBit(byte_position, null, null, 5, 19.5)

                var bet_number = [];
                if (did_len) {
                    for (var i = 0; i < did_len; i++) {
                        bet_number.push(i);
                    }
                }
                console.log(byte_position);
                bet_number.forEach(function (num) {
                    html += '<td height="60" colspan="8">';
                    html += '<div class="col-xs-12"><div class="row">';
                    /*if (content['byte' + num]) {
                        html += '<input type="text" style="letter-spacing: 13.5px; padding-right:0px; padding-left:' + fmInput[num][1] + 'px" class="tc-search-words col-xs-12" name="' + prid + '_byte' + num + '" id="' + prid + '_byte' + num + '" onkeyup=onKeyUpEvent(\'' + prid + '_byte' + num + '\',\'[01]+$\',\'[^01]\',\'请输入0或1\')' + ' maxlength="' + fmInput[num][0] + '" value="' + (content['byte' + num] || '') + '" ' + ((bit_position.length > 0) ? '' : 'disabled') + '>';
                    } else {*/
                        // if ($.inArray(num, _new_byte_position) > -1 || num == byte_position) {
                        //if (num >= byte_position && num <= byte_position + _new_byte_position.length) 
                        if (bit_position && bit_position.length > 0 && fmInput[num][0] > 0) {
                            html += '<input type="text" style="letter-spacing: 13.5px; padding-right:0px; padding-left:' + fmInput[num][1] + 'px" class="tc-search-words col-xs-12" name="' + prid + '_byte' + num + '" id="' + prid + '_byte' + num + '" onkeyup=onKeyUpEvent(\'' + prid + '_byte' + num + '\',\'[01]+$\',\'[^01]\',\'请输入0或1\')' + ' maxlength="' + fmInput[num][0] + '" value="' + (content['byte' + num] || '') + '">'; // show or hide
                        } else
                            html += '<input type="text" style="letter-spacing: 13.5px; padding-right:0px; padding-left:' + fmInput[num][1] + 'px" class="tc-search-words col-xs-12" name="' + prid + '_byte' + num + '" id="' + prid + '_byte' + num + '" onkeyup=onKeyUpEvent(\'' + prid + '_byte' + num + '\',\'[01]+$\',\'[^01]\',\'请输入0或1\')' + ' maxlength="' + fmInput[num][0] + '" value="" disabled>';
                    //}

                    html += '</div></div></td>';
                });


                html += '</tr>'
            });

			if (result) {
                html += '<tr><td height="60" colspan="24"/></tr>';
            }


            return html
        };

        this.project_fixthead_html = function () {
            var html = '';
            html += '<tr>';
            html += '<th height="52" width="100" style="vertical-align: middle; min-width: 100px"></th>';
            html += '<th height="52" width="120" style="vertical-align: middle; min-width: 120px">LAS</th>';
            html += '</tr>';
            return html;
		}
        this.project_thead_html = function (did_len, bit_position, byte_position, ext_bitPosition) {
            var html = '';
            html += '<tr>';
            //html += '<th height="50" width="100" style="vertical-align: middle; min-width: 100px"></th>';
            //html += '<th width="120" style="vertical-align: middle; min-width: 120px">LAS</th>';

            var aaaa = [];
            var _new_byte_position = [];
            var new_bit_position = [];
            if (bit_position && bit_position.length) {
                var start_bit = bit_position[0];
                var bit_len = start_bit + bit_position.length;
                var new_byte_position = Math.ceil(bit_len / 8) - 1 + Number(byte_position);
                var dif_did_len = new_byte_position - byte_position;

                var _n = bit_len - 8;
                if (dif_did_len > 1) {
                    _n = bit_position.length - (8 * (Math.ceil(bit_len / 8) - 1));
                }


                if (dif_did_len) {
                    for (var i = 1; i <= dif_did_len; i++) {
                        _new_byte_position.push(Number(byte_position) + i);
                    }

                    ext_bitPosition = Number(ext_bitPosition);
                    // alert(_n)
                    for (var j = ext_bitPosition; j <= _n + ext_bitPosition - 1; j++) {
                        new_bit_position.push(j)
                    }

                }

                console.log(_new_byte_position);
                aaaa = remove(_new_byte_position);
            }
            console.log(aaaa)

            if (did_len) {
                for (var i = 0; i < did_len; i++) {
                    html += '<th colspan="8" height="52"><div class="text-center with-bottom-border"><span>BYTE' + i + '</span></div>';
                    html += '<div style="width: 172px">';
                    var a = '';
                    if (_new_byte_position.length && $.inArray(i, _new_byte_position) > -1) {
                        if (!aaaa.length) {
                            for (var j = 7; j >= 0; j--) {
                                if ($.inArray(j, new_bit_position) > -1) {
                                    a += '<div style="width: 11.5%; float: left;background: #090; color: #fff; text-align: center"><span>' + j + '</span>';
                                } else {
                                    a += '<div style="width: 11.5%; float: left;text-align: center"><span>' + j + '</span>';
                                }
                                a += '</div>';
                            }
                        } else {
                            if ($.inArray(i, aaaa) > -1) {
                                for (var j = 7; j >= 0; j--) {
                                    a += '<div style="width: 11.5%; float: left;background: #090; color: #fff; text-align: center"><span>' + j + '</span>';
                                    a += '</div>';
                                }
                            } else {
                                for (var j = 7; j >= 0; j--) {
                                    if ($.inArray(j, new_bit_position) > -1) {
                                        a += '<div style="width: 11.5%; float: left;background: #090; color: #fff; text-align: center"><span>' + j + '</span>';
                                    } else {
                                        a += '<div style="width: 11.5%; float: left;text-align: center"><span>' + j + '</span>';
                                    }
                                    a += '</div>';
                                }
                            }
                        }
                    } else {
                        for (var j = 7; j >= 0; j--) {
                            if ($.inArray(j, bit_position) > -1 && byte_position == i) {
                                a += '<div style="width: 11.5%; float: left;background: #090; color: #fff; text-align: center"><span>' + j + '</span>';
                            } else {
                                a += '<div style="width: 11.5%; float: left;text-align: center"><span>' + j + '</span>';
                            }
                            a += '</div>';
                        }
                    }

                    html += a;
                    html += '</div></th>';
                }
            }
            html += '</tr>';
            return html;
        };
    }

    Projects.prototype = Object.create(AppCommonClass.prototype);
    Projects.prototype.constructor = Projects;

    var projects = new Projects();
    $.g_projects = new Projects();

    var create_project_modal = $('#create_project_modal');
    $('.add-project').click(function () {
        projects.show_modal(create_project_modal, $(this));
    });

    $('.submit_project').click(function () {
        var params = create_project_modal.find('form').serialize();
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
    var add_content = $('#add-content');
    $('.submit-content').click(function (e) {
        e.preventDefault();

        var params = add_content.find('form').serialize();
        var parent_id = add_content.find('[name="parent_id"]').val();
        var level = add_content.find('[name="level"]').val();
        params += '&parent_id=' + parent_id + '&level=' + level;

        $.post('/project/content/add/' + project_id, params, function (resp) {
            if (resp.success) {
                add_content.modal('hide');
                if (level >= 4) {
                    projects.get_project_data(project_id, parent_id);
                    $('.submit-project-data').show();
                }

                if (level < 4)
                    projects.get_protect_relation(project_id)
            } else
                toastr.error(resp.message)
        })
    });


    // submit attr
    $(document).on('click', '.submit-add-attr', function () {
        var form_ = $('form#attr-form');
        var form_data = form_.serialize();
        toastr.options.timeOut = null;
        toastr.info('正在保存中...，请稍等');
        $.post('/manage/attr/content/add?project_id=' + project_id, form_data, function (resp) {
            toastr.clear();
            toastr.options.timeOut = 2000;
            if (resp.success) {
                projects.get_project_data(project_id, $('[name="project_relation_id"]').val());
                projects.get_attr_input(project_id, form_.find('[name="level"]').val(), form_.find('[name="project_relation_id"]').val());

                toastr.success(resp['message']);
            } else {
                toastr.error(resp['message']);

            }

        })
    });

    // update username
    var update_name = $('#update-name-modal');
    update_name.on('hide.bs.modal', function () {
        $(this).find('form')[0].reset();
    });

    update_name.find('.submit_update_name').click(function () {
        var params = update_name.find('form').serialize();
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
        var this_form = $('form#project-data-form');
        var params = this_form.serialize();

        toastr.options.timeOut = null;
        toastr.info('正在保存中...');
        $.post('/project/data/submit/' + project_id + '?data_relation_id=' + $('[name="project_relation_id"]').val(), params, function (resp) {
            toastr.clear();
            toastr.options.timeOut = 2000;
            if (resp.success) {
                toastr.success(resp.message);
                projects.get_project_data(project_id, $.g_parent_id);
            } else
                toastr.error(resp.message);
        })
    });


    $(document).on('click', '.del-project-func', function () {
        var id = $(this).data('id');
        var _this = $(this);
        Modal.confirm({
            msg: '是否删除？'
        }).on(function (e) {
            if (e) {
                $.post('/project/tree/delete/' + id, '', function (data) {
                    if (data.success) {
                        toastr.success(data.message);
						var lastr = _this.parents('.data-class').attr('las-id');
                        _this.parents('.data-class').remove();
						
						var bit_table = document.getElementById('bittable')
						var bit_tr = document.getElementById('bit' + lastr)
						
						//var las_tr = _this.parentNode.parentNode.rowIndex
						if(bit_table && bit_tr){
							//toastr.info(bit_tr.rowIndex)
							bit_table.deleteRow(bit_tr.rowIndex)
						}
						
                        if (!$('.data-class').length) {
                            $('.default-v').remove();
                        }

                    } else {
                        toastr.error(data.message);
                    }
                })
            }
        })
    });

    // 修改las name
    function init_editTable() {
        $('.display_name').editable({
            type: "text",
            title: "显示名",
            disabled: false,
            display: false,
            emptytext: "无",
            url: '/change/project/data/name',
            validate: function (value) {
                if (!$.trim(value)) {
                    return '不能为空';
                }
            },
            success: function (response, newValue) {
                if (response.success) {
                    $(this).text(newValue);
                    toastr.success(response.message)
                } else {
                    toastr.error(response.message)
                }
            }
        });
    }

});

// extra config
$(document).ready(function () {
    $('.add-extra-config').click(function () {
        var level = $(this).attr('level');
        var name = $(this).attr('name');
        var project_relation_id = $(this).attr('project_relation_id');
        window.location.href = '/project/edit/' + project_id + '/extra?level=' + (level || 0) + '&name=' + (name || '') + '&project_relation_id=' + project_relation_id || '';
    })
});