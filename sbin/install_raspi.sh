#!/bin/bash

echo "This script is used for reference; do not run it manually"
exit 1

# Grab SD card
sudo fdisk -l 

# Install Raspian image
sudo dd if=2019-09-26-raspbian-buster-lite.img of=/dev/mmcblk0 # change this to your disk

# Enable SSH 
sudo mkdir -p /mnt/sd/boot
sudo mount /dev/mmcblk0p1 /mnt/sd/boot # mount boot drive
touch /mnt/sd/boot/ssh # enable ssh

# loop up IP on your router/DNS
ssh pi@$PIIP # password is "raspberry"

# Change password
passwd

# Install some essentials and upgrade the system
sudo apt update
sudo apt install vim git zsh python3-dev python3-pip
sudo apt upgrade 

# I'm getting my standard config here - use it if you want 
mkdir ~/workspace && cd workspace
git clone https://github.com/chollinger93/debian-scripts.git
cp -r debian-scripts/dotfiles/* ~
# Adjust my name to pi 
vim ~/.zshrc 
# :%s/christian/pi/g
source ~/.zshrc 

# Switch to zsh
zsh 
# Install oh-my-zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Set a static IP, comment out the "static IP configuration" and adjust for your router, DNS, and IP
sudo vim /etc/dhcpcd.conf

# Recommended: Change hostname if you have multiple raspis
sudo hostname 4g-raspberrypi
vim /etc/hosts # :%s/raspberrypi/4g-raspberrypi/g 

# Enable camera
sudo raspi-config # navigate to interface, enable camera

# Reboot, done!
sudo reboot 