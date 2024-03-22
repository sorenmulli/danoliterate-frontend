# After 
# 1. Installing Python 3.11
# 2. Cloning the repo to home dir
# 3. Installing the Python package in the repo, making sure that run.sh works.
# I followed the below steps to set up the server

## A. Configure nginx
# Make site available and enabled using configuration file
sudo cp dev/danoliterate /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/danoliterate /etc/nginx/sites-enabled
# Test syntax
sudo nginx -t

## B. Set up SSL using CertBot
sudo certbot --nginx -d danoliterate.compute.dtu.dk
# Test that renewal works
sudo certbot renew --dry-run

## C. Configure the server as a systemd service
sudo cp dev/danoliterate-server.service /etc/systemd/system
# Load the configuration
sudo systemctl daemon-reload
# Make it start at boot
sudo systemctl enable danoliterate-server

## D. Start the server
# Start the service and check status
sudo systemctl start danoliterate-server 
sudo systemctl status danoliterate-server
# Reload nginx to apply proxy changes
sudo systemctl reload nginx

## (E. Troubleshooting)
sudo systemctl restart nginx
sudo systemctl restart danoliterate-server
