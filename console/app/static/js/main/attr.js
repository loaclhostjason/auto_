var attr_html = function (data, content, id, level, default_name) {
    var _default_name = default_name || null;
    var attr_form = $('#attr-form');
    if (!data || !data.length) {
        attr_form.html('');
        return false
    }
    var form_html = '';
    form_html += '<input name="project_relation_id" type="hidden" value="' + id + '">';
    form_html += '<input name="level" type="hidden" value="' + level + '">';
    data.forEach(function (value) {
        form_html += '<div class="form-group">';
        if (value['item']  === 'DidNo') {
            form_html += '<div class="col-sm-4"><label class="control-label pull-right">' + required_html(value['item_required']) + value['item'] + '</label></div>';
            form_html += '<div class="col-sm-7">' + required_input(value['item'], value['item_required'], content, value['item_protocol'], value['item_default'] || _default_name, value['item_check']) + '</div>';
        } else {
            form_html += '<div class="col-sm-4"><label class="control-label pull-right">' + required_html(value['item_required']) + value['item'] + '</label></div>';
            form_html += '<div class="col-sm-7">' + required_input(value['item'], value['item_required'], content, value['item_protocol'], value['item_default'], value['item_check']) + '</div>';
        }

        form_html += '</div>';
    });
    form_html += '<div class="form-group"><div class="col-sm-4"></div><div class="col-sm-7"><button type="button" class="btn btn-primary submit-add-attr">保存</button></div></div>';
    attr_form.html(form_html);

};


function check_input(strCheck)
{
	var strRegExpCheck = ''
	var strRegExpReplace = ''
	var strInfo = ''
    switch(strCheck)
    {
        case "_N":  //自然数集
			strRegExpCheck = '[0-9]+$'
            strRegExpReplace = '[^0-9]'
			strInfo = '自然数'
            break;
        case "N+":  //正整数集
            //strRegExp = '^[1-9]\\d*$'
			strInfo = '正整数'
            break;
        case "_Z":  //整数集
            //strRegExp = '^-?[1-9]\\d*$'
			strInfo = '整数'
            break;
        case "_R":  //实数集
            //strRegExp = '^0\\.\\d+$|^[1-9]+(\\.\\d+)?$'
			strInfo = '实数'
            break;
        case "_S":  //不含数字大写串
            strRegExpCheck = '[A-Z]+$'
            strRegExpReplace = '[^A-Z]'
			strInfo = '大写字母'
            break;
        case "SD":  //含数字串且字母开头的大写串
            //strRegExp = '^(?!^[A-Z][A-Z0-9]*$)'
			strInfo = '大写字母开头的字母数字串'
            break;
        case "_s":  //不含数字小写串
            strRegExpCheck = '[a-z]+$'
            strRegExpReplace = '[^a-z]'
			strInfo = '小写字母'
            break;
        case "sd":  //含数字串且字母开头的小写串
            //strRegExp = '^[a-z][a-z0-9]*$'
			strInfo = '小写字母开头的字母数字串'
            break;
        case "_C":  //不含数字串(不判断大小写)
            strRegExpCheck = '[A-Za-z]+$'
            strRegExpReplace = '[^a-zA-Z]'
			strInfo = '字母串'
            break;
        case "CD":  //含数字串且字母开头的串(不判断大小写)
            //strRegExp = '^[a-zA-Z][a-zA-Z0-9]*$'
			strInfo = '字母开头的字母数字串'
            break;
        case "_B":  //布尔
            break;
		default:
			break;
    }
	return [strRegExpCheck, strRegExpReplace, strInfo];
}

function required_html(required) {
    var html = '';
    if (required)
        html = '<span class="text-danger">*</span>';
    return html

}
function onKeyUpEvent(inputName, strRegExpCheck, strRegExpReplace, strInfo)
{
	var inputValue = document.getElementById(inputName);
	var regExp = new RegExp(strRegExpCheck, 'g');

	if(!regExp.test(inputValue.value))
	{
		toastr.info(strInfo)
	}
  regExp = new RegExp(strRegExpReplace, 'g');
	inputValue.value=inputValue.value.replace(regExp, '');
}
function required_input(field, required, content, field_protocol, field_default, field_check) {
    var maxlen = 0, regExpCheck = '', regExpReplace, strInfo = ''
	if(typeof(field_check) != "undefined" && field_check != null)
	{
		var length = field_check.length
		if (length >= 11)
		{
		    //得到输入校验
			var retValue = check_input(field_check.substring(length - 9, length - 7))
            regExpCheck = retValue[0]
            regExpReplace = retValue[1]
			strInfo = retValue[2]
			//得到长度限制
			maxlen = parseInt(field_check.substring(length - 7, length - 4))
		}
	}

	//var html = '<input class="form-control pull-left" name="' + (field_protocol ? field_protocol + '-' : '') + field + '" type="text" value="' + (content ? content[field] || (field_default || '') : "") + '">';
    var html = '<input class="form-control pull-left" id="' + (field_protocol ? field_protocol + '-' : '') + field + '" name="' + (field_protocol ? field_protocol + '-' : '') + field + '" type="text" value="' + (content ? content[field] || (field_default|| '') : "") + '"' + ((maxlen == 0 || maxlen == NaN) ? 'maxlength="0"' : 'maxlength="' + String(maxlen) + '"') + ((regExpReplace != '') ? ' onkeyup=onKeyUpEvent(\'' + (field_protocol ? field_protocol + '-' : '') + field + '\',\'' + regExpCheck + '\',\'' + regExpReplace + '\',\'' + strInfo + '\')' : 'onkeyup=value=value')  + '>';
    if (required)
        html = '<input class="form-control pull-left" name="' + field + '" type="text" value="' + (content ? content[field] || (field_default || '') : "") + '" required>';

    return html

}

$(document).ready(function () {

    $(document).on('keyup', $('[name="BytePosition"]'), function () {
        var byte = $('[name="BytePosition"]');
        var tmptxt = byte.val();

        try {
            byte.val(tmptxt.replace(/\D/g, ''));
        } catch (e) {
            console.log(e)
        }

    }).bind("paste", function () {
        var byte = $('[name="BytePosition"]');
        var tmptxt = byte.val();

        try {
            byte.val(tmptxt.replace(/\D/g, ''));
        } catch (e) {
            console.log(e)
        }
    }).css("ime-mode", "disabled");


    $(document).on('keyup', $('[name="BitPosition"]'), function () {
        var bite = $('[name="BitPosition"]');
        var tmptxt = bite.val();

        try {
            bite.val(tmptxt.replace(/\D/g, ''));
        } catch (e) {
            console.log(e)
        }
    }).bind("paste", function () {
        var bite = $('[name="BitPosition"]');
        var tmptxt = bite.val();

        try {
            bite.val(tmptxt.replace(/\D/g, ''));
        } catch (e) {
            console.log(e)
        }
    }).css("ime-mode", "disabled");
});