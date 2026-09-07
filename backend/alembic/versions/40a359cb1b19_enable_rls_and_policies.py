"""enable rls and policies

Revision ID: 40a359cb1b19
Revises: d8ba2f4c2086
Create Date: 2026-09-01 16:19:38.777143

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '40a359cb1b19'
down_revision: Union[str, None] = 'd8ba2f4c2086'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Enable Row Level Security (RLS) on all business tables and create policies
    that isolate data per user. The backend FastAPI service connects with the
    postgres role (via the pooled DATABASE_URL) and therefore bypasses RLS.
    Direct Supabase REST/PostgREST access uses the anon/authenticated roles,
    so we lock those down to only their own rows.
    """

    # Enable RLS on every exposed table
    tables = ["users", "clients", "products", "invoices", "invoice_items"]
    for table in tables:
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY;")

    # The backend FastAPI service connects as the postgres role (table owner),
    # which bypasses RLS by default. We intentionally do NOT use FORCE ROW LEVEL
    # SECURITY so that the backend can manage all rows while direct Supabase
    # REST/PostgREST access (anon/authenticated roles) is still restricted.

    # Helper function to map a Supabase Auth uid to our internal users.id
    op.execute("""
        CREATE OR REPLACE FUNCTION public.current_app_user_id()
        RETURNS text
        LANGUAGE sql
        STABLE
        SECURITY DEFINER
        AS $$
            SELECT id::text
            FROM public.users
            WHERE supabase_uid = (select auth.uid()::text);
        $$;
    """)

    # 1. users table: users can only see/update their own profile.
    # The backend service role (postgres) bypasses RLS as table owner.
    op.execute("""
        CREATE POLICY users_select_own
        ON public.users
        FOR SELECT
        TO anon, authenticated
        USING (supabase_uid = (select auth.uid()::text));
    """)
    op.execute("""
        CREATE POLICY users_update_own
        ON public.users
        FOR UPDATE
        TO authenticated
        USING (supabase_uid = (select auth.uid()::text))
        WITH CHECK (supabase_uid = (select auth.uid()::text));
    """)

    # 2. clients table: only own clients
    op.execute("""
        CREATE POLICY clients_select_own
        ON public.clients
        FOR SELECT
        TO anon, authenticated
        USING (user_id = public.current_app_user_id());
    """)
    op.execute("""
        CREATE POLICY clients_insert_own
        ON public.clients
        FOR INSERT
        TO authenticated
        WITH CHECK (user_id = public.current_app_user_id());
    """)
    op.execute("""
        CREATE POLICY clients_update_own
        ON public.clients
        FOR UPDATE
        TO authenticated
        USING (user_id = public.current_app_user_id())
        WITH CHECK (user_id = public.current_app_user_id());
    """)
    op.execute("""
        CREATE POLICY clients_delete_own
        ON public.clients
        FOR DELETE
        TO authenticated
        USING (user_id = public.current_app_user_id());
    """)

    # 3. products table: only own products
    op.execute("""
        CREATE POLICY products_select_own
        ON public.products
        FOR SELECT
        TO anon, authenticated
        USING (user_id = public.current_app_user_id());
    """)
    op.execute("""
        CREATE POLICY products_insert_own
        ON public.products
        FOR INSERT
        TO authenticated
        WITH CHECK (user_id = public.current_app_user_id());
    """)
    op.execute("""
        CREATE POLICY products_update_own
        ON public.products
        FOR UPDATE
        TO authenticated
        USING (user_id = public.current_app_user_id())
        WITH CHECK (user_id = public.current_app_user_id());
    """)
    op.execute("""
        CREATE POLICY products_delete_own
        ON public.products
        FOR DELETE
        TO authenticated
        USING (user_id = public.current_app_user_id());
    """)

    # 4. invoices table: only own invoices
    op.execute("""
        CREATE POLICY invoices_select_own
        ON public.invoices
        FOR SELECT
        TO anon, authenticated
        USING (user_id = public.current_app_user_id());
    """)
    op.execute("""
        CREATE POLICY invoices_insert_own
        ON public.invoices
        FOR INSERT
        TO authenticated
        WITH CHECK (user_id = public.current_app_user_id());
    """)
    op.execute("""
        CREATE POLICY invoices_update_own
        ON public.invoices
        FOR UPDATE
        TO authenticated
        USING (user_id = public.current_app_user_id())
        WITH CHECK (user_id = public.current_app_user_id());
    """)
    op.execute("""
        CREATE POLICY invoices_delete_own
        ON public.invoices
        FOR DELETE
        TO authenticated
        USING (user_id = public.current_app_user_id());
    """)

    # 5. invoice_items: only rows belonging to the user's invoices
    op.execute("""
        CREATE POLICY invoice_items_select_own
        ON public.invoice_items
        FOR SELECT
        TO anon, authenticated
        USING (
            invoice_id IN (
                SELECT id FROM public.invoices
                WHERE user_id = public.current_app_user_id()
            )
        );
    """)
    op.execute("""
        CREATE POLICY invoice_items_insert_own
        ON public.invoice_items
        FOR INSERT
        TO authenticated
        WITH CHECK (
            invoice_id IN (
                SELECT id FROM public.invoices
                WHERE user_id = public.current_app_user_id()
            )
        );
    """)
    op.execute("""
        CREATE POLICY invoice_items_update_own
        ON public.invoice_items
        FOR UPDATE
        TO authenticated
        USING (
            invoice_id IN (
                SELECT id FROM public.invoices
                WHERE user_id = public.current_app_user_id()
            )
        )
        WITH CHECK (
            invoice_id IN (
                SELECT id FROM public.invoices
                WHERE user_id = public.current_app_user_id()
            )
        );
    """)
    op.execute("""
        CREATE POLICY invoice_items_delete_own
        ON public.invoice_items
        FOR DELETE
        TO authenticated
        USING (
            invoice_id IN (
                SELECT id FROM public.invoices
                WHERE user_id = public.current_app_user_id()
            )
        );
    """)


def downgrade() -> None:
    tables = ["users", "clients", "products", "invoices", "invoice_items"]

    # Drop all policies
    for table in tables:
        op.execute(f"DROP POLICY IF EXISTS {table}_select_own ON public.{table};")
        op.execute(f"DROP POLICY IF EXISTS {table}_insert_own ON public.{table};")
        op.execute(f"DROP POLICY IF EXISTS {table}_update_own ON public.{table};")
        op.execute(f"DROP POLICY IF EXISTS {table}_delete_own ON public.{table};")

    # Drop helper function
    op.execute("DROP FUNCTION IF EXISTS public.current_app_user_id();")

    # Disable RLS
    for table in tables:
        op.execute(f"ALTER TABLE public.{table} DISABLE ROW LEVEL SECURITY;")
        op.execute(f"ALTER TABLE public.{table} NO FORCE ROW LEVEL SECURITY;")
