from django.apps import AppConfig
from openedx.core.constants import COURSE_ID_PATTERN
from openedx.core.djangoapps.plugins.constants import (
    PluginSettings,
    PluginURLs,
    ProjectType,
    SettingsType,
)


class WeolcomeMailConfig(AppConfig):
    name = 'welcome_mail'
    plugin_app = {
        PluginURLs.CONFIG: {
            ProjectType.LMS: {
                PluginURLs.NAMESPACE: "welcome-mail",
                PluginURLs.REGEX: u'^courses/{}/welcome_mail/'.format(COURSE_ID_PATTERN),
                PluginURLs.RELATIVE_PATH: "urls",
            }}
    }
