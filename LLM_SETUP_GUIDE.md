# 🤖 LLM Provider Setup Guide

This guide covers setting up the various LLM providers supported by the Fraud Graph Intelligence demo. You can configure **one or more** providers and switch between them in the UI.

## Quick Comparison

| Provider | Speed | Free Tier | Best For | Setup Difficulty |
|----------|-------|-----------|----------|------------------|
| **Groq** | ⚡⚡⚡⚡ (300 tok/s) | 14,400 req/day | Most users | Easy |
| **Gemini** | ⚡⚡⚡ | 15 RPM, 1M tok/day | Google users | Easy |
| **OpenRouter** | ⚡⚡⚡ | Varies by model | Model variety | Easy |
| **Cerebras** | ⚡⚡⚡⚡⚡ (2000 tok/s) | Limited | Maximum speed | Medium |

---

## 🚀 Groq (Recommended)

**Why Groq?**
- Blazing fast inference (300+ tokens/second)
- Generous free tier (14,400 requests/day)
- Llama 3.3 70B is excellent at Cypher generation
- No credit card required

### Setup Steps

1. **Create Account**
   - Go to [console.groq.com](https://console.groq.com)
   - Sign up with email or Google/GitHub

2. **Generate API Key**
   - Navigate to "API Keys" section
   - Click "Create API Key"
   - Copy the key (starts with `gsk_`)

3. **Add to secrets.toml**
   ```toml
   [groq]
   api_key = "gsk_xxxxxxxxxxxxxxxxxxxx"
   ```

4. **Install SDK**
   ```bash
   pip install groq
   ```

### Available Models
- `llama-3.3-70b-versatile` - Best for complex Cypher queries (default)
- `llama-3.1-70b-versatile` - Slightly older but very stable
- `mixtral-8x7b-32768` - Good for longer context windows

### Rate Limits (Free Tier)
- 14,400 requests/day
- 6,000 tokens/minute
- 30 requests/minute

---

## 🧠 Google Gemini

**Why Gemini?**
- Google's flagship model with strong reasoning
- Good balance of speed and quality
- Large context window

### Setup Steps

1. **Create/Use Google Account**
   - Go to [aistudio.google.com](https://aistudio.google.com)
   - Sign in with your Google account

2. **Generate API Key**
   - Click "Get API Key" in the sidebar
   - Click "Create API Key"
   - Select a Google Cloud project (or create new)
   - Copy the generated key

3. **Add to secrets.toml**
   ```toml
   [gemini]
   api_key = "AIzaSy..."
   ```

4. **Install SDK**
   ```bash
   pip install google-generativeai
   ```

### Available Models
- `gemini-2.0-flash` - Latest and fastest (default)
- `gemini-1.5-flash-latest` - Stable, well-tested
- `gemini-pro` - Original model, very reliable

### Rate Limits (Free Tier)
- 15 requests/minute
- 1,000,000 tokens/day
- 1,500 requests/day

### Troubleshooting
- **404 Error**: The model may not be available in your region. Try a different model.
- **API Key not working**: Ensure you've enabled the Generative AI API in Google Cloud Console.

---

## 🌐 OpenRouter

**Why OpenRouter?**
- Single API for 30+ models
- Multiple free model options
- Easy to switch between providers
- Good fallback when other providers are down

### Setup Steps

1. **Create Account**
   - Go to [openrouter.ai](https://openrouter.ai)
   - Sign up with email or OAuth

2. **Generate API Key**
   - Go to [openrouter.ai/keys](https://openrouter.ai/keys)
   - Click "Create Key"
   - Copy the key (starts with `sk-or-`)

3. **Add to secrets.toml**
   ```toml
   [openrouter]
   api_key = "sk-or-v1-xxxxxxxxxxxx"
   ```

4. **Install SDK**
   ```bash
   pip install openai  # OpenRouter uses OpenAI-compatible API
   ```

### Free Models Available
- `meta-llama/llama-3.3-70b-instruct:free` - Best free option (default)
- `google/gemini-2.0-flash-exp:free` - Google's experimental
- `mistralai/mistral-7b-instruct:free` - Fast and capable
- `microsoft/phi-3-mini-128k-instruct:free` - Small but effective

### Rate Limits
- Varies by model
- Free models have lower limits
- Check [openrouter.ai/docs](https://openrouter.ai/docs) for current limits

---

## ⚡ Cerebras

**Why Cerebras?**
- World's fastest inference (2000+ tokens/second)
- Uses revolutionary wafer-scale chips
- 6x faster than Groq

### Setup Steps

1. **Create Account**
   - Go to [cloud.cerebras.ai](https://cloud.cerebras.ai)
   - Sign up for an account
   - May require approval/waitlist

2. **Generate API Key**
   - Navigate to API Keys section in dashboard
   - Create a new API key
   - Copy the key

3. **Add to secrets.toml**
   ```toml
   [cerebras]
   api_key = "csk-xxxxxxxxxxxx"
   ```

4. **Install SDK**
   ```bash
   pip install openai  # Cerebras uses OpenAI-compatible API
   ```

### Available Models
- `llama-3.3-70b` - Latest Llama (default)
- `llama-3.1-8b` - Smaller and even faster

### Notes
- Cerebras availability may be limited
- Check their status page if you encounter issues
- Best for users who need maximum speed

---

## 📝 Complete Configuration Example

Here's a `secrets.toml` with all providers configured:

```toml
# =============================================================================
# NEO4J DATABASE (Required)
# =============================================================================
[neo4j]
uri = "neo4j+s://xxxxxxxx.databases.neo4j.io"
user = "neo4j"
password = "your-neo4j-password"

# =============================================================================
# LLM PROVIDERS (Configure one or more)
# =============================================================================

# Groq - Recommended
[groq]
api_key = "gsk_your_groq_key_here"

# Google Gemini
[gemini]
api_key = "AIzaSy_your_gemini_key_here"

# OpenRouter
[openrouter]
api_key = "sk-or-v1-your_openrouter_key_here"

# Cerebras
[cerebras]
api_key = "csk-your_cerebras_key_here"
```

---

## 🔧 Installation

Install all required SDKs:

```bash
# Core requirements
pip install streamlit neo4j streamlit-agraph

# LLM SDKs
pip install groq                    # For Groq
pip install google-generativeai     # For Gemini
pip install openai                  # For OpenRouter & Cerebras
```

Or install everything at once:

```bash
pip install -r requirements.txt
```

---

## ⚠️ Security Best Practices

1. **Never commit secrets.toml to version control**
   ```bash
   # Add to .gitignore
   echo ".streamlit/secrets.toml" >> .gitignore
   ```

2. **Use environment variables in production**
   ```bash
   export GROQ_API_KEY="gsk_..."
   ```

3. **Rotate keys periodically**
   - All providers allow you to create multiple keys
   - Revoke old keys when creating new ones

4. **Monitor usage**
   - Check provider dashboards for unusual activity
   - Set up billing alerts if using paid tiers

---

## 🐛 Common Issues

### "Model not found" (404)
- The model name may have changed
- Try a different model from the dropdown
- Check the provider's documentation for current model names

### "Rate limit exceeded" (429)
- You've hit your free tier limit
- Wait and try again later
- Consider adding another provider as backup

### "Authentication failed" (401/403)
- API key is invalid or expired
- Regenerate your API key
- Check that the key is correctly copied (no extra spaces)

### "Connection refused"
- Provider may be experiencing downtime
- Check their status page
- Try a different provider

---

## 💡 Tips for Best Results

1. **Use Groq for development** - Fastest feedback loop
2. **Use Gemini for complex queries** - Best reasoning
3. **Keep OpenRouter as backup** - Works when others are down
4. **Test all providers** - Use the Administration page's test feature

---

## 📚 Additional Resources

- [Groq Documentation](https://console.groq.com/docs)
- [Google AI Studio](https://aistudio.google.com)
- [OpenRouter Docs](https://openrouter.ai/docs)
- [Cerebras Cloud](https://cloud.cerebras.ai/docs)
