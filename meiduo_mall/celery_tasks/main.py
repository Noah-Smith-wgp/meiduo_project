#Celery的启动文件
from celery import Celery

#创建celery实例
celery_app = Celery('meiduo')

#加载配置文件
celery_app.config_from_object('celery_tasks.config')