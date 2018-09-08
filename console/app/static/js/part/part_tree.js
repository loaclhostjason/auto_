var app_common = new AppCommonClass();

var $$ = go.GraphObject.make;

var myPartDiagram =
    $$(go.Diagram, "myDiagramProjectPart",
        {
            initialContentAlignment: go.Spot.Center,
            "undoManager.isEnabled": true,
            draggingTool: new NonRealtimeDraggingTool(),
            "draggingTool.isEnabled": false,
            layout: $$(go.TreeLayout,
                {
                    setsPortSpot: false,
                    setsChildPortSpot: false,
                    arrangement: go.TreeLayout.ArrangementHorizontal,
                    layerSpacing: 180
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

var firstMenu =
    $$(go.Adornment, "Vertical",
        makeButton("添加零件号", function (e, obj) {
            var node = obj.part.adornedPart;
            if (node === null) return false;

            var thisemp = node.data;
            var parent_id = thisemp['key'];
            var level = thisemp['level'];

            var add_content = $("#add-content");
            app_common.show_modal(add_content, $(this));
            add_content.find('[name="parent_id"]').val(parent_id);
            add_content.find('[name="level"]').val(Number(level) + 1);
        })
    );


var secondMenu =
    $$(go.Adornment, "Vertical",
        makeButton('修改名称', function (e, obj) {
            var node = obj.part.adornedPart;
            if (node === null) return false;

            var thisemp = node.data;
            var id = thisemp['key'];

            var update_name = $('#update-name-modal');
            app_common.show_modal(update_name);
            update_name.find('[name="id"]').val(id);
        }),
        makeButton("删除", function (e, obj) {
            var node = obj.part.adornedPart;
            if (node === null) return false;

            var thisemp = node.data;
            var id = thisemp['key'];
            $.post('/part/number/tree/delete/' + id, '', function (resp) {
                if (resp.success) {
                    toastr.success(resp.message);
                    $.g_part.get_part_relation(project_id);
                } else {
                    toastr.error(resp.message)
                }
            })

        }),
        makeButton("复制", function (e, obj) {
            var node = obj.part.adornedPart;
            if (node === null) return false;

            var thisemp = node.data;
            var key = thisemp['key'];
            var level = thisemp['level'];
            var name = thisemp['name'];

            var params = {
                'level': level,
                'content': name
            };
            $.post('/part/number/content/add/' + project_id + '?copy_id=' + key + '&action=copy', params, function (resp) {
                if (resp.success) {
                    toastr.success('复制成功');
                    $.g_part.get_part_relation(project_id);
                } else {
                    toastr.error(resp.message)
                }
            })

        }),
        makeButton("上移", function (e, obj) {
            var node = obj.part.adornedPart;
            if (node === null) return false;

            var thisemp = node.data;
            var key = thisemp['key'];

            $.post('/part/number/relation?id=' + key + '&type=up', '', function (resp) {
                if (resp.success) {
                    toastr.success(resp.message);
                    $.g_part.get_part_relation(project_id)
                } else {
                    toastr.error(resp.message)
                }
            })
        }),
        makeButton("下移", function (e, obj) {
            var node = obj.part.adornedPart;
            if (node === null) return false;

            var thisemp = node.data;
            var key = thisemp['key'];

            $.post('/part/number/relation?id=' + key + '&type=down', '', function (resp) {
                if (resp.success) {
                    toastr.success(resp.message);
                    $.g_part.get_part_relation(project_id)
                } else {
                    toastr.error(resp.message)
                }
            })
        })
    );

myPartDiagram.nodeTemplateMap.add("FirstNode",
    $$(go.Node, "Horizontal", {selectionObjectName: "FirstNode"},
        $$(go.Panel, "Auto", {name: "FirstNode"},
            $$(go.Shape, "RoundedRectangle", {strokeWidth: 1, fill: 'white'}),
            $$(go.TextBlock, {margin: 8}, new go.Binding("text", "name"))
        ),
        {
            click: function (e, obj) {
                var node = obj.part.data;
                if (node === null) return false;
                $.g_part.get_part_number(project_id, '', true);
                $('.part-panel').find('[name="part_num_relation_id"]').val('');

                $('.submit-project-part').hide();

                var part_attr_form = $('#part-attr-form');
                part_attr_form.hide();
                part_attr_form.find('[name="part_num_relation_id"]').val('');
            }
        }, {
            contextMenu: firstMenu
        },
        $$(go.Panel, {height: 15}, $$("TreeExpanderButton"))
    ));


myPartDiagram.nodeTemplateMap.add("SecondNode",
    $$(go.Node, "Horizontal", {selectionObjectName: "SecondNode"},
        $$(go.Panel, "Auto", {name: "SecondNode"},
            $$(go.Shape, "RoundedRectangle", {strokeWidth: 1, fill: 'white'}),
            $$(go.TextBlock, {margin: 8}, new go.Binding("text", "name"))
        ),
        {
            click: function (e, obj) {
                var node = obj.part.data;
                if (node === null) return false;
                var part_id = node['key'];
                $('.part-panel').find('[name="part_num_relation_id"]').val(part_id);
                $.g_part.get_part_number(project_id, part_id);

                $('.submit-project-part').show();

                var part_attr_form = $('#part-attr-form');
                part_attr_form.show();
                part_attr_form.find('[name="part_num_relation_id"]').val(part_id);

                $.g_part.get_part_attr(part_id);

            }
        }, {
            contextMenu: secondMenu
        },
        $$(go.Panel, {height: 15}, $$("TreeExpanderButton"))
    ));


myPartDiagram.linkTemplate =
    $$(go.Link,
        {
            selectionAdorned: false,
            routing: go.Link.Orthogonal,
            corner: 10,
            fromSpot: new go.Spot(1, 0.5),
            toSpot: new go.Spot(0, 0.5)
        },
        $$(go.Shape, {strokeWidth: 2, stroke: "#666"}),
        $$(go.Shape, {fill: '#666', stroke: null, toArrow: "Standard", segmentFraction: 0})
    );


