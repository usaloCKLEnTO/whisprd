# Contributing to Whisprd

**Personal Project by @AgenticToaster**

This is a personal project I built to solve my own dictation needs. I'm sharing it because it might help others, but please understand this isn't a community-driven project or business.

## 🤝 How to Contribute

**You're absolutely welcome to contribute!** But please keep these expectations in mind:

### ⏰ Response Times
- I may not respond quickly to issues or PRs
- This isn't my top priority - I have other commitments
- Don't take it personally if I'm slow to respond

### 🎯 What I'm Looking For
- **Bug fixes** that make the tool more reliable
- **Documentation improvements** that help others use it
- **Performance optimizations** that make it faster/better
- **New features** that solve real problems (not just "nice to have")

### 🚫 What I'm NOT Looking For
- Feature requests that don't solve a specific problem
- Demands for immediate responses or fixes
- Criticism about response times or maintenance
- Requests to make this a community project

## 🐛 Bug Reports

If you find a bug, please:

1. **Search existing issues** to avoid duplicates
2. **Create a new issue** with:
   - Clear title describing the problem
   - Detailed description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version, etc.)
   - Error messages or logs

**Note**: I'll fix bugs when I can, but don't expect immediate responses.

## 💡 Feature Requests

For new features:

1. **Search existing issues** to see if it's already requested
2. **Create a feature request** with:
   - Clear title describing the feature
   - Detailed description of the functionality
   - **Why you need this** (what problem does it solve?)
   - Any implementation ideas

**Note**: I'll only implement features that solve real problems I understand.

## 🔧 Code Contributions

### Prerequisites

- Python 3.12+
- Git
- Basic knowledge of Python, audio processing, and Linux systems

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/whisprd.git
   cd whisprd
   ```

2. **Set up development environment**
   ```bash
   # Install uv if not already installed
   pipx install uv
   
   # Install dependencies
   uv sync
   
   # Install development dependencies
   uv sync --extra dev
   
   # Install CUDA support (optional, for GPU development)
   uv sync --extra cuda
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

### Code Style

We use several tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Run the formatters before committing:
```bash
# Format code
uv run black .
uv run isort .

# Check types
uv run mypy .

# Run linting
uv run flake8 .
```

### Testing

Write tests for new functionality:

```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=whisprd --cov-report=html
```

### Commit Guidelines

Use conventional commit messages:

- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `style:` for formatting changes
- `refactor:` for code refactoring
- `test:` for adding tests
- `chore:` for maintenance tasks

Example:
```
feat: add support for custom voice commands

- Add configuration option for custom commands
- Implement command validation
- Add tests for new functionality
```

### Pull Request Process

1. **Ensure your code follows the style guidelines**
2. **Add tests for new functionality**
3. **Update documentation if needed**
4. **Create a pull request** with:
   - Clear title and description
   - Reference to related issues
   - Screenshots for UI changes
   - Test results

**Note**: I'll review PRs when I can, but don't expect immediate feedback.

## 🏗️ Project Structure

```
whisprd/
├── whisprd/                 # Main package
│   ├── __init__.py
│   ├── audio_capture.py     # Audio input handling
│   ├── command_processor.py # Voice command processing
│   ├── config.py           # Configuration management
│   ├── dictation_engine.py # Main engine
│   ├── hotkey_manager.py   # Global hotkey handling
│   ├── keystroke_injector.py # Input injection
│   └── whisper_transcriber.py # Speech recognition
├── whisprd_cli.py          # Command-line interface
├── config.yaml             # Default configuration
├── whisprd_prompts.yaml    # Alternate prompts
├── install.sh              # Installation script
├── whisprd.service         # Systemd service
└── README.md               # Documentation
```

## 🔧 Development Guidelines

### Audio Processing

- Use `sounddevice` for audio capture
- Support multiple audio formats
- Handle audio device selection gracefully
- Implement proper error handling for audio failures

### Whisper Integration

- Use `faster-whisper` for transcription
- Support multiple model sizes
- Implement proper model loading and caching
- Handle transcription errors gracefully
- Support CUDA GPU acceleration with automatic fallback
- Test both CPU and GPU modes

### Keystroke Injection

- Use `uinput` for Linux compatibility
- Implement proper permission handling
- Support multiple keyboard layouts
- Handle injection failures gracefully

### Configuration

- Use YAML for configuration files
- Implement configuration validation
- Support user-specific config overrides
- Provide sensible defaults

### Error Handling

- Log errors with appropriate levels
- Provide user-friendly error messages
- Implement graceful degradation
- Add error recovery mechanisms

## 🧪 Testing Guidelines

### Unit Tests

- Test individual components in isolation
- Mock external dependencies
- Test edge cases and error conditions
- Maintain high test coverage

### Integration Tests

- Test component interactions
- Test end-to-end workflows
- Test configuration loading
- Test audio processing pipeline

### Manual Testing

- Test on different Linux distributions
- Test with different audio devices
- Test with various Whisper models
- Test hotkey functionality
- Test CUDA GPU acceleration and CPU fallback

## 📚 Documentation

### Code Documentation

- Use docstrings for all public functions
- Follow Google docstring format
- Include type hints
- Document complex algorithms

### User Documentation

- Keep README.md up to date
- Document configuration options
- Provide usage examples
- Include troubleshooting guides

## 🚀 Release Process

### Versioning

We use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Release Checklist

- [ ] Update version in `pyproject.toml`
- [ ] Update version in `whisprd/__init__.py`
- [ ] Update CHANGELOG.md
- [ ] Run full test suite
- [ ] Update documentation
- [ ] Create release tag
- [ ] Build and test package
- [ ] Publish to PyPI (if applicable)

## 🤝 Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

- Be respectful and inclusive
- Help newcomers
- Provide constructive feedback
- Follow the project's coding standards
- **Don't be a jerk** - this is a personal project shared for free

### Communication

- Use GitHub issues for discussions
- Be clear and concise
- Provide context for problems
- **Be patient** - I may not respond quickly
- **Don't demand immediate attention**

## 📞 Getting Help

- **Issues**: [GitHub Issues](https://github.com/AgenticToaster/whisprd/issues)
- **Discussions**: [GitHub Discussions](https://github.com/AgenticToaster/whisprd/discussions)
- **Documentation**: [README.md](README.md)

**Note**: I'll help when I can, but this isn't a support business.

## 🙏 Acknowledgments

Thank you to all contributors who help make Whisprd better! Your contributions are greatly appreciated, even if I don't always respond quickly.

---

**Remember**: This is a personal project I'm sharing to help others. If you find it useful and want to keep it updated, consider taking ownership or maintaining your own fork. I'm not trying to build a community or business - just sharing something that worked for me.