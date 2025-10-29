# Environment Setup

## NVIDIA API Key Configuration

### Step 1: Get Your NVIDIA API Key

1. Go to [NVIDIA Build](https://build.nvidia.com/)
2. Sign in with your NVIDIA Developer account
3. Navigate to the API Keys section
4. Generate a new API key

### Step 2: Create .env File

Create a `.env` file in the root of the project:

```bash
# Create .env file
touch .env
```

### Step 3: Add Your API Key

Add the following to your `.env` file:

```bash
# NVIDIA API Configuration
NVIDIA_API_KEY=your_nvidia_api_key_here
```

Replace `your_nvidia_api_key_here` with your actual API key from NVIDIA.

### Step 4: Verify Setup

Run the test script to verify everything is working:

```bash
python test_agents.py
```

If configured correctly, you should see the agents running with NVIDIA Nemotron!

## Example .env File

```bash
# NVIDIA API Configuration
# Get your API key from: https://build.nvidia.com/
NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Troubleshooting

### "NVIDIA_API_KEY not found in environment"

- Make sure the `.env` file exists in the project root
- Check that the API key is correctly formatted
- Verify your API key is active at https://build.nvidia.com/

### API Connection Issues

- Check your internet connection
- Verify the API key hasn't expired
- Check NVIDIA API status page

