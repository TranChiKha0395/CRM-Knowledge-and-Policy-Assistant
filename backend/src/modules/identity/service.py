"""Identity & RBAC domain services (SEC 01)."""

from typing import NoReturn

from fastapi import HTTPException, status

from src.modules.identity.schemas import PermissionCheckResponse, UserProfileResponse
from src.shared.auth import AuthenticatedUser, check_policy_audience


class IdentityService:
    """Handles organizational authentication context and audience permission evaluation."""

    def get_profile(self, user: AuthenticatedUser) -> UserProfileResponse:
        """Serialize effective organizational identity and least-privilege grants."""
        return UserProfileResponse(
            user_id=user.user_id,
            email=user.email,
            roles=sorted(user.roles, key=lambda r: r.value),
            company=user.company,
            branch=user.branch,
            allowed_audiences=sorted(user.allowed_audiences),
        )

    def check_audience(
        self, user: AuthenticatedUser, required_audiences: list[str]
    ) -> PermissionCheckResponse:
        """Enforce uniform least-privilege audience matching."""
        allowed = check_policy_audience(user, required_audiences)
        return PermissionCheckResponse(
            allowed=allowed,
            user_id=user.user_id,
            effective_roles=sorted(user.roles, key=lambda r: r.value),
        )

    def exchange_token_not_configured(self) -> NoReturn:
        """Fail closed until organizational OIDC/SSO provider integration in Gate G1."""
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Organizational SSO/OIDC token exchange not configured (Gate G1).",
        )
