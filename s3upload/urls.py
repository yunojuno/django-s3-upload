from django.conf.urls import url

from .views import get_upload_params, get_download_link

urlpatterns = [
    url(
        r'^upload/',
        get_upload_params,
        name='s3upload'
    ),
    url(
        r'^download/(?P<bucket>[\w.-]+)/(?P<key>[\w.-/]+)$',
        get_download_link,
        name='s3download'
    )
]
