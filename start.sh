echo "正在配置环境......."
sudo apt update
sudo apt install python3-pip 

pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

pip3 uninstall bce-python-sdk
pip3 install bce-python-sdk
pip3 install baidubce

echo "正在启动服务......."
nohup python3 run.py &