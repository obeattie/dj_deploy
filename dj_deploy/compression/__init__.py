import os

from django.conf import settings

from dj_deploy.specs import ROOT_PATH, FileGetter
from dj_deploy.util.misc import uniquified

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
    preprocessed_extensions = []
    
    def call_compressor(self, stdin, *args, **kwargs):
        raise NotImplementedError
    
    def get_preprocessed_content(self, f):
        raise NotImplementedError
    
    def compress_file(self, f, preprocess_only=False):
        """Compresses the passed file, returning the result."""
        if not isinstance(f, file):
            f = file(f)
        f.seek(0)
        
        for ext in self.preprocessed_extensions:
            if f.name.endswith(ext):
                content = self.get_preprocessed_content(f)
                break
        else:
            content = f.read()
        
        if preprocess_only:
            return content
        else:
            return self.call_compressor(stdin=content)
    
    def compress_files(self, *files, **kwargs):
        """Compresses all of the passed files, returning a dictionary of the
           result."""
        result = {}
        
        for f in files:
            result[f] = self.compress_file(f, **kwargs)
        
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
    
    def get_spec_files(self, spec, include_indirect=False):
        """Returns all the files within the passed spec."""
        files = []
        for pattern in spec:
            if not pattern.startswith('include:'):
                if not pattern.startswith('indirect:'):
                    files.append(pattern)
                elif include_indirect:
                    files.append(pattern[9:])
        return FileGetter.process_globs(files)
    
    def compress_spec(self, spec, **kwargs):
        """Compresses all files in the passed spec, returning the result."""
        files = self.get_spec_files(spec=spec)
        
        result = []
        for f in uniquified(files):
            result.append(self.compress_file(os.path.join(ROOT_PATH, f), **kwargs))
        
        return '\n'.join(result)
    
    @classmethod
    def get_compressed_path(cls, spec, key):
        """Returns a path relative to htdocs/ for the spec name passed."""
        return u'%(extension)s/c-%(key)s-%(commit)s.%(extension)s' % {
            'extension': spec['__extension__'],
            'key': key,
            'commit': settings.VCS_COMMIT_IDENTIFIER,
        }
