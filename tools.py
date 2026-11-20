"""
ERP & Logistics Toolset for Supply Chain Disruption & Inventory Rebalancing.
Contains 3 core enterprise tools callable by the Agentic AI.
"""

from typing import Dict, Any, List
import datetime
import json


def format_inr(amount: float, decimals: int = 2) -> str:
    """Format INR values with Indian digit grouping, for example ₹1,72,000.00."""
    value = round(float(amount), decimals)
    sign = "-" if value < 0 else ""
    fixed = f"{abs(value):.{decimals}f}"
    whole, _, fraction = fixed.partition(".")
    if len(whole) > 3:
        last_three, remaining = whole[-3:], whole[:-3]
        groups = []
        while remaining:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        whole = ",".join(groups + [last_three])
    suffix = f".{fraction}" if decimals else ""
    return f"₹{sign}{whole}{suffix}"

# ==========================================
# SIMULATED ENTERPRISE ERP DATABASE
# ==========================================
# Deterministic mock ERP snapshot. Quantities, prices, suppliers, and routes are
# fictional demonstration data; route quotes are planning estimates.
ERP_DATABASE = {
    "currency": "INR",
    "products": {
        "SKU-402": {
            "name": "High-Efficiency Industrial Servo Drive",
            "category": "Robotics & Automation Components",
            "unit_price": 65000.00,
            "margin": 0.38,
            "penalty_per_day_stockout": 420000.00,
            "criticality": "A",
            "supplier_lead_time_days": 18,
            "reorder_point_units": 240,
            "unit_weight_kg": 8.4,
        },
        "SKU-108": {
            "name": "Precision Thermal Sensor Module",
            "category": "Electronics & Sensors",
            "unit_price": 12000.00,
            "margin": 0.45,
            "penalty_per_day_stockout": 150000.00,
            "criticality": "A",
            "supplier_lead_time_days": 10,
            "reorder_point_units": 720,
            "unit_weight_kg": 0.35,
        },
        "SKU-227": {
            "name": "Programmable Logic Controller Module",
            "category": "Controls & Automation",
            "unit_price": 89000.00,
            "margin": 0.34,
            "penalty_per_day_stockout": 520000.00,
            "criticality": "A",
            "supplier_lead_time_days": 21,
            "reorder_point_units": 180,
            "unit_weight_kg": 1.7,
        },
        "SKU-315": {
            "name": "Sealed Industrial Bearing Assembly",
            "category": "Mechanical Components",
            "unit_price": 8500.00,
            "margin": 0.29,
            "penalty_per_day_stockout": 110000.00,
            "criticality": "B",
            "supplier_lead_time_days": 14,
            "reorder_point_units": 420,
            "unit_weight_kg": 2.2,
        },
        "SKU-509": {
            "name": "Variable-Speed Motor Controller",
            "category": "Motors & Drives",
            "unit_price": 31000.00,
            "margin": 0.36,
            "penalty_per_day_stockout": 280000.00,
            "criticality": "A",
            "supplier_lead_time_days": 16,
            "reorder_point_units": 300,
            "unit_weight_kg": 4.6,
        },
    },
    "warehouses": {
        "WH-MUM": {
            "name": "West India Fulfillment Hub (Mumbai, Maharashtra)",
            "region": "West",
            "coordinates": [19.0760, 72.8777],
            "stock": {
                "SKU-402": {"on_hand": 85, "reserved": 45, "daily_burn_rate": 20, "safety_stock_units": 80, "lot_size": 10},
                "SKU-108": {"on_hand": 500, "reserved": 200, "daily_burn_rate": 60, "safety_stock_units": 300, "lot_size": 50},
                "SKU-227": {"on_hand": 120, "reserved": 40, "daily_burn_rate": 12, "safety_stock_units": 120, "lot_size": 5},
                "SKU-315": {"on_hand": 420, "reserved": 120, "daily_burn_rate": 35, "safety_stock_units": 210, "lot_size": 25},
                "SKU-509": {"on_hand": 260, "reserved": 80, "daily_burn_rate": 24, "safety_stock_units": 168, "lot_size": 10},
            }
        },
        "WH-DEL": {
            "name": "North India Regional Hub (Delhi NCR)",
            "region": "North",
            "coordinates": [28.6139, 77.2090],
            "stock": {
                "SKU-402": {"on_hand": 940, "reserved": 140, "daily_burn_rate": 18, "safety_stock_units": 270, "lot_size": 10},
                "SKU-108": {"on_hand": 300, "reserved": 100, "daily_burn_rate": 25, "safety_stock_units": 375, "lot_size": 50},
                "SKU-227": {"on_hand": 800, "reserved": 120, "daily_burn_rate": 15, "safety_stock_units": 225, "lot_size": 5},
                "SKU-315": {"on_hand": 900, "reserved": 180, "daily_burn_rate": 28, "safety_stock_units": 420, "lot_size": 25},
                "SKU-509": {"on_hand": 750, "reserved": 150, "daily_burn_rate": 20, "safety_stock_units": 300, "lot_size": 10},
            }
        },
        "WH-BLR": {
            "name": "South India Automation Hub (Bengaluru, Karnataka)",
            "region": "South",
            "coordinates": [12.9716, 77.5946],
            "stock": {
                "SKU-402": {"on_hand": 310, "reserved": 90, "daily_burn_rate": 15, "safety_stock_units": 225, "lot_size": 10},
                "SKU-108": {"on_hand": 800, "reserved": 150, "daily_burn_rate": 40, "safety_stock_units": 600, "lot_size": 50},
                "SKU-227": {"on_hand": 240, "reserved": 60, "daily_burn_rate": 10, "safety_stock_units": 150, "lot_size": 5},
                "SKU-315": {"on_hand": 600, "reserved": 120, "daily_burn_rate": 30, "safety_stock_units": 450, "lot_size": 25},
                "SKU-509": {"on_hand": 300, "reserved": 80, "daily_burn_rate": 18, "safety_stock_units": 270, "lot_size": 10},
            }
        },
        "WH-CHE": {
            "name": "Southeast Coast Distribution Hub (Chennai, Tamil Nadu)",
            "region": "South",
            "coordinates": [13.0827, 80.2707],
            "stock": {
                "SKU-402": {"on_hand": 600, "reserved": 80, "daily_burn_rate": 12, "safety_stock_units": 180, "lot_size": 10},
                "SKU-108": {"on_hand": 350, "reserved": 80, "daily_burn_rate": 20, "safety_stock_units": 300, "lot_size": 50},
                "SKU-227": {"on_hand": 180, "reserved": 40, "daily_burn_rate": 8, "safety_stock_units": 120, "lot_size": 5},
                "SKU-315": {"on_hand": 1200, "reserved": 200, "daily_burn_rate": 32, "safety_stock_units": 480, "lot_size": 25},
                "SKU-509": {"on_hand": 1000, "reserved": 140, "daily_burn_rate": 22, "safety_stock_units": 330, "lot_size": 10},
            }
        },
        "WH-KOL": {
            "name": "East India Fulfillment Hub (Kolkata, West Bengal)",
            "region": "East",
            "coordinates": [22.5726, 88.3639],
            "stock": {
                "SKU-402": {"on_hand": 450, "reserved": 90, "daily_burn_rate": 14, "safety_stock_units": 210, "lot_size": 10},
                "SKU-108": {"on_hand": 950, "reserved": 100, "daily_burn_rate": 45, "safety_stock_units": 675, "lot_size": 50},
                "SKU-227": {"on_hand": 300, "reserved": 40, "daily_burn_rate": 9, "safety_stock_units": 135, "lot_size": 5},
                "SKU-315": {"on_hand": 480, "reserved": 80, "daily_burn_rate": 26, "safety_stock_units": 390, "lot_size": 25},
                "SKU-509": {"on_hand": 400, "reserved": 50, "daily_burn_rate": 16, "safety_stock_units": 240, "lot_size": 10},
            }
        }
    },
    "suppliers": {
        "SUPP-BHARAT-MOTION": {
            "name": "Bharat Motion Systems",
            "qualification": "Authorized OEM partner · India",
            "available_skus": ["SKU-402", "SKU-108", "SKU-227", "SKU-315", "SKU-509"],
            "capacity_by_sku": {"SKU-402": 2000, "SKU-108": 2500, "SKU-227": 500, "SKU-315": 1800, "SKU-509": 1000},
            "reserved_by_sku": {},
            "lead_time_days": 1,
            "rush_premium_pct": 0.15,
            "freight_per_unit_inr": 3500.00,
            "carrier": "Nexus Express Air",
            "reliability_score": 0.91,
        },
        "SUPP-TRICOLOUR": {
            "name": "Tricolour Automation Supply",
            "qualification": "Approved industrial distributor · India",
            "available_skus": ["SKU-402", "SKU-227", "SKU-509"],
            "capacity_by_sku": {"SKU-402": 650, "SKU-227": 300, "SKU-509": 450},
            "reserved_by_sku": {},
            "lead_time_days": 2,
            "rush_premium_pct": 0.08,
            "freight_per_unit_inr": 2400.00,
            "carrier": "Blue Dart Priority Cargo",
            "reliability_score": 0.96,
        },
        "SUPP-DECCAN": {
            "name": "Deccan Components Network",
            "qualification": "Approved regional distributor · India",
            "available_skus": ["SKU-108", "SKU-315", "SKU-509"],
            "capacity_by_sku": {"SKU-108": 900, "SKU-315": 1200, "SKU-509": 500},
            "reserved_by_sku": {},
            "lead_time_days": 3,
            "rush_premium_pct": 0.10,
            "freight_per_unit_inr": 1800.00,
            "carrier": "TCI Express",
            "reliability_score": 0.94,
        },
    },
    "scenarios": {
        "Port congestion": {"description": "Monsoon-season congestion at Nhava Sheva (JNPT) delays inbound components.", "affected_hubs": ["WH-MUM", "WH-DEL"], "default_delay_days": 12},
        "Supplier bottleneck": {"description": "Tier-2 supplier capacity constraints in western India delay production release.", "affected_hubs": ["WH-MUM", "WH-BLR"], "default_delay_days": 18},
        "Severe weather": {"description": "Monsoon flooding disrupts regional linehaul and last-mile delivery.", "affected_hubs": ["WH-MUM", "WH-KOL"], "default_delay_days": 7},
        "Factory outage": {"description": "Unplanned plant downtime in southern India delays the next replenishment.", "affected_hubs": ["WH-BLR", "WH-DEL"], "default_delay_days": 10},
    },
    "transfer_orders": []
}

def get_product_info(sku: str) -> Dict[str, Any]:
    return ERP_DATABASE["products"].get(sku, {
        "name": f"Generic SKU ({sku})",
        "category": "General Industrial",
        "unit_price": 25000.00,
        "margin": 0.30,
        "penalty_per_day_stockout": 200000.00
    })


def get_route_quote(source_wh: str, destination_wh: str, expedited: bool = True) -> Dict[str, Any]:
    """Return deterministic planning estimates using hub coordinates."""
    source = ERP_DATABASE["warehouses"][source_wh]
    destination = ERP_DATABASE["warehouses"][destination_wh]
    lat1, lon1 = source["coordinates"]
    lat2, lon2 = destination["coordinates"]
    # Great-circle distance estimate in kilometres; road routing can differ.
    from math import asin, ceil, cos, radians, sin, sqrt
    earth_radius_km = 6371.0
    delta_lat, delta_lon = radians(lat2 - lat1), radians(lon2 - lon1)
    haversine = sin(delta_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(delta_lon / 2) ** 2
    distance_km = round(2 * earth_radius_km * asin(sqrt(haversine)))

    if source_wh == "WH-DEL" and destination_wh == "WH-MUM":
        return {"distance_km": distance_km, "transit_days": 2 if expedited else 4,
                "cost_per_unit_inr": 650.00 if expedited else 320.00,
                "carrier": "Nexus Priority Road Freight" if expedited else "National Surface Logistics"}
    transit_days = max(1, ceil(distance_km / (550 if expedited else 350)))
    cost_per_unit = round((350 + distance_km * 0.5) if expedited else (200 + distance_km * 0.28), 2)
    if expedited:
        carrier = "Blue Dart Priority Cargo" if distance_km <= 1200 else "TCI Express Priority Freight"
    else:
        carrier = "National Surface Logistics"
    return {"distance_km": distance_km, "transit_days": transit_days,
            "cost_per_unit_inr": cost_per_unit, "carrier": carrier}


def _business_day_eta(start: datetime.datetime, business_days: int) -> datetime.datetime:
    eta = start
    remaining = business_days
    while remaining > 0:
        eta += datetime.timedelta(days=1)
        if eta.weekday() < 5:
            remaining -= 1
    return eta


# ==========================================
# TOOL 1: check_inventory_impact
# ==========================================
def check_inventory_impact(sku: str, delay_days: int, warehouse_id: str = "WH-MUM") -> str:
    """
    Evaluates current inventory levels, burn rate, and financial stockout risk
    at a target warehouse given an incoming shipment delay.
    
    Args:
        sku: The product SKU identifier (e.g. 'SKU-402').
        delay_days: Inbound supplier shipment delay in days (e.g. 14).
        warehouse_id: Target distribution center (default: 'WH-MUM').
    """
    if not isinstance(delay_days, int) or delay_days < 0:
        return json.dumps({"error": "delay_days must be a non-negative integer."})
    wh = ERP_DATABASE["warehouses"].get(warehouse_id)
    if sku not in ERP_DATABASE["products"]:
        return json.dumps({"error": f"SKU {sku} not found."})
    if not wh:
        return json.dumps({"error": f"Warehouse {warehouse_id} not found."})

    product = get_product_info(sku)
    stock_info = wh["stock"].get(sku, {"on_hand": 0, "reserved": 0, "daily_burn_rate": 10})
    
    available_stock = max(0, stock_info["on_hand"] - stock_info["reserved"])
    burn_rate = stock_info["daily_burn_rate"]
    
    days_until_stockout = available_stock / burn_rate if burn_rate > 0 else 999
    is_stockout_risk = delay_days > days_until_stockout
    deficit_days = max(0, delay_days - days_until_stockout)
    projected_unit_deficit = int(round(deficit_days * burn_rate))
    revenue_at_risk = round(projected_unit_deficit * product["unit_price"], 2)
    gross_margin_at_risk = round(revenue_at_risk * product["margin"], 2)
    contract_penalty_risk = round(deficit_days * product["penalty_per_day_stockout"], 2)
    reorder_point = product["reorder_point_units"]
    safety_stock = stock_info.get("safety_stock_units", 0)

    result = {
        "status": "CRITICAL_STOCKOUT_RISK" if is_stockout_risk else ("REORDER_POINT_BREACH" if available_stock <= reorder_point else "HEALTHY"),
        "warehouse": wh["name"],
        "sku": sku,
        "product_name": product["name"],
        "criticality": product["criticality"],
        "on_hand_units": stock_info["on_hand"],
        "reserved_units": stock_info["reserved"],
        "current_available_units": available_stock,
        "safety_stock_units": safety_stock,
        "reorder_point_units": reorder_point,
        "below_reorder_point": available_stock <= reorder_point,
        "daily_burn_rate": burn_rate,
        "days_of_supply_remaining": round(days_until_stockout, 1),
        "inbound_delay_days": delay_days,
        "deficit_days": round(deficit_days, 1),
        "projected_stockout_units": projected_unit_deficit,
        "financial_risk": {
            "unfulfilled_revenue_risk_inr": revenue_at_risk,
            "gross_margin_at_risk_inr": gross_margin_at_risk,
            "sla_breach_penalties_inr": contract_penalty_risk,
            "total_risk_exposure_inr": round(revenue_at_risk + contract_penalty_risk, 2)
        },
        "urgency": "HIGH" if deficit_days >= 3 else "MEDIUM"
    }
    return json.dumps(result, indent=2)


# ==========================================
# TOOL 2: find_replenishment_options
# ==========================================
def find_replenishment_options(sku: str, units_needed: int, destination_wh: str = "WH-MUM") -> str:
    """
    Scans internal sister warehouses for surplus inventory and queries vetted spot suppliers.
    Compares lead times, available surplus, freight costs, and CO2 footprint.
    
    Args:
        sku: The product SKU identifier (e.g. 'SKU-402').
        units_needed: Quantity of units required to cover the deficit.
        destination_wh: Destination warehouse experiencing the shortage (default: 'WH-MUM').
    """
    if not isinstance(units_needed, int) or units_needed < 0:
        return json.dumps({"error": "units_needed must be a non-negative integer."})
    if destination_wh not in ERP_DATABASE["warehouses"]:
        return json.dumps({"error": f"Warehouse {destination_wh} not found."})
    if sku not in ERP_DATABASE["products"]:
        return json.dumps({"error": f"SKU {sku} not found."})
    options = []
    product = get_product_info(sku)

    # 1. Scan internal warehouse network, protecting each source's item-level buffer.
    for wh_id, wh in ERP_DATABASE["warehouses"].items():
        if wh_id == destination_wh:
            continue
        
        st = wh["stock"].get(sku, {"on_hand": 0, "reserved": 0, "daily_burn_rate": 15})
        usable_units = max(0, st["on_hand"] - st["reserved"])
        safety_buffer = st.get("safety_stock_units", st["daily_burn_rate"] * 15)
        transferable_surplus = max(0, usable_units - safety_buffer)

        if transferable_surplus > 0:
            pack_size = max(1, st.get("lot_size", 1))
            requested_qty = ((units_needed + pack_size - 1) // pack_size) * pack_size
            transfer_qty = min(requested_qty, (transferable_surplus // pack_size) * pack_size)
            if transfer_qty <= 0:
                continue
            route = get_route_quote(wh_id, destination_wh, expedited=True)

            options.append({
                "source_type": "INTERNAL_TRANSFER",
                "source_id": wh_id,
                "source_name": wh["name"],
                "available_surplus_units": transferable_surplus,
                "offered_quantity": transfer_qty,
                "pack_size_units": pack_size,
                "safety_stock_units": safety_buffer,
                "transit_time_days": route["transit_days"],
                "distance_km_estimate": route["distance_km"],
                "carrier": route["carrier"],
                "freight_cost_per_unit_inr": route["cost_per_unit_inr"],
                "total_cost_inr": round(transfer_qty * route["cost_per_unit_inr"], 2),
                "covers_full_deficit": transfer_qty >= units_needed,
                "recommendation_rank": 1
            })

    # 2. Compare only approved suppliers that stock this item and have capacity.
    for supplier_id, supplier in ERP_DATABASE["suppliers"].items():
        if sku not in supplier["available_skus"]:
            continue
        capacity = max(0, supplier["capacity_by_sku"].get(sku, 0) - supplier["reserved_by_sku"].get(sku, 0))
        pack_size = max(1, ERP_DATABASE["warehouses"][destination_wh]["stock"].get(sku, {}).get("lot_size", 1))
        requested_qty = ((units_needed + pack_size - 1) // pack_size) * pack_size
        offered = min(requested_qty, (capacity // pack_size) * pack_size)
        if offered <= 0:
            continue
        rush_unit_price = round(product["unit_price"] * (1 + supplier["rush_premium_pct"]), 2)
        options.append({
            "source_type": "EXTERNAL_SPOT_SUPPLIER",
            "source_id": supplier_id,
            "source_name": supplier["name"],
            "qualification": supplier["qualification"],
            "reliability_score": supplier["reliability_score"],
            "available_surplus_units": capacity,
            "offered_quantity": offered,
            "pack_size_units": pack_size,
            "transit_time_days": supplier["lead_time_days"],
            "carrier": supplier["carrier"],
            "freight_cost_per_unit_inr": supplier["freight_per_unit_inr"],
            "unit_purchase_cost_inr": rush_unit_price,
            "purchase_cost_inr": round(offered * rush_unit_price, 2),
            "total_cost_inr": round(offered * (rush_unit_price + supplier["freight_per_unit_inr"]), 2),
            "covers_full_deficit": offered >= units_needed,
            "recommendation_rank": 3,
            "note": f"Rush premium {supplier['rush_premium_pct']:.0%}; quote is a simulated estimate.",
        })

    # Prefer an option that covers the full need, then choose the lowest total cost.
    options.sort(key=lambda x: (not x["covers_full_deficit"], x["total_cost_inr"], x["transit_time_days"]))

    best_internal = next((option["source_name"] for option in options if option["source_type"] == "INTERNAL_TRANSFER"), None)
    response = {
        "sku": sku,
        "units_needed": units_needed,
        "destination_warehouse": destination_wh,
        "candidates_evaluated": len(options),
        "options": options,
        "best_internal_recommendation": best_internal
    }
    return json.dumps(response, indent=2)


# ==========================================
# TOOL 3: execute_stock_rebalance_order
# ==========================================
def execute_stock_rebalance_order(
    sku: str, 
    source_wh_or_vendor: str, 
    destination_wh: str, 
    quantity: int, 
    expedited: bool = True,
    incident_id: str = "",
) -> str:
    """
    Executes and books an automated stock rebalance transfer order in the ERP.
    Reserves source units, updates inbound logistics schedule, and issues a tracking BOL.
    
    Args:
        sku: The product SKU identifier (e.g. 'SKU-402').
        source_wh_or_vendor: Source warehouse ID (e.g. 'WH-DEL') or vendor ID.
        destination_wh: Target warehouse receiving the inventory (e.g. 'WH-MUM').
        quantity: Number of units to transfer.
        expedited: Whether to use priority expedited freight routing.
    """
    if incident_id:
        existing_order = next((order for order in ERP_DATABASE["transfer_orders"]
                               if order.get("incident_id") == incident_id
                               and order.get("status") == "AUTHORIZED_AND_DISPATCHED"), None)
        if existing_order:
            if existing_order.get("sku") != sku or existing_order.get("destination") != destination_wh:
                return json.dumps({
                    "success": False,
                    "error": f"Incident ID {incident_id} is already assigned to a different SKU or destination.",
                }, indent=2)
            return json.dumps({
                "success": True,
                "duplicate_prevented": True,
                "message": f"Incident {incident_id} already has dispatched order {existing_order['order_id']}; no additional reservation was made.",
                "order_details": existing_order,
            }, indent=2)
    if not isinstance(quantity, int) or quantity <= 0:
        return json.dumps({"success": False, "error": "quantity must be a positive integer."})
    if sku not in ERP_DATABASE["products"]:
        return json.dumps({"success": False, "error": f"SKU {sku} not found."})
    destination_stock = ERP_DATABASE["warehouses"].get(destination_wh, {}).get("stock", {}).get(sku)
    pack_size = destination_stock.get("lot_size", 1) if destination_stock else 1
    if quantity % pack_size != 0:
        return json.dumps({"success": False, "error": f"Quantity must be in multiples of the {pack_size}-unit case pack for {sku}."})
    if destination_wh not in ERP_DATABASE["warehouses"]:
        return json.dumps({"success": False, "error": f"Warehouse {destination_wh} not found."})
    if source_wh_or_vendor == destination_wh:
        return json.dumps({"success": False, "error": "Source and destination must differ."})
    is_internal = source_wh_or_vendor in ERP_DATABASE["warehouses"]
    if is_internal:
        source_stock = ERP_DATABASE["warehouses"][source_wh_or_vendor]["stock"].get(sku)
        if not source_stock:
            return json.dumps({"success": False, "error": f"SKU {sku} is unavailable at {source_wh_or_vendor}."})
        available = source_stock["on_hand"] - source_stock["reserved"]
        safety_stock = source_stock.get("safety_stock_units", source_stock["daily_burn_rate"] * 15)
        safe_transferable = max(0, available - safety_stock)
        if quantity > safe_transferable:
            return json.dumps({"success": False, "error": f"Only {safe_transferable} units can be transferred while preserving the {safety_stock}-unit safety stock at {source_wh_or_vendor}."})
    elif source_wh_or_vendor not in ERP_DATABASE["suppliers"]:
        return json.dumps({"success": False, "error": f"Unrecognized supplier {source_wh_or_vendor}."})
    else:
        supplier = ERP_DATABASE["suppliers"][source_wh_or_vendor]
        available_supplier_units = supplier["capacity_by_sku"].get(sku, 0) - supplier["reserved_by_sku"].get(sku, 0)
        if sku not in supplier["available_skus"]:
            return json.dumps({"success": False, "error": f"Supplier {source_wh_or_vendor} is not qualified for {sku}."})
        if quantity > available_supplier_units:
            return json.dumps({"success": False, "error": f"Supplier {source_wh_or_vendor} has only {available_supplier_units} units available."})

    created_at = datetime.datetime.now()
    timestamp = created_at.strftime("%Y-%m-%d %H:%M:%S")
    order_sequence = len(ERP_DATABASE["transfer_orders"]) + 1042
    order_id = f"TRX-{created_at.strftime('%y%m%d')}-{order_sequence}"
    
    # Internal transfer stock adjustment or qualified supplier reservation.
    if is_internal:
        src_wh = ERP_DATABASE["warehouses"][source_wh_or_vendor]
        # Deduct available by updating reserved
        if sku in src_wh["stock"]:
            src_wh["stock"][sku]["reserved"] += quantity
        route = get_route_quote(source_wh_or_vendor, destination_wh, expedited=expedited)
        transit_days = route["transit_days"]
        carrier = route["carrier"]
        total_freight = round(quantity * route["cost_per_unit_inr"], 2)
        procurement_cost = 0.0
        fulfillment_type = "INTERNAL_INTER_WAREHOUSE_TRANSFER"
    else:
        supplier = ERP_DATABASE["suppliers"][source_wh_or_vendor]
        supplier["reserved_by_sku"][sku] = supplier["reserved_by_sku"].get(sku, 0) + quantity
        transit_days = supplier["lead_time_days"]
        carrier = supplier["carrier"]
        total_freight = round(quantity * supplier["freight_per_unit_inr"], 2)
        procurement_cost = round(quantity * get_product_info(sku)["unit_price"] * (1 + supplier["rush_premium_pct"]), 2)
        fulfillment_type = "EMERGENCY_PURCHASE_ORDER"

    eta_date = _business_day_eta(created_at, transit_days).strftime("%Y-%m-%d")

    order_record = {
        "order_id": order_id,
        "incident_id": incident_id or None,
        "bill_of_lading": f"BOL-{created_at.strftime('%y%m%d')}-{order_sequence:06d}",
        "tracking_number": f"SIM-{created_at.strftime('%y%m%d')}-{order_sequence:08d}",
        "status": "AUTHORIZED_AND_DISPATCHED",
        "created_at": timestamp,
        "sku": sku,
        "quantity": quantity,
        "fulfillment_type": fulfillment_type,
        "source": source_wh_or_vendor,
        "destination": destination_wh,
        "freight_carrier": carrier,
        "priority_level": "EXPEDITED_CRITICAL" if expedited else "STANDARD",
        "estimated_delivery_date": eta_date,
        "logistics_cost_inr": total_freight,
        "procurement_cost_inr": procurement_cost,
        "estimated_total_cost_inr": round(total_freight + procurement_cost, 2),
        "estimated_distance_km": route["distance_km"] if is_internal else None,
        "erp_ledger_status": "STOCK_RESERVED_AND_IN_TRANSIT"
    }
    
    ERP_DATABASE["transfer_orders"].append(order_record)

    return json.dumps({
        "success": True,
        "message": f"Transfer Order {order_id} generated and successfully committed to ERP ledger.",
        "order_details": order_record
    }, indent=2)


# ==========================================
# TOOL SCHEMAS FOR AGENTIC LLM FUNCTION CALLING
# ==========================================
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "check_inventory_impact",
            "description": "Quantifies warehouse stockout risk, days of supply remaining, and financial revenue impact caused by a shipment delay.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sku": {
                        "type": "string",
                        "description": "The SKU identifier, e.g., 'SKU-402'."
                    },
                    "delay_days": {
                        "type": "integer",
                        "description": "Number of days the primary shipment is delayed."
                    },
                    "warehouse_id": {
                        "type": "string",
                        "description": "The target warehouse code (default 'WH-MUM')."
                    }
                },
                "required": ["sku", "delay_days"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_replenishment_options",
            "description": "Scans sister warehouse surplus inventory and spot suppliers to find viable stock rebalance sources.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sku": {
                        "type": "string",
                        "description": "The SKU identifier, e.g., 'SKU-402'."
                    },
                    "units_needed": {
                        "type": "integer",
                        "description": "Number of units required to prevent the stockout."
                    },
                    "destination_wh": {
                        "type": "string",
                        "description": "Destination warehouse code experiencing the deficit (default 'WH-MUM')."
                    }
                },
                "required": ["sku", "units_needed"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_stock_rebalance_order",
            "description": "Books an official stock transfer order in ERP, reserves units, and schedules priority carrier dispatch.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sku": {
                        "type": "string",
                        "description": "The SKU identifier, e.g., 'SKU-402'."
                    },
                    "source_wh_or_vendor": {
                        "type": "string",
                        "description": "Source warehouse ID (e.g. 'WH-DEL') or vendor code."
                    },
                    "destination_wh": {
                        "type": "string",
                        "description": "Target warehouse ID (e.g. 'WH-MUM')."
                    },
                    "quantity": {
                        "type": "integer",
                    "description": "Quantity to transfer; use the offered quantity from the sourcing tool so the SKU case-pack multiple and source availability are respected."
                    },
                    "expedited": {
                        "type": "boolean",
                        "description": "Whether to request expedited delivery."
                    },
                    "incident_id": {
                        "type": "string",
                        "description": "Optional disruption incident ID used to prevent duplicate transfer orders."
                    }
                },
                "required": ["sku", "source_wh_or_vendor", "destination_wh", "quantity"]
            }
        }
    }
]

# Map tool names to actual Python functions
TOOL_MAP = {
    "check_inventory_impact": check_inventory_impact,
    "find_replenishment_options": find_replenishment_options,
    "execute_stock_rebalance_order": execute_stock_rebalance_order
}

