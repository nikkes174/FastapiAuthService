from src.auth.service import RoleService

admin_required = RoleService.require_role("admin")

staff_required = RoleService.require_any_role(["admin", "moderator"])
