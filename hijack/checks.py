# -*- coding: utf-8 -*-
from django.core.checks import Error, Warning, register
from django.conf.global_settings import AUTH_USER_MODEL as default_auth_user_model
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required

from compat import import_string
from hijack import settings as hijack_settings


def check_display_admin_button_with_custom_user_model(app_configs, **kwargs):
    warnings = []
    if hijack_settings.HIJACK_DISPLAY_ADMIN_BUTTON \
            and settings.AUTH_USER_MODEL != default_auth_user_model:
        warnings.append(
            Warning(
                'Setting HIJACK_DISPLAY_ADMIN_BUTTON, which is True by default, '
                'does not work with a custom user model. '
                'Mix HijackUserAdminMixin into your custom UserAdmin or set HIJACK_DISPLAY_ADMIN_BUTTON to False.',
                hint=None,
                obj=settings.AUTH_USER_MODEL,
                id='hijack.W001',
            )
        )
    return warnings

def check_legacy_settings(app_configs, **kwargs):
    warnings = []
    for setting in hijack_settings.SETTINGS:
        legacy_name = setting['legacy_name']
        if legacy_name and hasattr(settings, legacy_name):
            warnings.append(
                Warning(
                    'Deprecation warning: Setting "%s" has been renamed to "%s"'
                    % (legacy_name, setting['name']),
                    hint=None,
                    obj=None,
                    id='hijack.W002',
                )
            )
    return warnings

def check_url_allowed_attributes(app_configs, **kwargs):
    errors = []
    required_attributes = [
        'user_id',
        'email',
        'username',
    ]
    set_attributes = hijack_settings.HIJACK_URL_ALLOWED_ATTRIBUTES
    if not any(attribute in set_attributes for attribute in required_attributes):
        errors.append(
            Error(
                'Setting HIJACK_URL_ALLOWED_ATTRIBUTES needs to be subset of (%s)'
                    % ', '.join(required_attributes),
                hint=None,
                obj=set_attributes,
                id='hijack.E001',
            )
        )
    return errors

def check_custom_authorization_check_importable(app_configs, **kwargs):
    errors = []
    handler = hijack_settings.HIJACK_AUTHORIZATION_CHECK
    try:
        if handler != staff_member_required:
            import_string(handler)
    except ImportError:
        errors.append(
            Error(
                'Setting HIJACK_AUTHORIZATION_CHECK cannot be imported',
                hint=None,
                obj=handler,
                id='hijack.E002',
            )
        )
    return errors

def check_hijack_decorator_importable(app_configs, **kwargs):
    errors = []
    decorator = hijack_settings.HIJACK_DECORATOR
    try:
        if decorator != 'django.contrib.admin.views.decorators.staff_member_required':
            import_string(decorator)
    except ImportError:
        errors.append(
            Error(
                'Setting HIJACK_DECORATOR cannot be imported',
                hint=None,
                obj=decorator,
                id='hijack.E003',
            )
        )
    return errors

def check_staff_authorization_settings(app_configs, **kwargs):
    errors = []
    if hijack_settings.HIJACK_AUTHORIZE_STAFF_TO_HIJACK_STAFF and not hijack_settings.HIJACK_AUTHORIZE_STAFF:
        errors.append(
            Error(
                'Setting HIJACK_AUTHORIZE_STAFF_TO_HIJACK_STAFF may not be True if HIJACK_AUTHORIZE_STAFF is False.',
                hint=None,
                obj=None,
                id='hijack.E004',
            )
        )
    return errors

def register_checks():
    for check in [
        check_display_admin_button_with_custom_user_model,
        check_legacy_settings,
        check_url_allowed_attributes,
        check_custom_authorization_check_importable,
        check_hijack_decorator_importable,
        check_staff_authorization_settings,
    ]:
        register(check)