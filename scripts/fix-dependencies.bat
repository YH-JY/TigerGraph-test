@echo off
echo 修复 Python 依赖冲突...

REM 卸载冲突的包
echo 卸载可能冲突的包...
pip uninstall -y pydantic pydantic-core pydantic-settings fastapi

REM 清理 pip 缓存
echo 清理 pip 缓存...
pip cache purge

REM 重新安装依赖
echo 重新安装依赖...
pip install --upgrade pip
pip install pydantic>=2.9.0
pip install pydantic-settings>=2.1.0
pip install fastapi==0.109.2
pip install -r requirements.txt

echo 依赖安装完成！
pause