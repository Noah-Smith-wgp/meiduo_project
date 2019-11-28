
def get_breadcrumb(category3):
    # 查询面包屑导航
    cat2 = category3.parent
    cat1 = cat2.parent
    bread_crumb = {
        'cat1': cat1,
        'cat2': cat2,
        'cat3': category3
    }

    return bread_crumb