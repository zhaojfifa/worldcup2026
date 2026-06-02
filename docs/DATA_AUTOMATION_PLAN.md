# Data Automation Plan

## Data Sources

Primary:

- API-FOOTBALL / API-Sports

Fallback:

- CSV import

Authority check:

- FIFA official schedule, manually checked when needed

Future sources:

- Transfermarkt
- FBref
- Elo Ratings
- Weather
- Travel distance
- Market consensus

## Automated Jobs

- sync_fixtures
- sync_teams
- sync_match_status
- generate_predictions
- generate_reports
- lineup_watch
- live_adjustment
- post_match_settlement

## Live Correction Flow

T-60min:

- enter lineup_watch status

T-45 to T-30min:

- check official lineups
- detect lineup changes
- trigger live_adjuster
- update probabilities
- generate change explanation
