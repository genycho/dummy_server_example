/usr/bin/pkill -f dummy_be.py || true

source /home/.bashrc

python --version

nohup python3 -u dummy_be.py > log_dummy_be.log &


