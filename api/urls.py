from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.urls import path

from rest_framework.routers import DefaultRouter

from api.views import views
from api.views import staff_views
from api.views import processing_staff_views
from api.views import activity_views
from api.views import prize_views
from api.views import lottery_views
from api.views import staffs_batch_views


def deploy_static_url():
    # 静态资源加载
    from django.views import static
    url_pattern = url(r'^interactive_api/static/(?P<path>.*)$', static.serve, {'document_root': settings.STATIC_ROOT}, name='static')
    return url_pattern


# 创建路由器并注册我们的视图。
router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'staffs', staff_views.StaffViewSet)
router.register(r'staffs_batch', staffs_batch_views.StaffBatchViewSet)
router.register(r'processing_staff', processing_staff_views.ProcessingStaffViewSet)
router.register(r'activity', activity_views.ActivityViewSet)
router.register(r'prizes', prize_views.PrizeViewSet)
router.register(r'lottery', lottery_views.LotteryViewSet)

urlpatterns = [
    url(r'', include(router.urls)),
]

# url路由器
urlpatterns += [
    url(r'^interactive_api/', include(router.urls)),
    url(r'^interactive_api/api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    deploy_static_url(),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += [url(r'^interactive_api/index/', views.index, name='index'), ]
urlpatterns += [url(r'^interactive_api/config/activity/', views.activity, name='activity'), ]
urlpatterns += [url(r'^interactive_api/config/prize/', views.prize, name='prize'), ]
urlpatterns += [url(r'^interactive_api/config/processing_staff/', views.processing_staff, name='processing_staff'), ]
urlpatterns += [url(r'^interactive_api/config/staffs/', views.staffs, name='staffs'), ]
