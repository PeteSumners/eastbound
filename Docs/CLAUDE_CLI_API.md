# Claude CLI API Integration

## Overview

Claude Code CLI can function as a programmable API, allowing you to integrate AI capabilities into automation scripts, pipelines, and applications without requiring API keys or authentication tokens.

## Why Use Claude CLI as an API?

- **No API Keys Required** - Uses your existing Claude Code authentication
- **Cost Effective** - Included with Claude subscription, no per-request billing
- **Full Feature Access** - Same capabilities as interactive mode
- **Structured Output** - JSON format with metadata (tokens, cost, session ID)
- **Tool Control** - Enable/disable specific capabilities as needed
- **Simple Integration** - Works with any language that can call shell commands

## Basic Usage

### Text Mode (Simple Response)
```bash
echo "Your prompt here" | claude --print
```

### JSON Mode (With Metadata)
```bash
echo "Your prompt" | claude --print --output-format json
```

## Key CLI Options

| Option | Description | Example |
|--------|-------------|---------|
| `--print` | Non-interactive mode, prints response and exits | Required for API usage |
| `--output-format <format>` | Output format: `text`, `json`, `stream-json` | `--output-format json` |
| `--tools <tools>` | Specify allowed tools or `""` to disable all | `--tools "Read,Write"` |
| `--model <model>` | Choose model: `sonnet`, `opus`, `haiku` | `--model haiku` |
| `--fallback-model <model>` | Auto-fallback when primary overloaded | `--fallback-model haiku` |
| `--system-prompt <prompt>` | Custom system prompt | `--system-prompt "You are..."` |
| `--session-id <uuid>` | Use specific session ID for context | `--session-id <uuid>` |

## JSON Response Structure

When using `--output-format json`, you receive a structured response:

```json
{
  "type": "result",
  "subtype": "success",
  "is_error": false,
  "result": "The actual response text",
  "session_id": "b814239f-be28-4cec-9cea-be9015fb523f",
  "duration_ms": 2788,
  "duration_api_ms": 6659,
  "num_turns": 1,
  "total_cost_usd": 0.010406,
  "usage": {
    "input_tokens": 2,
    "cache_creation_input_tokens": 327,
    "cache_read_input_tokens": 16989,
    "output_tokens": 36,
    "service_tier": "standard"
  },
  "modelUsage": {
    "claude-sonnet-4-5-20250929": {
      "inputTokens": 2,
      "outputTokens": 116,
      "cacheReadInputTokens": 16989,
      "costUSD": 0.00806895
    }
  },
  "permission_denials": []
}
```

## Python Integration

### Basic Function

```python
import subprocess
import json

def ask_claude(prompt, output_format="text", tools=None):
    """
    Send a prompt to Claude Code CLI and get the response.

    Args:
        prompt (str): The question or task for Claude
        output_format (str): "text", "json", or "stream-json"
        tools (str): Comma-separated tools or "" for none

    Returns:
        str or dict: Response (dict if output_format="json")
    """
    cmd = ["claude.cmd", "--print", "--output-format", output_format]

    if tools is not None:
        cmd.extend(["--tools", tools])

    result = subprocess.run(
        cmd,
        input=prompt,
        capture_output=True,
        text=True,
        check=True
    )

    if output_format == "json":
        return json.loads(result.stdout)
    return result.stdout.strip()
```

### Example Usage

```python
# Simple text query
answer = ask_claude("What is 2+2?")
print(answer)  # "4"

# JSON with metadata
response = ask_claude(
    "Explain Python in one sentence.",
    output_format="json"
)
print(response['result'])
print(f"Cost: ${response['total_cost_usd']:.6f}")
print(f"Tokens: {response['usage']['output_tokens']}")

# No tools (pure reasoning)
analysis = ask_claude(
    "What are the prime factors of 84?",
    tools=""  # Disable all tools
)
```

## PowerShell Integration

```powershell
# Simple text response
$response = "What is the capital of France?" | claude.cmd --print
Write-Output $response

# JSON response
$json = "Summarize this text" | claude.cmd --print --output-format json
$result = $json | ConvertFrom-Json
Write-Output $result.result
Write-Output "Cost: $($result.total_cost_usd)"
```

## Bash/Shell Integration

```bash
#!/bin/bash

# Simple query
response=$(echo "What is 2+2?" | claude --print)
echo "$response"

# JSON with jq parsing
result=$(echo "Explain Docker" | claude --print --output-format json)
echo "$result" | jq -r '.result'
echo "Cost: $(echo "$result" | jq -r '.total_cost_usd')"
```

## Use Cases

### 1. Content Analysis
```python
def analyze_sentiment(text):
    prompt = f"Analyze sentiment (POSITIVE/NEGATIVE/NEUTRAL): {text}"
    return ask_claude(prompt)
```

### 2. Data Extraction
```python
def extract_keywords(article):
    prompt = f"Extract top 5 keywords from this article:\n\n{article}"
    return ask_claude(prompt, tools="")
```

### 3. Content Generation
```python
def generate_summary(briefing_json):
    prompt = f"""
    Create a 3-paragraph summary of this news briefing:
    {json.dumps(briefing_json, indent=2)}
    """
    return ask_claude(prompt)
```

### 4. Batch Processing
```python
for file in article_files:
    with open(file) as f:
        content = f.read()

    analysis = ask_claude(
        f"Analyze this article:\n\n{content}",
        output_format="json"
    )

    save_analysis(analysis)
```

## Advanced Features

### Streaming Mode
```bash
echo "Your prompt" | claude --print \
  --output-format stream-json \
  --include-partial-messages
```

### Custom System Prompts
```bash
echo "Analyze this" | claude --print \
  --system-prompt "You are a geopolitical analyst specializing in Eastern Europe"
```

### Tool Restrictions
```bash
# Only allow reading files
echo "Summarize report.md" | claude --print --tools "Read"

# Disable all tools (pure reasoning)
echo "What is 15 * 23?" | claude --print --tools ""
```

### Session Continuity
```bash
# Use same session for related queries
SESSION_ID=$(uuidgen)

echo "Question 1" | claude --print --session-id $SESSION_ID
echo "Follow-up question" | claude --print --session-id $SESSION_ID
```

## Cost Tracking

JSON mode provides detailed cost information:

```python
response = ask_claude("Your prompt", output_format="json")

print(f"Total Cost: ${response['total_cost_usd']:.6f}")
print(f"Input Tokens: {response['usage']['input_tokens']}")
print(f"Output Tokens: {response['usage']['output_tokens']}")
print(f"Cache Hits: {response['usage']['cache_read_input_tokens']}")
print(f"Duration: {response['duration_ms']}ms")
```

## Security Best Practices

1. **Validate Input** - Never pass untrusted user input directly
2. **Restrict Tools** - Use `--tools ""` when you only need text generation
3. **Whitelist Tools** - Use `--allowed-tools` to explicitly permit specific tools
4. **Avoid Permissions Bypass** - Never use `--dangerously-skip-permissions` in production
5. **Sanitize Output** - Validate Claude's responses before using them in operations

## Error Handling

```python
def ask_claude_safe(prompt, output_format="text"):
    try:
        result = subprocess.run(
            ["claude.cmd", "--print", "--output-format", output_format],
            input=prompt,
            capture_output=True,
            text=True,
            check=True,
            timeout=120  # 2 minute timeout
        )

        if output_format == "json":
            return json.loads(result.stdout)
        return result.stdout.strip()

    except subprocess.TimeoutExpired:
        print("Claude request timed out")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Claude error: {e.stderr}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        return None
```

## Integration Examples

### Current Eastbound Pipeline

See `run_simple_automation.ps1` for a working example:

```powershell
# 1. Generate briefing
python scripts/monitor_russian_media.py --output research/$Date-briefing.json

# 2. Generate analysis with Claude
$briefing = Get-Content research/$Date-briefing.json
$prompt = @"
Analyze this news briefing and create a comprehensive analysis post.
Briefing data: $briefing
"@

$analysis = $prompt | claude.cmd --print

# 3. Save and commit
$analysis | Out-File _posts/$Date-analysis.md
git add . && git commit -m "Daily analysis: $Date [automated]"
```

## Performance Considerations

- **Response Time**: Typically 2-5 seconds for simple queries
- **Caching**: Claude CLI uses prompt caching to reduce costs on repeated contexts
- **Parallel Requests**: You can run multiple Claude CLI processes concurrently
- **Model Selection**: Use `--model haiku` for faster, cheaper responses on simple tasks

## Troubleshooting

### Command Not Found
- **Windows**: Use `claude.cmd` instead of `claude`
- **Linux/Mac**: Use `claude` directly
- **Path Issues**: Ensure Claude Code is in your PATH

### JSON Parse Errors
- Always use `--output-format json` for structured data
- Check for stderr output mixed with stdout
- Use `capture_output=True` to separate streams

### Timeout Issues
- Increase timeout for complex prompts
- Consider using `--model haiku` for faster responses
- Break large tasks into smaller chunks

## Reference

For complete CLI documentation, run:
```bash
claude --help
```

For the latest Claude Code docs, visit:
https://code.claude.com/docs
