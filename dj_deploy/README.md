## dj_deploy

Often, especially in large projects, media files (CSS and JavaScript) will become large and difficult to manage. Naturally, you will want to split the large files into smaller, and easier-to-manage chunks of specific functionality. However, this impacts on your application's performance, as the user will have to fetch more and more files as your site grows.

This is where `dj_deploy` comes in handy. You can create as many media files as you like and not impact your application's performance as a result. Instead of declaring your CSS and JS links directly in your templates, you specify them in a settings file, and include them with a simple template tag from the templates.

During development, the tag spits out the locations of the raw CSS files (since you don't care about performance then too much). When you deploy, you run a simple `manage.py` command, and the files are concatenated and compressed.

### Requirements

There are a few things you need to setup in your `settings.py` file:

*   `ROOT` — this should be an absolute path to the root of your project. You can either specify this manually, or add the following code snippet to fetch it dynamically (useful if your dev and production environments are configured differently):
    
        import os, sys
        ROOT = os.path.realpath(os.path.dirname(inspect.currentframe().f_code.co_filename))
    
    That may seem like an insane process just to get the root directory path, but it works in every edge-case I've come across.

*   `DEPLOY_CSS_SPEC` and `DEPLOY_JS_SPEC` — these are discussed in [Media specifications](http://wiki.github.com/obeattie/dj_deploy/media-specifications).

*   `VCS_COMMIT_IDENTIFIER` — this should be set to a commit identifier. Advise setting this to 'dev' and overriding it in a local_settings.py file built in a deployment script.

Finally, you need to make sure you have a working copy of Java on your system. More specifically, you need to ensure you can run [ShrinkSafe](http://www.dojotoolkit.org/docs/shrinksafe) and the [YUI compressor](http://developer.yahoo.com/yui/compressor/). For the moment these are not interchangeable with other compressors, but support for this is planned at some point.

### Usage

1.   You need to make sure that the settings `DEPLOY_CSS_SPEC` and `DEPLOY_JS_SPEC` are setup properly, as described in [Media specifications](http://wiki.github.com/obeattie/dj_deploy/media-specifications).

2.   Now you need to modify your templates to take advantage of `dj_deploy`'s features. This involves replacing your stylesheet and JS links with template tags.
    
    At the top of your template, place `{% load deployment %}`, and to load the media files, put `{% get_media js <spec name> %}` or `{% get_media css <spec name> %}`.

3.  When you deploy your site (i.e. whenever or wherever `settings.DEBUG` is set to `False`), you need to run `python manage.py compressmedia`. This will concatenate and compress all of the media files. Whenever `DEBUG` is `False`, the compressed files will be used in place of the raw files. I usually set this up so Fabric/Capistrano will run the command for me on deploy to a server. Now, wasn't that easy? :)

### Documentation

I realize that some of the documentation falls short in certain areas, and I'll be working to improve it soon. However, in the mean time, the code is fairly well-commented and pretty easy to read.

### License

Like [Django](http://www.djangoproject.org/), I'm releasing `dj_deploy` under the [BSD License](http://creativecommons.org/licenses/BSD/) – feel free to do whatever you like to the code, basically :)
