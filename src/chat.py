"""Free-text, deterministic analysis assistant. Every number comes from selected data."""
import re
from dataclasses import dataclass
import pandas as pd
from src.trends import analyze, explanation


@dataclass
class Reply:
    text: str
    derivation: str


def respond(question, annual, processed, provenance):
    q = " ".join(question.lower().strip().split())
    units = provenance["units"]
    variable = provenance["variable"]
    accepted = annual.loc[annual.included].sort_values("year")
    context = f"{provenance['location']} · {variable} · {provenance['source']}"
    def reply(text, how):
        return Reply(text, context + "\n" + how)
    if not q:
        return reply("Ask about the trend, a particular year, comparisons, uncertainty, missing data, or methods.", "No calculation requested.")
    # Check claims that require unavailable evidence before interpreting numeric dates.
    if re.search(r"\b(tomorrow|forecast|predict|next year|next week|future|will it|will there)\b", q):
        return reply("This analysis cannot predict future conditions. It describes the selected historical record; extrapolating the fitted trend is not a validated forecast.", "No forecasting function exists; no prediction calculated.")
    if re.search(r"\b(why|cause|caused|causes|causing|reason|responsible|because|attribution)\b", q) and not re.search(r"\b(excluded|missing|gap|p-value|significant|confidence)\b", q):
        return reply("This record can show what changed, but cannot establish why. Testing a cause needs additional evidence and an attribution study. A statistically significant trend alone does not prove a cause.", "Causal attribution is outside the supported analysis; no cause inferred.")
    other_locations = {"dhaka", "mirpur", "sylhet", "chattogram", "rajshahi", "khulna", "barishal", "rangpur", "mymensingh"}
    requested_places = [p for p in other_locations if re.search(r"\b" + p + r"\b", q) and p not in provenance["location"].lower()]
    if requested_places:
        return reply(f"The loaded record is for {provenance['location']}. Select {requested_places[0].title()} and Analyze to answer that location's question. I cannot compare a location that has not been analyzed.", "Only the selected location is available.")
    if "difference" in q and "surface" in q and "air" in q:
        return reply("Surface skin temperature represents the ground or other surface; air temperature here is measured/modelled at 2 metres. They are different physical variables. Switch the variable and Analyze for its own result; this selected record does not provide their numerical difference.", "Variable definitions; no cross-variable calculation performed.")
    requested_variable = "Vegetation" if re.search(r"\b(ndvi|vegetation)\b",q) else "Rainfall / precipitation" if re.search(r"\b(rainfall|precipitation)\b",q) else "Air temperature" if "air temperature" in q else "Surface temperature" if "surface temperature" in q else None
    if requested_variable and requested_variable != variable:
        return reply(f"This result is for {variable}, not {requested_variable}. Switch the trend type and Analyze before asking for that variable's change.", "No data for the requested variable in the selected analysis.")
    if re.search(r"\b(source|dataset|nasa|provenance|resolution|satellite|where.*data)\b", q):
        details = [f"Source: {provenance['source']}.", f"Variable: {variable}; units: {units}.",
                   f"Sampling: {provenance.get('frequency', 'unknown')}.",
                   f"Spatial resolution: {provenance.get('spatial_resolution', 'not recorded')}."]
        if provenance.get("declared_source"):
            details.append(f"User-declared source: {provenance['declared_source']} (not independently verified).")
        if provenance.get("request_url"):
            details.append("[Original data request](" + provenance["request_url"] + ")")
        return reply("\n\n".join(details), "Read directly from this analysis's provenance, not a general web search.")
    if re.search(r"\b(missing|gap|gaps|complete|completeness|excluded|quality|sample|observations|coverage)\b", q):
        valid = int(processed.value.count())
        total = len(processed)
        excluded = annual.loc[~annual.included]
        text = f"{valid:,} of {total:,} expected observations are valid ({valid/total:.1%}). {len(accepted)} years passed screening; {len(excluded)} did not." if total else "No expected observations in this selection."
        if len(excluded):
            text += "\n\n" + "; ".join(f"{int(r.year)}: {r.reason}" for r in excluded.itertuples())
        if provenance.get("frequency") == "Annual":
            text += " Within-year completeness is unknown for supplied annual means."
        return reply(text, "count(nonmissing processed values) / expected timestamps; annual inclusion flags and exclusion reasons. No imputation.")
    if re.search(r"\b(method|calculate|calculated|calculation|formula|theil|mann|how.*work)\b", q):
        return reply("First, observations are screened and aggregated into annual means. Mann–Kendall compares every pair of accepted annual values to test for a monotonic trend. Theil–Sen takes the median of all pairwise value changes divided by elapsed years. Its 95% interval describes uncertainty in the slope. Missing years keep their real calendar spacing. Serial dependence and multiple comparisons are not corrected.", "Pipeline: aggregate → analyze; formulas and exclusions appear in the Evidence tab.")
    years = list(dict.fromkeys(int(y) for y in re.findall(r"\b(?:19|20)\d{2}\b", q)))
    if len(years) > 2:
        return reply("Please compare two years at a time, or ask for a trend between two years.", "No ambiguous multi-year calculation performed.")
    if years:
        unavailable = [y for y in years if y not in set(accepted.year)]
        if unavailable:
            return reply(f"No accepted annual mean is available for {', '.join(map(str,unavailable))}. It is outside the selection or failed completeness screening. Check the annual table; I won't substitute another year.", "Looked up requested years in accepted annual observations.")
        if len(years) == 2 and re.search(r"\b(trend|slope|significant)\b", q):
            subset = annual.loc[annual.year.between(min(years),max(years))]
            try:
                result = analyze(subset)
                return reply(explanation(result, variable.lower(), units), f"Recomputed analyze() for accepted years in {min(years)}–{max(years)}; n={result.n}, S={result.s}, p={result.p:.6g}.")
            except ValueError as exc:
                return reply(str(exc), "Requested interval did not meet the minimum sample requirement; no trend inferred.")
        selected = accepted.set_index("year")
        if len(years) == 1:
            row = selected.loc[years[0]]
            return reply(f"The accepted {years[0]} annual mean was {row.annual_mean:.4f} {units}. This is an annual mean, not an individual day's value.", f"Direct lookup of annual_mean for {years[0]}.")
        first,last = sorted(years)
        v1,v2 = selected.loc[first,"annual_mean"],selected.loc[last,"annual_mean"]
        return reply(f"{first}: {v1:.4f} {units}. {last}: {v2:.4f} {units}. The difference is {v2-v1:+.4f} {units} ({last} minus {first}). Two endpoints alone do not establish a long-term trend.", f"annual_mean[{last}] − annual_mean[{first}]. This is observed endpoint change, not the fitted slope.")
    if re.search(r"\b(season|seasonal|month|monthly|summer|winter|monsoon)\b", q):
        return reply("The current trend test uses annual means. It does not test seasonal changes or identify a changing monsoon. You can inspect the original observations, but a seasonal-trend question needs a separate seasonal method.", "No seasonal significance test is implemented; no seasonal claim made.")
    if accepted.empty:
        return reply("No years passed quality screening. Ask about missing data or select a longer, more complete record.", "Zero accepted annual means; no trend or extrema calculated.")
    if re.search(r"\b(highest|lowest|maximum|minimum|hottest|coldest|warmest|coolest|wettest|driest|greenest|peak)\b", q):
        hi,lo = accepted.annual_mean.max(),accepted.annual_mean.min()
        high_years = ", ".join(map(str,accepted.loc[accepted.annual_mean==hi,"year"]))
        low_years = ", ".join(map(str,accepted.loc[accepted.annual_mean==lo,"year"]))
        return reply(f"Among accepted annual means, the highest was {hi:.4f} {units} in {high_years}; the lowest was {lo:.4f} {units} in {low_years}. These are annual averages, not daily extremes.", "max/min of accepted annual_mean; all tied years shown.")
    if re.search(r"\b(average|mean)\b", q) and not re.search(r"\b(trend|change|changed)\b", q):
        return reply(f"The equally weighted mean across {len(accepted)} accepted annual values is {accepted.annual_mean.mean():.4f} {units}. Each accepted year has equal weight.", "mean(accepted annual_mean), not a mean over every original observation.")
    try:
        result = analyze(annual)
    except ValueError as exc:
        return reply(str(exc), "analyze() declined inference because fewer than ten years passed screening.")
    how = f"Recomputed analyze(): n={result.n}, S={result.s}, Z={result.z:.5f}, p={result.p:.6g}; units {units}/year. No cached narrative or invented numbers."
    if re.search(r"\b(significant|significance|p-value|p value|certain|uncertain|uncertainty|confidence|reliable|trust|real)\b", q):
        conclusion = "passes" if result.p < .05 else "does not pass"
        return reply(f"The Mann–Kendall p-value is {result.p:.6g}, so this series {conclusion} the unadjusted 0.05 significance threshold. The 95% slope interval is {result.low:+.5f} to {result.high:+.5f} {units}/year. This is not a probability that the trend is true. Serial dependence, repeated testing and measurement uncertainty limit interpretation; significance does not prove causation.", how)
    if re.search(r"\b(change|changed|changing|trend|slope|rise|rising|increase|increasing|decrease|decreasing|warming|cooling|summary|summarize|explain|hotter|colder|greener|wetter|drier|result)\b", q):
        return reply(explanation(result,variable.lower(),units),how)
    return reply("I can calculate the trend, compare two years, find highest/lowest annual means, and explain significance, gaps, sources and methods for this selection. I cannot answer that question from the available analysis. Try ‘Compare 2005 and 2020’ or ‘How certain is this change?’.", "No matching supported analysis; no unsupported answer generated.")
