# Ponytail Rules — Minimalism for AI Agents

These rules apply to all AI coding agents working on the KhanijSetu codebase.

## The Ladder

Stop at the first rung that holds:

1. **Does this need to exist?** Speculative need = skip it (YAGNI).
2. **Already in this codebase?** Reuse the helper, util, or pattern that already lives here.
3. **Does the standard library do it?** Use it.
4. **Native platform feature covers it?** Use native over a library.
5. **Already-installed dependency solves it?** Use it. Don't add a new one.
6. **Can it be one line?** One line.
7. **Only then:** the minimum code that works.

## Principles

- **Stdlib over custom** — Python's stdlib and browser APIs before npm packages.
- **Native over deps** — `<input type="date">` over a date-picker library.
- **One line over fifty** — if a decorator, built-in, or one-liner does the job, use it.
- **Never simplify away safety** — validation, error handling, security, and accessibility are never cut.
- **Name the lazy alternative** — when building something custom, comment the simpler option.

## Specifics for This Project

- Use SQLAlchemy's built-in features before adding ORMs/wrappers.
- Use FastAPI's dependency injection (`Depends`) for auth/RBAC — don't roll custom middleware.
- Use Pydantic models for validation — don't write manual validation code.
- Use Tailwind's existing utility classes — don't create custom CSS unless necessary.
- Use Recharts (already installed) for charts — don't add another charting library.
- Use react-leaflet (already installed) for maps — don't add another mapping library.

## What Is Never Simplified

- Authentication and authorization checks
- Input validation and sanitization
- Error handling and user feedback
- Database constraints and relationships
- Audit logging for mutations
- CORS and security headers
- Accessibility attributes
