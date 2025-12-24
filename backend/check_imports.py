# Test script for checking imports
try:
    from pyTigergraph import TigerGraphConnection
    print("✅ pyTigergraph import successful")
    
    # Test TigerGraphConnection instantiation
    conn = TigerGraphConnection(
        host="http://localhost:9000",
        username="tigergraph",
        password="tigergraph",
        graphname="K8sSecurityGraph"
    )
    print(f"✅ TigerGraphConnection created")
    
    # Test getVersion method
    try:
        version = conn.getVersion()
        print(f"✅ Version: {version}")
    except Exception as e:
        print(f"❌ getVersion failed: {e}")
    
    # Test graphname attribute
    print(f"✅ Graph name: {conn.graphname}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")