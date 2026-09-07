"""secure infrastructure tables

Revision ID: eb3843103ee0
Revises: 40a359cb1b19
Create Date: 2026-09-07 17:28:13.244536

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'eb3843103ee0'
down_revision: Union[str, None] = '40a359cb1b19'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# List of internal / infrastructure tables that must never be reachable via
# Supabase PostgREST. They do not contain user-owned data; they only store
# operational metadata. We enable RLS and intentionally provide no policies
# for the anon or authenticated roles, so the API REST rejects/queries empty
# for them. The backend FastAPI service still has full access because it
# connects with the postgres role (table owner) which bypasses RLS.
INFRA_TABLES = [
    "alembic_version",
]


def upgrade() -> None:
    """
    Enable RLS on infrastructure tables and create restrictive default
    policies so they are invisible through the Supabase REST API.
    """
    for table in INFRA_TABLES:
        # Enable RLS
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY;")

        # Make sure we do not accidentally force RLS on the table owner
        # (postgres), because that would block the backend migrations too.
        op.execute(f"ALTER TABLE public.{table} NO FORCE ROW LEVEL SECURITY;")

        # Create an explicit "deny all" policy for authenticated users.
        # This policy exists so that RLS has at least one policy and the
        # default behavior becomes "deny everything" for that role.
        op.execute(f"""
            CREATE POLICY {table}_deny_all_authenticated
            ON public.{table}
            FOR ALL
            TO authenticated
            USING (false)
            WITH CHECK (false);
        """)

        # Same explicit denial for anonymous (not logged in) requests.
        op.execute(f"""
            CREATE POLICY {table}_deny_all_anon
            ON public.{table}
            FOR ALL
            TO anon
            USING (false)
            WITH CHECK (false);
        """)


def downgrade() -> None:
    """Remove the restrictive policies and disable RLS on infrastructure tables."""
    for table in INFRA_TABLES:
        op.execute(f"DROP POLICY IF EXISTS {table}_deny_all_authenticated ON public.{table};")
        op.execute(f"DROP POLICY IF EXISTS {table}_deny_all_anon ON public.{table};")
        op.execute(f"ALTER TABLE public.{table} DISABLE ROW LEVEL SECURITY;")
