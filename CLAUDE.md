# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered codebase tutorial generator that analyzes GitHub repositories or local directories to create beginner-friendly documentation. It uses PocketFlow (a 100-line LLM framework) to orchestrate a sequential workflow that identifies core abstractions, analyzes their relationships, and generates comprehensive tutorials with visualizations.

## Development Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Test LLM configuration
python utils/call_llm.py
```

### Running the Application
```bash
# Analyze a GitHub repository
python main.py --repo https://github.com/username/repo --include "*.py" "*.js" --exclude "tests/*" --max-size 50000

# Analyze a local directory
python main.py --dir /path/to/your/codebase --include "*.py" --exclude "*test*"

# Generate tutorial in different language
python main.py --repo https://github.com/username/repo --language "Chinese"

# A command to analyze a real local project (nextpnr-xilinx-win-Example)
python main.py --dir D:/Documents/workspace/cpp/nextpnr-xilinx-win-Example --include "*.h" --exclude "*.yml" ".cirrus/*" ".git/*" ".vs/*" "*/3rdparty/*" --max-size 5000 --language "Chinese"
```

### Docker
```bash
# Build Docker image
docker build -t pocketflow-app .

# Run with mounted output directory (OpenAI)
docker run -it --rm \
  -e OPENAI_API_KEY="YOUR_API_KEY" \
  -v "$(pwd)/output_tutorials":/app/output \
  pocketflow-app --repo https://github.com/username/repo

# Run with Gemini API key
docker run -it --rm \
  -e GEMINI_API_KEY="YOUR_API_KEY" \
  -v "$(pwd)/output_tutorials":/app/output \
  pocketflow-app --repo https://github.com/username/repo
```

## Architecture

### Core Workflow (flow.py)
The application uses PocketFlow's sequential node processing:
1. **FetchRepo** → **IdentifyAbstractions** → **AnalyzeRelationships** → **OrderChapters** → **WriteChapters** → **CombineTutorial**

### Key Nodes (nodes.py)
- **FetchRepo**: Crawls GitHub repos or local directories using `utils/crawl_github_files.py` or `utils/crawl_local_files.py`
- **IdentifyAbstractions**: Uses LLM to identify 5-10 core abstractions with file indices
- **AnalyzeRelationships**: Generates project summary and abstraction relationships
- **OrderChapters**: Determines optimal tutorial chapter sequence
- **WriteChapters** (BatchNode): Generates detailed Markdown chapters in parallel
- **CombineTutorial**: Assembles final tutorial with Mermaid diagrams

### Shared State Structure
The workflow maintains a shared dictionary containing:
- Input parameters (repo_url, local_dir, project_name, language, etc.)
- File data as list of (path, content) tuples
- Abstractions with file indices and relationships
- Generated chapters and final output directory

### LLM Integration (utils/call_llm.py)
- Supports multiple LLM providers (Gemini, OpenAI, Azure OpenAI, Anthropic Claude, OpenRouter)
- Implements caching in `llm_cache.json` to avoid redundant API calls
- Logs all interactions to `logs/llm_calls_YYYYMMDD.log`
- Currently configured for OpenAI GPT-4o-mini

#### OpenAI API Configuration
The current OpenAI integration requires proper API method calls:
- Use `client.chat.completions.create()` instead of `client.responses.create()`
- Access response with `response.choices[0].message.content` instead of `response.output_text`
- Pass `messages=[{"role": "user", "content": prompt}]` parameter

### Multi-language Support
The system supports generating tutorials in different languages:
- Translates abstraction names, descriptions, and content
- Keeps technical terms and fixed UI elements in English
- Uses language-specific prompting strategies

### File Processing
- Default include patterns: `*.py`, `*.js`, `*.jsx`, `*.ts`, `*.tsx`, `*.go`, `*.java`, etc.
- Default exclude patterns: `tests/*`, `*venv/*`, `node_modules/*`, etc.
- Respects `.gitignore` patterns when crawling local directories
- Configurable file size limits (default 100KB)

### Error Handling
- Nodes have built-in retry mechanisms (max_retries=5, wait=20)
- Robust YAML/JSON parsing with fallback strategies
- Validation of LLM outputs with specific error messages

### Output Structure
Generated tutorials include:
- `index.md`: Project overview with Mermaid relationship diagram
- `01_concept.md`, `02_concept.md`, etc.: Individual chapter files
- Structured in `output/{project_name}/` directory

## Common Issues and Solutions

### OpenAI API Integration
If switching from Gemini to OpenAI, ensure `utils/call_llm.py:69-70` uses:
```python
response = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": prompt}],
    max_tokens=50000
)
response_text = response.choices[0].message.content
```

### LLM Response Parsing
The system expects YAML/JSON structured responses from LLMs. If changing providers, verify:
- Response format matches expected structure
- `extract_structured_block()` in nodes.py:32-85 can parse the output
- Retry mechanisms handle parsing failures appropriately