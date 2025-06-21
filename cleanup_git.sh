#!/bin/bash

# Whisprd Git Cleanup Script
# Removes files from remote repository that should be ignored based on .gitignore

echo "🧹 Whisprd Git Cleanup Script"
echo "=============================="
echo ""

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

echo "📋 Current git status:"
git status --short
echo ""

echo "🔍 Checking for files that should be ignored:"
git status --ignored
echo ""

# Function to remove files from git tracking
remove_from_git() {
    local pattern="$1"
    local description="$2"
    
    echo "🔧 Removing $description..."
    
    # Find files matching the pattern that are currently tracked
    local files=$(git ls-files | grep -E "$pattern" || true)
    
    if [ -n "$files" ]; then
        echo "   Found files to remove:"
        echo "$files" | sed 's/^/   - /'
        
        # Remove from git tracking (but keep local files)
        echo "$files" | xargs -r git rm --cached
        
        echo "   ✅ Removed from git tracking"
    else
        echo "   ✅ No files to remove"
    fi
    echo ""
}

# Function to remove directories from git tracking
remove_directory_from_git() {
    local dir="$1"
    local description="$2"
    
    echo "🔧 Removing $description..."
    
    if git ls-files | grep -q "^$dir/"; then
        echo "   Found directory to remove: $dir"
        
        # Remove from git tracking (but keep local files)
        git rm -r --cached "$dir" 2>/dev/null || true
        
        echo "   ✅ Removed from git tracking"
    else
        echo "   ✅ Directory not tracked: $dir"
    fi
    echo ""
}

echo "🚀 Starting cleanup process..."
echo ""

# Remove Python cache files
remove_from_git "__pycache__" "Python cache directories"
remove_from_git "\.py[cod]$" "Python compiled files"

# Remove distribution files
remove_from_git "build/" "Build directories"
remove_from_git "dist/" "Distribution directories"
remove_from_git "\.egg-info/" "Egg info directories"
remove_from_git "\.egg$" "Egg files"

# Remove test coverage files
remove_from_git "\.coverage" "Coverage files"
remove_from_git "htmlcov/" "Coverage HTML reports"
remove_from_git "\.pytest_cache/" "Pytest cache"

# Remove environment files
remove_from_git "\.venv/" "Virtual environment"
remove_from_git "venv/" "Virtual environment"
remove_from_git "env/" "Environment directory"

# Remove IDE files
remove_from_git "\.idea/" "PyCharm files"
remove_from_git "\.vscode/" "VS Code files"

# Remove Whisprd specific files
remove_from_git "\.(wav|mp3|flac|ogg|m4a)$" "Audio files"
remove_from_git "whisprd_transcript\.txt" "Whisprd transcript files"
remove_from_git "dictation_transcript\.txt" "Dictation transcript files"
remove_from_git "\.log$" "Log files"
remove_from_git "\.(tmp|temp)$" "Temporary files"

# Remove OS generated files
remove_from_git "\.DS_Store" "macOS system files"

# Remove mypy cache
remove_directory_from_git ".mypy_cache" "MyPy cache"

echo "📝 Summary of changes:"
git status --short
echo ""

# Ask if user wants to commit the changes
echo "🤔 Do you want to commit these changes? (y/N)"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "💾 Committing changes..."
    git add -A
    git commit -m "chore: remove files that should be ignored based on .gitignore"
    
    echo "🚀 Do you want to push these changes to remote? (y/N)"
    read -r push_response
    
    if [[ "$push_response" =~ ^[Yy]$ ]]; then
        echo "📤 Pushing to remote..."
        git push
        echo "✅ Changes pushed successfully!"
    else
        echo "📤 Skipping push. Run 'git push' when ready."
    fi
else
    echo "💾 Skipping commit. Run 'git add -A && git commit -m \"your message\"' when ready."
fi

echo ""
echo "🎉 Cleanup complete!"
echo ""
echo "💡 Tips:"
echo "   - Run this script periodically to keep your repository clean"
echo "   - Add new patterns to .gitignore if you find files that shouldn't be tracked"
echo "   - Use 'git status --ignored' to see what files are being ignored" 