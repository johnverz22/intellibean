# Raspberry Pi Connection Setup Guide

## The Problem
SSH requires interactive password entry for security. Your .env file has the password, but SSH won't read it automatically.

## Solution: SSH Key Authentication (5 minutes setup)

### Step 1: Generate SSH Key (on your Windows PC)
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa_rpi
```
Press Enter for all prompts (no passphrase needed for automation)

### Step 2: View Your Public Key
```bash
cat ~/.ssh/id_rsa_rpi.pub
```
Copy the entire output (starts with `ssh-rsa`)

### Step 3: Connect to Raspberry Pi (one-time password entry)
```bash
ssh beans@192.168.100.197
Password: `Rpi5-HardwareDev26`

### Step 4: On the Raspberry Pi, add your key
```bash
mkdir -p ~/.ssh
echo "PASTE_YOUR_PUBLIC_KEY_HERE" >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
exit
```

### Step 5: Test password-less connection
```bash
ssh -i ~/.ssh/id_rsa_rpi intellibean@192.168.100.197
```
Should connect without asking for password!

### Step 6: Configure SSH to use this key automatically
Create/edit `~/.ssh/config`:
```
Host raspberrypi
    HostName 192.168.100.197
    User intellibean
    IdentityFile ~/.ssh/id_rsa_rpi
```

Now you can simply use:
```bash
ssh raspberrypi
scp file.py raspberrypi:~/
```

## Alternative: Manual Connection for Now

Until SSH keys are set up, connect manually:
```bash
ssh intellibean@192.168.100.197
# Enter password: Rpi5-HardwareDev26

# Then run commands:
python3 --version
```

## After SSH Keys Are Set Up

Run the deployment script:
```bash
python simple_deploy.py
```

It will work automatically without password prompts!
