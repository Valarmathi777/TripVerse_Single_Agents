"""
services/optimizer.py
When the calculated trip cost exceeds the user's budget, this module figures out
which category-level swaps (hotel downgrade, transport mode change, dining choice,
trimming shopping/attractions) close the gap while changing the experience as
little as possible, and returns both the savings suggestions and a recalculated
optimized breakdown.
"""
from services.calculator import (
    STYLE_TO_CATEGORY, calculate_hotel_cost, calculate_food_cost,
    calculate_transport_cost, calculate_attractions_cost,
    calculate_shopping_cost, calculate_emergency_buffer, build_daily_breakdown,
)
from utils.helpers import format_inr

# Downgrade path for each style, used one step at a time
DOWNGRADE_PATH = {"Luxury": "Standard", "Standard": "Budget", "Budget": "Budget"}

STATIC_TIPS = {
    "hotel": "Stay in a {cat} category hotel/guest house instead",
    "transport": "Use {cat} transport (bus/metro/shared auto) instead of a private cab",
    "food": "Eat at {cat} local restaurants instead of premium dining",
    "attractions": "Prioritize free attractions and skip 1-2 paid ones",
    "shopping": "Trim discretionary shopping budget",
}


def _category_step_down(style: str):
    return DOWNGRADE_PATH.get(style, style)


def optimize_budget(result: dict, sector_budgets: dict = None):
    """
    Takes the output of calculate_full_budget() and, if over budget, produces:
      - a list of human-readable savings suggestions (with estimated rupee impact)
      - a recalculated 'optimized' breakdown/summary using progressively cheaper categories
    If already within budget, returns light-touch optional suggestions instead.
    Supports custom sector_budgets comparisons and targeted recommendations.
    """
    destination = result["destination"]
    days = result["days"]
    travelers = result["travelers"]
    budget = result["budget"]
    style = result["travel_style"]
    breakdown = dict(result["breakdown"])
    total_cost = result["total_estimated_cost"]

    suggestions = []

    # 1. CUSTOM SECTOR BUDGETS COMPARISON AND DOWNGRADES
    if sector_budgets:
        optimized_breakdown = dict(breakdown)
        total_savings = 0.0
        
        # Hotel
        hotel_budget = sector_budgets.get("hotel", 0.0)
        actual_hotel = breakdown["hotel"]
        if actual_hotel > hotel_budget:
            next_style = _category_step_down(style)
            if next_style != style:
                new_hotel_cost, _ = calculate_hotel_cost(destination, days, travelers, next_style)
                hotel_saving = round(actual_hotel - new_hotel_cost, 2)
                if hotel_saving > 0:
                    optimized_breakdown["hotel"] = new_hotel_cost
                    total_savings += hotel_saving
                    suggestions.append(
                        f"⚠️ Your Hotel expense ({format_inr(actual_hotel)}) exceeds your allocated Hotel budget ({format_inr(hotel_budget)}) by {format_inr(actual_hotel - hotel_budget)}. Downsizing to {next_style.lower()} stays can save ~{format_inr(hotel_saving)}."
                    )
                else:
                    suggestions.append(
                        f"⚠️ Your Hotel expense ({format_inr(actual_hotel)}) exceeds your allocated Hotel budget ({format_inr(hotel_budget)}) by {format_inr(actual_hotel - hotel_budget)}. Consider reducing trip duration or number of rooms."
                    )
            else:
                suggestions.append(
                    f"⚠️ Your Hotel expense ({format_inr(actual_hotel)}) exceeds your allocated Hotel budget ({format_inr(hotel_budget)}) by {format_inr(actual_hotel - hotel_budget)}. Try booking budget homestays."
                )

        # Food
        food_budget = sector_budgets.get("food", 0.0)
        actual_food = breakdown["food"]
        if actual_food > food_budget:
            next_style = _category_step_down(style)
            if next_style != style:
                new_food_cost, _ = calculate_food_cost(destination, days, travelers, next_style)
                food_saving = round(actual_food - new_food_cost, 2)
                if food_saving > 0:
                    optimized_breakdown["food"] = new_food_cost
                    total_savings += food_saving
                    suggestions.append(
                        f"⚠️ Your Food expense ({format_inr(actual_food)}) exceeds your allocated Food budget ({format_inr(food_budget)}) by {format_inr(actual_food - food_budget)}. Dining at local {next_style.lower()} restaurants can save ~{format_inr(food_saving)}."
                    )
                else:
                    suggestions.append(
                        f"⚠️ Your Food expense ({format_inr(actual_food)}) exceeds your allocated Food budget ({format_inr(food_budget)}) by {format_inr(actual_food - food_budget)}. Try self-catering or street food options."
                    )
            else:
                suggestions.append(
                    f"⚠️ Your Food expense ({format_inr(actual_food)}) exceeds your allocated Food budget ({format_inr(food_budget)}) by {format_inr(actual_food - food_budget)}. Opt for budget dining local joints."
                )

        # Transport
        transport_budget = sector_budgets.get("transport", 0.0)
        actual_transport = breakdown["transport"]
        if actual_transport > transport_budget:
            next_style = _category_step_down(style)
            if next_style != style:
                new_transport_cost, _ = calculate_transport_cost(destination, days, travelers, next_style)
                transport_saving = round(actual_transport - new_transport_cost, 2)
                if transport_saving > 0:
                    optimized_breakdown["transport"] = new_transport_cost
                    total_savings += transport_saving
                    suggestions.append(
                        f"⚠️ Your Transport expense ({format_inr(actual_transport)}) exceeds your allocated Transport budget ({format_inr(transport_budget)}) by {format_inr(actual_transport - transport_budget)}. Using {next_style.lower()} transit (bus/shared cabs) can save ~{format_inr(transport_saving)}."
                    )
                else:
                    suggestions.append(
                        f"⚠️ Your Transport expense ({format_inr(actual_transport)}) exceeds your allocated Transport budget ({format_inr(transport_budget)}) by {format_inr(actual_transport - transport_budget)}. Consider public transit buses."
                    )
            else:
                suggestions.append(
                    f"⚠️ Your Transport expense ({format_inr(actual_transport)}) exceeds your allocated Transport budget ({format_inr(transport_budget)}) by {format_inr(actual_transport - transport_budget)}. Use metro or local buses."
                )

        # Attractions
        attractions_budget = sector_budgets.get("attractions", 0.0)
        actual_attractions = breakdown["attractions"]
        if actual_attractions > attractions_budget:
            attractions_saving = round(actual_attractions * 0.3, 2)
            if attractions_saving > 0:
                optimized_breakdown["attractions"] -= attractions_saving
                total_savings += attractions_saving
                suggestions.append(
                    f"⚠️ Your Attractions expense ({format_inr(actual_attractions)}) exceeds your allocated Attractions budget ({format_inr(attractions_budget)}) by {format_inr(actual_attractions - attractions_budget)}. Visiting free spots can save ~{format_inr(attractions_saving)}."
                )

        # Shopping
        shopping_budget = sector_budgets.get("shopping", 0.0)
        actual_shopping = breakdown["shopping"]
        if actual_shopping > shopping_budget:
            shopping_saving = round(actual_shopping * 0.5, 2)
            if shopping_saving > 0:
                optimized_breakdown["shopping"] -= shopping_saving
                total_savings += shopping_saving
                suggestions.append(
                    f"⚠️ Your Shopping expense ({format_inr(actual_shopping)}) exceeds your allocated Shopping budget ({format_inr(shopping_budget)}) by {format_inr(actual_shopping - shopping_budget)}. Trimming discretionary shopping can save ~{format_inr(shopping_saving)}."
                )

        # Recompute buffer
        core_subtotal = (
            optimized_breakdown["hotel"] + optimized_breakdown["food"]
            + optimized_breakdown["transport"] + optimized_breakdown["attractions"]
            + optimized_breakdown["shopping"]
        )
        optimized_breakdown["emergency"] = calculate_emergency_buffer(core_subtotal)
        optimized_total = round(core_subtotal + optimized_breakdown["emergency"], 2)
        optimized_remaining = round(budget - optimized_total, 2)

        if optimized_total > budget:
            suggestions.append(
                f"⚠️ Even with these changes, the trip may still run ~{format_inr(optimized_total - budget)} over budget. Consider reducing trip length by a day or lowering traveler count."
            )

        optimized_result = {
            **result,
            "breakdown": optimized_breakdown,
            "total_estimated_cost": optimized_total,
            "remaining": optimized_remaining,
            "is_over_budget": optimized_total > budget,
            "daily_breakdown": build_daily_breakdown(optimized_total, days),
        }

        return {
            "optimized": optimized_result,
            "suggestions": suggestions,
            "savings_applied": round(total_savings, 2),
            "original_over_by": round(total_cost - budget, 2),
        }

    # 2. DEFAULT DOWNGRADE PATH (NO SECTOR BUDGETS)
    if not result["is_over_budget"]:
        suggestions = [
            f"✓ Stay in a {_category_step_down(style)} category hotel to save further",
            "✓ Use public transport (metro/bus) instead of taxis where available",
            "✓ Visit free attractions like local markets, temples, and viewpoints",
            "✓ Eat at local restaurants rather than tourist-facing ones",
        ]
        return {
            "optimized": result,
            "suggestions": suggestions,
            "savings_applied": 0.0,
        }

    over_by = round(total_cost - budget, 2)
    working_style = style
    optimized_breakdown = dict(breakdown)
    total_savings = 0.0
    steps_taken = []

    for _ in range(2):
        if over_by - total_savings <= 0:
            break
        next_style = _category_step_down(working_style)
        if next_style == working_style:
            break

        new_hotel_cost, _ = calculate_hotel_cost(destination, days, travelers, next_style)
        hotel_saving = round(optimized_breakdown["hotel"] - new_hotel_cost, 2)
        if hotel_saving > 0:
            optimized_breakdown["hotel"] = new_hotel_cost
            total_savings += hotel_saving
            steps_taken.append({
                "category": "hotel",
                "tip": STATIC_TIPS["hotel"].format(cat=next_style.lower()),
                "estimated_saving": hotel_saving,
            })

        new_transport_cost, _ = calculate_transport_cost(destination, days, travelers, next_style)
        transport_saving = round(optimized_breakdown["transport"] - new_transport_cost, 2)
        if transport_saving > 0:
            optimized_breakdown["transport"] = new_transport_cost
            total_savings += transport_saving
            steps_taken.append({
                "category": "transport",
                "tip": STATIC_TIPS["transport"].format(cat=next_style.lower()),
                "estimated_saving": transport_saving,
            })

        working_style = next_style

    if over_by - total_savings > 0:
        next_style = _category_step_down(working_style)
        new_food_cost, _ = calculate_food_cost(destination, days, travelers, next_style)
        food_saving = round(optimized_breakdown["food"] - new_food_cost, 2)
        if food_saving > 0:
            optimized_breakdown["food"] = new_food_cost
            total_savings += food_saving
            steps_taken.append({
                "category": "food",
                "tip": STATIC_TIPS["food"].format(cat=next_style.lower()),
                "estimated_saving": food_saving,
            })

    if over_by - total_savings > 0:
        shopping_cut = round(optimized_breakdown["shopping"] * 0.5, 2)
        if shopping_cut > 0:
            optimized_breakdown["shopping"] -= shopping_cut
            total_savings += shopping_cut
            steps_taken.append({
                "category": "shopping",
                "tip": STATIC_TIPS["shopping"],
                "estimated_saving": shopping_cut,
            })

    if over_by - total_savings > 0:
        attractions_cut = round(optimized_breakdown["attractions"] * 0.3, 2)
        if attractions_cut > 0:
            optimized_breakdown["attractions"] -= attractions_cut
            total_savings += attractions_cut
            steps_taken.append({
                "category": "attractions",
                "tip": STATIC_TIPS["attractions"],
                "estimated_saving": attractions_cut,
            })

    core_subtotal = (
        optimized_breakdown["hotel"] + optimized_breakdown["food"]
        + optimized_breakdown["transport"] + optimized_breakdown["attractions"]
        + optimized_breakdown["shopping"]
    )
    optimized_breakdown["emergency"] = calculate_emergency_buffer(core_subtotal)
    optimized_total = round(core_subtotal + optimized_breakdown["emergency"], 2)
    optimized_remaining = round(budget - optimized_total, 2)

    for step in steps_taken:
        suggestions.append(f"✓ {step['tip']} (saves ~₹{round(step['estimated_saving']):,})")

    if optimized_total > budget:
        suggestions.append(
            f"⚠ Even with these changes, the trip may still run ~₹{round(optimized_total - budget):,} over budget. "
            f"Consider reducing trip length by a day or lowering traveler count."
        )

    optimized_result = {
        **result,
        "breakdown": optimized_breakdown,
        "total_estimated_cost": optimized_total,
        "remaining": optimized_remaining,
        "is_over_budget": optimized_total > budget,
        "daily_breakdown": build_daily_breakdown(optimized_total, days),
    }

    return {
        "optimized": optimized_result,
        "suggestions": suggestions,
        "savings_applied": round(total_savings, 2),
        "original_over_by": over_by,
    }
