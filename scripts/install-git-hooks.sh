#!/bin/bash

# Git hooks installation script for zhuangxiu-agent project
# Installs pre-commit and pre-push hooks to protect environment configuration

echo "🔧 Installing Git hooks for zhuangxiu-agent project..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not a git repository. Please run this script from the project root."
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p .git/hooks

# Copy hooks from shared directory
echo "📋 Copying Git hooks..."

# pre-commit hook
if [ -f "scripts/git-hooks/pre-commit" ]; then
    cp -f scripts/git-hooks/pre-commit .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit
    echo "✅ Installed pre-commit hook"
else
    echo "⚠️  Warning: scripts/git-hooks/pre-commit not found"
fi

# pre-push hook
if [ -f "scripts/git-hooks/pre-push" ]; then
    cp -f scripts/git-hooks/pre-push .git/hooks/pre-push
    chmod +x .git/hooks/pre-push
    echo "✅ Installed pre-push hook"
else
    echo "⚠️  Warning: scripts/git-hooks/pre-push not found"
fi

# Create pre-push hook if it doesn't exist in shared directory
if [ ! -f "scripts/git-hooks/pre-push" ]; then
    echo "📝 Creating pre-push hook..."
    cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash

# Git pre-push hook for zhuangxiu-agent project
# Prevents pushing dangerous changes to protected branches

echo "🔍 Running pre-push checks..."

# Get the target branch
while read local_ref local_sha remote_ref remote_sha; do
    if [ -n "$remote_ref" ]; then
        TARGET_BRANCH=$(echo "$remote_ref" | sed 's|refs/heads/||')
        break
    fi
done

# If no target branch, exit
if [ -z "$TARGET_BRANCH" ]; then
    echo "⚠️  Warning: Could not determine target branch"
    echo "✅ pre-push checks skipped."
    exit 0
fi

echo "📋 Target branch: $TARGET_BRANCH"

# Check if pushing to protected branches
PROTECTED_BRANCHES=("main" "master" "prod")

for protected in "${PROTECTED_BRANCHES[@]}"; do
    if [ "$TARGET_BRANCH" = "$protected" ]; then
        echo "⚠️  WARNING: You are pushing to protected branch: $TARGET_BRANCH"
        echo ""
        
        # Check for production configuration changes
        PROD_CONFIG_CHANGES=$(git diff --name-only "$remote_sha" "$local_sha" 2>/dev/null | grep -E "^config/prod/" | wc -l)
        
        if [ "$PROD_CONFIG_CHANGES" -gt 0 ]; then
            echo "❌ ERROR: Cannot push production configuration changes directly to $TARGET_BRANCH!"
            echo ""
            echo "📋 Modified production configuration files:"
            git diff --name-only "$remote_sha" "$local_sha" 2>/dev/null | grep -E "^config/prod/"
            echo ""
            echo "💡 Solution:"
            echo "  1. Create a pull request from dev to $TARGET_BRANCH"
            echo "  2. Get code review for production configuration changes"
            echo "  3. Merge through GitHub/GitLab interface"
            echo ""
            exit 1
        fi
        
        # Check for environment configuration files
        ENV_CONFIG_CHANGES=$(git diff --name-only "$remote_sha" "$local_sha" 2>/dev/null | grep -E "^\.env\.[^.]*$" | grep -v ".env.example" | wc -l)
        
        if [ "$ENV_CONFIG_CHANGES" -gt 0 ]; then
            echo "❌ ERROR: Cannot push environment configuration files to $TARGET_BRANCH!"
            echo ""
            echo "📋 Modified environment files:"
            git diff --name-only "$remote_sha" "$local_sha" 2>/dev/null | grep -E "^\.env\.[^.]*$" | grep -v ".env.example"
            echo ""
            echo "💡 Solution:"
            echo "  Environment configuration files should not be committed to Git."
            echo "  Use config/ directory templates instead."
            echo ""
            exit 1
        fi
        
        # Ask for confirmation
        echo "🔒 You are pushing to protected branch: $TARGET_BRANCH"
        echo "   This branch is used for production deployment."
        echo ""
        read -p "Are you sure you want to continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "❌ Push cancelled."
            exit 1
        fi
        
        echo "✅ Proceeding with push to $TARGET_BRANCH..."
        break
    fi
done

echo "✅ pre-push checks passed!"
exit 0
EOF
    chmod +x .git/hooks/pre-push
    echo "✅ Created and installed pre-push hook"
fi

echo ""
echo "🎉 Git hooks installation complete!"
echo ""
echo "📋 Installed hooks:"
echo "   - pre-commit: Prevents committing environment configuration files"
echo "   - pre-push: Protects production branches from dangerous changes"
echo ""
echo "💡 To update hooks for all team members:"
echo "   1. Commit changes to scripts/git-hooks/"
echo "   2. Team members run: ./scripts/install-git-hooks.sh"
echo ""
echo "✅ Git hooks are now active and will protect your environment configuration."
