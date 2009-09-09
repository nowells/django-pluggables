"""
A tool for allowing reusable apps to exist at multiple URLs within a project.

.. autosummary::
   :template: autosummary_module
   :toctree:

   templatetags.pluggable

"""
import copy
from functools import wraps
import uuid

from django.conf import settings
from django.conf.urls import defaults
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import resolve, reverse, RegexURLPattern, get_callable, get_mod_func, Resolver404
from django.core.exceptions import ViewDoesNotExist
from django.http import Http404
from django.db import models


def patterns(*args):
    return args


def url(*args, **kwargs):
    return 'url', list(args), kwargs,


def include(*args, **kwargs):
    return 'include', list(args), kwargs,


def pluggable_view(func, pluggable):
    @wraps(func)
    def view_wrapper(request, *args, **kwargs):
        request.pluggable = PluggableViewWrapper(pluggable, request, *args, **kwargs)
        pluggable_args, pluggable_kwargs = request.pluggable.pluggable_arguments
        return func(request, *pluggable_args, **pluggable_kwargs)
    view_wrapper.pluggable_unique_identifier = pluggable.pluggable_unique_identifier
    return view_wrapper


def pluggable_class_view(func, pluggable):
    @wraps(func)
    def class_view_wrapper(request, *args, **kwargs):
        request.pluggable = PluggableViewWrapper(pluggable, request, *args, **kwargs)
        request.pluggable.pluggable_initialize(request)
        pluggable_args, pluggable_kwargs = request.pluggable.pluggable_arguments
        return func(request, *pluggable_args, **pluggable_kwargs)
    class_view_wrapper.pluggable_unique_identifier = pluggable.pluggable_unique_identifier
    return class_view_wrapper


def pluggable_placeholder(*args, **kwargs):
    raise Http404


class PluggableViewWrapper(object):
    def __init__(self, pluggable_object, request, *args, **kwargs):
        # Public Data
        self.config = {}
        self.view_context = {}
        self.template_context = {}

        # Pluggable Configuration
        self.__pluggable_object = pluggable_object
        self.prefix = self.__pluggable_object.pluggable_prefix

        # Parent and Pluggable function args/kwargs.
        try:
            _, self.__parent_args, self.__parent_kwargs = resolve('%s%s' % (request.path_info, self.__pluggable_object.pluggable_unique_identifier))
        except Resolver404, e:
            # Try and catch when the parent application is calling a class based view directly
            try:
                reverse('%s%s' % (self.prefix and '%s_' % self.prefix or '', self.__pluggable_object.pluggable_unique_identifier), args=args, kwargs=kwargs)
            except:
                raise e
            else:
                self.__parent_args, self.__parent_kwargs = args, kwargs

        self.__pluggable_args = list(args[len(self.__parent_args):])
        self.__pluggable_kwargs = dict([(x[0], x[1]) for x in kwargs.items() if x[0] not in self.__parent_kwargs])

    def pluggable_initialize(self, request):
        # We seperate this out into its own function call so that each step has access to "request.pluggable" and the prior generated context.
        self.config = self.__pluggable_object.pluggable_config(request, *self.__parent_args, **self.__parent_kwargs)
        self.view_context = self.__pluggable_object.pluggable_view_context(request, *self.__parent_args, **self.__parent_kwargs)
        self.template_context = self.__pluggable_object.pluggable_template_context(request, *self.__parent_args, **self.__parent_kwargs)

    @property
    def pluggable_arguments(self):
        return self.__pluggable_args, self.__pluggable_kwargs

    @property
    def parent_arguments(self):
        return self.__parent_args, self.__parent_kwargs

    @property
    def pluggable_url_data(self):
        return {
            'prefix': self.prefix,
            'parent_args': self.__parent_args,
            'parent_kwargs': self.__parent_kwargs,
            }


class PluggableApp(object):
    urlpatterns = patterns('', )

    def __new__(cls, prefix=None):
        obj = object.__new__(cls)
        obj.pluggable_unique_identifier = '/@@pluggableapp@@/%s/' % str(uuid.uuid4())
        obj.pluggable_prefix = prefix
        view_prefix = cls.urlpatterns[0]
        urlpatterns = []
        for pattern_type, pattern_args, pattern_kwargs in copy.deepcopy(cls.urlpatterns[1:]):
            if pattern_type == 'url':
                view = pattern_args[1]
                if type(view) == list:
                    raise Exception("Pluggable applications do not support 'include(...)' url definitions.")

                # Handle a view directly
                if callable(view):
                    pattern_args[1] = pluggable_view(view, obj)
                # Handle a view_prefix combined with function name or a full view path
                elif isinstance(view, (str, unicode)) and (view_prefix or '.' in view):
                    view_name = view_prefix and '%s.%s' % (view_prefix, view) or view
                    try:
                        pattern_args[1] = pluggable_view(get_callable(view), obj)
                    except ImportError, e:
                        mod_name, _ = get_mod_func(view)
                        raise ViewDoesNotExist("Could not import %s. Error was: %s" % (mod_name, str(e)))
                    except AttributeError, e:
                        mod_name, func_name = get_mod_func(view)
                        raise ViewDoesNotExist("Tried %s in module %s. Error was: %s" % (func_name, mod_name, str(e)))
                # Handle class view.
                elif isinstance(view, (str, unicode)) and hasattr(obj, view):
                    # Avoid reapplying pluggable view decorator when it has aready been applied. (i.e. the same function is reused in the same configuration.
                    if not getattr(getattr(obj, view), 'pluggable_unique_identifier', '') == obj.pluggable_unique_identifier:
                        setattr(obj, view, pluggable_class_view(getattr(obj, view), obj))
                    pattern_args[1] = getattr(obj, view)
                else:
                    raise ViewDoesNotExist('Invalid view type. %s' % view)

                if 'name' in pattern_kwargs:
                    pattern_kwargs['name'] = '%s%s' % (obj.pluggable_prefix and '%s_' % obj.pluggable_prefix or '', pattern_kwargs['name'])

                urlpatterns.append(defaults.url(*pattern_args, **pattern_kwargs))
            elif pattern_type == 'include':
                urlpatterns.append(defaults.include(*pattern_args, **pattern_kwargs))
            else:
                raise Exception('Invalid url pattern type.')
        urlpatterns.append(defaults.url(r'^.*%s$' % obj.pluggable_unique_identifier, pluggable_placeholder, name='%s%s' % (obj.pluggable_prefix and '%s_' % obj.pluggable_prefix or '', obj.pluggable_unique_identifier)))
        obj.urlpatterns = defaults.patterns('', *urlpatterns)
        return obj

    def __iter__(self):
        return self.urlpatterns.__iter__()

    def __getitem__(self, index):
        return self.urlpatterns[index]

    def __len__(self):
        return len(self.urlpatterns)

    def pluggable_view_context(self, request, *args, **kwargs):
        return None

    def pluggable_template_context(self, request, *args, **kwargs):
        return {}

    def pluggable_config(self, request, *args, **kwargs):
        return {}


def pluggable_context_processor(request):
    if hasattr(request, 'pluggable'):
        return request.pluggable.template_context
    return {}


def pluggable_reverse(request, view_name, urlconf=None, args=None, kwargs=None, prefix=None):
    args = args or []
    kwargs = kwargs or {}

    if hasattr(request, 'pluggable'):
        view_name = request.pluggable.prefix and '%s_%s' % (request.pluggable.prefix, view_name) or '%s' % view_name
        parent_args, parent_kwargs = request.pluggable.parent_arguments
        if parent_args:
            args = parent_args + args

        if parent_kwargs:
            kwargs.update(parent_kwargs)

    return reverse(view_name, urlconf, args, kwargs, prefix)


def permalink(func):
    """
    Decorator that calls urlresolvers.reverse() to return a URL using
    parameters returned by the decorated function "func".

    "func" should be a function that returns a tuple in one of the
    following formats:
        (viewname, viewargs)
        (viewname, viewargs, viewkwargs)
    """
    from django.core.urlresolvers import reverse
    def inner(self, *args, **kwargs):
        bits = func(self, *args, **kwargs)
        if isinstance(self.pluggable_url, dict):
            view_name_prefix = self.pluggable_url.get('prefix', '')
            view_name = '%s%s' % (view_name_prefix and ('%s_' % view_name_prefix) or '', bits[0])
            parent_args = self.pluggable_url.get('parent_args', [])
            parent_kwargs = self.pluggable_url.get('parent_kwargs', {})
            if len(bits) >= 2 and bits[1]:
                parent_args = parent_args + bits[1]
            if len(bits) >= 3 and bits[2]:
                parent_kwargs.update(bits[2])
            bits = [view_name, parent_args, parent_kwargs]
        return reverse(bits[0], None, *bits[1:3])
    return inner
