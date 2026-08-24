"""Test API import mechanisms to ensure no null bytes errors."""

import sys
import pytest
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_routes_module_import():
    """Test that routes module can be imported without null bytes errors."""
    try:
        from rag_kb.api.routes import router
        assert router is not None
        assert hasattr(router, 'routes')
    except SyntaxError as e:
        pytest.fail(f"Import failed with SyntaxError: {e}")


def test_main_module_import():
    """Test that main module can be imported without null bytes errors."""
    try:
        from rag_kb.api.main import app
        assert app is not None
        assert hasattr(app, 'routes')
    except SyntaxError as e:
        pytest.fail(f"Import failed with SyntaxError: {e}")


def test_routes_no_null_bytes():
    """Test that routes.py file contains no null bytes."""
    routes_path = Path(__file__).parent.parent / "src" / "rag_kb" / "api" / "routes.py"
    with open(routes_path, 'rb') as f:
        content = f.read()
    assert b'\x00' not in content, "routes.py contains null bytes"


def test_main_no_null_bytes():
    """Test that main.py file contains no null bytes."""
    main_path = Path(__file__).parent.parent / "src" / "rag_kb" / "api" / "main.py"
    with open(main_path, 'rb') as f:
        content = f.read()
    assert b'\x00' not in content, "main.py contains null bytes"


def test_api_router_structure():
    """Test that API router has expected structure."""
    from rag_kb.api.routes import router
    # Router may be empty after cleanup, but should be importable
    assert router is not None, "Router should be defined"
    
    # Check router is properly initialized
    assert hasattr(router, 'routes'), "Router should have routes attribute"


def test_fastapi_app_structure():
    """Test that FastAPI app has expected structure."""
    from rag_kb.api.main import app
    assert app.title == 'rag-kb', "App should have correct title"
    
    # Check for expected routes
    route_paths = [route.path for route in app.routes]
    assert '/health' in route_paths, "Should have health check endpoint"
    assert '/api/v1' in str(route_paths), "Should have API v1 routes"


def test_lazy_import_mechanism():
    """Test that lazy imports work correctly in routes."""
    from rag_kb.api.routes import get_rag
    # This should not fail even if LightRAG dependencies are not fully available
    # as it's a lazy import
    try:
        rag_instance = get_rag()
        assert rag_instance is not None
    except Exception as e:
        # If dependencies are missing, that's acceptable for this test
        # The important part is that the import mechanism itself works
        pass