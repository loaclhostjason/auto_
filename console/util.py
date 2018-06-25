import xml.dom.minidom
import os
import json
from app import create_app
from app.main.models import Project
from app.manage.models import AttrContent

app = create_app()
app.app_context().push()


class ExportXml(object):

    def __init__(self, project_id):
        self.files_path = self.set_path()
        self.project_id = project_id

    @staticmethod
    def set_path():
        path = os.path.abspath(os.path.dirname(__file__))
        real_path = os.path.join(path, 'files')
        files_path = os.path.join(real_path, 'test.xml')

        if not os.path.exists(real_path):
            os.makedirs(real_path)
        return files_path

    @property
    def xml_managers_attr(self):
        project = Project.query.get_or_404(self.project_id)
        return project.name

    @property
    def xml_header_attr(self):
        result = dict()
        attr_content = AttrContent.query.filter_by(project_id=self.project_id,
                                                   project_relation_id=self.project_id).first()

        if not attr_content or not attr_content.real_content:
            return result

        content = json.loads(attr_content.real_content)
        return content

    def set_xml(self):
        doc = xml.dom.minidom.Document()
        # 创建一个根节点Managers对象
        root = doc.createElement('ConfigurationModule')

        # 设置根节点的属性
        root.setAttribute('%s-CONFIG-SCHEMA-VERSION' % self.xml_managers_attr, '1.0')
        # 将根节点添加到文档对象中
        doc.appendChild(root)

        manager_dict = self.xml_header_attr
        if manager_dict:
            for key, val in manager_dict.items():
                node_manager = doc.createElement('Header')
                node_name = doc.createElement(key)
                # 给叶子节点name设置一个文本节点，用于显示文本内容
                node_name.appendChild(doc.createTextNode(str(val)))

                # 将各叶子节点添加到父节点Manager中，
                # 最后将Manager添加到根节点Managers中
                node_manager.appendChild(node_name)
                root.appendChild(node_manager)
        return doc

    def run(self):
        doc = self.set_xml()
        fp = open(self.files_path, 'w', encoding='utf-8')
        doc.writexml(fp, indent='\t', addindent='\t', newl='\n', encoding="utf-8")


if __name__ == '__main__':
    export_xml = ExportXml(project_id=1)
    export_xml.run()
