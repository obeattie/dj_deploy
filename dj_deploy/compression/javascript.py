import subprocess

from dj_deploy.compression import CalledProcessError, Compressor

COMPRESSOR_PATH = 'yui-compressor'

class JavaScriptCompressor(Compressor):
    extensions = ['.js', ]
    
    def __init__(self, compressor=COMPRESSOR_PATH, *args, **options):
        self.options = options
        self.compressor = compressor
        return super(JavaScriptCompressor, self).__init__(*args)
    
    def call_compressor(self, stdin, *args, **kwargs):
        """Calls the compressor, returning the stdout."""
        cmd_args = [self.compressor]
        cmd_args.extend(args)
        
        # Add default options from self.options
        for key, value in self.options.items():
            if not key in kwargs:
                kwargs[key] = value
        
        # Add the kwargs to args
        for key, value in kwargs.items():
            cmd_args.append('--%s=%s' % (key, value))
        
        process = subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        stdout, stderr = process.communicate(stdin)
        
        if stderr.strip():
            raise CalledProcessError(process.returncode, cmd_args, stderr.strip())
        
        return stdout

compressor = JavaScriptCompressor()
