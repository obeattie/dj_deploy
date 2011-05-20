"""The monitormedia management command, for monitoring any of the (uncompressed)
   media files. Each time a change occurs, the media files are assembled but *not*
   compressed. This means that they are preprocessed (if there are preprocessors
   for the file types defined) but time is not wasted on unnecessary calls to
   compressors."""
# I realize some of this code is a bit dirty, but it works, and it's only a dev
# tool, so I'm not really too bothered.
import os
import sys
import time

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from dj_deploy.compression import CalledProcessError
from dj_deploy.compression.css import compressor as css_compressor
from dj_deploy.compression.javascript import compressor as js_compressor
from dj_deploy.specs import css as css_spec, javascript as js_spec
from dj_deploy.util.misc import uniquified

class Command(BaseCommand):
    help = 'Monitors media files either in the passed specs, or every spec if no specs ' \
           'are specified for changes, and recompiles the compressed versions on each change. ' \
           'The monitor will run continuously until it receives SIGINT (ctrl+c).'
    args = '[spec ...]'
    
    def handle(self, *specs, **options):
        js = []
        css = []
        
        if not specs:
            # Default to compressing every spec
            js = js_spec.SPEC.keys()
            css = css_spec.SPEC.keys()
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
        
        js_files = {}
        css_files = {}
        
        # Create a mapping from every file to the specs that it is a part of
        for spec in js:
            files = js_compressor.get_spec_files(js_spec.SPEC[spec])
            for f in files:
                f = os.path.join(settings.MEDIA_ROOT, f)
                assert os.path.exists(f), f
                if f in js_files:
                    js_files[f].append(spec)
                else:
                    js_files[f] = [spec, ]
        
        for spec in css:
            files = css_compressor.get_spec_files(css_spec.SPEC[spec])
            for f in files:
                f = os.path.join(settings.MEDIA_ROOT, f)
                assert os.path.exists(f), f
                if f in css_files:
                    css_files[f].append(spec)
                else:
                    css_files[f] = [spec, ]
        
        monitored_files = js_files
        monitored_files.update(css_files)
        
        # Now we have a list of files to monitor and a mapping back to the specs
        # they belong to, we can start monitoring for changes.
        # Since I use VMWare as a dev environment, can't use inotify (HGFS
        # doesn't emit the events :-)
        
        # First, get the last modification times of all the files
        file_timestamps = {}
        for path in monitored_files:
            file_timestamps[path] = os.path.getmtime(path)
        
        # Now, loop 2x per second and watch for changes
        try:
            print(':')
            while 1:
                modified_specs = set()
                for path, old_timestamp in file_timestamps.items():
                    new_timestamp = os.path.getmtime(path)
                    if not new_timestamp == old_timestamp:
                        print('    Modification of %s detected.' % path)
                        for spec in monitored_files[path]:
                            modified_specs.add(spec)
                        file_timestamps[path] = new_timestamp
                if modified_specs:
                    print('    -> Recompiling specs %s...' % (', '.join(modified_specs)))
                    try:
                        call_command('compressmedia', preprocess_only=True, *modified_specs)
                    except CalledProcessError:
                        print('        Error processing. Ignored.')
                    else:
                        print('        Done!')
                    print(':')
                time.sleep(1.5)
        except KeyboardInterrupt:
            print('Bye.')
            sys.exit(0)
