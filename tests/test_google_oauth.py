import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from main import app
from services.google_oauth_service import GoogleOAuthService
from schemas.auth import GoogleAuthRequest, GoogleUserInfo


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_google_user_info():
    return GoogleUserInfo(
        sub="google_user_123",
        email="test@example.com",
        email_verified=True,
        name="Test User",
        given_name="Test",
        family_name="User",
        picture="https://example.com/picture.jpg",
        locale="en",
    )


@pytest.fixture
def mock_google_auth_request():
    return GoogleAuthRequest(
        id_token="mock_google_id_token", access_token="mock_google_access_token"
    )


class TestGoogleOAuth:
    """Test cases for Google OAuth functionality"""

    @pytest.mark.asyncio
    async def test_verify_google_token_success(self, mock_google_user_info):
        """Test successful Google token verification"""
        with patch("google.oauth2.id_token.verify_oauth2_token") as mock_verify:
            mock_verify.return_value = {
                "sub": mock_google_user_info.sub,
                "email": mock_google_user_info.email,
                "email_verified": mock_google_user_info.email_verified,
                "name": mock_google_user_info.name,
                "given_name": mock_google_user_info.given_name,
                "family_name": mock_google_user_info.family_name,
                "picture": mock_google_user_info.picture,
                "locale": mock_google_user_info.locale,
                "exp": 9999999999,  # Future timestamp
                "aud": "test_client_id",
                "iss": "accounts.google.com",
            }

            service = GoogleOAuthService(
                db=AsyncMock(),
                user_service=AsyncMock(),
                token_service=AsyncMock(),
                audit_service=AsyncMock(),
                cache_service=AsyncMock(),
            )

            result = await service.verify_google_token("mock_token")

            assert result.sub == mock_google_user_info.sub
            assert result.email == mock_google_user_info.email
            assert result.email_verified == mock_google_user_info.email_verified

    @pytest.mark.asyncio
    async def test_verify_google_token_expired(self):
        """Test Google token verification with expired token"""
        with patch("google.oauth2.id_token.verify_oauth2_token") as mock_verify:
            mock_verify.return_value = {
                "exp": 0,  # Past timestamp
                "aud": "test_client_id",
                "iss": "accounts.google.com",
            }

            service = GoogleOAuthService(
                db=AsyncMock(),
                user_service=AsyncMock(),
                token_service=AsyncMock(),
                audit_service=AsyncMock(),
                cache_service=AsyncMock(),
            )

            with pytest.raises(Exception):
                await service.verify_google_token("mock_token")

    @pytest.mark.asyncio
    async def test_authenticate_google_user_new_user(
        self, mock_google_auth_request, mock_google_user_info
    ):
        """Test Google authentication for new user"""
        mock_user_service = AsyncMock()
        mock_user_service.get_by_email.return_value = None
        mock_user_service.create_google_user.return_value = MagicMock(
            id=1,
            email=mock_google_user_info.email,
            full_name=mock_google_user_info.name,
            is_active=True,
            google_id=mock_google_user_info.sub,
            to_dict=lambda: {
                "id": 1,
                "email": mock_google_user_info.email,
                "full_name": mock_google_user_info.name,
                "is_active": True,
                "google_id": mock_google_user_info.sub,
            },
        )

        with patch.object(
            GoogleOAuthService,
            "verify_google_token",
            return_value=mock_google_user_info,
        ):
            service = GoogleOAuthService(
                db=AsyncMock(),
                user_service=mock_user_service,
                token_service=AsyncMock(),
                audit_service=AsyncMock(),
                cache_service=AsyncMock(),
            )

            result = await service.authenticate_google_user(
                mock_google_auth_request, "127.0.0.1"
            )

            assert "access_token" in result
            assert "refresh_token" in result
            assert "user" in result
            assert result["user"]["email"] == mock_google_user_info.email

    @pytest.mark.asyncio
    async def test_authenticate_google_user_existing_user(
        self, mock_google_auth_request, mock_google_user_info
    ):
        """Test Google authentication for existing user"""
        mock_user = MagicMock(
            id=1,
            email=mock_google_user_info.email,
            full_name=mock_google_user_info.name,
            is_active=True,
            google_id=None,  # Not linked yet
            to_dict=lambda: {
                "id": 1,
                "email": mock_google_user_info.email,
                "full_name": mock_google_user_info.name,
                "is_active": True,
                "google_id": None,
            },
        )

        mock_user_service = AsyncMock()
        mock_user_service.get_by_email.return_value = mock_user
        mock_user_service.link_google_account.return_value = True
        mock_user_service.update_last_login.return_value = True

        with patch.object(
            GoogleOAuthService,
            "verify_google_token",
            return_value=mock_google_user_info,
        ):
            service = GoogleOAuthService(
                db=AsyncMock(),
                user_service=mock_user_service,
                token_service=AsyncMock(),
                audit_service=AsyncMock(),
                cache_service=AsyncMock(),
            )

            result = await service.authenticate_google_user(
                mock_google_auth_request, "127.0.0.1"
            )

            assert "access_token" in result
            assert "refresh_token" in result
            assert "user" in result
            mock_user_service.link_google_account.assert_called_once_with(
                1, mock_google_user_info.sub
            )

    def test_get_google_auth_url(self):
        """Test Google OAuth URL generation"""
        service = GoogleOAuthService(
            db=AsyncMock(),
            user_service=AsyncMock(),
            token_service=AsyncMock(),
            audit_service=AsyncMock(),
            cache_service=AsyncMock(),
        )

        auth_url = service.get_google_auth_url("test_state")

        assert "accounts.google.com" in auth_url
        assert "client_id" in auth_url
        assert "redirect_uri" in auth_url
        assert "response_type=code" in auth_url
        assert "scope=openid+email+profile" in auth_url

    @pytest.mark.asyncio
    async def test_exchange_code_for_tokens(self):
        """Test exchanging authorization code for tokens"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "mock_access_token",
            "id_token": "mock_id_token",
            "refresh_token": "mock_refresh_token",
        }

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            service = GoogleOAuthService(
                db=AsyncMock(),
                user_service=AsyncMock(),
                token_service=AsyncMock(),
                audit_service=AsyncMock(),
                cache_service=AsyncMock(),
            )

            result = await service.exchange_code_for_tokens("mock_code")

            assert result["access_token"] == "mock_access_token"
            assert result["id_token"] == "mock_id_token"
            assert result["refresh_token"] == "mock_refresh_token"


class TestGoogleOAuthEndpoints:
    """Test cases for Google OAuth API endpoints"""

    def test_get_google_auth_url_endpoint(self, client):
        """Test GET /auth/google/auth-url endpoint"""
        response = client.get("/auth/google/auth-url?state=test_state")
        assert response.status_code == 200
        assert "auth_url" in response.json()

    def test_google_auth_endpoint_missing_token(self, client):
        """Test POST /auth/google endpoint with missing token"""
        response = client.post("/auth/google", json={})
        assert response.status_code == 422  # Validation error

    def test_google_callback_endpoint_missing_code(self, client):
        """Test POST /auth/google/callback endpoint with missing code"""
        response = client.post("/auth/google/callback", json={})
        assert response.status_code == 422  # Validation error
