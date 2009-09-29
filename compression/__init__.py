import os

from dj_deploy.specs import ROOT_PATH, FileGetter
from dj_deploy.util.misc import uniquified
from dj_deploy.util.vcs import get_commit

class CalledProcessError(Exception):
    """Error to be raised whenever a subprocess returns with an error."""
    def __init__(self, cmd, returncode, output=None, *args, **kwargs):
        self.cmd = cmd
        self.returncode = returncode
        self.output = output
        return super(CalledProcessError, self).__init__(*args, **kwargs)
    
    def __str__(self):
        return self.output

class Compressor(object):
    extensions = []
    
    def call_compressor(self, *args, **kwargs):
        raise NotImplementedError
    
    def compress_file(self, f):
        """Compresses the passed file, returning the result."""
        if hasattr(f, 'name'):
            f = f.name
        
        return self.call_compressor(f)
    
    def compress_files(self, *files):
        """Compresses all of the passed files, returning a dictionary of the
           result."""
        result = {}
        
        for f in files:
            result[f] = self.compress_file(f)
        
        return result
    
    def find_files(self, root):
        """Recursively finds all compressable files under the passed path to a root
           directory."""
        hits = []
        
        for root, dirs, files in os.walk(root):
            for filename in files:
                for extension in self.extensions:
                    if filename.lower().endswith(extension):
                        hits.append(os.path.join(root, filename))
        
        return hits
    
    def compress_directory(self, directory):
        """Recursively compresses all compressable files under the passed directory,
           returning a dictionary of the result."""
        return self.compress_files(*self.find_files(root=directory))
    
    def compress_spec(self, spec):
        """Compresses all files in the passed spec, returning the result."""
        files = []
        for pattern in spec:
            if not pattern.startswith('include:'):
                files.append(pattern)
        files = FileGetter.process_globs(files)
        
        result = []
        for f in uniquified(files):
            result.append(self.compress_file(os.path.join(ROOT_PATH, f)))
        
        return '\n'.join(result)
    
    @classmethod
    def get_compressed_path(cls, spec, key):
        """Returns a path relative to htdocs/ for the spec name passed."""
        return u'%(extension)s/c-%(key)s-%(commit)s.%(extension)s' % {
            'extension': spec['__extension__'],
            'key': key,
            'commit': get_commit()
        }
