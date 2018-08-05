$(document).ready(function () {

    var table_type = ['readsection', 'writsection', 'resetsection'];

    function type_html(t) {
        var html_tr = '';
        html_tr += '<tr>';
        html_tr += '<td><input name="' + t + '_item" class="td-input" required/></td>';
        // html_tr += '<td><input name="' + t + '_item_zh" class="td-input" required/></td>';
        html_tr += '<td><a href="javascript:void(0);" class="td-remove">移除</a></td>';

        html_tr += '</tr>';
        return html_tr
    }


    $(document).on('click', '.td-add', function () {
        var _this = $(this);
        table_type.forEach(function (value) {
            var tables = _this.parents('table');
            var is_parents_table = tables.hasClass('table-extra-' + value);
            if (is_parents_table) {
                _this.parents('tr').before(type_html(value));
            }
        });
    });
    $(document).on('click', '.td-remove', function () {
        $(this).parents('tr').remove();
    });


});