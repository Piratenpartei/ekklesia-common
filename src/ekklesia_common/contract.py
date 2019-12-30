from functools import wraps
from itertools import tee
import colander
import dectate
import deform
from eliot import log_call, start_action, Message
import morepath
from morepath.directive import HtmlAction, ViewAction
from morepath.view import render_html
from deform.widget import Select2Widget, HiddenWidget
from more.babel_i18n.domain import Domain
from pkg_resources import resource_filename


def string_property(**kwargs):
    return colander.SchemaNode(colander.String(), **kwargs)


def decimal_property(**kwargs):
    return colander.SchemaNode(colander.Decimal(), **kwargs)


def int_property(**kwargs):
    return colander.SchemaNode(colander.Int(), **kwargs)


def bool_property(**kwargs):
    return colander.SchemaNode(colander.Boolean(), **kwargs)


def list_property(**kwargs):
    return colander.SchemaNode(colander.List(), **kwargs)


def set_property(**kwargs):
    return colander.SchemaNode(colander.Set(), **kwargs)


def date_property(**kwargs):
    return colander.SchemaNode(colander.Date(), **kwargs)


def datetime_property(**kwargs):
    return colander.SchemaNode(colander.DateTime(), **kwargs)

def enum_property(enum_cls, **kwargs):
    return colander.SchemaNode(colander.Enum(enum_cls), **kwargs)


def datetime_property(**kwargs):
    return colander.SchemaNode(colander.DateTime(), **kwargs)


class Schema(colander.MappingSchema):
    pass


COLANDER_TRANSLATION_DIR = resource_filename('colander', 'locale/')
DEFORM_TRANSLATION_DIR = resource_filename('deform', 'locale/')


class Form(deform.Form):
    """
    Deform Form with more.babel_i18n integration.
    """

    deform_template_dirs = [resource_filename('deform', 'templates/')]

    def __init__(self, schema: Schema, request: morepath.Request, *args, **kwargs) -> None:
        # Domain depends on request, so it must be created here
        domains = {
            'colander': Domain(request=request, dirname=COLANDER_TRANSLATION_DIR, domain='colander'),
            'deform': Domain(request=request, dirname=DEFORM_TRANSLATION_DIR, domain='deform'),
            'messages': Domain(request=request, dirname=self.__class__.app_translation_dir, domain='messages')
        }

        def translator(term):
            domain = domains.get(term.domain)
            if domain is None:
                return term.interpolate()
            else:
                translated = domain.gettext(term)
                return term.interpolate(translated)

            return domain.gettext(term)

        renderer = deform.ZPTRendererFactory(
            self.__class__.deform_template_dirs,
            translator=translator
        )
        super().__init__(schema, *args, renderer=renderer, **kwargs)

    @classmethod
    def set_deform_override_dir(cls, dirpath):
        cls.deform_template_dirs = [dirpath, resource_filename('deform', 'templates/')]

    def prepare_for_render(self):
        # Can be used by subclasses to customize field widgets, for example.
        pass


def get_form_data(model, form_class, cell_class, request):
    form = form_class(request, request.link(model))
    controls = list(request.POST.items())
    with start_action(action_type='validate_form',
                    controls=dict(c for c in controls if not c[0].startswith('_')),
                    form=form):
        try:
            return form.validate(controls), None
        except deform.ValidationFailure:
            Message.log(validation_errors=form.error.asdict())
            if request.app.settings.app.fail_on_form_validation_error:
                raise form.error
            return None, cell_class(request=request, form=form, model=model).show()


def select2_widget_or_hidden(values):
    """ Render a select2 widget or a hidden field if no values were given.
    XXX: Is there a better way to hide unwanted fields?
    """
    if values is None:
        return HiddenWidget(hidden=True)
    else:
        return Select2Widget(values=values)


class HtmlFormAction(HtmlAction):
    group_class = ViewAction

    @log_call
    def __init__(self, model, form, cell, render=None, template=None, load=None, permission=None, internal=False, **predicates):
        self.form = form
        self.cell = cell
        if 'request_method' not in predicates:
            predicates['request_method'] = 'POST'

        super().__init__(model, render or render_html, template, load, permission, internal, **predicates)

    @log_call
    def perform(self, obj, template_engine_registry, app_class):
        form_class = self.form
        model_class = self.model
        cell_class = self.cell

        @log_call
        @wraps(obj)
        def wrapped(self, request):
            appstruct, failure_response = get_form_data(self, form_class, cell_class, request)

            if failure_response:
                return failure_response

            with start_action(action_type='call_view'):
                response = obj(self, request, appstruct)
            return response

        super().perform(wrapped, template_engine_registry, app_class)


class FormApp(morepath.App):

    html_form_post = dectate.directive(HtmlFormAction)
