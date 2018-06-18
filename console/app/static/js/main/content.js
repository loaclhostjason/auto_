$(document).ready(function () {
    let add_content = $('#add-content');
    add_content.on('hide.bs.modal', function () {
        $(this).find('form')[0].reset();
    })
});