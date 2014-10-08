from .forms import SetupForm
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from splunkdj.decorators.render import render_to
from splunkdj.setup import create_setup_view_context

# Imports for the setup view
from .forms import SetupForm
from django.core.urlresolvers import reverse
from splunkdj.setup import config_required
from splunkdj.setup import create_setup_view_context

@login_required
def home(request):
    # Redirect to the default view, which happens to be a non-framework view
    return redirect('/app/SplunkConf2014Example/home')

@render_to()
@login_required
#@config_required   # enable when using a real setup view
def render_page(request, tmpl):
    return {
        "TEMPLATE": "SplunkConf2014Example:%s.html" % tmpl
    }

@render_to('SplunkConf2014Example:setup.html')
@login_required
def setup(request):
    result = create_setup_view_context(
        request,
        SetupForm,
        reverse('SplunkConf2014Example:home'))
    
    service = request.service
    app_name = service.namespace['app']
    service.apps[app_name].post('_reload')
    
    return result