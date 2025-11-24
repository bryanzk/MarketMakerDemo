# API Reference Documentation

This page provides links to all API and code reference documentation for the AlphaLoop Market Maker project.

## 📚 Documentation Resources

### 1. **Auto-Generated API Documentation** (pdoc)
Browse the full API reference with all modules, classes, and functions:
- **[AlphaLoop API Reference](api/index.html)** 
  - Automatically generated from code docstrings
  - Includes type hints and parameter documentation
  - Updated on every push to `main`

### 2. **Interactive API Documentation** (FastAPI)
Explore and test the REST API endpoints interactively:
- **[Swagger UI](/docs)** - Interactive API explorer with "Try it out" functionality
- **[ReDoc](/redoc)** - Alternative API documentation with a cleaner read-through interface

*Note: Start the server (`python run.py` or `uvicorn server:app --port 3000`) to access these endpoints.*

---

## 🔧 For Developers

### Generating Documentation Locally
```bash
# Install pdoc if not already installed
pip install -r requirements.txt

# Generate API docs
./scripts/build_docs.sh

# View the generated documentation
open docs/api/index.html
```

### Documentation Standards
- **Docstrings**: Use Google-style or NumPy-style docstrings
- **Type Hints**: Add type hints to all function signatures
- **Module Docstrings**: Include a module-level docstring explaining the purpose

### Auto-Documentation in CI/CD
Documentation is automatically regenerated and deployed on every push to the `main` branch via GitHub Actions.

---

## 📖 Related Documentation
- [README](../README.md) - Project overview and quick start
- [CI/CD Guide](cicd.md) - Continuous integration and deployment
- [Dashboard Guide](dashboard.md) - Monitoring metrics and charts
- [AlphaLoop Framework](alphaloop/framework_design.md) - Architecture and design
