import argparse
import asyncio
import secrets
import sys

from sqlalchemy.future import select

from app.core.config import settings
from app.db.session import SessionLocal
from app.domain.auth import PrincipalType, Role
from app.models.principal import PrincipalDB
from app.services.auth_service import AuthService


async def bootstrap_admin():
    print("Bootstrapping local admin credential...")
    
    # Check if a database connection can be established
    if not settings.sqlalchemy_database_uri:
        print("Error: Database URI is not configured.")
        sys.exit(1)
        
    async with SessionLocal() as session:
        # Check if an admin already exists
        stmt = select(PrincipalDB).where(
            PrincipalDB.roles.contains([Role.ADMIN.value]),
            PrincipalDB.is_active == True
        )
        result = await session.execute(stmt)
        admin = result.scalars().first()
        
        if admin:
            print("An active admin credential already exists.")
            print("For security reasons, bootstrap-admin will not generate a new key.")
            sys.exit(0)
            
        # Generate a new secure API key
        raw_api_key = f"aegis-{secrets.token_urlsafe(32)}"
        key_hash = AuthService.hash_api_key(raw_api_key)
        
        # Create the new principal
        new_admin = PrincipalDB(
            name="Local Admin",
            principal_type=PrincipalType.ADMIN.value,
            api_key_hash=key_hash,
            roles=[Role.ADMIN.value],
            is_active=True
        )
        session.add(new_admin)
        await session.commit()
        
        print("\n" + "=" * 60)
        print("SUCCESS: Local admin credential bootstrapped.")
        print("=" * 60)
        print("API Key: ")
        print(raw_api_key)
        print("\nIMPORTANT: This key has been printed exactly once.")
        print("Copy it now. It is NOT stored in plaintext anywhere.")
        print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description="Aegis Security Engine CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # bootstrap-admin command
    subparsers.add_parser("bootstrap-admin", help="Bootstrap a local admin credential")
    
    args = parser.parse_args()
    
    if args.command == "bootstrap-admin":
        asyncio.run(bootstrap_admin())

if __name__ == "__main__":
    main()
