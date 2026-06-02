"""Constants for the Google Health integration."""

DOMAIN = "google_health_scale_sync"

OAUTH2_AUTHORIZE = "https://accounts.google.com/o/oauth2/v2/auth"
OAUTH2_TOKEN = "https://oauth2.googleapis.com/token"

# Using the primary scopes for Google Health API
OAUTH2_SCOPES = [
    "https://www.googleapis.com/auth/googlehealth.health_metrics_and_measurements.writeonly"
]

# Configuration keys for the options flow (Profile data)
CONF_GENDER = "gender"
CONF_DOB = "date_of_birth"
CONF_HEIGHT = "height"
