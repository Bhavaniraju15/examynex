# Environment Variables Setup

## Quick Setup

The app will work **without** a `.env` file (it uses defaults), but it's **recommended** to create one for better security and configuration.

## Create .env File

1. **Copy the example file:**
   ```bash
   cd backend
   copy .env.example .env
   ```
   (On Linux/Mac: `cp .env.example .env`)

2. **Edit `.env` file** and update the values as needed.

## Environment Variables

### Required (but has defaults)

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./exam.db` | Database connection string |
| `SECRET_KEY` | `EXAMYNEX_SECRET_KEY_CHANGE_IN_PRODUCTION` | JWT secret key (CHANGE THIS!) |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Token expiration time |
| `CORS_ORIGINS` | `*` | Allowed CORS origins (comma-separated) |

### Database Configuration

**SQLite (Default - No setup needed):**
```
DATABASE_URL=sqlite:///./exam.db
```

**PostgreSQL (Optional):**
```
DATABASE_URL=postgresql://username:password@localhost:5432/examynex
```

### Security

**IMPORTANT:** Change the `SECRET_KEY` in production!

Generate a secure secret key:
```python
import secrets
print(secrets.token_urlsafe(32))
```

Or use:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### CORS Configuration

**Development (allow all):**
```
CORS_ORIGINS=*
```

**Production (specific domains):**
```
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

## Example .env File

```env
# Database
DATABASE_URL=sqlite:///./exam.db

# JWT
SECRET_KEY=your-super-secret-key-here-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS
CORS_ORIGINS=*
```

## Notes

- The `.env` file is automatically loaded by `python-dotenv`
- The `.env` file is in `.gitignore` (won't be committed to git)
- Always use `.env.example` as a template
- Never commit your actual `.env` file with real secrets!

