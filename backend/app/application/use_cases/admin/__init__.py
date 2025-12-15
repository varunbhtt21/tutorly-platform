"""Admin use cases."""

from .reject_instructor import RejectInstructorUseCase
from .suspend_instructor import SuspendInstructorUseCase
from .suspend_user import SuspendUserUseCase
from .ban_user import BanUserUseCase
from .activate_user import ActivateUserUseCase
from .get_pending_instructors import GetPendingInstructorsUseCase
from .get_admin_dashboard_stats import GetAdminDashboardStatsUseCase

__all__ = [
    "RejectInstructorUseCase",
    "SuspendInstructorUseCase",
    "SuspendUserUseCase",
    "BanUserUseCase",
    "ActivateUserUseCase",
    "GetPendingInstructorsUseCase",
    "GetAdminDashboardStatsUseCase",
]
