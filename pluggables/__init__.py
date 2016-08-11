"""
A tool for allowing reusable apps to exist at multiple URLs within a project.

.. autosummary::
   :template: autosummary_module
   :toctree:

   templatetags.pluggable

"""
import copy
import uuid
from functools import wraps

from django.conf import urls
from django.core.exceptions import ViewDoesNotExist
from django.core.urlresolvers import (Resolver404,
                                      get_callable, get_mod_func, resolve,
                                      reverse)
from django.http import Http404
from django.utils import six
from django.utils.encoding import force_text


def url(*args, **kwargs):
    return 'url', list(args), kwargs,


def include(*args, **kwargs):
    return 'include', list(args), kwargs,


def pluggable_view(func, pluggable):

    @wraps(func)
    def view_wrapper(request, *args, **kwargs):
        request.pluggable = PluggableViewWrapper(
            pluggable, request, *args, **kwargs
        )
        pluggable_args, pluggable_kwargs = \
            request.pluggable.pluggable_arguments
        return func(request, *pluggable_args, **pluggable_kwargs)

    view_wrapper.pluggable_unique_identifier = \
        pluggable.pluggable_unique_identifier
    return view_wrapper


def pluggable_class_view(func, pluggable):

    @wraps(func)
    def class_view_wrapper(request, *args, **kwargs):
        request.pluggable = PluggableViewWrapper(
            pluggable, request, *args, **kwargs
        )
        request.pluggable.pluggable_initialize(request)
        pluggable_args, pluggable_kwargs = \
            request.pluggable.pluggable_arguments
        return func(request, *pluggable_args, **pluggable_kwargs)

    class_view_wrapper.pluggable_unique_identifier = \
        pluggable.pluggable_unique_identifier
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
            _, self.__parent_args, self.__parent_kwargs = resolve(
                '{}{}'.format(
                    request.path_info,
                    self.__pluggable_object.pluggable_unique_identifier
                )
            )
        except Resolver404:
            # Try and catch when the parent application is calling a class
            # based view directly
            try:
                reverse('{}{}'.format(
                    '{}_'.format(self.prefix) if self.prefix else '',
                    self.__pluggable_object.pluggable_unique_identifier
                ), args=args, kwargs=kwargs)
            except:
                raise
            else:
                self.__parent_args, self.__parent_kwargs = args, kwargs

        self.__pluggable_args = list(args[len(self.__parent_args):])
        self.__pluggable_kwargs = {
            k: v for k, v in kwargs.items() if k not in self.__parent_kwargs
        }

    def pluggable_initialize(self, request):
        # We seperate this out into its own function call so that each step
        # has access to "request.pluggable" and the prior generated context.
        self.config = self.__pluggable_object.pluggable_config(
            request, *self.__parent_args, **self.__parent_kwargs
        )
        self.view_context = self.__pluggable_object.pluggable_view_context(
            request, *self.__parent_args, **self.__parent_kwargs
        )
        self.template_context = \
            self.__pluggable_object.pluggable_template_context(
                request, *self.__parent_args, **self.__parent_kwargs
            )

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
    urlpatterns = []

    def __new__(cls, prefix=None):
        obj = object.__new__(cls)
        obj.pluggable_unique_identifier = '/@@pluggableapp@@/{}/'.format(
            force_text(uuid.uuid4())
        )
        obj.pluggable_prefix = prefix
        urlpatterns = []
        for pattern_type, pattern_args, pattern_kwargs in copy.deepcopy(
                cls.urlpatterns):
            if pattern_type == 'url':
                view = pattern_args[1]
                if type(view) == list:
                    raise Exception(
                        "Pluggable applications do not support 'include(...)' "
                        "url definitions."
                    )

                # Handle a view directly
                if callable(view):
                    pattern_args[1] = pluggable_view(view, obj)
                # Handle a view_prefix combined with function name or a full
                # view path
                elif isinstance(view, six.string_types) and '.' in view:
                    try:
                        pattern_args[1] = pluggable_view(
                            get_callable(view), obj
                        )
                    except ImportError as e:
                        mod_name, _ = get_mod_func(view)
                        raise ViewDoesNotExist(
                            'Could not import {}. Error was: {}'.format(
                                mod_name, force_text(e)
                            )
                        )
                    except AttributeError as e:
                        mod_name, func_name = get_mod_func(view)
                        raise ViewDoesNotExist(
                            'Tried {} in module {}. Error was: {}'.format(
                                func_name, mod_name, force_text(e)
                            )
                        )
                # Handle class view.
                elif isinstance(view, six.string_types) and hasattr(obj, view):
                    # Avoid reapplying pluggable view decorator when it has
                    # aready been applied. (i.e. the same function is reused
                    # in the same configuration.
                    pluggable_unique_identifier = getattr(
                        getattr(obj, view), 'pluggable_unique_identifier', ''
                    )
                    if not pluggable_unique_identifier == \
                            obj.pluggable_unique_identifier:
                        setattr(
                            obj, view,
                            pluggable_class_view(getattr(obj, view), obj)
                        )
                    pattern_args[1] = getattr(obj, view)
                else:
                    raise ViewDoesNotExist('Invalid view type. %s' % view)

                if 'name' in pattern_kwargs:
                    pattern_kwargs['name'] = '{}{}'.format(
                        '{}_'.format(obj.pluggable_prefix) if
                        obj.pluggable_prefix else '',
                        pattern_kwargs['name']
                    )

                urlpatterns.append(urls.url(*pattern_args, **pattern_kwargs))
            elif pattern_type == 'include':
                urlpatterns.append(urls.include(
                    *pattern_args, **pattern_kwargs
                ))
            else:
                raise Exception('Invalid url pattern type.')
        urlpatterns.append(urls.url(
            r'^.*{}$'.format(obj.pluggable_unique_identifier),
            pluggable_placeholder,
            name='{}{}'.format(
                '{}_'.format(obj.pluggable_prefix) if
                obj.pluggable_prefix else '',
                obj.pluggable_unique_identifier
            )
        ))
        obj.urlpatterns = urlpatterns
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


def pluggable_reverse(
        request, view_name, urlconf=None, args=None, kwargs=None, prefix=None):
    args = args or []
    kwargs = kwargs or {}

    if hasattr(request, 'pluggable'):
        view_name = '{}_{}'.format(request.pluggable.prefix, view_name) if \
            request.pluggable_prefix else view_name
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
            view_name = '{}{}'.format(
                '{}_'.format(view_name_prefix) if view_name_prefix else '',
                bits[0]
            )
            parent_args = self.pluggable_url.get('parent_args', [])
            parent_kwargs = self.pluggable_url.get('parent_kwargs', {})
            if len(bits) >= 2 and bits[1]:
                parent_args = parent_args + bits[1]
            if len(bits) >= 3 and bits[2]:
                parent_kwargs.update(bits[2])
            bits = [view_name, parent_args, parent_kwargs]
        return reverse(bits[0], None, *bits[1:3])
    return inner
