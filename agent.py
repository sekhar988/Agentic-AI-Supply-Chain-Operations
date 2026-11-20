"""Supply-chain ReAct agent with OpenAI Responses API tool calling and local fallback."""

import json
import os
import time
from typing import Dict, Any, List, Optional, Generator
from tools import TOOL_MAP, TOOLS_SCHEMA, format_inr

SYSTEM_PROMPT = """You are 'Nexus-Ops', an Autonomous Enterprise Supply Chain & Operations Agent.
Your mandate is to mitigate operational disruptions, prevent stockouts, and protect revenue.
You have direct access to ERP inventory systems via tool calls:
1. `check_inventory_impact`: Quantify warehouse deficit and revenue risk.
2. `find_replenishment_options`: Locate surplus stock in sister hubs or qualified spot suppliers.
3. `execute_stock_rebalance_order`: Dispatch an official stock transfer order.

Always follow a strict ReAct decision framework:
- Reason over the business problem and calculate financial exposure.
- Execute appropriate tool calls step-by-step.
- Optimize for lowest logistics cost while guaranteeing zero stockout SLA breaches.
- Provide a clear, actionable Executive Operations Summary.
Use the available tool in the order requested by the system. Use only values supported by tool observations.
Do not claim that an order succeeded unless the order tool returns success=true.
"""

class SupplyChainAgent:
    def __init__(self, api_key: Optional[str] = None, provider: str = "auto"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.provider = provider
        self.logs: List[Dict[str, Any]] = []

    def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Safely executes a registered tool and returns JSON string."""
        if tool_name not in TOOL_MAP:
            return json.dumps({"error": f"Tool '{tool_name}' is not recognized."})
        try:
            func = TOOL_MAP[tool_name]
            return func(**arguments)
        except Exception as e:
            return json.dumps({"error": f"Tool execution failed: {str(e)}"})

    def run_agentic_workflow(
        self, 
        user_prompt: str, 
        sku: str = "SKU-402", 
        delay_days: int = 12,
        destination_wh: str = "WH-MUM",
        force_demo_mode: bool = False,
        incident_id: Optional[str] = None,
    ) -> Generator[Dict[str, Any], None, Dict[str, Any]]:
        """
        Runs the full 3-step Agentic AI loop.
        Yields intermediate events for live streaming UI and terminal logging:
        { "type": "thought" | "tool_call" | "tool_result" | "final_report", "data": ... }
        """
        self.logs = []

        # Check if live LLM should be used and credentials exist
        use_live_llm = bool(self.api_key) and not force_demo_mode and self.provider in ("auto", "openai")

        if use_live_llm:
            try:
                # Attempt live model calling
                yield from self._run_live_llm_loop(user_prompt, sku, delay_days, destination_wh, incident_id)
                return
            except Exception as e:
                # Fallback gracefully to demo engine so presentation NEVER crashes
                yield {
                    "type": "thought",
                    "step": 0,
                    "title": "LLM Fallback Activated",
                    "content": f"OpenAI tool calling unavailable ({str(e)[:120]}). Switching to the deterministic local engine."
                }

        # Demo-Safe Autonomous Engine (Deterministic ReAct Loop with Dynamic Execution)
        yield from self._run_autonomous_engine(user_prompt, sku, delay_days, destination_wh, incident_id)

    def _run_autonomous_engine(
        self,
        user_prompt: str,
        sku: str,
        delay_days: int,
        destination_wh: str,
        incident_id: Optional[str] = None,
    ) -> Generator[Dict[str, Any], None, Dict[str, Any]]:
        """
        High-fidelity ReAct Agent Execution Loop.
        Performs genuine tool calls, analyzes the real tool output data,
        reasons dynamically, and generates the final decision.
        """
        # =========================================================================
        # STEP 1: Assess Incident & Quantify Risk (Tool Call 1)
        # =========================================================================
        yield {
            "type": "thought",
            "step": 1,
            "title": "Phase 1: Assessing Disruption & Quantifying Risk",
            "content": f"Analyzing inbound notification: '{user_prompt}'. Target SKU: {sku}. Primary shipment delayed by {delay_days} days. Before committing capital or dispatching freight, I must query the ERP for the destination's available stock, demand rate, and projected stockout date."
        }
        time.sleep(0.4) # Realistic agent pacing

        tool_1_name = "check_inventory_impact"
        tool_1_args = {"sku": sku, "delay_days": delay_days, "warehouse_id": destination_wh}

        yield {
            "type": "tool_call",
            "step": 1,
            "tool_name": tool_1_name,
            "arguments": tool_1_args
        }

        # Real Tool Execution
        tool_1_raw = self._execute_tool(tool_1_name, tool_1_args)
        tool_1_data = json.loads(tool_1_raw)
        time.sleep(0.3)

        yield {
            "type": "tool_result",
            "step": 1,
            "tool_name": tool_1_name,
            "result": tool_1_data
        }

        if "error" in tool_1_data:
            yield {"type": "final_report", "content": {
                "executive_headline": "Inventory assessment could not be completed",
                "status": "NEEDS REVIEW",
                "metrics": {"revenue_protected_inr": 0, "rebalance_logistics_cost_inr": 0,
                            "net_financial_savings_inr": 0, "transit_lead_time": "Not booked",
                            "carrier": "None", "order_tracking_id": "None"},
                "autonomous_actions_taken": [tool_1_data["error"]],
                "human_in_the_loop_recommendation": "Check the SKU, warehouse, and delay values, then retry."
            }}
            return

        deficit_units = tool_1_data.get("projected_stockout_units", 0)
        days_left = tool_1_data.get("days_of_supply_remaining", 2.0)
        exposure = tool_1_data.get("financial_risk", {}).get("total_risk_exposure_inr", 0)

        if deficit_units <= 0:
            yield {"type": "final_report", "content": {
                "executive_headline": f"No replenishment needed for {sku}",
                "status": "NO STOCKOUT RISK",
                "metrics": {"revenue_protected_inr": 0, "rebalance_logistics_cost_inr": 0,
                            "net_financial_savings_inr": 0, "transit_lead_time": "Not applicable",
                            "carrier": "None", "order_tracking_id": "None"},
                "autonomous_actions_taken": [f"Validated inventory at {destination_wh}; available supply covers the {delay_days}-day delay."],
                "human_in_the_loop_recommendation": "No action required."
            }}
            return

        # =========================================================================
        # STEP 2: Replenishment Sourcing Analysis (Tool Call 2)
        # =========================================================================
        yield {
            "type": "thought",
            "step": 2,
            "title": "Phase 2: Evaluating Sourcing & Freight Alternatives",
            "content": f"Observation confirms CRITICAL RISK: {tool_1_data.get('warehouse', destination_wh)} has about {days_left} days of available supply. We face a deficit of {deficit_units} units, exposing {format_inr(exposure)} in estimated unfulfilled revenue and SLA penalties. I will now query the network for options that cover the deficit and arrive before stockout."
        }
        time.sleep(0.4)

        tool_2_name = "find_replenishment_options"
        tool_2_args = {"sku": sku, "units_needed": deficit_units, "destination_wh": destination_wh}

        yield {
            "type": "tool_call",
            "step": 2,
            "tool_name": tool_2_name,
            "arguments": tool_2_args
        }

        # Real Tool Execution
        tool_2_raw = self._execute_tool(tool_2_name, tool_2_args)
        tool_2_data = json.loads(tool_2_raw)
        time.sleep(0.3)

        yield {
            "type": "tool_result",
            "step": 2,
            "tool_name": tool_2_name,
            "result": tool_2_data
        }

        # Determine best candidate
        options = tool_2_data.get("options", [])
        viable_options = [o for o in options if o.get("covers_full_deficit") and
                          o.get("transit_time_days", 999) <= days_left]
        if not viable_options:
            yield {"type": "final_report", "content": {
                "executive_headline": f"No safe replenishment option found for {sku}",
                "status": "ESCALATION REQUIRED",
                "metrics": {"revenue_protected_inr": 0, "rebalance_logistics_cost_inr": 0,
                            "net_financial_savings_inr": 0, "transit_lead_time": "Not booked",
                            "carrier": "None", "order_tracking_id": "None"},
                "autonomous_actions_taken": [f"Identified a {deficit_units}-unit deficit, but no option both covers it and arrives within {days_left:.1f} days."],
                "human_in_the_loop_recommendation": "Escalate to the operations team for an alternate supply plan."
            }}
            return
        best_option = viable_options[0]

        selected_source = best_option["source_id"]
        # Source options honor the destination SKU's case pack and may include
        # a small quantity buffer above the calculated deficit.
        transfer_qty = best_option.get("offered_quantity", deficit_units)
        spot_option = next((o for o in options if o.get("source_type") == "EXTERNAL_SPOT_SUPPLIER"), None)
        spot_quote_cost = (spot_option or {}).get("total_cost_inr", 0)
        cost_saved_vs_spot = round(spot_quote_cost - best_option.get("total_cost_inr", 0), 2)

        # =========================================================================
        # STEP 3: Autonomous Order Dispatch (Tool Call 3)
        # =========================================================================
        yield {
            "type": "thought",
            "step": 3,
            "title": "Phase 3: Dispatching Autonomous Stock Rebalance",
            "content": f"Decision: {best_option['source_name']} can cover the {deficit_units}-unit deficit with a {transfer_qty}-unit case-pack shipment and deliver in {best_option.get('transit_time_days', 2)} business days, before projected stockout. Its estimated cost is {format_inr(best_option.get('total_cost_inr', 0))}; the lowest-priced spot quote is {format_inr(spot_quote_cost)}. Authorizing the selected replenishment order."
        }
        time.sleep(0.4)

        tool_3_name = "execute_stock_rebalance_order"
        tool_3_args = {
            "sku": sku,
            "source_wh_or_vendor": selected_source,
            "destination_wh": destination_wh,
            "quantity": transfer_qty,
            "expedited": True
        }
        if incident_id:
            tool_3_args["incident_id"] = incident_id

        yield {
            "type": "tool_call",
            "step": 3,
            "tool_name": tool_3_name,
            "arguments": tool_3_args
        }

        # Real Tool Execution
        tool_3_raw = self._execute_tool(tool_3_name, tool_3_args)
        tool_3_data = json.loads(tool_3_raw)
        time.sleep(0.3)

        yield {
            "type": "tool_result",
            "step": 3,
            "tool_name": tool_3_name,
            "result": tool_3_data
        }

        # =========================================================================
        # FINAL SYNTHESIS: Executive Summary
        # =========================================================================
        order_info = tool_3_data.get("order_details", {})
        if tool_3_data.get("duplicate_prevented"):
            executive_headline = f"Incident already mitigated: order {order_info.get('order_id')} remains in transit"
            dispatch_action = f"Confirmed existing order {order_info.get('order_id')}; duplicate reservation prevented."
        elif tool_3_data.get("success"):
            executive_headline = f"Disruption mitigated: {order_info.get('quantity', transfer_qty)} units of {sku} sent to {destination_wh}"
            dispatch_action = f"3. Executed priority transfer order {order_info.get('order_id')}, reserving stock and dispatching carrier."
        else:
            executive_headline = f"Transfer for {sku} was not committed"
            dispatch_action = f"3. Order not committed: {tool_3_data.get('error', 'unknown error')}"
        final_summary = {
            "executive_headline": executive_headline,
            "status": "RESOLVED - STOCKOUT AVERTED" if tool_3_data.get("success") else "ORDER FAILED - ESCALATION REQUIRED",
            "metrics": {
                "revenue_protected_inr": exposure if tool_3_data.get("success") else 0,
                "rebalance_logistics_cost_inr": order_info.get("logistics_cost_inr", 0.0),
                # This is avoided disruption exposure less freight, not accounting profit.
                "net_financial_savings_inr": round(exposure - order_info.get("logistics_cost_inr", 0.0), 2) if tool_3_data.get("success") else 0,
                "transit_lead_time": f"{order_info.get('estimated_delivery_date')} ({best_option.get('transit_time_days')} Business Days)",
                "carrier": order_info.get("freight_carrier", "None"),
                "order_tracking_id": order_info.get("order_id", "Not created"),
                "source": best_option.get("source_id", "Unknown"),
                "comparison_savings_vs_spot_inr": cost_saved_vs_spot
            },
            "autonomous_actions_taken": [
                f"1. Validated the {delay_days}-day supplier delay against {tool_1_data.get('warehouse', destination_wh)} inventory, detecting a {tool_1_data.get('deficit_days')}-day stockout window.",
                f"2. Queried multi-node distribution network, identifying {best_option['source_name']} as the lowest-cost viable source.",
                dispatch_action
            ],
            "human_in_the_loop_recommendation": "No manual escalation required; order dispatched." if tool_3_data.get("success") else tool_3_data.get("error", "Order failed; escalate to operations.")
        }

        yield {
            "type": "final_report",
            "content": final_summary
        }

    def _run_live_llm_loop(
        self,
        user_prompt: str,
        sku: str,
        delay_days: int,
        destination_wh: str,
        incident_id: Optional[str] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """Run three sequential function calls through the OpenAI Responses API.

        Read-only discovery steps may safely fall back and repeat. The dispatch is the
        final API tool call, so there is no later network request that could cause a
        successful order to be duplicated by the local fallback.
        """
        import requests

        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        endpoint = "https://api.openai.com/v1/responses"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        previous_response_id = None

        def request_tool(tool_name: str, prompt_or_output: Any) -> Dict[str, Any]:
            nonlocal previous_response_id
            schema = next(item["function"] for item in TOOLS_SCHEMA
                          if item["function"]["name"] == tool_name)
            response_tool = {
                "type": "function",
                "name": schema["name"],
                "description": schema["description"],
                "parameters": schema["parameters"],
                "strict": False,
            }
            payload: Dict[str, Any] = {
                "model": model,
                "instructions": SYSTEM_PROMPT,
                "tools": [response_tool],
                "tool_choice": "required",
                "parallel_tool_calls": False,
                "input": prompt_or_output,
            }
            if previous_response_id:
                payload["previous_response_id"] = previous_response_id
            result = requests.post(endpoint, headers=headers, json=payload, timeout=(5, 25))
            if not result.ok:
                raise RuntimeError(f"OpenAI API returned HTTP {result.status_code}")
            data = result.json()
            previous_response_id = data.get("id")
            call = next((item for item in data.get("output", [])
                         if item.get("type") == "function_call" and item.get("name") == tool_name), None)
            if not call:
                raise RuntimeError(f"Model did not call the required tool {tool_name}")
            try:
                call["parsed_arguments"] = json.loads(call.get("arguments", "{}"))
            except (TypeError, json.JSONDecodeError) as exc:
                raise RuntimeError(f"Model returned invalid arguments for {tool_name}") from exc
            return call

        def run_tool(step: int, name: str, canonical_args: Dict[str, Any], call: Dict[str, Any]) -> Dict[str, Any]:
            supplied = call["parsed_arguments"]
            if not isinstance(supplied, dict):
                raise RuntimeError(f"Model arguments for {name} were not an object")
            # Never let the model change the incident being assessed or exceed
            # the source, quantity, and destination selected from ERP observations.
            if any(key in supplied and supplied[key] != value for key, value in canonical_args.items()):
                raise RuntimeError(f"Model proposed unsafe or inconsistent arguments for {name}")
            yield_event = {"type": "tool_call", "step": step, "tool_name": name, "arguments": canonical_args}
            self.logs.append(yield_event)
            events.append(yield_event)
            raw = self._execute_tool(name, canonical_args)
            try:
                result_data = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"Tool {name} returned invalid JSON") from exc
            result_event = {"type": "tool_result", "step": step, "tool_name": name, "result": result_data}
            self.logs.append(result_event)
            events.append(result_event)
            return result_data

        # Events produced inside run_tool are yielded to the outer generator via this
        # small queue, keeping the UI's existing trace format intact.
        events: List[Dict[str, Any]] = []

        yield {"type": "thought", "step": 1, "title": "OpenAI: Assessing disruption",
               "content": "OpenAI is selecting the inventory impact tool. The tool result, not model estimates, supplies the stock and risk figures."}
        first_args = {"sku": sku, "delay_days": delay_days, "warehouse_id": destination_wh}
        first_call = request_tool("check_inventory_impact", f"Incident: {user_prompt}. Use SKU {sku}, delay {delay_days} days, warehouse {destination_wh}.")
        impact = run_tool(1, "check_inventory_impact", first_args, first_call)
        yield from events
        events.clear()
        if "error" in impact:
            yield {"type": "final_report", "content": self._simple_report("NEEDS REVIEW", "Inventory assessment failed", [impact["error"]])}
            return
        deficit = impact.get("projected_stockout_units", 0)
        days_left = impact.get("days_of_supply_remaining", 0)
        exposure = impact.get("financial_risk", {}).get("total_risk_exposure_inr", 0)
        if deficit <= 0:
            yield {"type": "final_report", "content": self._simple_report("NO STOCKOUT RISK", f"No replenishment needed for {sku}", [f"Available supply at {destination_wh} covers the {delay_days}-day delay."])}
            return

        yield {"type": "thought", "step": 2, "title": "OpenAI: Finding replenishment options",
               "content": f"ERP reports {deficit} units at risk and {format_inr(exposure)} exposure. OpenAI is selecting the sourcing analysis tool."}
        second_args = {"sku": sku, "units_needed": deficit, "destination_wh": destination_wh}
        second_call = request_tool("find_replenishment_options", [{"type": "function_call_output", "call_id": first_call["call_id"], "output": json.dumps(impact)}])
        options_data = run_tool(2, "find_replenishment_options", second_args, second_call)
        yield from events
        events.clear()
        if "error" in options_data:
            yield {"type": "final_report", "content": self._simple_report("NEEDS REVIEW", "Sourcing analysis failed", [options_data["error"]])}
            return
        options = options_data.get("options", [])
        viable = [o for o in options if o.get("covers_full_deficit") and o.get("transit_time_days", 999) <= days_left]
        if not viable:
            yield {"type": "final_report", "content": self._simple_report("ESCALATION REQUIRED", f"No safe replenishment source for {sku}", [f"No option covers {deficit} units and arrives within {days_left:.1f} days."])}
            return
        selected = viable[0]
        yield {"type": "thought", "step": 3, "title": "OpenAI: Authorizing rebalance",
               "content": "OpenAI is selecting an ERP option. A local safety gate will require full coverage and on-time arrival before dispatch."}
        third_call = request_tool("execute_stock_rebalance_order", [{"type": "function_call_output", "call_id": second_call["call_id"], "output": json.dumps(options_data)}])
        proposed = third_call["parsed_arguments"]
        proposed_source = proposed.get("source_wh_or_vendor", selected["source_id"])
        selected_choice = next((option for option in viable if option["source_id"] == proposed_source), None)
        if selected_choice is None:
            raise RuntimeError("Model selected a source that is not a safe, full-coverage on-time option")
        selected = selected_choice
        third_args = {"sku": sku, "source_wh_or_vendor": selected["source_id"], "destination_wh": destination_wh,
                      "quantity": selected.get("offered_quantity", deficit), "expedited": True}
        if incident_id:
            third_args["incident_id"] = incident_id
        dispatch = run_tool(3, "execute_stock_rebalance_order", third_args, third_call)
        yield from events

        order = dispatch.get("order_details", {})
        spot = next((o for o in options if o.get("source_type") == "EXTERNAL_SPOT_SUPPLIER"), {})
        saved = round(spot.get("total_cost_inr", 0) - selected.get("total_cost_inr", 0), 2)
        succeeded = dispatch.get("success") is True
        yield {"type": "final_report", "content": {
            "executive_headline": (f"Incident already mitigated: order {order.get('order_id')} remains in transit" if dispatch.get("duplicate_prevented") else f"{'Disruption mitigated' if succeeded else 'Transfer failed'}: {order.get('quantity', deficit)} units of {sku} for {destination_wh}"),
            "status": "RESOLVED - STOCKOUT AVERTED" if succeeded else "ORDER FAILED - ESCALATION REQUIRED",
            "metrics": {"revenue_protected_inr": exposure if succeeded else 0,
                        "rebalance_logistics_cost_inr": order.get("logistics_cost_inr", 0),
                        "net_financial_savings_inr": round(exposure - order.get("logistics_cost_inr", 0), 2) if succeeded else 0,
                        "transit_lead_time": f"{order.get('estimated_delivery_date', 'Not booked')} ({selected['transit_time_days']} Business Days)",
                        "carrier": order.get("freight_carrier", "None"), "order_tracking_id": order.get("order_id", "Not created"),
                        "source": selected["source_id"], "comparison_savings_vs_spot_inr": saved},
            "autonomous_actions_taken": [f"Measured {impact['deficit_days']} days of stockout exposure at {destination_wh}.",
                                         f"Selected {selected['source_name']} from {len(options)} replenishment options.",
                                         dispatch.get("message", dispatch.get("error", "Order not committed."))],
            "human_in_the_loop_recommendation": "No manual escalation required; order dispatched." if succeeded else dispatch.get("error", "Escalate to operations.")
        }}

    @staticmethod
    def _simple_report(status: str, headline: str, actions: List[str]) -> Dict[str, Any]:
        return {"executive_headline": headline, "status": status,
                "metrics": {"revenue_protected_inr": 0, "rebalance_logistics_cost_inr": 0,
                            "net_financial_savings_inr": 0, "transit_lead_time": "Not applicable",
                            "carrier": "None", "order_tracking_id": "None"},
                "autonomous_actions_taken": actions,
                "human_in_the_loop_recommendation": "Review the issue before retrying."}

