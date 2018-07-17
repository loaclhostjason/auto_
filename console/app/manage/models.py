from .. import db
from enum import Enum
from datetime import datetime
from ..base import Tool
import json


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
        _ecu = [{"item_required": "y", "item_zh": "EcuName", "item": "EcuName"},
                {"item_required": "y", "item_zh": "RequestId", "item": "RequestId"},
                {"item_required": "y", "item_zh": "ResponseId", "item": "ResponseId"},
                {"item_required": "y", "item_zh": "ConfigurationFileNumber", "item": "ConfigurationFileNumber"},
                {"item_zh": "ApplicationLayerSpec", "item_protocol": "ApplicationLayer",
                 "item": "ApplicationLayerSpec"}, {"item_zh": "P2", "item_protocol": "ApplicationLayer", "item": "P2"},
                {"item_zh": "P2Star", "item_protocol": "ApplicationLayer", "item": "P2Star"},
                {"item_zh": "S3", "item_protocol": "ApplicationLayer", "item": "S3"},
                {"item_zh": "Baudrate", "item_protocol": "PhysicalLayer", "item": "Baudrate"},
                {"item_zh": "PhysicalLayerSpec", "item_protocol": "PhysicalLayer", "item": "PhysicalLayerSpec"},
                {"item_zh": "SecurityLevel", "item": "SecurityLevel"},
                {"item_zh": "AlgorithmNumber", "item": "AlgorithmNumber"},
                {"item_zh": "ConfigurationIndex", "item": "ConfigurationIndex"}]

        _content = [{"item_zh": "ParameterName:", "item": "ParameterName", "item_required": "y"},
                    {"item_zh": "BytePosition:", "item": "BytePosition", "item_required": "y"},
                    {"item_zh": "BitPosition:", "item": "BitPosition", "item_required": "y"},
                    {"item_zh": "BitLength:", "item": "BitLength", "item_required": "y"}]

        _did_len = [{"item_zh": "DidNo", "item": "DidNo"}, {"item_zh": "DidIndicator", "item": "DidIndicator"},
                    {"item_zh": "Name", "item": "Name"}, {"item_zh": "DidLength", "item": "DidLength"},
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
