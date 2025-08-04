# 🚀 Atlassian MCP Server

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://docker.com)
[![Python](https://img.shields.io/badge/Python-3.12+-green?logo=python)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-Compatible-orange)](https://modelcontextprotocol.io)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Atlassian](https://img.shields.io/badge/Atlassian-Jira%20%26%20Bitbucket-blue?logo=atlassian)](https://atlassian.com)

A powerful **Model Context Protocol (MCP) server** that integrates **Atlassian products** (Jira & Bitbucket) with AI assistants like Amazon Q, Claude, and other MCP-compatible tools.

## ✨ Features

### 🎯 Jira Integration
- ✅ **Issue Management**: Create, update, search, and manage Jira issues
- 🔄 **Status Transitions**: Move issues through workflow states
- 💬 **Comments**: Add and manage issue comments
- 🔍 **Advanced Search**: Use JQL (Jira Query Language) for complex queries
- 👥 **Assignment**: Assign issues to team members

### 🔧 Bitbucket Integration
- 📁 **Repository Management**: Clone, pull, and manage repositories
- 🌿 **Branch Operations**: Create feature branches, switch branches
- 🔀 **Git Operations**: Commit, push, pull, and status checks
- 🔗 **SSH Support**: Secure authentication with SSH keys

### 🤖 AI Assistant Integration
- 🧠 **Amazon Q CLI**: Native integration with Q CLI
- 🎭 **Claude**: Compatible with Anthropic's Claude
- 🔌 **MCP Standard**: Works with any MCP-compatible AI assistant

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/atlassian-mcp-server.git
cd atlassian-mcp-server

# Copy and configure environment
cp config/.env.example .env
# Edit .env with your Jira and Bitbucket credentials

# Start with Docker Compose
docker-compose up -d

# Check status
docker-compose ps
```

### Option 2: Local Installation

```bash
# Clone and setup
git clone https://github.com/yourusername/atlassian-mcp-server.git
cd atlassian-mcp-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp config/.env.example .env
# Edit .env with your credentials

# Run the server
python src/main.py
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with your configuration:

```env
# Jira Configuration
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your-jira-api-token

# Bitbucket Configuration
BITBUCKET_USERNAME=your-username
BITBUCKET_WORKSPACE=your-workspace

# Git Configuration
GIT_DEFAULT_BRANCH=main
GIT_REPOS_PATH=/app/repos

# Server Configuration
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8000
LOG_LEVEL=INFO
```

### Getting API Tokens

#### Jira API Token
1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Give it a descriptive name
4. Copy the token to your `.env` file

#### Bitbucket SSH Setup
1. Generate SSH key: `ssh-keygen -t rsa -b 4096 -C "your-email@example.com"`
2. Add public key to [Bitbucket SSH Keys](https://bitbucket.org/account/settings/ssh-keys/)
3. Test connection: `ssh -T git@bitbucket.org`

## 🔧 Usage Examples

### With Amazon Q CLI

```bash
# Search for Jira issues
q chat "Search for issues assigned to me in project SCRUM"

# Create a new issue
q chat "Create a bug report in project DEV with title 'API returning 500 errors'"

# Create feature branch for an issue
q chat "Create a feature branch for issue SCRUM-123 in the main repository"

# Update issue status
q chat "Move issue SCRUM-123 to In Progress"
```

### Available MCP Tools

- `jira-server___search_issues` - Search Jira issues with JQL
- `jira-server___get_issue` - Get detailed issue information
- `jira-server___create_issue` - Create new Jira issues
- `jira-server___update_issue` - Update existing issues
- `jira-server___add_comment` - Add comments to issues
- `jira-server___transition_issue` - Change issue status
- `bitbucket-git___clone_repository` - Clone repositories
- `bitbucket-git___create_branch` - Create feature branches
- `bitbucket-git___git_status` - Check repository status

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Assistant  │    │   MCP Server    │    │   Atlassian     │
│   (Q CLI, etc.) │◄──►│  (This Project) │◄──►│ (Jira/Bitbucket)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

The server acts as a bridge between AI assistants and your Atlassian development tools, providing a standardized interface for common development workflows.

## 🐳 Docker Deployment

### Development
```bash
docker-compose up -d
```

### Production
```bash
# Use production profile with nginx
docker-compose --profile production up -d
```

### Custom Configuration
```bash
# Use custom environment file
docker-compose --env-file .env.production up -d
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src

# Run specific test
python -m pytest tests/test_jira_integration.py
```

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Logs
```bash
# Docker logs
docker-compose logs -f atlassian-mcp-server

# Local logs
tail -f atlassian-mcp-server.log
```

## 🔒 Security

- **API Tokens**: Store securely in environment variables
- **SSH Keys**: Use read-only access where possible
- **Network**: Run in isolated Docker network
- **User**: Container runs as non-root user
- **Secrets**: Never commit credentials to version control

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Run code formatting
black src/ tests/
flake8 src/ tests/

# Run type checking
mypy src/
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 **Documentation**: Check the [docs/](docs/) directory
- 🐛 **Issues**: Report bugs on [GitHub Issues](https://github.com/yourusername/atlassian-mcp-server/issues)
- 💬 **Discussions**: Join [GitHub Discussions](https://github.com/yourusername/atlassian-mcp-server/discussions)

## 🙏 Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io) for the standard
- [Amazon Q](https://aws.amazon.com/q/) for AI assistant integration
- [Atlassian](https://atlassian.com) for Jira and Bitbucket APIs

---

**Made with ❤️ by [Sandeep Nalam](https://github.com/yourusername)**

## ✨ Features

### 🎯 Jira Integration
- ✅ **Issue Management**: Create, update, search, and manage Jira issues
- 🔄 **Status Transitions**: Move issues through workflow states
- 💬 **Comments**: Add and manage issue comments
- 🔍 **Advanced Search**: Use JQL (Jira Query Language) for complex queries
- 👥 **Assignment**: Assign issues to team members

### 🔧 Bitbucket Integration
- 📁 **Repository Management**: Clone, pull, and manage repositories
- 🌿 **Branch Operations**: Create feature branches, switch branches
- 🔀 **Git Operations**: Commit, push, pull, and status checks
- 🔗 **SSH Support**: Secure authentication with SSH keys

### 🤖 AI Assistant Integration
- 🧠 **Amazon Q CLI**: Native integration with Q CLI
- 🎭 **Claude**: Compatible with Anthropic's Claude
- 🔌 **MCP Standard**: Works with any MCP-compatible AI assistant

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/jira-mcp-server.git
cd jira-mcp-server

# Copy and configure environment
cp config/.env.example .env
# Edit .env with your Jira and Bitbucket credentials

# Start with Docker Compose
docker-compose up -d

# Check status
docker-compose ps
```

### Option 2: Local Installation

```bash
# Clone and setup
git clone https://github.com/yourusername/jira-mcp-server.git
cd jira-mcp-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp config/.env.example .env
# Edit .env with your credentials

# Run the server
python src/main.py
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with your configuration:

```env
# Jira Configuration
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your-jira-api-token

# Bitbucket Configuration
BITBUCKET_USERNAME=your-username
BITBUCKET_WORKSPACE=your-workspace

# Git Configuration
GIT_DEFAULT_BRANCH=main
GIT_REPOS_PATH=/app/repos

# Server Configuration
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8000
LOG_LEVEL=INFO
```

### Getting API Tokens

#### Jira API Token
1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Give it a descriptive name
4. Copy the token to your `.env` file

#### Bitbucket SSH Setup
1. Generate SSH key: `ssh-keygen -t rsa -b 4096 -C "your-email@example.com"`
2. Add public key to [Bitbucket SSH Keys](https://bitbucket.org/account/settings/ssh-keys/)
3. Test connection: `ssh -T git@bitbucket.org`

## 🔧 Usage Examples

### With Amazon Q CLI

```bash
# Search for Jira issues
q chat "Search for issues assigned to me in project SCRUM"

# Create a new issue
q chat "Create a bug report in project DEV with title 'API returning 500 errors'"

# Create feature branch for an issue
q chat "Create a feature branch for issue SCRUM-123 in the main repository"

# Update issue status
q chat "Move issue SCRUM-123 to In Progress"
```

### Available MCP Tools

- `jira-server___search_issues` - Search Jira issues with JQL
- `jira-server___get_issue` - Get detailed issue information
- `jira-server___create_issue` - Create new Jira issues
- `jira-server___update_issue` - Update existing issues
- `jira-server___add_comment` - Add comments to issues
- `jira-server___transition_issue` - Change issue status
- `bitbucket-git___clone_repository` - Clone repositories
- `bitbucket-git___create_branch` - Create feature branches
- `bitbucket-git___git_status` - Check repository status

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Assistant  │    │   MCP Server    │    │   Jira/Bitbucket│
│   (Q CLI, etc.) │◄──►│  (This Project) │◄──►│   APIs          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

The server acts as a bridge between AI assistants and your development tools, providing a standardized interface for common development workflows.

## 🐳 Docker Deployment

### Development
```bash
docker-compose up -d
```

### Production
```bash
# Use production profile with nginx
docker-compose --profile production up -d
```

### Custom Configuration
```bash
# Use custom environment file
docker-compose --env-file .env.production up -d
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src

# Run specific test
python -m pytest tests/test_jira_integration.py
```

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Logs
```bash
# Docker logs
docker-compose logs -f jira-mcp-server

# Local logs
tail -f mcp-server.log
```

## 🔒 Security

- **API Tokens**: Store securely in environment variables
- **SSH Keys**: Use read-only access where possible
- **Network**: Run in isolated Docker network
- **User**: Container runs as non-root user
- **Secrets**: Never commit credentials to version control

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Run code formatting
black src/ tests/
flake8 src/ tests/

# Run type checking
mypy src/
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 **Documentation**: Check the [docs/](docs/) directory
- 🐛 **Issues**: Report bugs on [GitHub Issues](https://github.com/yourusername/jira-mcp-server/issues)
- 💬 **Discussions**: Join [GitHub Discussions](https://github.com/yourusername/jira-mcp-server/discussions)

## 🙏 Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io) for the standard
- [Amazon Q](https://aws.amazon.com/q/) for AI assistant integration
- [Atlassian](https://atlassian.com) for Jira and Bitbucket APIs

---

**Made with ❤️ by [Sandeep Nalam](https://github.com/yourusername)**
