#!/bin/bash
# Author: Diyi Wang (wang.di@husky.neu.edu)
#
# Functional test script for PyDFS project.

cd pydfs
# Bring up master and minions
python3 master.py &
if [[ $? -ne 0 ]]; then
  echo "Master fireup failed!"
  exit 1
fi

python3 minion.py &
if [[ $? -ne 0 ]]; then
  echo "Minions fireup failed!"
  exit 1
fi

# Wait for server and minion
sleep 3

# Create file with test msg
TEST_MSG="Put and Get are all green!"
echo $TEST_MSG > tmp.txt

# Put
python3 client.py put tmp.txt tmp
if [[ $? -ne 0 ]]; then
  echo "Put operation failed!"
  exit 1
fi

# Get
output=$(python3 client.py get tmp)
echo $output
if [[ $output != $TEST_MSG  ]]; then
  echo "GET operation failed!"
  exit 1
fi

# Clean up
pkill -f master.py
pkill -f minion.py
rm -f tmp.txt
#rm -f fs.img

exit 0
