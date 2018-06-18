let app_common = new AppCommonClass();

let $$ = go.GraphObject.make;

let myDiagram =
    $$(go.Diagram, "myDiagramProject",
        {
            initialContentAlignment: go.Spot.Center,
            "undoManager.isEnabled": true,
            draggingTool: new NonRealtimeDraggingTool(),
            "draggingTool.isEnabled": false,
            layout: $$(go.TreeLayout,
                {
                    setsPortSpot: false,
                    setsChildPortSpot: false,
                    arrangement: go.TreeLayout.ArrangementHorizontal
                }
            )
        });

function makeButton(text, action, visiblePredicate) {
    return $$("ContextMenuButton",
        $$(go.TextBlock, text),
        {click: action},
        visiblePredicate ? new go.Binding("visible", "", function (o, e) {
            return o.diagram ? visiblePredicate(o, e) : false;
        }).ofObject() : {});
}

let projectContextMenu =
    $$(go.Adornment, "Vertical",
        makeButton("新增DID", function (e, obj) {
            let node = obj.part.adornedPart;
            if (node === null) return false;

            let thisemp = node.data;
            let parent_id = thisemp['key'];


            let add_content = $("#add-content");
            app_common.show_modal(add_content, $(this));
            add_content.find('[name="parent_id"]').val(parent_id);
        }),
        makeButton("新增配置", function (e, obj) {

        }),
        makeButton("新增配置选项", function (e, obj) {

        }),
        makeButton("删除", function (e, obj) {

        }),
        makeButton("复制", function (e, obj) {

        }),
        makeButton("黏贴", function (e, obj) {

        }),
        makeButton("上移", function (e, obj) {

        }),
        makeButton("下移", function (e, obj) {

        }),
    );

myDiagram.nodeTemplate =
    $$(go.Node, "Auto",
        $$(go.Shape, "RoundedRectangle", {strokeWidth: 1, fill: 'white'}),
        $$(go.TextBlock, {margin: 8}, new go.Binding("text", "name")),
        {
            click: function (e, obj) {


            }
        },
        {
            contextMenu: projectContextMenu
        }
    );

myDiagram.linkTemplate =
    $$(go.Link, {selectionAdorned: false},
        $$(go.Shape, {strokeWidth: 2, stroke: "#666"}),
        $$(go.Shape, {fill: '#666', stroke: null, toArrow: "Standard", segmentFraction: 0})
    );


