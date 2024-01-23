#安装pipreqs#
pip install pipreqs

#同步requirements.txt#
#同步增加或者删除包#
pycharm > Tools -> Sync Python Requirements

#创建requirements.txt#
#有些项目编码不对，统一携带iso-8859-1编码
pipreqs --encoding=iso-8859-1  --force

#安装所有依赖包#
pip install -r requirements.txt

#版本检测#
cmd your project dir
pip list --outdated

#升级某个包#
#以fastapi为例
pip install -U fastapi

#升级所有包#
#慎用该命令
pip install -U -r requirements.txt

#是否缺依赖#
python -m pip check