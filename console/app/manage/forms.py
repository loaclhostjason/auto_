# coding: utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_wtf.file import FileField

from ..base import BaseForm


class LasFileForm(FlaskForm, BaseForm):
    file = FileField('帮助文档:')
    description = StringField('描述:')

    submit = SubmitField('确定')
