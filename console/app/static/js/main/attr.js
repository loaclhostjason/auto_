var attr_html = function (data, content, id, level) {
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
        form_html += '<div class="col-sm-3"><label class="control-label pull-right">' + required_html(value['item_required']) + value['item_zh'] + '</label></div>';
        form_html += '<div class="col-sm-8">' + required_input(value['item'], value['item_required'], content, value['item_protocol']) + '</div>';
        form_html += '</div>';
    });
    form_html += '<div class="form-group"><div class="col-sm-3"></div><div class="col-sm-8"><button type="button" class="btn btn-primary submit-add-attr">保存</button></div></div>';
    attr_form.html(form_html);

};


function required_html(required) {
    var html = '';
    if (required)
        html = '<span class="text-danger">*</span>';
    return html

}

function required_input(field, required, content, field_protocol) {
    var html = '<input class="form-control pull-left" name="' + (field_protocol ? field_protocol + '-' : '') + field + '" type="text" value="' + (content ? content[field] || '' : "") + '">';
    if (required)
        html = '<input class="form-control pull-left" name="' + field + '" type="text" value="' + (content ? content[field] || '' : "") + '" required>';

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