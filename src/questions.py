"""An explicit allowlist of result-grounded questions; no language model."""
from src.trends import explanation

QUESTIONS = ["What is the trend?", "What is the slope?", "How complete is the data?", "What is the source?"]


def answer(question, result, provenance, completeness):
    q = question.strip().lower().rstrip("?")
    if q == "what is the trend":
        return explanation(result)
    if q == "what is the slope":
        return f"{result.slope:+.4f} °C/year; 95% CI {result.low:+.4f} to {result.high:+.4f} °C/year. Unadjusted for serial dependence."
    if q == "how complete is the data":
        return f"{completeness:.1%} of requested daily values are valid; {result.n} years passed the annual and monthly screens."
    if q == "what is the source":
        return provenance["source"] + ". " + provenance.get("request_url", "No NASA observations used.")
    return "Unsupported question. I only answer the four listed questions from this analysis; I cannot infer causes, tomorrow’s weather, or flood forecasts."
