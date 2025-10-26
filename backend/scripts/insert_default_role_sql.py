#!/usr/bin/env python3
"""Insert default User role via raw SQL to avoid ORM relationship issues."""

import psycopg2

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/zerotrust_iam"

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

try:
    # Insert default User role
    cursor.execute(
        """
        INSERT INTO role (id, name, display_name, description, permissions, is_system_role, is_active, version)
        VALUES (gen_random_uuid(), 'User', 'User', 'Standard user with basic permissions',
                '["read_own_data", "update_own_profile"]', true, true, 1)
        ON CONFLICT (name) DO NOTHING
        RETURNING name;
    """
    )

    result = cursor.fetchone()
    if result:
        print(f"[+] Created role: {result[0]}")
    else:
        print("[*] Role 'User' already exists")

    conn.commit()
    print("[+] Success!")

except Exception as e:
    print(f"[!] Error: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()
