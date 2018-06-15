function AppCommonClass() {
    this.name = 'admin'
}

AppCommonClass.prototype.show_modal = function (dom, btn) {
    dom.modal({
        backdrop: "static"
    }, btn);
};

AppCommonClass.prototype.hide_modal = function (dom) {
    dom.find('form')[0].reset();
};