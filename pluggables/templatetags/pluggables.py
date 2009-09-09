from django.template import Node, Library
from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.encoding import smart_str

register = Library()


class PluggableURLNode(Node):
    def __init__(self, request, view_name, args, kwargs, asvar):
        self.request = request
        self.view_name = view_name
        self.args = args
        self.kwargs = kwargs
        self.asvar = asvar

    def render(self, context):
        args = [arg.resolve(context) for arg in self.args]
        kwargs = dict([(smart_str(k, 'ascii'), v.resolve(context)) for k, v in self.kwargs.items()])

        request = self.request.resolve(context)
        view_name = self.view_name
        if hasattr(request, 'pluggable'):
            view_name = request.pluggable.prefix and '%s_%s' % (request.pluggable.prefix, self.view_name) or '%s' % self.view_name
            parent_args, parent_kwargs = request.pluggable.parent_arguments
            if parent_args:
                args = parent_args + args
            if parent_kwargs:
                kwargs.update(parent_kwargs)

        # Try to look up the URL twice: once given the view name, and again
        # relative to what we guess is the "main" app. If they both fail,
        # re-raise the NoReverseMatch unless we're using the
        # {% url ... as var %} construct in which cause return nothing.
        url = ''
        try:
            url = reverse(view_name, args=args, kwargs=kwargs)
        except NoReverseMatch:
            project_name = settings.SETTINGS_MODULE.split('.')[0]
            try:
                url = reverse(project_name + '.' + view_name,
                              args=args, kwargs=kwargs)
            except NoReverseMatch:
                if self.asvar is None:
                    raise

        if self.asvar:
            context[self.asvar] = url
            return ''
        else:
            return url


def pluggable_url(parser, token):
    """
    Returns an absolute URL matching given view with its parameters.

    This is a way to define links that aren't tied to a particular URL
    configuration::

        {% url path.to.some_view arg1,arg2,name1=value1 %}

    The first argument is a path to a view. It can be an absolute python path
    or just ``app_name.view_name`` without the project name if the view is
    located inside the project.  Other arguments are comma-separated values
    that will be filled in place of positional and keyword arguments in the
    URL. All arguments for the URL should be present.

    For example if you have a view ``app_name.client`` taking client's id and
    the corresponding line in a URLconf looks like this::

        ('^client/(\d+)/$', 'app_name.client')

    and this app's URLconf is included into the project's URLconf under some
    path::

        ('^clients/', include('project_name.app_name.urls'))

    then in a template you can create a link for a certain client like this::

        {% url app_name.client client.id %}

    The URL will look like ``/clients/client/123/``.
    """
    bits = token.contents.split(' ')
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument"
                                  " (path to a view)" % bits[0])
    request = parser.compile_filter('request')
    viewname = bits[1]
    args = []
    kwargs = {}
    asvar = None

    if len(bits) > 2:
        bits = iter(bits[2:])
        for bit in bits:
            if bit == 'as':
                asvar = bits.next()
                break
            else:
                for arg in bit.split(","):
                    if '=' in arg:
                        k, v = arg.split('=', 1)
                        k = k.strip()
                        kwargs[k] = parser.compile_filter(v)
                    elif arg:
                        args.append(parser.compile_filter(arg))
    return PluggableURLNode(request, viewname, args, kwargs, asvar)
pluggable_url = register.tag(pluggable_url)
