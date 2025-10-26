#!/usr/bin/env python3
"""
Initialize default roles in the database.

This script creates the default system roles (User, Admin, Analyst, Viewer)
if they don't already exist.
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal
from app.models.role import Role


def init_default_roles():
    """Create default system roles if they don't exist."""
    db = SessionLocal()

    try:
        default_roles = [
            {
                "name": "User",
                "display_name": "User",
                "description": "Standard user with basic permissions",
                "permissions": '["read_own_data", "update_own_profile"]',
                "is_system_role": True,
                "is_active": True,
            },
            {
                "name": "Admin",
                "display_name": "Administrator",
                "description": "Full system administrator with all permissions",
                "permissions": '["*"]',
                "is_system_role": True,
                "is_active": True,
            },
            {
                "name": "Analyst",
                "display_name": "Security Analyst",
                "description": "Security analyst with scan and policy management permissions",
                "permissions": '["read", "scan", "analyze", "create_policies", "update_policies"]',
                "is_system_role": True,
                "is_active": True,
            },
            {
                "name": "Viewer",
                "display_name": "Viewer",
                "description": "Read-only access to reports and policies",
                "permissions": '["read"]',
                "is_system_role": True,
                "is_active": True,
            },
        ]

        created_count = 0
        for role_data in default_roles:
            # Check if role already exists
            existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()

            if not existing_role:
                role = Role(**role_data)
                db.add(role)
                created_count += 1
                print(f"[+] Created role: {role_data['name']}")
            else:
                print(f"[*] Role already exists: {role_data['name']}")

        db.commit()
        print(f"\n[+] Initialization complete. Created {created_count} new roles.")

    except Exception as e:
        print(f"[!] Error initializing roles: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("INITIALIZING DEFAULT ROLES")
    print("=" * 60)
    init_default_roles()
