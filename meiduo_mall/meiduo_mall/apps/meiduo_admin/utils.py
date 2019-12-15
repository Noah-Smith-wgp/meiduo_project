from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PageNum(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'pagesize'
    max_page_size = 20

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),       # 总记录数
            ('lists', data),                            # 当前页码的查询结果
            ('page', self.page.number),                 # 当前页码
            ('pages', self.page.paginator.num_pages),   # 总共多少页
            ('pagesize', self.page_size),   # 页容量
        ]))


def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt认证成功返回数据
    """
    return {
        'token': token,
        'id': user.id,
        'username': user.username
    }
