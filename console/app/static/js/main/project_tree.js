var app_common = new AppCommonClass();

var $$ = go.GraphObject.make;

var myDiagram =
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

var firstContextMenu =
    $$(go.Adornment, "Vertical",
        makeButton("新增DID", function (e, obj) {
            var node = obj.part.adornedPart;
            if (node === null) return false;

            var thisemp = node.data;
            var parent_id = thisemp['key'];
            var level = thisemp['level'];


            var add_content = $("#add-content");
            app_common.show_modal(add_content, $(this));
            add_content.find('[name="parent_id"]').val(parent_id);
            add_content.find('[name="level"]').val(Number(level) + 1);
        }),
        makeButton('修改名称', function (e, obj) {
            var node = obj.part.adornedPart;
            if (node === null) return false;

            var thisemp = node.data;
            var id = thisemp['key'];

            var update_name = $('#update-name-modal');
            app_common.show_modal(update_name);
            update_name.find('[name="id"]').val(id);
        })
    );

var secondContextMenu =
    $$(go.Adornment, "Vertical",
        makeButton("新增配置", function (e, obj) {
            var node = obj.part.adornedPart;
            if (node === null) return false;

            var thisemp = node.data;
            var parent_id = thisemp['key'];
            var level = thisemp['level'];


            var add_content = $("#add-content");
            app_common.show_modal(add_content, $(this));
            add_content.find('[name="parent_id"]').val(parent_id);
            add_content.find('[name="level"]').val(Number(level) + 1);
        }),
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
            $.post('/project/content/add/' + project_id + '?copy_id=' + key + '&action=copy', params, function (resp) {
                if (resp.success) {
                    toastr.success('复制成功');
                    $.g_projects.get_protect_relation(project_id);
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
            var node = obj.part.adornedPart;
            if (node === null) return false;

            var thisemp = node.data;
            var key = thisemp['key'];

            $.post('/project/relation?id=' + key + '&type=down', '', function (resp) {
                if (resp.success) {
                    toastr.success(resp.message);
                    $.g_projects.get_protect_relation(project_id)
                } else {
                    toastr.error(resp.message)
                }
            })
        })
    );


var thirdContextMenu =
    $$(go.Adornment, "Vertical",
        makeButton("新增配置选项", function (e, obj) {
            var node = obj.part.adornedPart;
            if (node === null) return false;

            var thisemp = node.data;
            var parent_id = thisemp['key'];
            var level = thisemp['level'];


            var add_content = $("#add-content");
            app_common.show_modal(add_content, $(this));
            add_content.find('[name="parent_id"]').val(parent_id);
            add_content.find('[name="level"]').val(Number(level) + 1);
        }),
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
            $.post('/project/content/add/' + project_id + '?copy_id=' + key + '&action=copy', params, function (resp) {
                if (resp.success) {
                    toastr.success('复制成功');
                    $.g_projects.get_protect_relation(project_id);
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
            var node = obj.part.adornedPart;
            if (node === null) return false;

            var thisemp = node.data;
            var key = thisemp['key'];

            $.post('/project/relation?id=' + key + '&type=down', '', function (resp) {
                if (resp.success) {
                    toastr.success(resp.message);
                    $.g_projects.get_protect_relation(project_id)
                } else {
                    toastr.error(resp.message)
                }
            })
        })
    );

myDiagram.nodeTemplateMap.add("FirstNode",
    $$(go.Node, "Horizontal", {selectionObjectName: "FirstNode"},
        $$(go.Panel, "Auto", {name: "FirstNode"},
            $$(go.Shape, "RoundedRectangle", {strokeWidth: 1, fill: 'white'}),
            $$(go.TextBlock, {margin: 8}, new go.Binding("text", "name"))
        ),
        {
            click: function (e, obj) {
                var node = obj.part.data;
                if (node === null) return false;

                var parent_id = node['key'];
                var level = node['level'];

                $.g_projects.get_attr_input(project_id, level, parent_id);

                // extra config
                $('.add-extra-config').show();
                $('.add-extra-config').attr('level', 1);
                $('.add-extra-config').attr('project_relation_id', parent_id);
                $('.submit-project-data').hide();
            }
        }, {
            contextMenu: firstContextMenu
        },
        $$(go.Panel, {height: 15}, $$("TreeExpanderButton"))
    ));


myDiagram.nodeTemplateMap.add("SecondNode",
    $$(go.Node, "Horizontal", {selectionObjectName: "SecondNode"},
        $$(go.Panel, "Auto", {name: "SecondNode"},
            $$(go.Shape, "RoundedRectangle", {strokeWidth: 1, fill: 'white'}),
            $$(go.TextBlock, {margin: 8}, new go.Binding("text", "name"))
        ),
        {
            click: function (e, obj) {
                var node = obj.part.data;
                if (node === null) return false;

                var parent_id = node['key'];
                var level = node['level'];
                $.g_projects.get_project_data(project_id, parent_id);
                $.g_projects.get_attr_input(project_id, level, parent_id);

                // extra config
                $('.add-extra-config').show();
                $('.add-extra-config').attr('level', 2);
                $('.add-extra-config').attr('name', node['name']);
                $('.add-extra-config').attr('project_relation_id', parent_id);
                $('.submit-project-data').hide();
            }
        }, {
            contextMenu: secondContextMenu
        },
        $$(go.Panel, {height: 15}, $$("TreeExpanderButton"))
    ));


myDiagram.nodeTemplateMap.add("ThirdNode",
    $$(go.Node, "Auto",
        $$(go.Shape, "RoundedRectangle", {strokeWidth: 1, fill: 'white'}),
        $$(go.TextBlock, {margin: 8}, new go.Binding("text", "name")),
        {
            click: function (e, obj) {
                var node = obj.part.data;
                if (node === null) return false;

                var parent_id = node['key'];
                var level = node['level'];
                console.log(level);

                $.g_parent_id = parent_id;
                $.g_projects.get_project_data(project_id, parent_id);
                $.g_projects.get_attr_input(project_id, level, parent_id);

                // extra config
                $('.add-extra-config').hide();
                $('.submit-project-data').show();
            }
        }, {
            contextMenu: thirdContextMenu
        }
    ));

myDiagram.linkTemplate =
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


