import glob, os

from django.conf import settings

from dj_deploy.util.misc import flattened, uniquified
from dj_deploy.util.vcs import get_commit

ROOT_PATH = settings.MEDIA_ROOT

class FileGetter(object):
    root_path = ROOT_PATH
    
    def __init__(self, spec, extension=None, *args, **kwargs):
        self.keys_processed = []
        self.spec = spec
        # Extension defaults to the extension of one of the files in the spec (if not passed,
        # extensions are assumed to be the same).
        self.extension = extension or self.spec['__extension__']
        return super(FileGetter, self).__init__(*args, **kwargs)
    
    @classmethod
    def process_globs(self, patterns):
        """Expands the globs into full file paths, and returns a list of the
           results (the results will be in the original, relative form)."""
        
        def _process_glob(p):
            if '*' in p or '?' in p or '[' in p or ']' in p:
                return glob.glob(os.path.join(self.root_path, p))
            else:
                return p
        
        results = flattened([_process_glob(p) for p in flattened(patterns)])
        return [p.split(self.root_path)[-1] for p in results]
    
    def process_pattern(self, pattern):
        """Processes the specified pattern, expanding dependencies if necessary."""
        raise NotImplementedError
    
    def process_patterns(self, *patterns):
        """Processes all of the specified patterns using process_pattern."""
        return uniquified(flattened([self.process_pattern(s) for s in patterns]))
    
    def get_file_list(self, *keys):
        """Returns a list of paths to files for the keys specified. This expands
           dependencies and globs. Essentially, this ties together process_pattern
           and process_globs."""
        raise NotImplementedError

class SourceFileGetter(FileGetter):
    """Gets source files (appropriate for development)."""
    def process_pattern(self, pattern):
        compiled = []
        
        if pattern.startswith('include:'):
            pattern = pattern[8:]
            # Avoid cyclic dependencies, doing nothing if they exist
            if pattern not in self.keys_processed:
                self.keys_processed.append(pattern)
                compiled.append([self.process_pattern(s) for s in self.spec[pattern]])
        else:
            # Not a dependency
            compiled.append(pattern)
        
        return flattened(compiled)
    
    def get_file_list(self, *keys):
        patterns = flattened([self.spec[key] for key in keys])
        compiled = self.process_patterns(*patterns)
        return uniquified(self.process_globs(compiled))

class CompressedFileGetter(FileGetter):
    """Gets compressed files (appropriate for production/testing)."""
    def process_pattern(self, pattern):
        compiled = []
        
        if pattern.startswith('include:'):
            pattern = pattern[8:]
            if pattern not in self.keys_processed:
                self.keys_processed.append(pattern)
                compiled.append([self.process_pattern(s) for s in self.spec[pattern]])
                compiled.append(pattern)
        
        return flattened(compiled)
    
    def get_file_list(self, *keys):
        compiled = []
        
        for key in keys:
            value = self.spec[key]
            compiled.append(self.process_patterns(*value))
            compiled.append(key)
        
        compiled = uniquified(flattened(compiled))
        commit = get_commit()
        return [u'%s/c-%s-%s.%s' % (self.extension, p, commit, self.extension) for p in compiled]

def compile_file_list(spec, *keys):
    """Compiles a path pattern list for the specified keys in spec, returning the
       compressed files."""
    return CompressedFileGetter(spec=spec).get_file_list(*keys)
