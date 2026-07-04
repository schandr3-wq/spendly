# Spec: Login and Logout

## Overview
Implement session-based authentication so registered users can sign in and out of Spendly. This step upgrades the existing stub `GET /login` route into a working form that accepts a POST, verifies credentials against the `users` table, and stores the user's identity in the Flask session. It also replaces the `logout` placeholder with a real route that clears the session. The navbar becomes session-aware, showing "Sign in / Get started" to visitors and a greeting plus "Log out" to authenticated users. This completes the authentication loop started in Step 02 (Registration) and unblocks every logged-in feature that follows (profile, dashboard, expenses).

## Depends on
- Step 01 — Database setup (`users` table, `get_db()`)
- Step 02 — Registration (`create_user()`, `app.secret_key`, global flash-message block in `base.html`)

## Routes
- `GET /login` — render login form — public (already exists as stub, upgrade it)
- `POST /login` — verify credentials, set session, redirect to landing page — public
- `GET /logout` — clear session, redirect to login page — logged-in (already exists as placeholder, replace it)

## Database changes
No new tables or columns. The existing `users` table covers all requirements.

A new DB helper must be added to `database/db.py`:
- `get_user_by_email(email)` — parameterised `SELECT` on `users` by email; returns the row (`sqlite3.Row`) or `None` if not found. The caller verifies the password with `werkzeug.security.check_password_hash`.

## Templates
- **Create:** none
- **Modify:** `templates/login.html`
  - Change the form `action` to `url_for('login')` (currently hardcoded `/login`)
  - Remove the now-dead `{% if error %}` block — errors flow through the global flash block added in Step 02
  - Keep all existing visual design
- **Modify:** `templates/base.html`
  - Make the navbar session-aware:
    - Logged out (no `session['user_id']`): keep the current "Sign in" and "Get started" links
    - Logged in: show the user's name (from `session['user_name']`) and a "Log out" link via `url_for('logout')`
  - Keep all existing visual design and classes

## Files to change
- `app.py` — upgrade `login()` to handle `GET` and `POST`; replace the `logout()` placeholder; import `session` and `check_password_hash`
- `database/db.py` — add `get_user_by_email()` helper
- `templates/login.html` — wire form action to `url_for`, remove dead error block
- `templates/base.html` — session-aware navbar

## Files to create
None.

## New dependencies
No new dependencies. Uses Flask's built-in `session` and `werkzeug.security.check_password_hash` (already installed).

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only — never use f-strings in SQL
- Passwords hashed with werkzeug — verify with `check_password_hash(user["password_hash"], password)`; never compare plaintext
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Use `url_for()` for every internal link — never hardcode URLs
- On successful login, store exactly `session['user_id']` and `session['user_name']` — never store the password or hash in the session
- Use the same generic error message — "Invalid email or password." — for both unknown email and wrong password, so the form does not reveal which emails are registered
- Server-side validation must check:
  1. Both fields are non-empty ("All fields are required.")
  2. Email exists AND password matches (generic error above; catch both cases the same way)
- On any validation failure, re-render the form with a flashed error message (`error` category) — do not redirect
- On successful login, flash a success message and `redirect(url_for('landing'))` (the dashboard does not exist yet; a later step will retarget this)
- If an already-logged-in user visits `GET /login`, redirect them to `url_for('landing')` instead of showing the form
- `logout` must clear the session with `session.clear()`, flash "You have been logged out.", and `redirect(url_for('login'))`; logging out when not logged in must not error — just redirect
- Use `abort(405)` if an unsupported HTTP method reaches the route

## Definition of done
- [ ] `GET /login` renders the login form without errors
- [ ] Submitting valid credentials (e.g. demo@spendly.com / demo123) sets `session['user_id']` and redirects to `/` with a success flash
- [ ] After login, the navbar shows the user's name and a "Log out" link instead of "Sign in / Get started"
- [ ] Submitting a wrong password re-renders the form with "Invalid email or password." — no session is created
- [ ] Submitting an unregistered email shows the same generic error message (no email enumeration)
- [ ] Submitting with any empty field re-renders the form with a validation error
- [ ] Visiting `/login` while already logged in redirects to `/`
- [ ] `GET /logout` clears the session, flashes a message, and redirects to `/login`; the navbar reverts to "Sign in / Get started"
- [ ] Visiting `/logout` while not logged in redirects to `/login` without error
- [ ] A user registered in Step 02 can immediately log in with the credentials they registered with
