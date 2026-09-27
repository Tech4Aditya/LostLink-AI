# API Contract

Base URL: `/api/v1`

## Auth

`POST /auth/register`

`POST /auth/login`

`GET /auth/me`

## Reports

`POST /reports` multipart form:
- type: lost|found
- category
- description
- location_name
- color
- latitude
- longitude
- event_time
- image

`GET /reports?type=lost|found`

`GET /reports/{id}`

## Matches

`GET /matches`

`GET /matches/{id}`

`POST /matches/{id}/claims`

The current API intentionally treats match scores as candidate evidence.

## Health

`GET /health`
