from requests import post, Response
from typing import Union, List
import os
import logging

import messages.en as msgs


class MailGunException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class Mailgun:
    MAIL_DOMAIN = os.environ.get("MAIL_DOMAIN", None)
    MAILGUN_API_BASEURL = "https://api.eu.mailgun.net/v3/{}".format(MAIL_DOMAIN)
    MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY", None)

    @classmethod
    def send_email(
        cls,
        from_email: str,
        from_title: str,
        to_email: List[str],
        subject: str,
        text: str,
        html: str,
    ) -> Union[Response, None]:
        """
        Send an address confirmation email to the user
        """
        if cls.MAILGUN_API_KEY is None:
            raise MailGunException(msgs.MAILGUN_NO_API_KEY)
        if cls.MAIL_DOMAIN is None:
            logging.error('MAILGUN: MAILGUN_NO_DOMAIN')
            raise MailGunException(msgs.MAILGUN_NO_DOMAIN)
        response = post(
            cls.MAILGUN_API_BASEURL + "/messages",
            auth=("api", cls.MAILGUN_API_KEY),
            data={
                "from": f"{from_title} <{from_email}>",
                "to": to_email,
                "subject": subject,
                "text": text,
                "html": html,
            },
        )
        if not response.ok:
            logging.error(f"MAILGUN API exception: {response.text}")
            raise MailGunException(msgs.MAILGUN_FAILED_TO_SEND.format(response.text))
        return response
