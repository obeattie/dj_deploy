import inspect, os, subprocess

from dj_deploy.compression import CalledProcessError, Compressor

# Path to the shrinksafe.jar
COMPRESSOR_ROOT = os.path.realpath(os.path.dirname(inspect.currentframe().f_code.co_filename))
COMPRESSOR_PATH = os.path.join(os.path.dirname(COMPRESSOR_ROOT), 'dependencies/yuicompressor.jar')
LESS_PATH = os.path.join(os.path.dirname(COMPRESSOR_ROOT), 'dependencies/less_compress.rb')

class CssCompressor(Compressor):
    extensions = ['.css', ]
    preprocessed_extensions = ['.less', ]
    
    def __init__(self, compressor=COMPRESSOR_PATH, *args, **options):
        self.options = options
        self.compressor = compressor
        return super(CssCompressor, self).__init__(*args)
    
    def get_preprocessed_content(self, f):
        """Runs the file through the LESS preprocessor."""
        cmd_args = ['ruby', LESS_PATH, f.name]
        process = subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if stderr.strip():
            raise CalledProcessError(process.returncode, cmd_args, stderr.strip())
        
        return stdout
    
    def call_compressor(self, stdin, *args, **kwargs):
        """Calls the compressor, returning the stdout."""
        cmd_args = ['java', '-jar', self.compressor]
        cmd_args.extend(args)
        
        # Add default options from self.options
        for key, value in self.options.items():
            if not key in kwargs:
                kwargs[key] = value
        
        # Add the kwargs to args
        kwargs.setdefault('type', 'css');
        for key, value in kwargs.items():
            cmd_args.append('--%s=%s' % (key, value))
        
        process = subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        stdout, stderr = process.communicate(stdin)
        
        if stderr.strip():
            raise CalledProcessError(process.returncode, cmd_args, stderr.strip())
        
        return stdout

compressor = CssCompressor()
