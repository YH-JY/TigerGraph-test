import sys
import importlib

print("=== Python 环境诊断 ===")
print(f"Python 可执行文件路径: {sys.executable}")
print(f"Python 版本: {sys.version}")
print(f"Python 路径:")
for path in sys.path:
    print(f"  - {path}")
print()

print("=== 检查模块安装 ===")

modules_to_check = [
    "pytigergraph",
    "fastapi", 
    "uvicorn",
    "pydantic",
    "kubernetes",
    "pydantic_settings",
    "python_dotenv"
]

for module in modules_to_check:
    try:
        mod = importlib.import_module(module)
        version = getattr(mod, '__version__', 'unknown')
        print(f"✓ {module}: 已安装 (版本: {version})")
    except ImportError as e:
        print(f"✗ {module}: 未安装 - {e}")
    except Exception as e:
        print(f"! {module}: 错误 - {e}")

print("\n=== 尝试导入 pytigergraph ===")
try:
    import pytigergraph
    print(f"✓ 成功导入 pytigergraph")
    print(f"  - 版本: {pytigergraph.__version__}")
    print(f"  - 位置: {pytigergraph.__file__}")
except ImportError as e:
    print(f"✗ 导入失败: {e}")
    
print("\n=== pip 检查 ===")
try:
    import pip
    print(f"✓ pip 版本: {pip.__version__}")
except:
    print("无法导入 pip")

print("\n=== 建议 ===")
print("1. 确认你在正确的Python环境中")
print("2. 尝试运行: python -m pip install pytigergraph==1.9.1 --force-reinstall")
print("3. 如果有多个Python版本，确保使用正确的python命令")