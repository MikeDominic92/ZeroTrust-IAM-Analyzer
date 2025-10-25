#!/usr/bin/env python3
"""
Database Schema Verification Script
Verifies PostgreSQL database schema for ZeroTrust IAM Analyzer
Checks tables, columns, constraints, indexes, and foreign keys
"""

import os
import sys
from typing import List, Tuple, Dict, Any
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from dotenv import load_dotenv
except ImportError as e:
    print(f"[!] Import error: {e}")
    print("[!] Install requirements: pip install psycopg2-binary python-dotenv")
    sys.exit(1)


class SchemaVerifier:
    """PostgreSQL schema verification utility"""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.conn = None
        self.cursor = None
        self.failures: List[str] = []

    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.database_url)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            print("[+] Database connection established")
            return True
        except Exception as e:
            print(f"[!] Database connection failed: {e}")
            return False

    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def verify_table_exists(self, table_name: str) -> bool:
        """Verify table exists in database"""
        query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = %s
            );
        """
        self.cursor.execute(query, (table_name,))
        result = self.cursor.fetchone()
        return result['exists']

    def verify_tables(self) -> bool:
        """Verify all required tables exist"""
        print("\n" + "="*60)
        print("TABLE EXISTENCE VERIFICATION")
        print("="*60)

        required_tables = [
            'user',
            'scan',
            'policy',
            'recommendation',
            'role',
            'session',
            'user_roles'
        ]

        all_exist = True
        for table in required_tables:
            exists = self.verify_table_exists(table)
            status = "[+]" if exists else "[!]"
            print(f"{status} Table '{table}': {'EXISTS' if exists else 'MISSING'}")
            if not exists:
                self.failures.append(f"Missing table: {table}")
                all_exist = False

        return all_exist

    def get_table_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """Get column information for a table"""
        query = """
            SELECT
                column_name,
                data_type,
                character_maximum_length,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = %s
            ORDER BY ordinal_position;
        """
        self.cursor.execute(query, (table_name,))
        return self.cursor.fetchall()

    def verify_role_table(self) -> bool:
        """Verify role table structure"""
        print("\n" + "="*60)
        print("ROLE TABLE VERIFICATION")
        print("="*60)

        expected_columns = {
            'id': {'type': 'integer', 'nullable': 'NO', 'default': 'nextval'},
            'name': {'type': 'character varying', 'nullable': 'NO'},
            'description': {'type': 'text', 'nullable': 'YES'},
            'created_at': {'type': 'timestamp without time zone', 'nullable': 'NO', 'default': 'now()'}
        }

        return self._verify_table_structure('role', expected_columns)

    def verify_session_table(self) -> bool:
        """Verify session table structure"""
        print("\n" + "="*60)
        print("SESSION TABLE VERIFICATION")
        print("="*60)

        expected_columns = {
            'id': {'type': 'uuid', 'nullable': 'NO', 'default': 'gen_random_uuid()'},
            'user_id': {'type': 'integer', 'nullable': 'NO'},
            'token': {'type': 'character varying', 'nullable': 'NO'},
            'expires_at': {'type': 'timestamp without time zone', 'nullable': 'NO'},
            'created_at': {'type': 'timestamp without time zone', 'nullable': 'NO', 'default': 'now()'},
            'last_activity': {'type': 'timestamp without time zone', 'nullable': 'NO', 'default': 'now()'}
        }

        return self._verify_table_structure('session', expected_columns)

    def verify_user_roles_table(self) -> bool:
        """Verify user_roles junction table structure"""
        print("\n" + "="*60)
        print("USER_ROLES TABLE VERIFICATION")
        print("="*60)

        expected_columns = {
            'user_id': {'type': 'integer', 'nullable': 'NO'},
            'role_id': {'type': 'integer', 'nullable': 'NO'},
            'assigned_at': {'type': 'timestamp without time zone', 'nullable': 'NO', 'default': 'now()'}
        }

        return self._verify_table_structure('user_roles', expected_columns)

    def _verify_table_structure(self, table_name: str, expected_columns: Dict) -> bool:
        """Verify table structure matches expected schema"""
        columns = self.get_table_columns(table_name)

        if not columns:
            print(f"[!] No columns found for table '{table_name}'")
            self.failures.append(f"No columns in {table_name} table")
            return False

        actual_columns = {col['column_name']: col for col in columns}
        all_valid = True

        for col_name, expected in expected_columns.items():
            if col_name not in actual_columns:
                print(f"[!] Missing column: {col_name}")
                self.failures.append(f"{table_name}.{col_name} missing")
                all_valid = False
                continue

            actual = actual_columns[col_name]

            # Verify data type
            if expected['type'] not in actual['data_type']:
                print(f"[!] Column {col_name}: type mismatch (expected {expected['type']}, got {actual['data_type']})")
                self.failures.append(f"{table_name}.{col_name} type mismatch")
                all_valid = False
            else:
                print(f"[+] Column {col_name}: {actual['data_type']} - OK")

            # Verify nullable constraint
            if 'nullable' in expected:
                if expected['nullable'] != actual['is_nullable']:
                    print(f"[!] Column {col_name}: nullable mismatch (expected {expected['nullable']}, got {actual['is_nullable']})")
                    self.failures.append(f"{table_name}.{col_name} nullable mismatch")
                    all_valid = False

            # Verify default value (partial match for functions like nextval, gen_random_uuid)
            if 'default' in expected:
                default_val = actual['column_default'] or ''
                if expected['default'] not in default_val:
                    print(f"[!] Column {col_name}: default mismatch (expected '{expected['default']}' in '{default_val}')")
                    self.failures.append(f"{table_name}.{col_name} default mismatch")
                    all_valid = False

        return all_valid

    def verify_foreign_keys(self) -> bool:
        """Verify foreign key constraints"""
        print("\n" + "="*60)
        print("FOREIGN KEY VERIFICATION")
        print("="*60)

        query = """
            SELECT
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name,
                tc.constraint_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public'
            AND tc.table_name IN ('session', 'user_roles');
        """

        self.cursor.execute(query)
        fks = self.cursor.fetchall()

        expected_fks = [
            {'table': 'session', 'column': 'user_id', 'ref_table': 'user', 'ref_column': 'id'},
            {'table': 'user_roles', 'column': 'user_id', 'ref_table': 'user', 'ref_column': 'id'},
            {'table': 'user_roles', 'column': 'role_id', 'ref_table': 'role', 'ref_column': 'id'}
        ]

        all_valid = True
        for expected in expected_fks:
            found = False
            for fk in fks:
                if (fk['table_name'] == expected['table'] and
                    fk['column_name'] == expected['column'] and
                    fk['foreign_table_name'] == expected['ref_table'] and
                    fk['foreign_column_name'] == expected['ref_column']):
                    found = True
                    print(f"[+] FK {expected['table']}.{expected['column']} -> {expected['ref_table']}.{expected['ref_column']} - OK")
                    break

            if not found:
                print(f"[!] Missing FK: {expected['table']}.{expected['column']} -> {expected['ref_table']}.{expected['ref_column']}")
                self.failures.append(f"Missing FK: {expected['table']}.{expected['column']}")
                all_valid = False

        return all_valid

    def verify_indexes(self) -> bool:
        """Verify indexes exist on key columns"""
        print("\n" + "="*60)
        print("INDEX VERIFICATION")
        print("="*60)

        query = """
            SELECT
                tablename,
                indexname,
                indexdef
            FROM pg_indexes
            WHERE schemaname = 'public'
            AND tablename IN ('role', 'session', 'user_roles')
            ORDER BY tablename, indexname;
        """

        self.cursor.execute(query)
        indexes = self.cursor.fetchall()

        # Expected indexes (primary keys and foreign keys should have indexes)
        expected_patterns = [
            ('role', 'PRIMARY KEY'),  # id primary key
            ('session', 'PRIMARY KEY'),  # id primary key
            ('session', 'user_id'),  # foreign key index
            ('user_roles', 'PRIMARY KEY'),  # composite primary key
        ]

        all_valid = True
        for table, pattern in expected_patterns:
            found = False
            for idx in indexes:
                if idx['tablename'] == table and pattern.lower() in idx['indexdef'].lower():
                    found = True
                    print(f"[+] Index on {table} ({pattern}) - OK: {idx['indexname']}")
                    break

            if not found:
                print(f"[!] Missing index pattern on {table}: {pattern}")
                # Not treating missing indexes as hard failure, just warning

        # Display all found indexes for reference
        print("\n[*] All indexes found:")
        for idx in indexes:
            print(f"    {idx['tablename']}.{idx['indexname']}")

        return all_valid

    def run_verification(self) -> bool:
        """Run complete schema verification"""
        print("\n" + "="*60)
        print("DATABASE SCHEMA VERIFICATION")
        print("="*60)

        if not self.connect():
            return False

        try:
            # Run all verifications
            verifications = [
                ("Tables", self.verify_tables),
                ("Role Table", self.verify_role_table),
                ("Session Table", self.verify_session_table),
                ("User_Roles Table", self.verify_user_roles_table),
                ("Foreign Keys", self.verify_foreign_keys),
                ("Indexes", self.verify_indexes)
            ]

            all_passed = True
            for name, verify_func in verifications:
                try:
                    if not verify_func():
                        all_passed = False
                except Exception as e:
                    print(f"[!] Error during {name} verification: {e}")
                    self.failures.append(f"{name} verification failed: {e}")
                    all_passed = False

            # Print summary
            print("\n" + "="*60)
            print("VERIFICATION SUMMARY")
            print("="*60)

            if all_passed and not self.failures:
                print("[+] ALL VERIFICATIONS PASSED")
                print("[+] Database schema is correct")
                return True
            else:
                print(f"[!] VERIFICATION FAILED ({len(self.failures)} issues)")
                print("\n[!] Issues found:")
                for failure in self.failures:
                    print(f"    - {failure}")
                return False

        finally:
            self.disconnect()


def main():
    """Main entry point"""
    # Load environment variables
    env_path = backend_dir / '.env'
    if not env_path.exists():
        print(f"[!] .env file not found at {env_path}")
        print("[!] Create .env with DATABASE_URL=postgresql://user:pass@host:port/db")
        sys.exit(1)

    load_dotenv(env_path)

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("[!] DATABASE_URL not found in .env file")
        sys.exit(1)

    # Run verification
    verifier = SchemaVerifier(database_url)
    success = verifier.run_verification()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
