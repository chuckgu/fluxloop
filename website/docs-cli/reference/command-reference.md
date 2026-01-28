# Command Reference

Comprehensive list of all FluxLoop CLI commands.

| Command | Description |
|---------|-------------|
| `init` | Initialize a new project |
| `auth` | Manage authentication |
| `projects` | List and select projects |
| `scenarios` | Manage test scenarios |
| `apikeys` | Manage API keys |
| `generate` | Generate test inputs |
| `test` | Run agent tests |
| `upload` | Upload data to platform |
| `pull` | Pull data from platform |
| `sync` | Bidirectional sync |
| `status` | Check project status |
| `config` | Manage configuration |

## Project Management

### `fluxloop init scenario`
Create a new project directory with default configuration.

### `fluxloop status`
Check the status of your local environment and project.

## Authentication

### `fluxloop auth login`
Authenticate with the Web Platform using an API key.

### `fluxloop auth status`
Check your current authentication status.

## Testing

### `fluxloop test`
Run agent tests with local or remote scenarios.

### `fluxloop generate`
Generate synthetic test inputs using LLMs.

## Synchronization

### `fluxloop sync pull`
Download scenarios from the Web Platform.

### `fluxloop sync upload`
Upload test results to the Web Platform.

### `fluxloop sync`
Bidirectional synchronization of scenarios and metadata.
