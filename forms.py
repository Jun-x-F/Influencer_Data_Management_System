from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, validators

class ProjectForm(FlaskForm):
    class Meta:
        csrf = False  # 禁用 CSRF 保护

    project_name = StringField('项目', [validators.Length(max=100)])
    manager = StringField('负责人', [validators.Length(max=50)])
    progress = StringField('合作进度', [validators.Length(max=50)])
    cost = IntegerField('花费（$）', [validators.Optional(), validators.NumberRange(min=0)])
    product = StringField('产品', [validators.Length(max=100)])
    estimated_views = IntegerField('预估观看量', [validators.Optional(), validators.NumberRange(min=0)])
    estimated_launch_date = DateField('预估上线时间', [validators.Optional()])
