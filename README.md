## dj_deploy

Often, especially in large projects, media files (CSS and JavaScript) will become large and difficult to manage. Naturally, you will want to split the large files into smaller, and easier-to-manage chunks of specific functionality. However, this impacts on your application's performance, as the user will have to fetch more and more files as your site grows.

This is where `dj_deploy` comes in handy. You can create as many media files as you like and not impact your application's performance as a result. Instead of declaring your CSS and JS links directly in your templates, you specify them in a settings file, and include them with a simple template tag from the templates.

During development, the tag spits out the locations of the raw CSS files (since you don't care about performance then too much). When you deploy, you run a simple `manage.py` command, and the files are concatenated and compressed.

### Requirements

There are a few things you need to setup in your `settings.py` file:

*   `ROOT` — this should be an absolute path to the root of your project. You can either specify this manually, or add the following code snippet to fetch it dynamically (useful if your dev and production environments are configured differently):
    
        import os, sys
        ROOT = os.path.realpath(os.path.dirname(inspect.currentframe().f_code.co_filename))
    
    That may seem like an insane process just to get the root directory path, but it works in every edge-case I've come across too.

*   `DEPLOY_CSS_SPEC` and `DEPLOY_JS_SPEC` — these are discussed in [Media specifications](http://github.com/obeattie/dj-deploy/wikis/media-specifications).

In addition, `dj_deploy` makes use of your version control system's commit id's to generate its compressed filenames (to work around caching issues among other things). If you are using git as a vcs, you need to install GitPython. If you are using SVN, you need do nothing. If you are not using a vcs at all, your filenames will always be the same.

Finally, you need to make sure you have a working copy of Java on your system. More specifically, you need to ensure you can run [ShrinkSafe](http://www.dojotoolkit.org/docs/shrinksafe) and the [YUI compressor](http://developer.yahoo.com/yui/compressor/). For the moment these are not interchangeable with other compressors, but support for this is planned at some point.

### Usage

1.   You need to make sure that the settings `DEPLOY_CSS_SPEC` and `DEPLOY_JS_SPEC` are setup properly, as described in [Media specifications](http://github.com/obeattie/dj-deploy/wikis/media-specifications).

2.   Now you need to modify your templates to take advantage of `dj_deploy`'s features. This involves replacing your stylesheet and JS links with template tags.
    
    At the top of your template, place `{% load deployment %}`, and to load the media files, put `{% get_media js <spec name> %}` or `{% get_media css <spec name> %}`.

3.  When you deploy your site (i.e. whenever or wherever `settings.DEBUG` is set to `False`), you need to run `python manage.py compressmedia`. This will concatenate and compress all of the media files. Whenever `DEBUG` is `False`, the compressed files will be used in place of the raw files. Now, wasn't that easy? :)

### Bugs

So far, I haven't found any. The code has been in use on multiple production sites for nearly a year. That said, there's always the potential for something to go wrong. If you come across anything, open an Issue and I'll get it fixed :)
