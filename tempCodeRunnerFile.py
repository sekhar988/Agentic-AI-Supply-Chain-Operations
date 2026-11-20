"""
================================================================================
AGENTIC AI WITH TOOL CALLING: SUPPLY CHAIN DISRUPTION & INVENTORY REBALANCING
================================================================================
A deterministic demonstration of an agentic supply-chain workflow.
Simulates an Autonomous Supply Chain Agent handling a live disruption incident
using 3 real-world Enterprise ERP tool calls.

Run in VS Code:
    python DEMO.py
================================================================================
"""

import sys
import time
import json
from agent import SupplyChainAgent
from tools import get_product_info, ERP_DATABASE, format_inr

# Color formatting helpers for clear terminal presentation
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

def print_banner():
    print(f"\n{BLUE}{BOLD}{'='*80}{RESET}")
    print(f"{CYAN}{BOLD}   AGENTIC AI ENTERPRISE DEMO: AUTONOMOUS SUPPLY CHAIN OPERATIONS   {RESET}")
    print(f"{DIM}   Pattern: ReAct (Reasoning + 3 Simulated ERP Tool Calls)                 {RESET}")
    print(f"{BLUE}{BOLD}{'='*80}{RESET}\n")

def print_incident_box(prompt: str, sku: str, delay: int, wh: str):
    print(f"{YELLOW}{BOLD}CRITICAL INCIDENT INGESTION:{RESET}")
    print(f"  {BOLD}Trigger:{RESET}     {prompt}")
    product_name = get_product_info(sku)["name"]
    warehouse_name = ERP_DATABASE["warehouses"].get(wh, {}).get("name", wh)
    print(f"  {BOLD}SKU ID:{RESET}      {sku} ({product_name})")
    print(f"  {BOLD}Disruption:{RESET}  +{delay} Days Inbound Delay")
    print(f"  {BOLD}Target DC:{RESET}   {warehouse_name}")
    print(f"{DIM}{'-'*80}{RESET}\n")

def run_demo():
    print_banner()

    # Default parameters that tell a compelling business story
    default_prompt = "Inbound component shipment delayed by congestion at Nhava Sheva port. Assess stockout risk and rebalance inventory across Indian hubs."
    default_sku = "SKU-402"
    default_delay = 12
    destination_wh = "WH-MUM"

    print(f"{GREEN}Ready to initialize Agent 'Nexus-Ops' with 3 Enterprise Tools:{RESET}")
    print(f"  [Tool 1] {BOLD}check_inventory_impact{RESET}       -> Queries ERP stock, demand, and INR exposure")
    print(f"  [Tool 2] {BOLD}find_replenishment_options{RESET}   -> Scans regional sister warehouses for surplus & lead time")
    print(f"  [Tool 3] {BOLD}execute_stock_rebalance_order{RESET}-> Books transfer PO, reserves stock & dispatches carrier")
    print(f"\n{GREEN}{BOLD}>>> Initializing autonomous agent workflow in 2 seconds...{RESET}")
    print(f"{DIM}    (To customize delay or SKU, run: python DEMO.py --custom){RESET}\n")
    
    if "--custom" in sys.argv:
        try:
            custom_delay = input("Enter shipment delay in days (e.g. 10, 14, 21) [default: 12]: ").strip()
            if custom_delay.isdigit():
                default_delay = int(custom_delay)
        except Exception:
            pass
    else:
        time.sleep(1.5)

    print()
    print_incident_box(default_prompt, default_sku, default_delay, destination_wh)

    # Initialize Agent
    agent = SupplyChainAgent()
    print(f"{MAGENTA}{BOLD}[AGENT ENGAGED]{RESET} Initiating ReAct Tool-Calling Loop...\n")

    step_counter = 1
    demo_succeeded = False
    for event in agent.run_agentic_workflow(
        user_prompt=default_prompt,
        sku=default_sku,
        delay_days=default_delay,
        destination_wh=destination_wh,
        force_demo_mode=True
    ):
        event_type = event.get("type")

        if event_type == "thought":
            print(f"{CYAN}{BOLD}--- [REASONING STEP {event.get('step', step_counter)}] {event.get('title', '')} ---{RESET}")
            print(f"{BOLD}Agent Thought:{RESET} {event['content']}\n")
            time.sleep(0.5)

        elif event_type == "tool_call":
            print(f"  {YELLOW}{BOLD}ACTION -> Invoking Tool:{RESET} {BOLD}{event['tool_name']}{RESET}")
            print(f"  {DIM}Arguments:{RESET} {json.dumps(event['arguments'], indent=4)}")
            time.sleep(0.4)

        elif event_type == "tool_result":
            print(f"  {GREEN}{BOLD}OBSERVATION <- ERP System Response:{RESET}")
            formatted_res = json.dumps(event['result'], indent=4)
            # Indent output nicely
            indented = "\n".join("    " + line for line in formatted_res.split("\n"))
            print(f"{DIM}{indented}{RESET}\n")
            time.sleep(0.5)

        elif event_type == "final_report":
            report = event["content"]
            demo_succeeded = report.get("status", "").startswith(("RESOLVED", "NO STOCKOUT RISK"))
            print(f"\n{GREEN}{BOLD}{'='*80}{RESET}")
            print(f"{GREEN}{BOLD}   EXECUTIVE OPERATIONS SUMMARY (AUTONOMOUS RESOLUTION)   {RESET}")
            print(f"{GREEN}{BOLD}{'='*80}{RESET}")
            print(f"{BOLD}Headline:{RESET} {report['executive_headline']}")
            print(f"{BOLD}Status:{RESET}   {GREEN}{report['status']}{RESET}\n")

            print(f"{BOLD}Key Financial & Operational Metrics:{RESET}")
            metrics = report["metrics"]
            print(f"  * Estimated Exposure Avoided: {GREEN}{format_inr(metrics['revenue_protected_inr'])}{RESET}")
            print(f"  * Rebalance Freight Cost:  {format_inr(metrics['rebalance_logistics_cost_inr'])}")
            print(f"  * Exposure Less Freight:   {BOLD}{format_inr(metrics['net_financial_savings_inr'])}{RESET}")
            print(f"  * Logistics Transit ETA:   {metrics['transit_lead_time']}")
            print(f"  * Freight Carrier:         {metrics['carrier']}")
            print(f"  * Transfer Order ID:       {CYAN}{metrics['order_tracking_id']}{RESET}\n")
            order_id = metrics.get("order_tracking_id")
            order = next((item for item in reversed(ERP_DATABASE["transfer_orders"]) if item["order_id"] == order_id), None)
            if order:
                print(f"  * Bill of Lading:          {order['bill_of_lading']}")
                print(f"  * Simulated Tracking:      {order['tracking_number']}\n")

            print(f"{BOLD}Audit Trail of Autonomous Actions:{RESET}")
            for action in report["autonomous_actions_taken"]:
                print(f"  {action}")

            print(f"\n{BOLD}Human-in-the-Loop Governance:{RESET}")
            print(f"  {report['human_in_the_loop_recommendation']}")
            print(f"{GREEN}{BOLD}{'='*80}{RESET}\n")

    if demo_succeeded:
        print(f"{CYAN}Demo completed: mitigation succeeded in the local simulation.{RESET}")
    else:
        print(f"{YELLOW}Demo completed with no successful mitigation; review the status and audit details above.{RESET}")
    print(f"{DIM}Tip: You can also launch the Web UI with: streamlit run app.py{RESET}\n")

if __name__ == "__main__":
    run_demo()
