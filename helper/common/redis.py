from helper.common import manager as helper_manager
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.core.cache import cache


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)
CACHE_MAX_TTL = getattr(settings, 'CACHE_MAX_TTL', DEFAULT_TIMEOUT)



def set_crm_branch(request):
    branch = helper_manager.get_current_user_branch(request.user)
    current_branch = branch[0]
    current_branch_slug = branch[0].slug

    cache.delete('crm_branch_slug')
    cache.set('crm_branch_slug', current_branch_slug, timeout=CACHE_MAX_TTL)

    cache.delete('crm_branch')
    cache.set('crm_branch', current_branch, timeout=CACHE_MAX_TTL)
    