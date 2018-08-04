$(document).ready(function () {


    var fixHelperModified = function (e, ui) {
            //console.log(ui)
            ui.children().each(function () {
                $(this).width($(this).width());
            });
            return ui;
        },
        updateIndex = function (e, ui) {
            $('td.index', ui.item.parent()).each(function (i) {
                $(this).html(i + 1);
            });
        };

    $(".sort_table tbody").sortable({
        cursor: "move",
        axis: "y",
        helper: fixHelperModified,
        update: function (e, ui) {
            var this_ = $(this);
            toastr.remove();
            updateIndex(e, ui);

            var params = $('form').serialize();
            $.post('/manage/attrs/edit/' + attr_id + '?action=json', params, function (resp) {
                if (resp.success) {
                    toastr.success(resp.message);
                } else {
                    toastr.error(resp.message);
                    this_.sortable('cancel');
                }
            })
        }
    }).disableSelection();
});