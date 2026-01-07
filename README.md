# Gemini + E2B Code Execution Agent

A simple CLI agent that uses **Google Gemini** to write Python code and **E2B** to execute it securely.

## Features

- 🤖 **Gemini AI** - Powered by Google's latest language model
- 🔒 **Secure Execution** - Code runs in isolated E2B sandbox
- 💬 **Conversational** - Multi-turn conversations with context
- 📦 **Package Support** - Install and use Python packages
- 🔄 **Error Handling** - Graceful error recovery

## Architecture

```
User Input → Gemini (via Vertex AI) → Code Generation → E2B Sandbox → Results
              ↑ (ADC Auth)                                ↑ (API Key)
```

## Prerequisites

1. **Google Cloud Project** with Vertex AI API enabled
2. **E2B Account** with API key
3. **Python 3.8+**
4. **gcloud CLI** installed and configured

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Google Cloud Authentication (ADC)

```bash
# Authenticate with Google Cloud
gcloud auth application-default login

# Set your project (optional)
gcloud config set project YOUR_PROJECT_ID
```

This sets up **Application Default Credentials (ADC)** which the agent uses to authenticate with Vertex AI.

### 3. Get E2B API Key

1. Visit https://e2b.dev/
2. Sign up for a free account
3. Go to dashboard → API Keys
4. Create a new key and copy it

### 4. Configure Environment

```bash
# Copy the template
cp .env.template .env

# Edit .env and add your keys
nano .env  # or use your preferred editor
```

Required in `.env`:
```bash
E2B_API_KEY=your-actual-e2b-key

# Optional (can be set at runtime)
GCP_PROJECT_ID=your-gcp-project-id
GCP_LOCATION=us-central1
GEMINI_MODEL=gemini-2.0-flash-exp
```

### 5. Verify Setup

Test that everything is configured correctly:

```bash
# This should not error
python -c "import config"
```

You should see:
```
✓ Configuration loaded
  E2B API Key: ********************xyz
  GCP Location: us-central1
  Gemini Model: gemini-2.0-flash-exp
```

## Usage

### Start the Agent

```bash
python simple_agent.py
```

If you didn't set `GCP_PROJECT_ID` in `.env`, you'll be prompted:
```
Enter your GCP Project ID: my-project-123
```

### Example Session

```
You: Calculate the first 10 Fibonacci numbers

🤖 Gemini is thinking...

Agent: I'll write a function to calculate the Fibonacci sequence:

```python
def fibonacci(n):
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib[:n]

result = fibonacci(10)
print(result)
```

This creates a list starting with 0 and 1, then builds the sequence
by adding consecutive numbers.

──────────────────────────────────────────────────────────────────────
Found 1 code block(s) to execute
──────────────────────────────────────────────────────────────────────

▶ Executing code block 1/1...

📤 Output:
[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

──────────────────────────────────────────────────────────────────────

You: Now find their sum and average

🤖 Gemini is thinking...

Agent: Here's the sum and average:

```python
numbers = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
total = sum(numbers)
average = total / len(numbers)

print(f"Sum: {total}")
print(f"Average: {average}")
```

▶ Executing code block 1/1...

📤 Output:
Sum: 88
Average: 8.8

You: quit
👋 Goodbye!
✓ Sandbox closed
```

## Example Prompts

Try these to see what the agent can do:

### Math & Computation
```
- What's the factorial of 20?
- Calculate the first 100 prime numbers
- Solve the quadratic equation x^2 + 5x + 6 = 0
```

### Data Analysis
```
- Generate 1000 random numbers and show their distribution
- Create a list of squares from 1 to 50 and find their sum
- Calculate the standard deviation of [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
```

### Visualization (if matplotlib available)
```
- Create a bar chart of [5, 10, 15, 20, 25]
- Plot a sine wave from 0 to 2π
- Create a scatter plot of random points
```

### Working with Packages
```
- Install numpy and create a 3x3 identity matrix
- Use pandas to create a dataframe with student names and grades
- Install requests and fetch a random joke from an API
```

## How It Works

1. **User asks a question** → Sent to Gemini via Vertex AI
2. **Gemini generates response** → May include Python code blocks
3. **Code extraction** → Regex finds all ```python blocks
4. **Code execution** → E2B sandbox runs the code securely
5. **Results display** → Output shown to user
6. **Context maintained** → Conversation history preserved

## File Structure

```
.
├── simple_agent.py      # Main CLI application
├── code_executor.py     # E2B sandbox wrapper
├── config.py            # Configuration loader
├── requirements.txt     # Python dependencies
├── .env.template        # Environment template
├── .env                 # Your config (create this)
└── README.md           # This file
```

## Configuration Options

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `E2B_API_KEY` | Yes | - | E2B API key from e2b.dev |
| `GCP_PROJECT_ID` | No | Prompt at runtime | Your GCP project ID |
| `GCP_LOCATION` | No | `us-central1` | Vertex AI location |
| `GEMINI_MODEL` | No | `gemini-2.0-flash-exp` | Gemini model to use |

### Gemini Models

Available models (update `GEMINI_MODEL` in `.env`):

- `gemini-2.0-flash-exp` - Latest, fastest (default)
- `gemini-1.5-pro` - Most capable, slower
- `gemini-1.5-flash` - Fast, balanced

### Generation Parameters

Edit in `simple_agent.py`:

```python
generation_config = GenerationConfig(
    temperature=0.7,      # Creativity (0-1)
    top_p=0.95,          # Nucleus sampling
    top_k=40,            # Top-k sampling
    max_output_tokens=2048,  # Max response length
)
```

## Troubleshooting

### "E2B_API_KEY not found"
- Create `.env` file from template: `cp .env.template .env`
- Add your E2B API key to `.env`

### "Failed to initialize Vertex AI"
- Run: `gcloud auth application-default login`
- Verify project exists: `gcloud projects list`
- Enable Vertex AI API: `gcloud services enable aiplatform.googleapis.com`

### "Could not automatically determine credentials"
- Your ADC is not set up
- Run: `gcloud auth application-default login`
- Or set: `export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json`

### "Permission denied" or "API not enabled"
- Enable Vertex AI API in your project
- Console: https://console.cloud.google.com/apis/library/aiplatform.googleapis.com
- Or CLI: `gcloud services enable aiplatform.googleapis.com`

### Code execution fails
- Check E2B sandbox status: Agent prints sandbox ID on startup
- Try simpler code first: `print("Hello")`
- Check E2B service status: https://status.e2b.dev

### Package installation fails
- Some packages require system dependencies
- Try common packages first: numpy, pandas, matplotlib
- E2B has many packages pre-installed

### "Model not found" error
- Check model name in `.env` matches available models
- Verify region supports your chosen model
- Try default: `gemini-2.0-flash-exp`

## Advanced Usage

### Multi-turn Conversations

The agent maintains conversation history, so you can have contextual exchanges:

```
You: Create a list of numbers from 1 to 10
Agent: [creates list]

You: Now square each number
Agent: [uses previous list, squares them]

You: Find their average
Agent: [calculates average of squared numbers]
```

### Installing Packages

Just ask naturally:

```
You: Install the requests library and fetch data from https://api.github.com/zen
```

Gemini will:
1. Write code to install requests
2. Write code to fetch the data
3. Both will be executed automatically

### Error Recovery

If code has errors, the agent sees them:

```
You: Calculate 1/0

Agent: [writes code with division by zero]

❌ Error:
ZeroDivisionError: division by zero

💬 Sending error back to Gemini for debugging...
```

## Limitations

- E2B free tier has usage limits (check e2b.dev for details)
- Each session creates a new sandbox (state not preserved between runs)
- Large outputs may be truncated
- Network access in sandbox may be limited
- Some system-level operations not available

## Security

- Code runs in isolated E2B sandbox
- No access to your local filesystem
- Network access limited by E2B
- Sandboxes are ephemeral (destroyed after use)

## Cost Considerations

- **E2B**: Free tier available, check pricing at e2b.dev
- **Vertex AI**: Gemini usage billed to your GCP project
  - gemini-2.0-flash-exp: Very low cost
  - gemini-1.5-pro: Higher cost, more capable
  - Check current pricing: https://cloud.google.com/vertex-ai/pricing

## Next Steps

To extend this agent:

1. **Add file upload** - Let users upload CSV/data files
2. **Save conversation** - Persist chat history to database
3. **Visualization** - Automatically save and display plots
4. **Tool calling** - Use Gemini's function calling for explicit tools
5. **Web interface** - Build a Streamlit/Gradio UI
6. **Scheduled tasks** - Run code on schedule
7. **Monitoring** - Add logging and metrics

## Resources

- **E2B Docs**: https://e2b.dev/docs
- **Vertex AI Docs**: https://cloud.google.com/vertex-ai/docs
- **Gemini API**: https://ai.google.dev/docs
- **ADC Setup**: https://cloud.google.com/docs/authentication/application-default-credentials

## License

MIT License - feel free to use and modify as needed.

---

Built with ❤️ using [Google Gemini](https://deepmind.google/technologies/gemini/) and [E2B](https://e2b.dev/)
