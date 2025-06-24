import logging

import pendulum
import sentry_sdk
from sentry_sdk.integrations.logging import SentryHandler

from base.config import config

SENTRY_INIT = False


def sentry_init():
    global SENTRY_INIT
    if SENTRY_INIT:
        return
    SENTRY_INIT = True

    if not config.has_option('sentry', 'dsn'):
        return

    sentry_sdk.init(
        dsn=config.get('sentry', 'dsn'),
        release=pendulum.now().to_date_string(),
        attach_stacktrace=True,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for tracing.
        traces_sample_rate=1.0,
    )

    shlr = SentryHandler()
    shlr.setLevel('WARNING')
    logging.getLogger().addHandler(shlr)
    logging.getLogger(__name__).addHandler(shlr)
