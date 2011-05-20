"""Tools for interacting with version control systems (at the moment svn and Git
   are supported)."""
import re

from django.conf import settings
from django.utils.version import get_svn_revision as dj_svn_revision

def get_svn_commit(fail_silently=True):
    """Returns the current svn revision number of the project."""
    try:
        commit = dj_svn_revision(settings.ROOT)
        # Try and coerce to an integer
        return int(re.compile(r'\D').sub('', commit))
    except:
        if fail_silently:
            return 'Unknown'
        raise

def get_git_commit(fail_silently=True):
    """Returns the current git commit hash for the project.
       NOTE: This depends on GitPython being available."""
    try:
        from git import Repo
        repo = Repo(settings.ROOT)
        return repo.commits(repo.active_branch, max_count=1)[0].id_abbrev
    except:
        if fail_silently:
            return 'Unknown'
        raise

def get_commit():
    """Returns the current commit id/hash (fetched from svn or git [in that order])."""
    try:
        return get_svn_commit(fail_silently=False)
    except:
        return get_git_commit(fail_silently=True)
