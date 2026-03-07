---
allowed-tools: Bash
description: Set up TickTick OAuth authentication (generates access token)
---

# /ticktick:setup

Walk through the TickTick OAuth flow to generate an access token for the MCP server.

## Usage

```bash
/ticktick:setup
```

## Behavior

1. Check that `TICKTICK_CLIENT_ID` and `TICKTICK_CLIENT_SECRET` are set
2. If missing, explain how to set them and exit
3. Launch the OAuth flow — browser opens, user approves, pastes redirect URL back
4. Display instructions for adding the resulting token to `~/.zshrc`
5. Note how to verify the connection after restarting Claude Code

## Implementation

```bash
# Check for required credentials
CLIENT_ID="${TICKTICK_CLIENT_ID:-NOT_SET}"
CLIENT_SECRET="${TICKTICK_CLIENT_SECRET:-NOT_SET}"

[ "$CLIENT_ID" = "NOT_SET" ] && echo "TICKTICK_CLIENT_ID:     NOT_SET" || echo "TICKTICK_CLIENT_ID:     [set]"
[ "$CLIENT_SECRET" = "NOT_SET" ] && echo "TICKTICK_CLIENT_SECRET: NOT_SET" || echo "TICKTICK_CLIENT_SECRET: [set]"

if [ "$CLIENT_ID" = "NOT_SET" ] || [ "$CLIENT_SECRET" = "NOT_SET" ]; then
    echo ""
    echo "Missing credentials. Add these to ~/.zshrc:"
    echo ""
    echo "  export TICKTICK_CLIENT_ID='your-client-id'"
    echo "  export TICKTICK_CLIENT_SECRET='your-client-secret'"
    echo ""
    echo "Then run: source ~/.zshrc"
    echo "Then re-run /ticktick:setup"
    exit 1
fi

echo ""
echo "Credentials found. Starting OAuth flow..."
echo "A browser window will open. Approve access, then paste the redirect URL back here."
echo ""
uvx --from git+https://github.com/jacepark12/ticktick-mcp ticktick-mcp auth
```

## After Auth

Once the flow completes, add the token to your shell config:

```bash
export TICKTICK_ACCESS_TOKEN='<token shown after auth>'
```

Then reload: `source ~/.zshrc`

## Verify

Restart Claude Code and run `/ticktick:today` to confirm the connection works.

## Error Handling

- **Missing CLIENT_ID / CLIENT_SECRET**: Instructions to set them are shown and the command exits early
- **Browser does not open**: Copy the auth URL printed to the terminal and open it manually
- **Redirect URL rejected**: Ensure the redirect URI configured in your TickTick developer app matches exactly
