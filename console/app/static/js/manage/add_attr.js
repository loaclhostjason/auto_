$(document).ready(function () {
    var html_tr = '';

    html_tr += '<tr>';
    html_tr += '<td><input name="item" class="td-input" required/></td>';
    html_tr += '<td><input name="item_protocol" class="td-input"/></td>';
    // html_tr += '<td><input name="item_zh" class="td-input" required/></td>';
    html_tr += '<td><input name="item_default" class="td-input"/></td>';
    html_tr += '<td><input name="item_check" type="td-input" maxlength="11" class="td-input" onkeyup="onCheckKeyUpEvent(\'item_check\')"/></td>';
    html_tr += '<td><input name="item_required" type="checkbox" class="td-input" value="y"/></td>';
    html_tr += '<td><a href="javascript:void (0)"><i class="glyphicon glyphicon-resize-vertical"></i></a><span class="text-explode">|</span><a href="javascript:void(0);" class="td-remove">移除</a></td>';

    html_tr += '</tr>';


    $('.td-add').click(function () {
        $(this).parents('tr').before(html_tr);
    });
    $(document).on('click', '.td-remove', function () {
        $(this).parents('tr').remove();
    });


});