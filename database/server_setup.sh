#!/bin/bash

# Read the .env file and evaluate it line by line
while IFS='=' read -r key value; do
  # Ignore comments and empty lines
  [[ "$key" =~ ^#.*$ || -z "$key" ]] && continue
  
  # Assign the variable locally in the script
  declare "$key=$value"
done < .env

# Creating user specifically for connection with database
if id "$DB_SCRAPER_USER" &>/dev/null; then
  # user already exists
  echo "User $DB_SCRAPER_USER already exists!"
  exit 1
fi

# user doesn't exist
sudo adduser --gecos "" "$DB_SCRAPER_USER"
# Creating necessary folders
authkeys="/home/$DB_SCRAPER_USER/.ssh/authorized_keys"
sudo mkdir -p "/home/$DB_SCRAPER_USER/.ssh"
sudo touch "$authkeys"

# Generating SSH keys
KEY_COMMENT="scraper-ssh-key"
KEY_FILENAME="scraper_ssh_ed25519"
if [ ! -f "./$KEY_FILENAME" ]; then
  sudo -u "$DB_SCRAPER_USER" ssh-keygen -t ed25519 -f "./$KEY_FILENAME" -N "" -C "$KEY_COMMENT"
  pubkey_content=$(< "./$KEY_FILENAME.pub")
  sudo bash -c "echo 'no-agent-forwarding,no-pty,no-user-rc,permitopen=localhost:5432 $pubkey_content' >> '$authkeys'"
else
  echo "SSH key already exists at ./$KEY_FILENAME"
  exit 1
fi

# Setting permissions
sudo chown -R "$DB_SCRAPER_USER:$DB_SCRAPER_USER /home/$DB_SCRAPER_USER/.ssh"
sudo chmod 700 "/home/$DB_SCRAPER_USER/.ssh"
sudo chmod 600 "$authkeys"

echo "Created unpriviledged $DB_SCRAPER_USER user with the ability to connect to database and generated ed25519 private/public keys!"