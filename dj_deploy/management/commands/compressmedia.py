"""The compressmedia management command, for compressing css and javascript files into
   discrete modules."""
import os
from optparse import make_option

from django.core.management.base import BaseCommand

from dj_deploy.compression.css import compressor as css_compressor
from dj_deploy.compression.javascript import compressor as js_compressor
from dj_deploy.specs import css as css_spec, javascript as js_spec, ROOT_PATH
from dj_deploy.util.misc import uniquified

class Command(BaseCommand):
    help = 'Creates (or replaces) compressed media (css/js) files.'
    args = '[spec ...]'
    option_list = BaseCommand.option_list + (
        make_option('--nocompress', action='store_true', dest='preprocess_only', default=False,
            help='Specifies that no compression should be performed; just preprocessing and assembling.'),
    )
    
    def handle(self, *specs, **options):
        preprocess_only = options['preprocess_only']
        js = []
        css = []
        
        if not specs:
            # Default to compressing every spec
            js.extend(js_spec.SPEC.keys())
            css.extend(css_spec.SPEC.keys())
        else:
            # Figure out what goes where
            for s in specs:
                if s in js_spec.SPEC:
                    js.append(s)
                if s in css_spec.SPEC:
                    css.append(s)
        
        # Remove any dupes
        js, css = list(uniquified(js)), list(uniquified(css))
        # ...and any undesired keys
        unwanted = ('__extension__', )
        for i in unwanted:
            for m in (js, css):
                try:
                    m.remove(i)
                except ValueError:
                    pass
        
        # Get the compressed media file for each spec (the compressor takes care
        # of glob expansion etc)
        js = [(k, js_compressor.compress_spec(js_spec.SPEC[k], preprocess_only=preprocess_only)) for k in js]
        css = [(k, css_compressor.compress_spec(css_spec.SPEC[k], preprocess_only=preprocess_only)) for k in css]
        
        js = {
            'compressed': js,
            'compressor': js_compressor,
            'spec': js_spec.SPEC,
        }
        css = {
            'compressed': css,
            'compressor': css_compressor,
            'spec': css_spec.SPEC,
        }
        
        for media in (js, css):
            for key, compressed in media['compressed']:
                # Figure out the location for each compressed file
                path = media['compressor'].get_compressed_path(media['spec'], key)
                path = os.path.join(ROOT_PATH, path)
                
                # If a file already exists here, delete it
                if os.path.exists(path):
                    os.remove(path)
                
                # Write the compressed data to the file
                f = open(path, 'w')
                f.write(compressed)
                f.close()
