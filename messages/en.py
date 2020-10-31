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

# Mailings
FROM_TITLE = "CSAFE Admin"
FROM_EMAIL = "admin@csafe.com"
CONFIRMATION_MAIL_SUBJECT = "CSAFE User - Confirm your email"
CONFIRMATION_MAIL_BODY = """
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
CONFIRMATION_MAIL_BODY_HTML = """
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
RELATIONSHIP_MAIL_SUBJECT = "CSAFE Relationship Update"
RELATIONSHIP_START_MAIL_BODY = """
Dear {name}, \n
\n
Please be aware, Keyholder {kh_displayname} has just taken control of your safe.
\n\n
You should be careful not to displease them.  When (and whether) your safe opens again is now up to them.
\n\n
Thank you for using the CSAFE service.
\n\n
CSAFE Administrator
"""
RELATIONSHIP_START_MAIL_BODY_HTML = """
<html>
<strong>Dear {name},</strong><br><br>
Please be aware, Keyholder <strong>{kh_displayname}</strong> has just taken control of your safe.
<br><br>
You should be careful not to displease them.  When (and whether) your safe opens again is now up to them.
<br><br>
Thank you for registering to use the CSAFE service.<br>
<br><br>
CSAFE Administrator
</html>
"""
RELATIONSHIP_END_MAIL_BODY = """
Dear {name}, \n
\n
Please be aware, Keyholder {kh_displayname} has relinquished control of your safe.
\n
You are now at liberty to give control to another Keyholder using a new Digital key, {digital_key}
\n
IMPORTANT: Please keep this email, or the digital key above, safe. It will be needed if a new Keyholder is to 
take over control of the safe.
\n
For safety, your safe is now unlocked.
\n
Thank you for using the CSAFE service.
\n
CSAFE Administrator
"""
RELATIONSHIP_END_MAIL_BODY_HTML = """
<html>
<strong>Dear {name},</strong><br><br>
Please be aware, Keyholder <strong>{kh_displayname}</strong> has relinquished control of your safe.
<br><br>
You are now at liberty to give control to another Keyholder using a new Digital key, <strong>{digital_key}</strong>
<br><br>
<strong>IMPORTANT: Please keep this email, or the digital key above, safe. It will be needed if a new Keyholder is to 
take over control of the safe.</strong>
<br><br>
For safety, your safe is now unlocked.
<br><br>
Thank you for using the CSAFE service.<br>
<br>
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

# Operations messages
CLAIM_NO_SAFE = "That safe does not exist"
CLAIM_NOT_AVAILABLE = "That safe cannot be claimed"
RELEASE_NOT_OWNED = "You do not own that safe"
INCORRECT_KEY = "Incorrect digital key"
KH_EQ_SH = "You cannot be a keholder for your own safe"
SH_IN_RELATIONSHIP = "The safeholder already has a keyholder for that safe"
RELATIONSHIP_ESTABLISHED = "Relationship established"
RELATIONSHIP_TERMINATED = "Relationship terminated"
INCORRECT_KH = "You are not the keyholder for that safe"
BAD_REQUEST = "Unexpected API Request"
NOT_AUTHORISED = "Not authorised"
