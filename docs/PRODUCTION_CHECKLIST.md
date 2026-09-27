# Production checklist

Before exposing LostLink to the public internet:

- [ ] Replace local uploads with private object storage + signed URLs.
- [ ] Run HTTPS everywhere.
- [ ] Replace `JWT_SECRET=CHANGE_ME`.
- [ ] Add refresh-token/session rotation.
- [ ] Add rate limiting on auth, report, upload and claim endpoints.
- [ ] Add image malware/content scanning.
- [ ] Encrypt private verification evidence at rest.
- [ ] Add admin-only claim review endpoints and role checks.
- [ ] Add audit events for report edits, claims and status changes.
- [ ] Add database backups and restore drills.
- [ ] Add structured logging and error monitoring.
- [ ] Add automated API/integration/e2e tests.
- [ ] Lock the ML evaluation set before fine-tuning.
- [ ] Measure false-match rate before enabling any automatic notification.
- [ ] Add data retention/deletion controls.
- [ ] Obtain consent and publish privacy/terms documents for real users.
