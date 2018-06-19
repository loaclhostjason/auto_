let app_common = new AppCommonClass();

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
        makeButton("删除", function (e, obj) {
            let node = obj.part.adornedPart;
            if (node === null) return false;

            let thisemp = node.data;
            let id = thisemp['key'];
            $.post('/project/tree/delete/' + id, '', function (resp) {
                if (resp.success) {
                    toastr.success(resp.message);
                    $.g_projects.get_protect_relation(project_id);
                } else {
                    toastr.error(resp.message)
                }
            })

        }),
        makeButton("复制", function (e, obj) {
            let node = obj.part.adornedPart;
            if (node === null) return false;

            let thisemp = node.data;
            let key = thisemp['key'];
            let level = thisemp['level'];
            let name = thisemp['name'];

            console.log(thisemp);
            if (key) {
                let params = {
                    'level': level,
                    'content': name
                };
                $.post('/project/content/add/' + project_id + '?copy_id=' + key + '&action=copy', params, function (resp) {
                    if (resp.success) {
                        toastr.success('复制成功');
                        $.g_projects.get_protect_relation(project_id);
                    } else {
                        toastr.error(resp.message)
                    }
                })
            }
        }),
        makeButton("上移", function (e, obj) {
            let node = obj.part.adornedPart;
            if (node === null) return false;

            let thisemp = node.data;
            let key = thisemp['key'];

            $.post('/project/relation?id=' + key + '&type=up', '', function (resp) {
                if (resp.success) {
                    toastr.success(resp.message);
                    $.g_projects.get_protect_relation(project_id)
                } else {
                    toastr.error(resp.message)
                }
            })
        }),
        makeButton("下移", function (e, obj) {
            let node = obj.part.adornedPart;
            if (node === null) return false;

            let thisemp = node.data;
            let key = thisemp['key'];

            $.post('/project/relation?id=' + key + '&type=down', '', function (resp) {
                if (resp.success) {
                    toastr.success(resp.message);
                    $.g_projects.get_protect_relation(project_id)
                } else {
                    toastr.error(resp.message)
                }
            })
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


