# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.0.1

### Added
- Initial release of the Google Health Scale Sync custom component.
- Uses the new Google Health API v4 which has significantly better rate limits compared to the legacy Fitbit API (which is scheduled for deprecation).
- Included log_body_measurements unified action to easily log both weight and body fat percentage.
- Implemented smart calculation for body fat percentage when only raw impedance and weight are provided, using demographics (age, height, gender) entered during configuration setup.
