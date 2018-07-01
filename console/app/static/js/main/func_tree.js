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

    function makeButton(text, action, visiblePredicate) {
        return $$("ContextMenuButton",
            $$(go.TextBlock, text),
            {click: action},
            visiblePredicate ? new go.Binding("visible", "", function (o, e) {
                return o.diagram ? visiblePredicate(o, e) : false;
            }).ofObject() : {});
    }

    let funcContextMenu =
        $$(go.Adornment, "Vertical",
            makeButton('修改名称', function (e, obj) {
                let node = obj.part.adornedPart;
                if (node === null) return false;

                let thisemp = node.data;
                let id = thisemp['key'];

                let update_name = $('#update-name-modal');
                app_common.show_modal(update_name);
                update_name.find('[name="id"]').val(id);
            }),
            makeButton('删除', function (e, obj) {
                let node = obj.part.adornedPart;
                if (node === null) return false;

                let thisemp = node.data;
                let id = thisemp['key'];
                let parent_id = thisemp['parent_id'];
                $.post('/project/tree/delete/' + id, '', function (resp) {
                    if (resp.success) {
                        toastr.success(resp.message);
                        $.g_projects.get_func_relation(project_id, parent_id, 3);
                    } else {
                        toastr.error(resp.message)
                    }
                })
            })
        );

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
            }, {
                contextMenu: funcContextMenu
            }
        ));


    myDiagram.linkTemplateMap.add("ProductLink",
        $$(go.Link, {selectionAdorned: false},
            $$(go.Shape, {strokeWidth: 2, stroke: "#666"})
        ));


    $.g_func_myDiagram = myDiagram;
});