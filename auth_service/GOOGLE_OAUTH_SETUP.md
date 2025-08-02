# Google OAuth Setup Guide

This guide explains how to set up and use Google OAuth authentication in the Food & Fast E-commerce application.

## Prerequisites

1. Google Cloud Console account
2. A Google Cloud Project
3. OAuth 2.0 credentials configured

## Google Cloud Console Setup

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API and Google OAuth2 API

### 2. Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" user type
3. Fill in the required information:
   - App name: "Food & Fast E-commerce"
   - User support email: Your email
   - Developer contact information: Your email
4. Add scopes:
   - `openid`
   - `email`
   - `profile`
5. Add test users (for development)

### 3. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Web application"
4. Add authorized redirect URIs:
   - `http://localhost:3000/auth/google/callback` (development)
   - `https://yourdomain.com/auth/google/callback` (production)
5. Copy the Client ID and Client Secret

## Environment Configuration

Add the following environment variables to your `.env` file:

```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback
```

## API Endpoints

### 1. Get Google OAuth URL

**GET** `/auth/google/auth-url`

Get the Google OAuth authorization URL.

**Query Parameters:**
- `state` (optional): State parameter for CSRF protection

**Response:**
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?..."
}
```

### 2. Google OAuth Authentication

**POST** `/auth/google`

Authenticate or register a user with Google OAuth.

**Request Body:**
```json
{
  "id_token": "google_id_token_here",
  "access_token": "google_access_token_here" // optional
}
```

**Response:**
```json
{
  "access_token": "jwt_access_token",
  "refresh_token": "jwt_refresh_token",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "google_id": "google_user_id"
  }
}
```

### 3. Google OAuth Callback

**POST** `/auth/google/callback`

Handle Google OAuth callback with authorization code.

**Request Body:**
```json
{
  "code": "authorization_code_from_google",
  "state": "state_parameter" // optional
}
```

## Frontend Integration

### 1. Google Sign-In Button

```javascript
// Load Google Sign-In API
<script src="https://accounts.google.com/gsi/client" async defer></script>

// Initialize Google Sign-In
google.accounts.id.initialize({
  client_id: 'YOUR_GOOGLE_CLIENT_ID',
  callback: handleCredentialResponse
});

// Handle the response
function handleCredentialResponse(response) {
  // Send the ID token to your backend
  fetch('/auth/google', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      id_token: response.credential
    })
  })
  .then(response => response.json())
  .then(data => {
    // Store tokens and redirect
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    window.location.href = '/dashboard';
  });
}
```

### 2. Redirect Flow (Alternative)

```javascript
// Redirect to Google OAuth
function signInWithGoogle() {
  fetch('/auth/google/auth-url')
    .then(response => response.json())
    .then(data => {
      window.location.href = data.auth_url;
    });
}

// Handle callback
function handleCallback() {
  const urlParams = new URLSearchParams(window.location.search);
  const code = urlParams.get('code');
  const state = urlParams.get('state');
  
  fetch('/auth/google/callback', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ code, state })
  })
  .then(response => response.json())
  .then(data => {
    // Store tokens and redirect
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    window.location.href = '/dashboard';
  });
}
```

## Database Migration

Run the database migration to add Google OAuth fields:

```bash
cd auth_service
alembic upgrade head
```

## Security Considerations

1. **Token Verification**: Always verify Google ID tokens on the server side
2. **HTTPS**: Use HTTPS in production for all OAuth flows
3. **State Parameter**: Use state parameter to prevent CSRF attacks
4. **Token Storage**: Store tokens securely (httpOnly cookies recommended)
5. **Scope Limitation**: Only request necessary scopes
6. **Error Handling**: Implement proper error handling for OAuth failures

## Testing

### 1. Test Google OAuth Flow

1. Start the auth service
2. Use the Google Sign-In button or redirect flow
3. Verify user creation/authentication
4. Check token generation and storage

### 2. Test Error Scenarios

- Invalid Google tokens
- Expired tokens
- Network failures
- Missing required fields

## Troubleshooting

### Common Issues

1. **"Invalid client" error**: Check your Google Client ID
2. **"Redirect URI mismatch"**: Verify redirect URIs in Google Console
3. **"Invalid token" error**: Ensure proper token verification
4. **Database errors**: Run migrations and check database connection

### Debug Mode

Enable debug logging by setting the log level to DEBUG in your environment:

```env
LOG_LEVEL=DEBUG
```

## Production Deployment

1. Update redirect URIs in Google Console
2. Use HTTPS for all OAuth endpoints
3. Set proper CORS headers
4. Implement rate limiting
5. Monitor OAuth usage and errors
6. Set up proper logging and monitoring

## Support

For issues related to Google OAuth:

1. Check Google Cloud Console logs
2. Review application logs
3. Verify environment variables
4. Test with Google's OAuth playground 