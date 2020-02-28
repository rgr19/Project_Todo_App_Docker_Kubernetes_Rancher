#!/usr/bin/env bash

# Fix issue as in
# https://askubuntu.com/questions/766883/there-is-no-public-key-available-for-the-following-key-ids-1397bc53640db551

wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -