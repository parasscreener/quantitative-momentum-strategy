#!/usr/bin/env python3
"""
AUTO-FIX SCRIPT for quantitative_momentum_strategy.py
Fixes pandas index alignment issue automatically
Run: python fix_pandas_index.py
"""

import os
import sys

def fix_pandas_index_issue():
    """Automatically fix the pandas index misalignment"""
    
    file_path = 'quantitative_momentum_strategy.py'
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        print("   Make sure you run this script in the project root directory")
        return False
    
    # Read the file
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        print(f"✅ Read file: {file_path}")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    # Apply fixes
    original_content = content
    fixes_applied = 0
    
    # FIX 1: Line with "df = pd.DataFrame(results)"
    if 'df = pd.DataFrame(results)' in content and '.reset_index(drop=True)' not in content.split('df = pd.DataFrame(results)')[1].split('\n')[0]:
        content = content.replace(
            'df = pd.DataFrame(results)',
            'df = pd.DataFrame(results).reset_index(drop=True)'
        )
        print("✅ Fix 1: Added .reset_index() after df = pd.DataFrame(results)")
        fixes_applied += 1
    
    # FIX 2: Line with "top_momentum = df[df['Momentum_Rank']"
    if "top_momentum = df[df['Momentum_Rank'] <= self.momentum_percentile]" in content:
        content = content.replace(
            "top_momentum = df[df['Momentum_Rank'] <= self.momentum_percentile]",
            "top_momentum = df[df['Momentum_Rank'] <= self.momentum_percentile].reset_index(drop=True)"
        )
        print("✅ Fix 2: Added .reset_index() after top_momentum filtering")
        fixes_applied += 1
    
    # FIX 3: Line with "portfolio = top_momentum.nlargest"
    if 'portfolio = top_momentum.nlargest(self.portfolio_size, \'Combined_Score\')' in content:
        content = content.replace(
            'portfolio = top_momentum.nlargest(self.portfolio_size, \'Combined_Score\')',
            'portfolio = top_momentum.nlargest(self.portfolio_size, \'Combined_Score\').reset_index(drop=True)'
        )
        print("✅ Fix 3: Added .reset_index() before returning portfolio")
        fixes_applied += 1
    
    # Check if changes were made
    if content == original_content:
        print("⚠️  No fixes applied - file may already be fixed or has different structure")
        print("   Please verify the fixes manually")
        return False
    
    # Write the fixed content back
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"\n✅ File updated: {file_path}")
        print(f"✅ Fixes applied: {fixes_applied}")
        return True
    except Exception as e:
        print(f"❌ Error writing file: {e}")
        return False

def verify_fix():
    """Verify the fixes were applied correctly"""
    
    file_path = 'quantitative_momentum_strategy.py'
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        checks = {
            'Fix 1': 'pd.DataFrame(results).reset_index(drop=True)',
            'Fix 2': "df[df['Momentum_Rank'] <= self.momentum_percentile].reset_index(drop=True)",
            'Fix 3': 'nlargest(self.portfolio_size, \'Combined_Score\').reset_index(drop=True)'
        }
        
        print("\n📋 Verifying fixes:")
        all_good = True
        for name, check_str in checks.items():
            if check_str in content:
                print(f"✅ {name}: Found")
            else:
                print(f"❌ {name}: NOT FOUND")
                all_good = False
        
        return all_good
    except Exception as e:
        print(f"❌ Error verifying: {e}")
        return False

def main():
    print("=" * 80)
    print("AUTOMATIC FIX: Pandas Index Alignment Issue")
    print("=" * 80)
    
    # Apply fixes
    if fix_pandas_index_issue():
        print("\n" + "=" * 80)
        # Verify fixes
        if verify_fix():
            print("\n" + "=" * 80)
            print("✅ ALL FIXES APPLIED SUCCESSFULLY!")
            print("\nNext steps:")
            print("1. Test locally: python scripts/screening.py")
            print("2. If successful, commit: git add -A && git commit -m 'Fix pandas index'")
            print("3. Push: git push")
            print("=" * 80)
            return 0
        else:
            print("\n⚠️  Verification failed - please check file manually")
            return 1
    else:
        print("\n❌ Fix could not be applied automatically")
        print("Please apply fixes manually using GITHUB_ACTIONS_FIX.md")
        return 1

if __name__ == "__main__":
    sys.exit(main())
