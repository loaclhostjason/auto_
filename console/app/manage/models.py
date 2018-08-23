from .. import db
from enum import Enum
from datetime import datetime
from ..base import Tool
import json
from .func import del_os_filename


class AttrType(Enum):
    worker = '工作树'
    func = '功能树'


class Attr(db.Model):
    __tablename__ = 'attr'
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(16))
    level = db.Column(db.Integer)
    type = db.Column(db.Enum(AttrType))

    update_time = db.Column(db.DateTime, default=datetime.now)
    content = db.Column(db.Text)
    username = db.Column(db.String(12), default='系统')

    @classmethod
    def edit(cls, form_data, attr):
        cls.update_model(attr, form_data)
        db.session.add(attr)
        return

    @classmethod
    def init_attr(cls):
        _ecu = [{"item_zh": "EcuName", "item_required": "y", "item": "EcuName"},
                {"item_zh": "RequestId", "item_required": "y", "item": "RequestId"},
                {"item_zh": "ResponseId", "item_required": "y", "item": "ResponseId"},
                {"item_zh": "ConfigurationFileNumber", "item_required": "y", "item": "ConfigurationFileNumber"},
                {"item_zh": "ApplicationLayerSpec", "item_protocol": "ApplicationLayer",
                 "item": "ApplicationLayerSpec"}, {"item_zh": "P2", "item_protocol": "ApplicationLayer", "item": "P2"},
                {"item_zh": "P2Star", "item_protocol": "ApplicationLayer", "item": "P2Star"},
                {"item_zh": "S3", "item_protocol": "ApplicationLayer", "item": "S3"},
                {"item_zh": "Baudrate", "item_protocol": "PhysicalLayer", "item": "Baudrate"},
                {"item_zh": "PhysicalLayerSpec", "item_protocol": "PhysicalLayer", "item": "PhysicalLayerSpec"},
                {"item_zh": "SecurityLevel", "item": "SecurityLevel"},
                {"item_zh": "AlgorithmNumber", "item": "AlgorithmNumber"},
                {"item_zh": "ConfigurationIndex", "item": "ConfigurationIndex"}]

        _content = [{"item_zh": "ParameterName:", "item_required": "y", "item": "ParameterName"},
                    {"item_zh": "BytePosition:", "item_required": "y", "item": "BytePosition"},
                    {"item_zh": "BitPosition:", "item_required": "y", "item": "BitPosition"},
                    {"item_zh": "BitLength:", "item_required": "y", "item": "BitLength"}]

        _did_len = [{"item_zh": "DidNo", "item": "DidNo"}, {"item_zh": "DidIndicator", "item": "DidIndicator"},
                    {"item_zh": "Name", "item": "Name"}, {"item_zh": "DidLength", "item": "DidLength"},
                    {"item_zh": "FeatureCode", "item": "FeatureCode"},
                    {"item_zh": "DefaultValue", "item": "DefaultValue"}]
        r = [
            {'name': 'ECU属性配置', 'level': 1, 'type': 'worker', 'content': json.dumps(_ecu)},
            {'name': 'DID属性配置', 'level': 2, 'type': 'worker', 'content': json.dumps(_did_len)},
            {'name': '装配项属性配置', 'level': 3, 'type': 'worker', 'content': json.dumps(_content)},
        ]
        attr = Attr.query.all()
        if attr:
            return
        result = []
        for info in r:
            new_attr = cls(**info)
            result.append(new_attr)
        db.session.add_all(result)
        db.session.commit()
        return


class AttrContent(db.Model):
    __tablename__ = 'attr_content'
    id = db.Column(db.Integer, primary_key=True)
    project_relation_id = db.Column(db.Integer, db.ForeignKey('project_relation.id'))

    real_content = db.Column(db.Text)

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

    project = db.relationship('Project', backref=db.backref("attr_content", cascade="all, delete-orphan"))
    project_relation = db.relationship('ProjectRelation',
                                       backref=db.backref("attr_content", cascade="all, delete-orphan"))

    @staticmethod
    def get_did_len(project_relation_id):
        attr = AttrContent.query.filter_by(project_relation_id=project_relation_id).first()

        attr = json.loads(attr.real_content or '{}')
        _len_did = 0
        try:
            _len_did = int(attr.get('DidLength'))
        except:
            pass
        return _len_did

    @staticmethod
    def get_attr_info(project_relation_id, is_parent=False, show_ext_bit=False, show_param=False):
        from ..main.models import ProjectRelation
        project_relation = ProjectRelation.query.filter_by(id=project_relation_id).first()

        if not is_parent:
            attr = AttrContent.query.filter_by(
                project_relation_id=project_relation.parent_id if project_relation else '').first()
        else:
            attr = AttrContent.query.filter_by(
                project_relation_id=project_relation.id if project_relation else '').first()

        attr = json.loads(attr.real_content or '{}') if attr else {}
        bit_line = 0
        start_bit = 0
        byte_info = 0
        ext_bit = 0
        parameter_name = ''
        if attr:
            try:

                bit_line = int(attr.get('BitLength') or 0) or 0
                start_bit = int(attr.get('BitPosition') or 0) or 0
                byte_info = int(attr.get('BytePosition') or 0) or 0
                ext_bit = int(attr.get('ExtBitPosition') or 0) or 0
                parameter_name = attr.get('ParameterName') or ''
            except Exception as e:
                print(e)
                pass

        if show_ext_bit:
            return bit_line, start_bit, byte_info, ext_bit

        if show_param:
            return bit_line, start_bit, byte_info, ext_bit, parameter_name

        return bit_line, start_bit, byte_info

    def get_insert_data(self, data, project_id):
        if not data:
            return
        project_relation_id = data.get('project_relation_id')

        Tool.remove_key(data, ['level', 'project_relation_id'])

        d = {
            'project_id': project_id,
            'project_relation_id': project_relation_id,
            'real_content': json.dumps(data),
        }
        return d

    @classmethod
    def create_edit(cls, data, project_id, project_relation_id):
        is_have_content = cls.query.filter_by(project_id=project_id, project_relation_id=project_relation_id).first()

        data = cls().get_insert_data(data, project_id)
        if not is_have_content:
            content = cls(**data)
            db.session.add(content)
            return

        cls.update_model(is_have_content, data)
        return


class ExtraAttrContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attr_id = db.Column(db.Integer, db.ForeignKey('attr.id'))

    content = db.Column(db.Text)
    content_val = db.Column(db.Text)

    content_section = db.Column(db.Text)
    content_section_val = db.Column(db.Text)
    attr = db.relationship('Attr',
                           backref=db.backref("extra_attr_content", uselist=False, cascade="all, delete-orphan"))

    @classmethod
    def edit(cls, form_data, attr):
        cls.update_model(attr, form_data)
        db.session.add(attr)
        return

    @classmethod
    def init_content(cls):
        attr_1 = dict()
        attr_1['content'] = json.dumps(
            [
                {"item_zh": "PinDefinition", "item": "PinDefinition"},
                {"item_zh": "PinNumber", "item": "PinNumber"},
                {"pin_num": "2"}
            ]
        )

        attr_1['content_section'] = json.dumps(
            [
                {"resetsection_item_zh": "NeedReset", "resetsection_item": "NeedReset"},
                {"resetsection_item_zh": "DelayForMS", "resetsection_item": "DelayForMS"}
            ]
        )

        attr_2 = dict()
        attr_2['content'] = json.dumps(
            {
                "writsection": [
                    {"item_zh": "DidWriteScope", "item": "DidWriteScope"},
                    {"item_zh": "ReadBackCompare", "item": "ReadBackCompare"},
                    {"item_zh": "DelayForMS", "item": "DelayForMS"}
                ],
                "readsection": [
                    {"item_zh": "OverrideDefault", "item": "OverrideDefault"}
                ]}
        )

        attr_info = Attr.query.filter_by(level=1).first()
        attr_info2 = Attr.query.filter_by(level=2).first()
        attr_1['attr_id'] = attr_info.id
        attr_2['attr_id'] = attr_info2.id

        attr_content = AttrContent.query.all()
        if attr_content:
            return
        result = [cls(**attr_1), cls(**attr_2)]
        db.session.add_all(result)
        db.session.commit()
        return


class Las(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200))

    file_name = db.Column(db.String(100))
    file = db.Column(db.String(100))

    project_group_id = db.Column(db.Integer, db.ForeignKey('project_group.id'))
    project_group = db.relationship('ProjectGroup', backref=db.backref("las"))

    @classmethod
    def edit_or_create_las(cls, form_data, las, path):
        if not las:
            doc = cls(**form_data)
            db.session.add(doc)
            return

        if form_data.get('file'):
            del_os_filename(path, las.file)
            las.file = form_data['file']
            las.file_name = form_data.get('file_name')

        db.session.add(las)
        return
