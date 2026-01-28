---
sidebar_position: 6
---

# Security Guide

Security best practices for using FluxLoop.

## Overview

Security considerations when using FluxLoop:
- API key management
- Sensitive data handling
- Access control
- Network security

## API Key Security

### Never Commit Keys

❌ **Don't:**

```bash
# fluxloop.yaml
api:
  key: "flx_api_abc123..."  # ❌ Committed to git!
```

```bash
# script.sh
export FLUXLOOP_API_KEY="flx_api_abc123..."  # ❌ In source control!
```

✅ **Do:**

```bash
# .gitignore
.fluxloop/credentials
.env
api_key.txt
```

```bash
# Use environment variables
export FLUXLOOP_API_KEY="flx_api_abc123..."

# Or secure key store
fluxloop config set api_key_file ~/.secrets/fluxloop_key
```

### Rotate Keys Regularly

Rotate API keys periodically:

```bash
# Monthly rotation
fluxloop apikeys create --name "cli-$(date +%Y%m)"

# Update environment
export FLUXLOOP_API_KEY=flx_new_key...

# Revoke old key after grace period
fluxloop apikeys revoke flx_old_key...
```

### Use Minimal Scopes

Grant minimal necessary permissions:

```bash
# ❌ Too broad
fluxloop apikeys create --scope admin

# ✅ Least privilege
fluxloop apikeys create --scope read-write
```

### Separate Keys Per Environment

Use different keys for different environments:

```bash
# Development
export FLUXLOOP_API_KEY_DEV=flx_dev_...

# Staging
export FLUXLOOP_API_KEY_STAGING=flx_staging_...

# Production
export FLUXLOOP_API_KEY_PROD=flx_prod_...
```

## Sensitive Data

### Don't Upload Sensitive Data

Avoid uploading sensitive information:

❌ **Don't upload:**
- User credentials
- API keys
- Personal information (PII)
- Proprietary data
- Health records (PHI)
- Financial data

✅ **Do:**

```yaml
# Sanitize before testing
inputs:
  - text: "Reset password for user [REDACTED]"
  - text: "API key is [REDACTED]"
```

### Sanitize Test Data

Use sanitization:

```bash
# Sanitize before upload
fluxloop test --sanitize --upload
```

```yaml
# Sanitization config
sanitization:
  patterns:
    - type: email
      replace: "user@example.com"
    - type: api_key
      replace: "[REDACTED]"
    - type: phone
      replace: "555-0000"
```

### Use Synthetic Data

Generate synthetic data:

```bash
# Generate synthetic inputs (no real user data)
fluxloop inputs generate --persona test_user --count 100
```

### Local-Only Testing

Keep sensitive tests local:

```bash
# Test locally without upload
fluxloop test --no-upload

# Results stay on your machine
```

## Access Control

### Project Permissions

Use appropriate role:

| Role | Permissions | Use Case |
|------|-------------|----------|
| Viewer | Read only | Stakeholders |
| Editor | Read + Write | Developers |
| Admin | Full control | Project leads |

### Team Members

Invite only trusted members:

```
1. Go to app.fluxloop.ai/projects/my-project/settings
2. Review team members
3. Remove unnecessary access
4. Use principle of least privilege
```

### Service Accounts

Use service accounts for automation:

```bash
# Create service account
fluxloop apikeys create \
  --name "ci-bot" \
  --type service-account \
  --scope read-write

# Limit scope
```

## Network Security

### HTTPS Only

FluxLoop uses HTTPS by default:

```yaml
api:
  endpoint: "https://api.fluxloop.ai"  # ✅ HTTPS
```

Never use HTTP:

```yaml
api:
  endpoint: "http://api.fluxloop.ai"  # ❌ Insecure
```

### Network Restrictions

Restrict network access in production:

```yaml
# firewall rules
allow:
  - api.fluxloop.ai (HTTPS)
deny:
  - * (all other traffic)
```

### VPN/Private Networks

For sensitive environments:

```bash
# Use VPN
vpn connect company-network

# Then use FluxLoop
fluxloop test --upload
```

## CI/CD Security

### Secrets Management

Use CI/CD secret management:

**GitHub Actions:**

```yaml
# .github/workflows/test.yml
- name: Run Tests
  env:
    FLUXLOOP_API_KEY: ${{ secrets.FLUXLOOP_API_KEY }}
  run: fluxloop test --upload
```

**GitLab CI:**

```yaml
# .gitlab-ci.yml
test:
  script:
    - fluxloop test --upload
  variables:
    FLUXLOOP_API_KEY: $FLUXLOOP_API_KEY_SECRET
```

### Limit CI Permissions

Use read-only keys for CI:

```bash
# Create read-only key for viewing results
fluxloop apikeys create --name "ci-viewer" --scope read
```

### Audit CI Logs

Review CI logs for exposed secrets:

```bash
# ❌ Key exposed in logs
echo "API Key: $FLUXLOOP_API_KEY"

# ✅ Masked in logs
echo "API Key: ***"
```

## Monitoring & Auditing

### API Key Usage

Monitor key usage:

```
app.fluxloop.ai/settings/api-keys
- Last used: 2024-11-01 14:30
- Request count: 1,234
- Failed attempts: 0
```

### Activity Logs

Review activity logs:

```
app.fluxloop.ai/projects/my-project/activity
- 2024-11-01 14:30: alice@company.com uploaded scenarios
- 2024-11-01 15:00: bob@company.com ran tests
```

### Anomaly Detection

Watch for unusual activity:

```
⚠️ Alerts:
- Unusual upload location: Russia
- High request rate: 1000 req/min
- Failed authentication: 10 attempts
```

## Data Privacy

### Data Retention

Understand data retention:

```
FluxLoop retains:
- Test results: 90 days (configurable)
- Scenarios: Until deleted
- Audit logs: 1 year
```

Delete when no longer needed:

```bash
# Delete old results
fluxloop results delete --older-than 90d

# Delete scenario
fluxloop scenarios delete old-scenario
```

### Data Location

Data stored in:

```
- United States (default)
- Europe (on request)
- Custom (enterprise)
```

### Compliance

FluxLoop complies with:
- SOC 2 Type II
- GDPR
- CCPA

See [Privacy Policy](https://fluxloop.ai/privacy) for details.

## Incident Response

### Compromised API Key

If key is compromised:

```bash
# 1. Immediately revoke
fluxloop apikeys revoke flx_compromised_key

# 2. Create new key
fluxloop apikeys create --name "replacement-$(date +%Y%m%d)"

# 3. Update all services
export FLUXLOOP_API_KEY=flx_new_key...

# 4. Notify team
```

### Data Breach

If sensitive data uploaded:

```bash
# 1. Delete immediately
fluxloop results delete --run-id run_with_sensitive_data

# 2. Contact support
support@fluxloop.ai

# 3. Review sanitization process
```

## Security Checklist

### Before Deployment

- [ ] API keys stored securely (not in code)
- [ ] Keys rotated regularly
- [ ] Minimal scopes granted
- [ ] Sensitive data sanitized
- [ ] Test data is synthetic
- [ ] CI/CD secrets configured
- [ ] Team access reviewed
- [ ] Activity monitoring enabled

### Regular Audits

- [ ] Review API key usage monthly
- [ ] Rotate keys quarterly
- [ ] Audit team access monthly
- [ ] Review activity logs weekly
- [ ] Update security practices

## Vulnerability Reporting

Found a security issue?

```
Email: security@fluxloop.ai
PGP Key: https://fluxloop.ai/security.asc

Please include:
- Description of vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We respond within 24 hours.
```

## Resources

### Documentation

- [Authentication Guide](../configuration/authentication)
- [API Keys Command](../commands/apikeys)
- [Privacy Policy](https://fluxloop.ai/privacy)
- [Terms of Service](https://fluxloop.ai/terms)

### Security Updates

Subscribe to security updates:

```
https://fluxloop.ai/security/updates
```

## Best Practices Summary

### Do ✅

- Use environment variables for keys
- Rotate keys regularly
- Use minimal scopes
- Sanitize sensitive data
- Monitor API key usage
- Review team access
- Use HTTPS only

### Don't ❌

- Commit keys to git
- Share keys between environments
- Upload sensitive data
- Grant excessive permissions
- Ignore security alerts
- Use HTTP
- Expose keys in logs

## Related

- [Authentication](../configuration/authentication)
- [API Keys Command](../commands/apikeys)
- [Team Collaboration](../workflows/team-collaboration)

## Next Steps

- Review your API keys
- Set up key rotation
- Configure sanitization
- Enable monitoring
- Train team on security
