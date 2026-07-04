# Spec: Profile Page Creation

## Overview
Implement the user profile page — the first authenticated page in Spendly. This step replaces the `profile()` placeholder with a real page where a logged-in user can see their account details (name, email, member-since date), update their name and email, and change their password. Because this is the first route that requires authentication, this step also introduces a reusable `login_required` decorator that every later logged-in feature (dashboard, expenses) will use. The navbar user name added in Step 03 becomes a link to this page.

## Depends on
- Step 01 — Database setup (`users` table, `get_db()`)
- Step 02 — Registration (`create_user()`, flash block in `base.html`, `.flash-*` CSS)
- Step 03 — Login and Logout (`session['user_id']` / `session['user_name']`, `get_user_by_email()`, session-aware navbar)

## Routes
- `GET /profile` — render profile page with current user details and both forms — logged-in
- `POST /profile` — update the user's name and email — logged-in
- `POST /profile/password` — change the user's password — logged-in

Unauthenticated access to any of these redirects to `url_for('login')` with a flashed message.

## Database changes
No new tables or columns. The existing `users` table covers all requirements.

New DB helpers must be added to `database/db.py` (same open/`finally`-close pattern as `create_user()` / `get_user_by_email()`):
- `get_user_by_id(user_id)` — parameterised `SELECT` on `users` by id; returns the row or `None`.
- `update_user(user_id, name, email)` — parameterised `UPDATE` of name and email; raises `sqlite3.IntegrityError` if the email is taken by another user (UNIQUE constraint).
- `update_user_password(user_id, password)` — hashes with `generate_password_hash` and updates `password_hash`.

## Templates
- **Create:** `templates/profile.html`
  - Extends `base.html`
  - Shows the user's name, email, and account creation date (from `created_at`)
  - "Account details" form: `name`, `email` inputs, posting to `url_for('profile')`
  - "Change password" form: `current_password`, `new_password`, `confirm_password` inputs, posting to `url_for('profile_password')`
  - Reuse the existing form design language: `.auth-card`, `.form-group`, `.form-input`, `.btn-submit` (consistent with `login.html` / `register.html`)
- **Modify:** `templates/base.html`
  - The logged-in user name in the navbar (`.nav-user`) becomes a link to `url_for('profile')`

## Files to change
- `app.py` — add `login_required` decorator (`functools.wraps`); replace the `profile()` placeholder with GET/POST handling; add `profile_password()` route
- `database/db.py` — add `get_user_by_id()`, `update_user()`, `update_user_password()`
- `templates/base.html` — navbar user name links to profile
- `static/css/style.css` — profile-page styles only if needed (reuse `.auth-*` / form classes first; any additions must use CSS variables)

## Files to create
- `templates/profile.html`

## New dependencies
No new dependencies. Uses `functools.wraps` (standard library) and `werkzeug.security` (already installed).

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only — never use f-strings in SQL
- Passwords hashed with werkzeug — verify the current password with `check_password_hash`; hash the new one with `generate_password_hash`
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Use `url_for()` for every internal link — never hardcode URLs
- `login_required` decorator: if `session.get('user_id')` is missing, flash "Please sign in to continue." (`error`) and `redirect(url_for('login'))`; use `functools.wraps` so route names are preserved
- Always load the user fresh with `get_user_by_id(session['user_id'])` on each request — do not trust stale session data for display; if the id no longer exists in the DB, clear the session and redirect to login
- Account details validation (POST `/profile`):
  1. Name and email must be non-empty ("All fields are required.")
  2. Email taken by another user → catch `sqlite3.IntegrityError`, flash "Email already registered."
  3. On success, update `session['user_name']` so the navbar reflects the new name immediately, flash a success message
- Change password validation (POST `/profile/password`):
  1. All three fields non-empty ("All fields are required.")
  2. `current_password` must match the stored hash ("Current password is incorrect.")
  3. `new_password == confirm_password` ("Passwords do not match.")
  4. On success, flash "Password updated." — the user stays logged in
- POST-redirect-GET everywhere: on success AND on any validation failure, flash the message (`success` / `error` category) and `redirect(url_for('profile'))` — never render a page directly as the response to a POST (a re-render would strand the browser on the POST-only `/profile/password` URL, where a refresh resubmits and a direct GET returns 405)
- Use `abort(405)` if an unsupported HTTP method reaches a route

## Definition of done
- [ ] Visiting `/profile` while logged out redirects to `/login` with "Please sign in to continue."
- [ ] Visiting `/profile` while logged in renders the page showing the user's name, email, and member-since date
- [ ] The navbar user name links to `/profile` when logged in
- [ ] Submitting new valid name/email updates the row in `users`, updates the navbar name immediately, and shows a success flash
- [ ] Submitting an email already used by another user shows "Email already registered." and changes nothing
- [ ] Submitting empty name or email shows a validation error and changes nothing
- [ ] Changing the password with the correct current password succeeds; the user can log out and log back in with the new password only
- [ ] Changing the password with a wrong current password shows "Current password is incorrect." and the old password still works
- [ ] Mismatched new/confirm passwords show "Passwords do not match." and the old password still works
- [ ] After any form submission — success or validation failure — the browser lands on a clean GET of `/profile` (POST-redirect-GET; no resubmission warning on refresh, no stranded `/profile/password` URL)
