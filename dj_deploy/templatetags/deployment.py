import urlparse

from django import template
from django.conf import settings

from dj_deploy.specs import compile_file_list, css as css_spec, javascript as js_spec
from dj_deploy.util.templatetags.deployment_utils import check_not_quoted

register = template.Library()

class MediaNode(template.Node):
    def __init__(self, media_type, categories, *args, **kwargs):
        self.media_type = media_type
        self.categories = categories
        return super(MediaNode, self).__init__(*args, **kwargs)
    
    def render_media(self, context, spec, output, indent=4):
        categories = self.categories or spec.keys()
        result = []
        
        for f in compile_file_list(spec, *categories):
            result.append(output % urlparse.urljoin(settings.MEDIA_URL, f))
        
        # Join each line with a newline and the requested number of indent spaces
        return ('\n%s' % (' ' * indent)).join(result)
    
    def render(self, context):
        if self.media_type == 'css':
            return self.render_media(
                context=context,
                spec=css_spec.SPEC,
                output=u'<link rel="stylesheet" href="%s" media="screen,projection" />'
            )
        elif self.media_type == 'js':
            return self.render_media(
                context=context,
                spec=js_spec.SPEC,
                output=u'<script type="text/javascript" src="%s"></script>'
            )
        else:
            raise KeyError

@register.tag
def get_media(parser, token):
    """Template tag for getting media files for specific site areas, which
       change depending on the current environment (development or production)."""
    try:
        tokens = token.split_contents()[1:]
        assert 1 <= len(tokens)
        assert tokens[0] in ('css', 'js')
    except AssertionError:
        raise template.TemplateSyntaxError(u'%r tag requires a media type (css or js) and optionally a site area as its arguments' % token.contents.split()[0])
    
    # Check that none of the arguments are quoted
    [check_not_quoted('get_media', t) for t in tokens]
    
    return MediaNode(media_type=tokens[0], categories=tokens[1:])
