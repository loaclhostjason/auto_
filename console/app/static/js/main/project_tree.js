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
        makeButton("新增过程",
            function (e, obj) {

            })
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


