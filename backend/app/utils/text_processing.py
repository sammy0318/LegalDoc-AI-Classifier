import re


def normalize(text: str) -> str:
    """Port of qaMatcher.js normalize().
    Lowercase, strip non-alphanumeric (keep spaces), collapse whitespace.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def jaccard_similarity(a: str, b: str) -> float:
    """Port of qaMatcher.js similarity().
    Returns intersection / max(|A|, |B|) on word-level sets.
    NOTE: The existing JS uses max(A.size, B.size), NOT standard Jaccard (union).
    We preserve this exactly for behavioral parity.
    """
    set_a = set(a.split())
    set_b = set(b.split())
    if not set_a and not set_b:
        return 0.0
    intersection = set_a & set_b
    return len(intersection) / max(len(set_a), len(set_b))


def strip_markdown(text: str) -> str:
    """Return a plaintext version of `text` with common Markdown removed.

    This is a minimal, conservative stripper sufficient for our UI: removes
    headings (#), bold/italic markers (*, _, **, __), code fences/backticks,
    list markers (-, *, +), blockquotes (>), and converts links [text](url)
    to `text`.
    """
    if not text:
        return text
    # Remove code fences ```...``` and inline backticks
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    # Convert markdown links [text](url) -> text
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    # Remove images ![alt](url) -> alt
    text = re.sub(r"!\[([^\]]*)\]\([^\)]+\)", r"\1", text)
    # Remove heading markers #### -> newline
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.M)
    # Remove emphasis markers *, **, _, __
    text = re.sub(r"(\*\*|__)(.*?)\1", r"\2", text)
    text = re.sub(r"(\*|_)(.*?)\1", r"\2", text)
    # Remove list markers at line starts
    text = re.sub(r"^[\s>*-]*([-+\*]|\d+\.)\s+", "", text, flags=re.M)
    # Remove blockquote markers
    text = re.sub(r"^>\s?", "", text, flags=re.M)
    # Remove horizontal rules
    text = re.sub(r"^(-{3,}|\*{3,})$", "", text, flags=re.M)
    # Collapse multiple newlines to max two
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Trim leading/trailing whitespace
    return text.strip()
