# GitHub Actions Auto-Deployment Setup

This guide will help you set up automatic deployment to your Hetzner server whenever you push to the `main` branch.

## How It Works

When you push to the `main` branch on GitHub, the workflow will:
1. Connect to your Hetzner server via SSH
2. Navigate to `/root/oneshot_wordle/oneshot_guessle`
3. Run the `deploy.sh` script which:
   - Fetches latest code from GitHub
   - Rebuilds Docker containers
   - Runs migrations
   - Restarts services

## Required GitHub Secrets

You need to add the following secrets to your GitHub repository:

### 1. Go to Repository Settings
1. Navigate to your repository on GitHub: `https://github.com/bitFez/oneshot_wordle`
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

### 2. Add These Secrets

#### HETZNER_HOST
- **Value**: `135.181.149.112`
- **Description**: IP address of your Hetzner server

#### HETZNER_USER
- **Value**: `root` (or whatever user runs the deploy.sh script)
- **Description**: SSH username for server access

#### HETZNER_PORT
- **Value**: `22` (default SSH port, change if you use a custom port)
- **Description**: SSH port number

#### HETZNER_SSH_KEY
- **Value**: Your private SSH key
- **Description**: Private key for SSH authentication

**How to generate and add SSH key:**

1. **On your local machine**, generate a new SSH key pair:

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Path "$env:USERPROFILE\.ssh" -Force
"y`n`n`n" | ssh-keygen -t ed25519 -C "github-actions-deploy" -f "$env:USERPROFILE\.ssh\github_deploy"
```

**macOS/Linux:**
```bash
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_deploy
```

2. **Copy the public key to your Hetzner server**:

**Windows (PowerShell):**
```powershell
Get-Content "$env:USERPROFILE\.ssh\github_deploy.pub" | ssh root@135.181.149.112 "mkdir -p ~/.ssh; cat >> ~/.ssh/authorized_keys"
```

**macOS/Linux:**
```bash
ssh-copy-id -i ~/.ssh/github_deploy.pub root@135.181.149.112
```

3. **Test the connection**:

**Windows (PowerShell):**
```powershell
ssh -i "$env:USERPROFILE\.ssh\github_deploy" root@135.181.149.112
```

**macOS/Linux:**
```bash
ssh -i ~/.ssh/github_deploy root@135.181.149.112
```

4. **Copy the private key contents** for GitHub secret:

**Windows (PowerShell):**
```powershell
Get-Content "$env:USERPROFILE\.ssh\github_deploy"
```

**macOS/Linux:**
```bash
cat ~/.ssh/github_deploy
```
Copy the entire output (including `-----BEGIN OPENSSH PRIVATE KEY-----` and `-----END OPENSSH PRIVATE KEY-----`)

5. **Add to GitHub**:
- Name: `HETZNER_SSH_KEY`
- Value: Paste the entire private key content

### 3. Existing Secrets
The workflow also preserves these existing secrets:
- `YR10_MOCKS`
- `YR11_MOCKS`

These are available as environment variables during deployment.

## Testing the Deployment

1. Make a small change to your code
2. Commit and push to main:
```bash
git add .
git commit -m "Test deployment"
git push origin main
```

3. Watch the deployment:
   - Go to your repository on GitHub
   - Click **Actions** tab
   - You'll see the "Deploy to Hetzner" workflow running
   - Click on it to see live logs

## Troubleshooting

### Permission Denied (publickey)
- Make sure you added the public key to the server with `ssh-copy-id`
- Test SSH connection manually: `ssh -i ~/.ssh/github_deploy root@135.181.149.112`

### deploy.sh not found
- Ensure `/root/oneshot_wordle/oneshot_guessle/deploy.sh` exists on server
- Check the path in `.github/workflows/deploy.yml` matches your server structure

### Docker command not found
- Ensure Docker and Docker Compose are installed on your Hetzner server
- The deploy user needs permission to run Docker commands

### Deployment takes too long / times out
- GitHub Actions has a default timeout of 60 minutes
- If needed, add `timeout-minutes: 30` to the job configuration

## Security Best Practices

1. **Never commit the private key** to your repository
2. **Use GitHub Secrets** for all sensitive information
3. **Rotate SSH keys periodically** for security
4. **Limit SSH key permissions** - this key should only be used for deployment
5. **Monitor GitHub Actions logs** for any suspicious activity

## Manual Deployment

If you need to deploy manually, SSH into your server and run:
```bash
ssh root@135.181.149.112
cd /root/oneshot_wordle/oneshot_guessle
bash deploy.sh
```

## Workflow File Location

The GitHub Actions workflow is defined in:
- `.github/workflows/deploy.yml`

You can modify this file to:
- Change the deployment trigger (e.g., on tags, on specific branches)
- Add pre-deployment checks
- Send notifications on success/failure
- Run tests before deploying

## docker cleanup commands:
```bash
docker system prune -f --volumes  # Remove unused resource
docker image prune -a --filter "until=720h" -f  # Remove images older than 30 days
```
