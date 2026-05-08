"""Global constants used across the TGIT project."""

DEFAULT_MODEL = "gpt-4o-mini"
OPENAI_DEFAULT_MODEL = "gpt-4o-mini"
DEEPSEEK_DEFAULT_MODEL = "deepseek-chat"
ANTHROPIC_DEFAULT_MODEL = "claude-3-5-haiku-20241022"
GEMINI_DEFAULT_MODEL = "gemini-2.5-flash"

# Provider presets: maps provider name to (default_base_url, env_var_for_api_key, default_model)
PROVIDER_PRESETS: dict[str, tuple[str, str, str]] = {
    "openai": ("https://api.openai.com/v1", "OPENAI_API_KEY", OPENAI_DEFAULT_MODEL),
    "deepseek": ("https://api.deepseek.com/v1", "DEEPSEEK_API_KEY", DEEPSEEK_DEFAULT_MODEL),
    "anthropic": ("", "ANTHROPIC_API_KEY", ANTHROPIC_DEFAULT_MODEL),
    "google": ("", "GEMINI_API_KEY", GEMINI_DEFAULT_MODEL),
    "gemini": ("", "GEMINI_API_KEY", GEMINI_DEFAULT_MODEL),
    "auto": ("", "", DEFAULT_MODEL),
}

# OpenAI-specific reasoning model hints (only applied when provider is openai)
OPENAI_REASONING_MODEL_HINTS = ("-reasoning", "o1", "o3", "o4", "gpt-5")
REASONING_EFFORT_CHOICES = ("none", "minimal", "low", "medium", "high", "xhigh")
