from django.shortcuts import render
from django.views import View
import logging
from django import http
from django.core.cache import cache

from .models import Area
from meiduo_mall.utils.response_code import RETCODE

# Create your views here.

logger = logging.getLogger('django')


class AreasView(View):
    """省市区数据"""
    def get(self, request):
        """提供省市区数据"""
        area_id = request.GET.get('area_id')

        # 判断要查询的是省还是市区
        if not area_id:
            #读取省份缓存
            province_list = cache.get('province_list')
            if province_list:
                return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})
            try:
                #查询省份数据
                # province_model_list = Area.objects.filter(parent__isnull=True)
                province_model_list = Area.objects.filter(parent=None)

                #生成省份字典列表
                province_list = []
                for province_model in province_model_list:
                    province_dict = {
                        'id': province_model.id,
                        'name': province_model.name
                    }
                    province_list.append(province_dict)

                #设置省份缓存
                cache.set('province_list', province_list, 3600)

                #响应省份数据:JsonResponse只能识别字典或者列表数据，他不能识别模型列表（查询集）
                return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})
            except Exception as e:
                logger.error(e)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '省份数据错误'})

        else:
            #获取城市或地区缓存
            sub_area = cache.get('sub_area_' + area_id)
            if sub_area:
                return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_area': sub_area})
            #提供城市或取现数据
            try:
                parent_model = Area.objects.get(id = area_id)  #查询城市或区县数据
                sub_model_list = parent_model.subs.all()

                #生成城市或区县字典列表
                sub_list = []
                for sub_model in sub_model_list:
                    sub_list.append({'id': sub_model.id, 'name': sub_model.name})

                sub_area = {
                    'id': parent_model.id,  # 父级pk
                    'name': parent_model.name,  # 父级name
                    'subs': sub_list  # 父级对应的子级
                }
                #设置城市或地区缓存
                cache.set('sub_area_' + area_id, sub_area, 3600)

                #响应城市或区县数据
                return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_area': sub_area})
            except Exception as e:
                logger.error(e)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '城市或区县数据错误'})
