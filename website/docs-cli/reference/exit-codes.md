# Exit Codes

FluxLoop CLI uses standard exit codes to indicate the result of command execution.

| Code | Status | Description |
|------|--------|-------------|
| 0 | Success | Command completed successfully |
| 1 | General Error | Catch-all for general errors |
| 2 | Configuration Error | Missing or invalid configuration |
| 3 | Authentication Error | Not logged in or invalid API key |
| 4 | Network Error | Failed to connect to Web Platform |
| 5 | Resource Not Found | Requested project, scenario, or bundle not found |
| 10 | Test Failure | One or more tests failed |
| 11 | Generation Error | Failed to generate test inputs |
| 12 | Sync Conflict | Merge conflicts during sync |

## Usage in Scripts

You can use these exit codes in your CI/CD pipelines:

```bash
# Example in a shell script
fluxloop test --yes --no-skip-upload

if [ $? -eq 0 ]; then
  echo "Tests passed!"
elif [ $? -eq 10 ]; then
  echo "Tests failed, but execution completed."
else
  echo "A critical error occurred."
  exit 1
fi
```
