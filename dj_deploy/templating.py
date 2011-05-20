import urlparse

from django.conf import settings

from dj_deploy.specs import compile_file_list, css as css_spec, javascript as js_spec

def _get_media_urls(spec, keys):
    """Returns the URLs to the media files in the passed spec with the passed keys."""
    return [urlparse.urljoin(settings.MEDIA_URL, p) for p in compile_file_list(spec, *keys)]

def _get_media_markup(spec, keys, template, indent=4):
    """Returns the HTML markup to be inserted into the template for the passed media type
       (spec) and keys."""
    urls = _get_media_urls(spec=spec, keys=keys)
    urls = [template % url for url in urls]
    
    return ('\n%s' % (' ' * indent)).join(urls)

def _get_media(spec, keys, template, indent=4, raw=False):
    """Returns the HTML to be inserted into the template for the passed specification
       and media type."""
    if raw:
        return _get_media_urls(spec=spec, keys=keys)
    else:
        return _get_media_markup(spec=spec, keys=keys, template=template, indent=indent)

def get_css(keys, media='screen,projection', raw=False):
    """Returns the HTML necessary to insert the CSS files for the passed specs into
       a template."""
    return _get_media(
        spec=css_spec.SPEC,
        keys=keys,
        template=u'<link rel="stylesheet" href="%%s" media="%s" />' % media,
        raw=raw
    )

def get_js(keys, mimetype='text/javascript', raw=False):
    """Returns the HTML necessary to insert the JavaScript files for the passed specs into
       a template."""
    return _get_media(
        spec=js_spec.SPEC,
        keys=keys,
        template=u'<script type="%s" src="%%s"></script>' % mimetype,
        raw=raw
    )

GLOBAL_VARS = {
    'get_css': get_css,
    'get_js': get_js,
}
