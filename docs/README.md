# Sophos Tenant ID Retrieval

This project demonstrates how to get your Sophos tenant ID using the Sophos Central API.

## Prerequisites

- Python 3.6+
- Sophos Central account with API access
- Client ID and Client Secret (already provided)

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the script to get your tenant ID:

```bash
python sophos_tenant_id.py
```

## How to Get Tenant ID in Sophos

### Method 1: From Sophos Central Admin Console
1. Log into your [Sophos Central Admin Console](https://central.sophos.com/)
2. Navigate to **Global Settings** → **API Credentials**
3. Your tenant ID will be displayed there

### Method 2: Using the API (This Script)
The script automatically retrieves your tenant ID by:
1. Authenticating with your client credentials
2. Calling the `/whoami/v1` endpoint
3. Extracting the tenant ID from the response

### Method 3: From API Response Headers
When making API calls, the tenant ID is often included in response headers or can be found in the authentication response.

## API Endpoints Used

- **Authentication**: `https://id.sophos.com/api/v2/oauth2/token`
- **Whoami**: `https://api.central.sophos.com/whoami/v1`
- **Tenant Details**: `https://api.central.sophos.com/tenant/v1/tenants/{tenant_id}`

## Security Notes

- Keep your client credentials secure
- Never commit credentials to version control
- Use environment variables for production deployments

## Troubleshooting

If you encounter issues:
1. Verify your client ID and secret are correct
2. Ensure your API credentials have the necessary permissions
3. Check that your Sophos Central account is active
4. Verify network connectivity to Sophos endpoints 