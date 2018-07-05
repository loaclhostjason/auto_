let attr_html = function (data, content, id, level) {
    let attr_form = $('#attr-form');
    if (!data || !data.length) {
        attr_form.html('');
        return false
    }
    let form_html = '';
    form_html += '<input name="project_relation_id" type="hidden" value="' + id + '">';
    form_html += '<input name="level" type="hidden" value="' + level + '">';
    data.forEach(function (value) {
        form_html += '<div class="form-group">';
        form_html += '<div class="col-sm-3"><label class="control-label pull-right">' + required_html(value['item_required']) + value['item_zh'] + '</label></div>';
        form_html += '<div class="col-sm-8">' + required_input(value['item'], value['item_required'], content, value['item_protocol']) + '</div>';
        form_html += '</div>';
    });
    form_html += '<div class="form-group"><div class="col-sm-2"></div><div class="col-sm-8"><button type="button" class="btn btn-primary submit-add-attr">保存</button></div></div>';
    attr_form.html(form_html);

};


function required_html(required) {
    let html = '';
    if (required)
        html = '<span class="text-danger">*</span>';
    return html

}

function required_input(field, required, content, field_protocol) {
    let html = '<input class="form-control pull-left" name="' + (field_protocol ? field_protocol + '-' : '') + field + '" type="text" value="' + (content ? content[field] : "") + '">';
    if (required)
        html = '<input class="form-control pull-left" name="' + field + '" type="text" value="' + (content ? content[field] : "") + '" required>';

    return html

}