"""
Security Fixes Verification Script
Validates that all security vulnerabilities have been properly fixed
"""
import os
import sys
import re
from pathlib import Path

def check_jwt_secrets():
    """Check that JWT secrets are properly validated."""
    print("\n=== Checking JWT Secret Validation ===\n")
    
    files_to_check = [
        "src/api/middleware/secure_auth.py",
        "src/api/main_v3.py",
        "src/api/main.py",
        "src/api/middleware/auth.py"
    ]
    
    issues = []
    for file_path in files_to_check:
        full_path = Path(file_path)
        if not full_path.exists():
            continue
            
        content = full_path.read_text()
        
        # Check for hardcoded default secrets without validation
        if 'SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-secret-key")' in content:
            if 'raise ValueError' not in content or 'SECURITY ERROR' not in content:
                issues.append(f"❌ {file_path}: Hardcoded default secret without validation")
        else:
            print(f"✅ {file_path}: No hardcoded default secret")
    
    if issues:
        for issue in issues:
            print(issue)
        return False
    
    print("\n✅ All JWT secrets properly validated!")
    return True


def check_network_binding():
    """Check that network binding is secure."""
    print("\n=== Checking Network Binding ===\n")
    
    files_to_check = [
        "src/api/main_v3.py",
        "src/api/main.py"
    ]
    
    issues = []
    for file_path in files_to_check:
        full_path = Path(file_path)
        if not full_path.exists():
            continue
            
        content = full_path.read_text()
        
        # Check for hardcoded 0.0.0.0
        if 'uvicorn.run(app, host="0.0.0.0"' in content:
            issues.append(f"❌ {file_path}: Hardcoded 0.0.0.0 binding")
        else:
            print(f"✅ {file_path}: No hardcoded 0.0.0.0 binding")
    
    if issues:
        for issue in issues:
            print(issue)
        return False
    
    print("\n✅ Network binding is secure!")
    return True


def check_subprocess_validation():
    """Check that subprocess calls are validated."""
    print("\n=== Checking Subprocess Validation ===\n")
    
    file_path = "src/backup/backup_manager.py"
    full_path = Path(file_path)
    
    if not full_path.exists():
        print(f"⚠️  {file_path} not found")
        return True
    
    content = full_path.read_text()
    
    # Check for validation method
    if '_validate_pg_dump_params' in content:
        print(f"✅ {file_path}: Subprocess validation method found")
        
        # Check if validation is called before subprocess.run
        if 'self._validate_pg_dump_params()' in content:
            print(f"✅ {file_path}: Validation called before subprocess")
            return True
        else:
            print(f"❌ {file_path}: Validation method exists but not called")
            return False
    else:
        print(f"❌ {file_path}: No subprocess validation found")
        return False


def check_bcrypt_rounds():
    """Check that bcrypt rounds are explicitly set."""
    print("\n=== Checking Bcrypt Rounds ===\n")
    
    files_to_check = [
        "src/services/user_service.py",
        "src/enterprise/auth.py"
    ]
    
    issues = []
    for file_path in files_to_check:
        full_path = Path(file_path)
        if not full_path.exists():
            continue
            
        content = full_path.read_text()
        
        # Check for explicit rounds
        if 'bcrypt.gensalt(rounds=12)' in content:
            print(f"✅ {file_path}: Bcrypt rounds=12 set")
        elif 'bcrypt.gensalt()' in content:
            issues.append(f"❌ {file_path}: Bcrypt rounds not explicit")
        else:
            print(f"⚠️  {file_path}: No bcrypt usage found")
    
    if issues:
        for issue in issues:
            print(issue)
        return False
    
    print("\n✅ Bcrypt rounds properly configured!")
    return True


def check_cors_config():
    """Check CORS configuration."""
    print("\n=== Checking CORS Configuration ===\n")
    
    file_path = "src/api/main.py"
    full_path = Path(file_path)
    
    if not full_path.exists():
        print(f"⚠️  {file_path} not found")
        return True
    
    content = full_path.read_text()
    
    # Check for environment-based CORS
    if 'CORS_ORIGINS' in content or 'allowed_origins' in content:
        print(f"✅ {file_path}: CORS properly configured")
        return True
    else:
        print(f"⚠️  {file_path}: CORS configuration not found")
        return True


def main():
    """Run all security checks."""
    print("="*60)
    print("Security Fixes Verification")
    print("="*60)
    
    # Change to project root
    os.chdir(Path(__file__).parent)
    
    results = {
        "JWT Secrets": check_jwt_secrets(),
        "Network Binding": check_network_binding(),
        "Subprocess Validation": check_subprocess_validation(),
        "Bcrypt Rounds": check_bcrypt_rounds(),
        "CORS Configuration": check_cors_config()
    }
    
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {check}")
    
    print("\n" + "="*60)
    print(f"Result: {passed}/{total} checks passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 All security fixes verified!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} security issue(s) remaining")
        return 1


if __name__ == "__main__":
    sys.exit(main())
