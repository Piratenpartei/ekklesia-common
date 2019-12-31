import random
import string
letters = string.ascii_lowercase

settings = {
    "app": {
        "title": "Ekklesia Common Dev",
        "fail_on_form_validation_error": False,
        "instance_name": "ekklesia_common",
        "insecure_development_mode": False,
        "internal_login_enabled": True,
        "custom_footer_url": None,
        "tos_url": None,
        "faq_url": None,
        "imprint_url": None
    },
    "database": {
        "uri": "postgresql+psycopg2://ekklesia_common:ekklesia_common@127.0.0.1/ekklesia_common"
    },
    "browser_session": {
        "secret_key": "".join(random.choice(letters) for x in range(32)),
        "cookie_secure": False
    }
}