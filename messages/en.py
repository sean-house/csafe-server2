"""
File with message constants in English
:var
"""
FIELD_REQUIRED = "'{}' field must be specified"
USER_EXISTS = "User with that name already exists"
EMAIL_EXISTS = "A user with that email already exists"
USER_NONEXISTANT = "User with ID {} does not exist"
USER_ACTIVATED = "User {} has ben activated"
CREATED = "'{}' has been created"
DELETED = "'{}' has been deleted"
INVALID_PASSWORD = "Invalid credentials"
OWN_RECORD_ONLY = "You are only permitted to delete your own record"
NOT_CONFIRMED = "You have not confirmed your ID. Check your email - <{}>"
FAILED_TO_MAIL = (
    "Failed to send confirmation e-mail to {}. Check the details and try again"
)
FAILED_TO_CREATE = "Failed to create an account.  Server returned error message: {}"
MAILGUN_NO_API_KEY = "Cannot load Mailgun API key from environment - cannot send emails"
MAILGUN_NO_DOMAIN = "Cannot load mail domain from environment - cannot send emails"
MAILGUN_FAILED_TO_SEND = "Failure in Mailgun service. Error = {}.  Cannot send mail."

# Confirmation email
FROM_TITLE = "CSAFE Admin"
FROM_EMAIL = "admin@csafe.com"
MAIL_SUBJECT = "CSAFE User - Confirm your email"
MAIL_BODY = """
Dear {name}, \n
\n
Thank you for registering to use the CSAFE service. \n
Please click this link to activate your account: {link}  \n
\n
Please note: The link expires in 30 minutes
\n
If you did not register for the CSAFE service you can safely ignore this message. \n
\n
CSAFE Administrator
"""
MAIL_BODY_HTML = """
<html>
<strong>Dear {name},</strong><br><br>
Thank you for registering to use the CSAFE service.<br>
<br>
Please click this link to activate your account:<br>
<a href="{link}">{link}</a><br><br>
Please note: The link expires in 30 minutes<br><br>
CSAFE Administrator
</html>
"""
NOT_FOUND = 'This ID is not found. Have you already registered?'
EXPIRED = 'This registration has expired.  Please re-register'
ALREADY_CONFIRMED = 'You have already confirmed this email. No need to do so again'
RESEND_SUCCESSFUL = 'Resent confirmation mail.  Check your mailbox'
RESEND_FAILED = 'Failed to resend confirmation mail.  Problem with the Mailgun service'

# Safe message
SAFE_REGISTRATION_ERROR = "Registration error"
SAFE_CHECKIN_ERROR = "Checkin error"
