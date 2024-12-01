from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from .v1.views import LoginViewV1, PostViewSetV1, CommentViewSetV1, SignUpViewV1
from .v2.views import LoginViewV2, PostViewSetV2, CommentViewSetV2, SignUpViewV2

router_v1 = DefaultRouter()
router_v1.register(r'posts', PostViewSetV1)
router_v1.register(r'comments', CommentViewSetV1)

router_v2 = DefaultRouter()
router_v2.register(r'posts', PostViewSetV2)
router_v2.register(r'comments', CommentViewSetV2)

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="API documentation for the project",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    path('', include(router_v1.urls)),
    path('v1/', include(router_v1.urls)),
    path('v1/signup/', SignUpViewV1.as_view(), name='signup'),
    path('v1/login/', LoginViewV1.as_view(), name='login'),
    path('v2/', include(router_v2.urls)),
    path('v2/signup/', SignUpViewV2.as_view(), name='signup'),
    path('v2/login/', LoginViewV2.as_view(), name='login'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
