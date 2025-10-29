# Security Policy

## Supported Versions

The following versions of AgentPsyAssessment are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | ✅ Yes             |
| < 1.0   | ❌ No              |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please follow these steps:

### 1. Do not report security vulnerabilities through public GitHub issues
Instead, contact the maintainers directly through private communication.

### 2. How to Report
- Email: [your-email@example.com] (replace with actual email)
- Include detailed information about the vulnerability
- Provide steps to reproduce if possible
- Describe the potential impact

### 3. Response Expectation
- You will receive an acknowledgment within 48 hours
- We will investigate and provide updates on our findings
- If the vulnerability is accepted, we will work on a fix
- If declined, we will provide reasoning

### 4. Security Update Process
- Verified vulnerabilities will be addressed promptly
- Fixes will be released as quickly as possible
- Security advisories will be published after fixes are deployed

## Security Best Practices

When using this software, please follow these security practices:

### API Keys
- Never commit API keys to version control
- Use environment variables for sensitive information
- Rotate API keys regularly
- Use keys with minimal required permissions

### Data Handling
- Be aware of data privacy regulations in your jurisdiction
- Anonymize personal data when possible
- Encrypt sensitive data in transit and at rest
- Regularly backup important data

### Local Models
- Keep local model software updated
- Monitor model access and usage
- Review downloaded models from trusted sources

## Dependencies Security

This project uses various third-party dependencies. We:
- Regularly update dependencies to their latest versions
- Monitor security advisories for our dependencies
- Use dependency scanning tools when possible
- Test for security issues in the CI pipeline

## Additional Security Notes

1. **LLM API Security**: Be cautious when sending sensitive data to LLMs, as this data may be stored by the provider.

2. **Local Model Security**: When using local models, ensure proper access controls to the model server.

3. **Data Privacy**: The software processes potentially sensitive psychological assessment data. Handle this data in accordance with applicable privacy laws and ethical guidelines.

4. **Network Security**: When using cloud models, ensure secure network connections.

## Security Features

1. **Environment Variable Loading**: Uses python-dotenv for secure configuration management
2. **JSON Validation**: Implements schema validation to prevent injection attacks in data processing
3. **Error Handling**: Comprehensive error handling to prevent information disclosure

## Contact

For security-related inquiries, please contact [your-email@example.com].