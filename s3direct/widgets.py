import os

from django.forms import widgets
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse


class S3DirectWidget(widgets.TextInput):

    html = (
        '<div class="s3direct" data-policy-url="{policy_url}">'
        '  <a class="file-link" target="_blank" href="{file_url}">{file_name}</a>'
        '  <a class="file-remove" href="#remove">Remove</a>'
        '  <input class="file-url" type="hidden" value="{file_url}" id="{element_id}" name="{name}" />'
        '  <input class="file-upload-to" type="hidden" value="{upload_to}">'
        '  <input class="file-input" type="file" />'
        '  <div class="progress progress-striped active">'
        '    <div class="bar"></div>'
        '  </div>'
        '</div>'
    )

    class Media:
        js = (
            's3direct/js/scripts.js',
        )
        css = {
            'all': (
                's3direct/css/bootstrap-progress.min.css',
                's3direct/css/styles.css',
            )
        }

    def __init__(self, upload_to):
        self.upload_to = upload_to
        super(S3DirectWidget, self).__init__()

    def render(self, name, value='', attrs=None):

        output = self.html.format(
                policy_url=reverse('s3direct'),
                element_id=self.build_attrs(attrs).get('id'),
                file_name=os.path.basename(value),
                file_url=value,
                name=name,
                upload_to=self.upload_to)

        return mark_safe(output)