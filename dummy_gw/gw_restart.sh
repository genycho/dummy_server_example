/usr/bin/pkill -f dummy_gw.py || true

source /home/.bashrc

python --version

nohup python3 -u dummy_gw.py > log_dummy_gw.log &


