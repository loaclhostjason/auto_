$(document).ready(function () {
    let $$ = go.GraphObject.make;

    let myDiagram =
        $$(go.Diagram, "myDiagramFunc",
            {
                initialContentAlignment: go.Spot.Center,
                "undoManager.isEnabled": true,
                draggingTool: new NonRealtimeDraggingTool(),
                "draggingTool.isEnabled": false,
                layout: $$(go.TreeLayout,
                    {
                        setsPortSpot: false,
                        setsChildPortSpot: false,
                        arrangement: go.TreeLayout.ArrangementVertical
                    }
                )
            });

    // function makeButton(text, action, visiblePredicate) {
    //     return $$("ContextMenuButton",
    //         $$(go.TextBlock, text),
    //         {click: action},
    //         visiblePredicate ? new go.Binding("visible", "", function (o, e) {
    //             return o.diagram ? visiblePredicate(o, e) : false;
    //         }).ofObject() : {});
    // }

    myDiagram.nodeTemplateMap.add("ProductNode",
        $$(go.Node, "Auto",
            $$(go.Shape, "RoundedRectangle", {strokeWidth: 1, fill: 'white'}),
            $$(go.TextBlock, {margin: 8}, new go.Binding("text", "name")),
            {
                click: function (e, obj) {
                    let node = obj.part.data;
                    if (node === null) return false;

                    let parent_id = node['key'];
                    let level = node['level'];

                    $.g_projects.get_attr_input(project_id, level, parent_id)
                }
            }
        ));

    myDiagram.nodeTemplateMap.add("FuncNode",
        $$(go.Node, "Auto",
            $$(go.Shape, "RoundedRectangle", {strokeWidth: 1, fill: 'white', stroke: "green"}),
            $$(go.TextBlock, {margin: 8, stroke: "green"}, new go.Binding("text", "name")),
            {
                click: function (e, obj) {
                    let node = obj.part.data;
                    if (node === null) return false;

                    let parent_id = node['key'];
                    let level = node['level'];

                    $.g_projects.get_attr_input(project_id, level, parent_id)
                }
            }
        ));


    myDiagram.linkTemplateMap.add("ProductLink",
        $$(go.Link, {selectionAdorned: false},
            $$(go.Shape, {strokeWidth: 2, stroke: "#666"})
        ));


    $.g_func_myDiagram = myDiagram;
});