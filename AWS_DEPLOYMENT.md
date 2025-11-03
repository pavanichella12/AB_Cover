# AWS EC2 Deployment Guide for Streamlit Dashboard

## Step 1: Launch EC2 Instance

1. Go to AWS Console → EC2 → Launch Instance
2. Choose **Ubuntu 22.04 LTS** (free tier eligible)
3. Select **t2.micro** (free tier) or t2.small for better performance
4. Configure Security Group:
   - Add **Inbound Rule**: 
     - Type: Custom TCP
     - Port: 8501
     - Source: 0.0.0.0/0 (or your IP for security)
     - Description: Streamlit
5. Launch and download your key pair (.pem file)

## Step 2: Connect to EC2 Instance

```bash
# Make key file secure
chmod 400 your-key-file.pem

# Connect to instance
ssh -i your-key-file.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

## Step 3: Install Dependencies on EC2

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip -y

# Install Git
sudo apt install git -y

# Clone your repository
git clone https://github.com/pavanichella12/AB_Cover.git
cd AB_Cover

# Install Python dependencies
pip3 install -r requirements.txt
```

## Step 4: Run Streamlit Dashboard

```bash
# Run Streamlit (will be accessible on port 8501)
streamlit run dashboard_fresh.py --server.port 8501 --server.address 0.0.0.0
```

## Step 5: Make it Persistent (Run in Background)

Install **screen** or **tmux** to keep it running:

```bash
# Install screen
sudo apt install screen -y

# Create a new screen session
screen -S dashboard

# Run Streamlit inside screen
streamlit run dashboard_fresh.py --server.port 8501 --server.address 0.0.0.0

# Detach: Press Ctrl+A, then D
# Reattach: screen -r dashboard
```

## Step 6: Access Your Dashboard

Open browser and go to:
```
http://YOUR_EC2_PUBLIC_IP:8501
```

## Alternative: Use systemd Service (Recommended)

Create a service file for automatic startup:

```bash
# Create service file
sudo nano /etc/systemd/system/streamlit.service
```

Add this content:
```ini
[Unit]
Description=Streamlit Dashboard
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/AB_Cover
ExecStart=/usr/local/bin/streamlit run dashboard_fresh.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
# Reload systemd
sudo systemctl daemon-reload

# Start service
sudo systemctl start streamlit

# Enable on boot
sudo systemctl enable streamlit

# Check status
sudo systemctl status streamlit
```

## Important Notes

1. **Security**: Consider using Security Groups to restrict access to your IP only
2. **Domain**: You can add a domain name and use Route 53 + Application Load Balancer
3. **HTTPS**: Use AWS Certificate Manager + ALB for HTTPS
4. **Cost**: t2.micro is free tier eligible, monitor your usage

## Troubleshooting

- **Can't access dashboard**: Check Security Group allows port 8501
- **Dashboard stops**: Use systemd service or screen/tmux
- **Memory issues**: Upgrade to t2.small or larger instance

