---
name: spotify-api-migration-2026
description: Spotify deprecated /users/{id}/playlists endpoint; use /me/playlists instead
metadata:
  type: project
---

## Spotify API Migration — Feb 2026

**Issue:** `user_playlist_create()` returns 403 Forbidden when creating playlists.

**Root Cause:** Spotify deprecated the `/v1/users/{user_id}/playlists` endpoint (likely as part of their Feb 2026 API migration). The endpoint now returns 403 for all requests, even with valid tokens and correct scopes.

**Solution:** Use `current_user_playlist_create()` instead, which calls `/v1/me/playlists` (the current supported endpoint).

**Verification:**
- `/v1/users/{user_id}/playlists` POST → 403 Forbidden (no error details)
- `/v1/me/playlists` POST → 201 Created (works)
- Authentication is valid (current_user() works, token has correct scope)

**Why:** The `/me` endpoint implicitly uses the authenticated user instead of requiring a user ID parameter. This is the modern Spotify API pattern.

**Applied In:** commit 3588b7c (May 22, 2026)
