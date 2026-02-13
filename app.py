"""
Insurance Fraud Ring Detection
Graph-Powered Investigation Platform for SIU Teams

Demonstrates how graph database technology reveals hidden fraud networks
that traditional relational methods consistently miss.

Version: 2.3 - Investigation Assistant Prompt Audit v3 Fixes
               - GAP-1: System prompt integration in call_llm()
               - GAP-2: Enhanced REASONING_PROMPT with investigative depth
               - GAP-3: Relationship direction guards in CYPHER_GENERATION_PROMPT
               - GAP-4: Multi-hop chain examples in few-shot prompts
               - GAP-5: Analytical framework in SYNTHESIS_PROMPT
               - GAP-6: Removed entity leakage from get_graph_schema_context()
               - GAP-7: Investigation chain patterns in SCHEMA_LITE
               - GAP-8: Extended complexity router patterns
"""

import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
from neo4j import GraphDatabase
import time
import json

# Import data generator
from scenario_data_generator import ScenarioDataGenerator

# =============================================================================
# LLM SDK IMPORTS (for Investigation Assistant)
# =============================================================================

GROQ_AVAILABLE = False
AZURE_OPENAI_AVAILABLE = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    pass

try:
    from openai import AzureOpenAI
    AZURE_OPENAI_AVAILABLE = True
except ImportError:
    pass

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Fraud Ring Detection | SIU Investigation Platform",
    layout="wide",
    page_icon="🔍",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 600;
    }
    .traditional-box {
        background-color: #FEE2E2;
        border-left: 4px solid #DC2626;
        padding: 1rem;
        border-radius: 4px;
        margin: 0.5rem 0;
        color: #1F2937;
    }
    .graph-box {
        background-color: #D1FAE5;
        border-left: 4px solid #059669;
        padding: 1rem;
        border-radius: 4px;
        margin: 0.5rem 0;
        color: #1F2937;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# PERFORMANCE TIMER
# =============================================================================

class PerformanceTimer:
    def __init__(self):
        self.start_time = None
        self.duration_ms = 0
        self.entity_count = 0
        self.relationship_count = 0
    
    def start(self):
        self.start_time = time.time()
    
    def stop(self):
        if self.start_time:
            self.duration_ms = round((time.time() - self.start_time) * 1000, 2)
        return self.duration_ms
    
    def set_counts(self, entities, relationships):
        self.entity_count = entities
        self.relationship_count = relationships

# =============================================================================
# NEO4J CONNECTION
# =============================================================================

@st.cache_resource
def get_neo4j_driver():
    try:
        uri = st.secrets["neo4j"]["uri"]
        user = st.secrets["neo4j"]["user"]
        password = st.secrets["neo4j"]["password"]
             
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        return driver
    
    except KeyError:
        st.error("**Configuration Required**: Neo4j credentials not found.")
        st.info("Please configure `.streamlit/secrets.toml` with Neo4j connection details.")
        return None
    
    except Exception as e:
        st.error(f"**Connection Failed**: {e}")
        return None

driver = get_neo4j_driver()
if driver is None:
    st.stop()

# =============================================================================
# VISUAL DESIGN SYSTEM
# =============================================================================

COLOR_MAP = {
    "Claim": "#4A90A4",
    "Claimant": "#5DADE2",
    "Witness": "#85C1E9",
    "Adjuster": "#58D68D",
    "Employee": "#48C9B0",
    "Provider": "#AF7AC5",
    "Attorney": "#F5B041",
    "BodyShop": "#EB984E",
    "Address": "#45B7A0",
    "Phone": "#5499C7",
    "Location": "#9B7ED9",
    "Vehicle": "#E74C3C",
    "Person": "#5DADE2",
    "Firm": "#D35400",
    "Policy": "#34495E",
    "Insurer": "#1A5276",
}

RELATIONSHIP_LABELS = {
    "FILED_BY": "filed by",
    "TREATED_AT": "treated at",
    "REPRESENTED_BY": "represented by",
    "HANDLED_BY": "handled by",
    "WITNESSED_BY": "witnessed by",
    "OCCURRED_AT": "occurred at",
    "INVOLVES_VEHICLE": "involves",
    "LIVES_AT": "lives at",
    "HAS_PHONE": "uses device",
    "COVERS": "covers",
    "HAS_POLICY": "policyholder",
    "UNDER_POLICY": "under policy",
    "INSURED_BY": "insured by",
    "LOCATED_AT": "located at",
    "OWNED_BY": "owned by",
    "FORMER_EMPLOYEE_OF": "formerly employed at",
    "INVOLVED": "involved in",
}

# =============================================================================
# SCENARIO DEFINITIONS (unchanged - all 4 scenarios remain identical)
# =============================================================================

SCENARIOS = {
    1: {
        "title": "Provider-Attorney Collusion",
        "subtitle": "Provider-Attorney Collusion via Unstructured Data",
        "icon": "🕸️",
        "starting_entity": ("Provider", "PROV_S1_MAIN", "Metro Care Clinic"),
        "exposure": "$162,000",
        "claims_count": 45,
        "trigger": """
**Predictive Model Alert:** *"Provider Billing Anomaly"*

**Metro Care Clinic** flagged: Average claim severity **20% higher** than regional peers for minor-impact soft tissue claims.

| Metric | Metro Care | Peer Average | Variance |
|--------|-----------|--------------|----------|
| Avg. Claim | $3,600 | $3,000 | +20% |
| Attorney Rep. | ? | ~12% | Unknown |

**Standard Assessment:** 20% variance warrants review but isn't conclusive. Could be patient mix or treatment protocols.

**The Question:** Statistical noise, or organized fraud?
        """,
        "hops": [
            {
                "depth": 0,
                "title": "The Flagged Provider",
                "narrative": "We begin with the anomalous provider. 20% above peers warrants a look, but isn't conclusive. Metro Care has valid licenses and proper billing codes.",
                "traditional": "Query shows 45 claims with valid CPT codes. Multiple referring attorneys suggest a diverse, legitimate referral base. <strong>20% variance noted but not actionable.</strong>",
                "graph_insight": None,
                "business_impact": None,
                "query": """
                    MATCH (p:Provider {id: 'PROV_S1_MAIN'})
                    RETURN p
                """
            },
            {
                "depth": 1,
                "title": "The Referral Pattern",
                "narrative": "Expanding one hop: Who sends patients here, and who represents them? We expect diverse sources for a legitimate high-volume clinic.",
                "traditional": "Attorney names appear independent: 'Smith & Associates', 'Doe Legal Group', 'Rapid Legal Services'. Different names, different tax IDs. <strong>Nothing unusual.</strong>",
                "graph_insight": "<strong>First Red Flag:</strong> 100% of Metro Care's patients have attorney representation. Industry norm is 10-15%. And all 45 claims funnel through just 3 law firms.",
                "business_impact": "Traditional view sees 3 separate firms. Graph reveals total concentration.",
                "query": """
                    MATCH (p:Provider {id: 'PROV_S1_MAIN'})
                    MATCH (c:Claim)-[:TREATED_AT]->(p)
                    MATCH (c)-[:REPRESENTED_BY]->(a:Attorney)
                    MATCH (c)-[:FILED_BY]->(claimant:Person)
                    RETURN p, c, a, claimant
                """
            },
            {
                "depth": 2,
                "title": "The Hidden Link (OCR Discovery)",
                "narrative": "Three attorneys with different names and tax IDs. Are they truly independent competitors? We check for shared attributes extracted from unstructured documents.",
                "traditional": "No SQL join exists between these attorney entities. They appear in separate tables with no foreign key relationship. <strong>Investigation stalls here.</strong>",
                "graph_insight": "<strong>The Breakthrough:</strong> OCR extraction from demand letter headers reveals all 3 'competing' attorneys share the <strong>same fax number</strong>: (555) 019-9999. They operate from the same office suite - a single operation masquerading as three independent firms.",
                "business_impact": "This link exists only in scanned PDFs - completely invisible to relational queries.",
                "query": """
                    MATCH (p:Provider {id: 'PROV_S1_MAIN'})<-[:TREATED_AT]-(c:Claim)-[:REPRESENTED_BY]->(a:Attorney)
                    MATCH (a)-[:HAS_PHONE]->(fax:Phone {type: 'Fax'})
                    RETURN p, c, a, fax
                """
            },
            {
                "depth": 3,
                "title": "Quantifying the Ring",
                "narrative": "With collusion proven, we isolate and quantify the fraud ring's full exposure.",
                "traditional": "Proving collusion requires manually reviewing 45 claim files, comparing demand letters, checking office addresses. <strong>Weeks of work - if attempted at all.</strong>",
                "graph_insight": "<strong>Instant Quantification:</strong> The graph isolates all claims flowing through the collusion network: <strong>45 claims x $3,600 = $162,000</strong> in provable exposure. All claims now deniable for fraud.",
                "business_impact": "20% variance alone was not actionable. Proving collusion makes 100% of claims deniable.",
                "query": """
                    MATCH (fax:Phone {id: 'FAX_S1_SHARED'})<-[:HAS_PHONE]-(a:Attorney)<-[:REPRESENTED_BY]-(c:Claim)-[:TREATED_AT]->(p:Provider {id: 'PROV_S1_MAIN'})
                    MATCH (c)-[:FILED_BY]->(per:Person)
                    RETURN fax, a, c, p, per
                """
            }
        ],
        "conclusion": {
            "exposure": "$162,000 (45 claims x $3,600 avg)",
            "traditional_time": "3-4 weeks manual file review",
            "graph_time": "45 seconds",
            "key_finding": "20% billing variance alone was not actionable. Graph proved three 'independent' law firms are a single operation - making all 45 claims deniable for fraud conspiracy.",
            "actions": [
                "Deny all 45 claims citing proven collusion",
                "Flag Metro Care Clinic for SIU investigation",
                "File complaint with State Bar regarding shell firm structure",
                "Add shared fax/device pattern to fraud detection rules"
            ]
        }
    },
    
    2: {
        "title": "Staged Accident",
        "subtitle": "Staged Accident Ring via Role Rotation",
        "icon": "🎭",
        "starting_entity": ("Person", "P_S2_A", "Darius Thorne"),
        "exposure": "$120,000",
        "claims_count": 4,
        "trigger": """
**Weak Signal Alert:** *"Participant Recurrence"*

A witness on a newly filed intersection collision, **Darius Thorne**, has one prior database appearance - as a **passenger** in an unrelated accident 6 months ago.

| Current Claim | Prior History |
|--------------|---------------|
| Role: Witness | 1 prior claim (Passenger) |
| Claim Amount: $35,000 | Below frequency threshold |

**Standard Assessment:** Two claims in different roles = coincidence. No flag triggered.

**The Question:** Bad luck at a busy intersection, or something more coordinated?
        """,
        "hops": [
            {
                "depth": 0,
                "title": "The Recurring Witness",
                "narrative": "Darius Thorne provided a witness statement for the current claim. Standard procedure: check if he's filed claims before.",
                "traditional": "Search 'Darius Thorne' in claimant database. Result: 1 prior claim as passenger. Below frequency threshold. <strong>No flag triggered.</strong>",
                "graph_insight": None,
                "business_impact": None,
                "query": """
                    MATCH (p:Person {id: 'P_S2_A'})
                    RETURN p
                """
            },
            {
                "depth": 1,
                "title": "Cross-Role History",
                "narrative": "Instead of searching 'claimants named Darius', we ask: 'Show me every claim Darius touched, in any capacity.'",
                "traditional": "Systems segregate data by role. Claimant tables != Witness tables != Passenger tables. Cross-referencing requires manual effort across multiple systems.",
                "graph_insight": "<strong>Role Rotation Detected:</strong> Darius appears in 4 claims with 3 different roles: Driver (1), Passenger (1), Witness (2). No single-role query catches this pattern.",
                "business_impact": "Graph treats the Person as the entity, not the role. All touchpoints visible instantly.",
                "query": """
                    MATCH (p:Person {id: 'P_S2_A'})
                    MATCH (p)-[r]-(c:Claim)
                    RETURN p, r, c
                """
            },
            {
                "depth": 2,
                "title": "The Ring Topology",
                "narrative": "Who else was involved in Darius's claims? We expand to see if the same people keep appearing together.",
                "traditional": "Requires reading police reports from 4 different accidents to manually note other parties. Time-prohibitive for a 'minor' witness flag.",
                "graph_insight": "<strong>Crash Ring Identified:</strong> The same 4 people (Darius, Sarah, Mike, Lisa) rotate through Driver/Passenger/Witness roles across all claims. They're never in the same role twice.",
                "business_impact": "Classic 'Swoop and Squat' pattern: participants cycle roles to evade per-role frequency counters.",
                "query": """
                    MATCH (p:Person {id: 'P_S2_A'})-[r1]-(c:Claim)-[r2]-(associate:Person)
                    WHERE associate.id <> p.id
                    RETURN DISTINCT p, c, associate, r1, r2
                """
            },
            {
                "depth": 3,
                "title": "The Ghost Address",
                "narrative": "These four claim to live at different addresses now. But did they ever share an address? We check historical residence data.",
                "traditional": "Current address searches show 4 different locations. No obvious connection. <strong>Case closed as coincidence.</strong>",
                "graph_insight": "<strong>Safe House Found:</strong> All 4 individuals listed the same address (778 Elm Street) on claims filed 2+ years ago. This 'Ghost Address' was used to incubate identities before the ring went active.",
                "business_impact": "Graph preserves historical relationships that point-in-time queries miss entirely.",
                "query": """
                    MATCH (ghost:Address {id: 'ADDR_S2_GHOST'})
                    MATCH (p:Person)-[:LIVES_AT]->(ghost)
                    RETURN ghost, p
                """
            }
        ],
        "conclusion": {
            "exposure": "$120,000 (4 claims x $30k avg)",
            "traditional_time": "Missed entirely (looked like unrelated accidents)",
            "graph_time": "Instant pattern detection",
            "key_finding": "Classic Crash-for-Cash ring using Role Rotation to evade frequency-based detection. Connected by historical 'Ghost Address'.",
            "actions": [
                "Deny current claim - witness bias/conspiracy",
                "Mark all 4 individuals as 'Ring Members' in ISO ClaimSearch",
                "Refer to NICB for organized fraud investigation",
                "Add role-rotation detection to fraud scoring model"
            ]
        }
    },
    
    3: {
        "title": "Vehicle Recycling",
        "subtitle": "Vehicle Recycling & Policy Hopping",
        "icon": "🚗",
        "starting_entity": ("Vehicle", "VEH_S3_MAIN", "BMW X5 (VIN: ...3456)"),
        "exposure": "$185,000",
        "claims_count": 3,
        "trigger": """
**New Policy Alert:** *"High-Value Asset / Short Tenure"*

A 2023 BMW X5 was insured **50 days ago**. A **Total Loss** claim has just been filed for "Hit and Run" damage while street parked.

| Attribute | Value | Risk Signal |
|-----------|-------|-------------|
| Policy Tenure | 50 days | Warning: Short |
| Claim Amount | $65,000 | Full vehicle value |
| Policyholder | Alice Vane | Clean record |
| Prior Claims (Alice) | 0 | No history |

**Standard Assessment:** Clean claimant + valid policy + documented damage = Approve payment.

**The Question:** Is this legitimate bad luck, or is the *vehicle itself* the problem?
        """,
        "hops": [
            {
                "depth": 0,
                "title": "Person-Centric View (Traditional)",
                "narrative": "Standard investigation focuses on the claimant. Alice Vane has a clean record - no prior claims, valid license, good credit.",
                "traditional": "Claimant check: Clean. Vehicle exists and matches registration. Premium was paid. <strong>Claim approved for payment.</strong>",
                "graph_insight": None,
                "business_impact": None,
                "query": """
                    MATCH (v:Vehicle {id: 'VEH_S3_MAIN'})
                    RETURN v
                """
            },
            {
                "depth": 1,
                "title": "Asset-Centric View (Graph)",
                "narrative": "We pivot the investigation: instead of 'Who is Alice?', we ask 'What is the history of this VIN?'",
                "traditional": "ISO/NICB might show prior claims on this VIN, but without policy context (tenure, ownership chain) the pattern is not clear.",
                "graph_insight": "<strong>Repeat Offender Vehicle:</strong> This VIN has been involved in <strong>3 Total Loss claims</strong> in 18 months, with 3 different 'owners'. Each time: same pattern.",
                "business_impact": "The fraud follows the asset, not the person. Person-centric systems miss this entirely.",
                "query": """
                    MATCH (v:Vehicle {id: 'VEH_S3_MAIN'})
                    MATCH (c:Claim)-[:INVOLVES_VEHICLE]->(v)
                    MATCH (c)-[:FILED_BY]->(p:Person)
                    RETURN v, c, p
                """
            },
            {
                "depth": 2,
                "title": "The Policy Hopping Pattern",
                "narrative": "Overlaying policy tenure data on each claim. How long was the vehicle insured before each 'accident'?",
                "traditional": "Policy systems and claims systems are separate. Correlating tenure-to-loss requires manual data pulls across platforms.",
                "graph_insight": "<strong>Bind-Crash-Cash Pattern:</strong> All 3 losses occurred within 45-50 days of policy binding. Vehicle is insured, 'totaled' on paper, payout collected, vehicle retained and re-insured.",
                "business_impact": "Temporal pattern is invisible without graph edges connecting Policy to Vehicle to Claim.",
                "query": """
                    MATCH (v:Vehicle {id: 'VEH_S3_MAIN'})
                    MATCH (c:Claim)-[:INVOLVES_VEHICLE]->(v)
                    MATCH (c)-[:FILED_BY]->(p:Person)
                    MATCH (p)-[:HAS_POLICY]->(pol:Policy)-[:COVERS]->(v)
                    RETURN v, c, p, pol
                """
            },
            {
                "depth": 3,
                "title": "The Device Fingerprint",
                "narrative": "Three different owners with clean records. Are they truly unrelated? We check for shared digital identifiers.",
                "traditional": "Alice, Marcus, and Keisha have different SSNs, addresses, and phone numbers. <strong>No link found.</strong>",
                "graph_insight": "<strong>Same Operator:</strong> All 3 'owners' bound their policies using the <strong>same mobile device fingerprint</strong>. They're either the same person with fake IDs, or a coordinated crew.",
                "business_impact": "Digital breadcrumbs (device IDs, IP addresses) create links invisible to traditional identity matching.",
                "query": """
                    MATCH (v:Vehicle {id: 'VEH_S3_MAIN'})<-[:INVOLVES_VEHICLE]-(c:Claim)-[:FILED_BY]->(p:Person)
                    MATCH (p)-[:HAS_PHONE]->(device:Phone)
                    RETURN v, c, p, device
                """
            }
        ],
        "conclusion": {
            "exposure": "$185,000 (3 Total Loss payouts)",
            "traditional_time": "Paid as 'bad luck' (clean claimant)",
            "graph_time": "< 2 minutes",
            "key_finding": "Vehicle Recycling Scheme: Asset is 'totaled' on paper, retained by the crew, and re-insured under new identities. Digital fingerprint connects seemingly unrelated owners.",
            "actions": [
                "Deny current claim - Pre-existing damage / Fraud",
                "Flag VIN as 'Do Not Insure' in underwriting systems",
                "Investigate body shop that inspected prior 'total losses'",
                "Add device fingerprint matching to policy binding workflow"
            ]
        }
    },
    
    4: {
        "title": "Network Migration",
        "subtitle": "Post-Prosecution Network Evolution",
        "icon": "🔄",
        "starting_entity": ("Provider", "PROV_S4_BERNARD", "Dr. Bernard's Auto Injury Center"),
        "exposure": "$280,000+",
        "claims_count": 49,
        "trigger": """
**Case Review:** *Closed Investigation - 6 Months Ago*

**Dr. Bernard's Auto Injury Center** was successfully prosecuted for insurance fraud.

| Outcome | Result |
|---------|--------|
| Fraudulent Claims | 15 identified |
| Total Denied | ~$65,000 |
| Provider License | **Revoked** |
| Referring Attorney | Noted, not sanctioned |
| Case Status | **Closed & Archived** |

**Standard Outcome:** Provider eliminated. Claims denied. Victory declared. Resources redeployed.

**The Question:** Did we dismantle the fraud operation, or merely remove one replaceable component?
        """,
        "hops": [
            {
                "depth": 0,
                "title": "The Closed Case",
                "narrative": "Dr. Bernard's was confirmed fraud. License revoked, claims denied, case closed. Investigation resources moved to new matters.",
                "traditional": "Case file archived. Provider blacklisted. <strong>Success recorded. Move on.</strong>",
                "graph_insight": None,
                "business_impact": None,
                "query": """
                    MATCH (p:Provider {id: 'PROV_S4_BERNARD'})
                    RETURN p
                """
            },
            {
                "depth": 1,
                "title": "The Original Network",
                "narrative": "Reviewing the prosecuted case: 15 fraudulent claims, all denied. But who else was involved?",
                "traditional": "Case notes mention 'multiple claimants used same attorney' but no systematic follow-up on the attorney was conducted.",
                "graph_insight": "<strong>Concentration Pattern:</strong> 12 of 15 claimants (80%) were represented by <strong>Attorney Michael Chen</strong>. Chen was noted in the file but <strong>never sanctioned</strong>.",
                "business_impact": "Relational case management closes the provider node. Graph reveals the network persists.",
                "query": """
                    MATCH (prov:Provider {id: 'PROV_S4_BERNARD'})
                    MATCH (c:Claim)-[:TREATED_AT]->(prov)
                    OPTIONAL MATCH (c)-[:REPRESENTED_BY]->(a:Attorney)
                    OPTIONAL MATCH (c)-[:FILED_BY]->(p:Person)
                    RETURN prov, c, a, p
                """
            },
            {
                "depth": 2,
                "title": "The Unsanctioned Attorney",
                "narrative": "What is Attorney Michael Chen doing now? We check his current client activity.",
                "traditional": "Chen faced no sanctions. Checking his current caseload requires pulling 34 individual claim files. <strong>Resource-prohibitive for a 'closed' case.</strong>",
                "graph_insight": "<strong>Active and Growing:</strong> Chen has acquired <strong>34 new clients</strong> since Dr. Bernard's was shut down. His practice continues unimpeded - and accelerating.",
                "business_impact": "The 'bridge' between old and new fraud networks is often an unsanctioned professional.",
                "query": """
                    MATCH (a:Attorney {id: 'ATT_S4_CHEN'})
                    MATCH (c:Claim)-[:REPRESENTED_BY]->(a)
                    WHERE c.status = 'Open'
                    OPTIONAL MATCH (c)-[:FILED_BY]->(p:Person)
                    RETURN a, c, p
                """
            },
            {
                "depth": 3,
                "title": "The New Treatment Facility",
                "narrative": "Where are Chen's new clients being treated? We analyze provider distribution.",
                "traditional": "Pulling 34 claim files to check treatment providers. For a closed case, this investigation would never be initiated.",
                "graph_insight": "<strong>Concentration Recurs:</strong> 28 of 34 Chen clients (82%) are treated at <strong>Rapid Recovery Medical</strong> - a clinic that opened 2 months after Dr. Bernard's was shut down.",
                "business_impact": "The fraud operation migrated, not ended. Same attorney, new provider front.",
                "query": """
                    MATCH (a:Attorney {id: 'ATT_S4_CHEN'})<-[:REPRESENTED_BY]-(c:Claim)-[:TREATED_AT]->(prov:Provider)
                    WHERE c.status = 'Open'
                    OPTIONAL MATCH (c)-[:FILED_BY]->(p:Person)
                    RETURN a, c, prov, p
                """
            },
            {
                "depth": 4,
                "title": "The Ownership Connection",
                "narrative": "Who owns Rapid Recovery Medical? We check corporate registry data integrated into the graph.",
                "traditional": "Corporate registry research on a new provider connected to a closed case? <strong>This investigation would never be initiated.</strong>",
                "graph_insight": "<strong>The Phoenix:</strong> Rapid Recovery is owned by <strong>Dr. Patricia Simmons</strong> - a former Associate Physician at Dr. Bernard's. The fraud network didn't die; it <strong>migrated</strong>.",
                "business_impact": "Employment history creates 'soft links' between old and new operations that blacklists miss entirely.",
                "query": """
                    MATCH (new:Provider {id: 'PROV_S4_RAPID'})
                    MATCH (new)-[:OWNED_BY]->(owner:Person)
                    MATCH (owner)-[:FORMER_EMPLOYEE_OF]->(old:Provider {id: 'PROV_S4_BERNARD'})
                    RETURN new, owner, old
                """
            }
        ],
        "conclusion": {
            "exposure": "Original: ~$65K denied | Active Network: $280,000+",
            "traditional_time": "Case closed. Network continues undetected.",
            "graph_time": "Network migration detected in < 2 minutes",
            "key_finding": "Fraud networks adapt and migrate. Graph reveals persistent connection points (the attorney) linking old and new operations through employment history.",
            "actions": [
                "Reopen investigation - Network Active",
                "Initiate SIU review of Rapid Recovery Medical",
                "Subpoena Attorney Chen's complete case files",
                "Flag all 34 active claimants for expedited review",
                "Add 'former employee' checks to new provider vetting"
            ]
        }
    }
}

# =============================================================================
# GRAPH VISUALIZATION (original streamlit-agraph based)
# =============================================================================

def get_node_label(labels):
    priority = ["Claimant", "Witness", "Adjuster", "Employee", "Provider", 
                "Attorney", "BodyShop", "Address", "Phone", "Location", "Claim", 
                "Person", "Vehicle", "Policy", "Firm", "Insurer"]
    for p in priority:
        if p in labels:
            return p
    return labels[0] if labels else "Unknown"


def format_currency(amount):
    if amount:
        return f"${amount:,.0f}"
    return "N/A"


def create_graph_visualization(records, root_id=None, entity_filters=None):
    """Create graph visualization with enhanced tooltips and optional entity filtering."""
    nodes = {}
    edges = []
    
    for record in records:
        for key, value in record.items():
            if value is None:
                continue
            
            if hasattr(value, 'labels'):
                element_id = value.element_id
                if element_id in nodes:
                    continue
                
                labels = list(value.labels)
                props = dict(value)
                label = get_node_label(labels)
                
                # Apply entity filter if specified
                if entity_filters and label not in entity_filters:
                    continue
                
                node_id = props.get('id', str(element_id))
                name = props.get('name', props.get('number', props.get('street', props.get('vin', node_id))))
                
                color = COLOR_MAP.get(label, "#AAB7B8")
                size = 30
                is_root = (root_id and node_id == root_id)
                if is_root:
                    size = 50
                
                tooltip_lines = [f"--- {label.upper()} ---", f"Name: {name}"]
                
                if label == "Claim":
                    if props.get('claim_amount'):
                        tooltip_lines.append(f"Amount: {format_currency(props['claim_amount'])}")
                    if props.get('status'):
                        tooltip_lines.append(f"Status: {props['status']}")
                    if props.get('incident_type'):
                        tooltip_lines.append(f"Type: {props['incident_type']}")
                elif label == "Policy":
                    if props.get('bind_date'):
                        tooltip_lines.append(f"Bound: {props['bind_date']}")
                elif label == "Phone":
                    if props.get('type'):
                        tooltip_lines.append(f"Device: {props['type']}")
                    if props.get('number'):
                        tooltip_lines.append(f"Number: {props['number']}")
                
                tooltip_lines.append(f"\nID: {node_id}")
                
                nodes[element_id] = Node(
                    id=str(element_id),
                    label=str(name)[:20] + "..." if len(str(name)) > 20 else str(name),
                    size=size,
                    color=color,
                    title="\n".join(tooltip_lines),
                    shape="star" if is_root else "dot",
                    borderWidth=3 if is_root else 2,
                    font={"size": 11, "color": "#FFFFFF", "strokeWidth": 2, "strokeColor": "#000000"}
                )
    
    # Process relationships
    edge_set = set()
    for record in records:
        record_dict = dict(record)
        for key, value in record_dict.items():
            if value is None:
                continue
            
            # Handle relationship objects
            if hasattr(value, 'type') and hasattr(value, 'start_node'):
                rel = value
                if rel.start_node.element_id in nodes and rel.end_node.element_id in nodes:
                    source = str(rel.start_node.element_id)
                    target = str(rel.end_node.element_id)
                    edge_key = f"{source}-{target}-{rel.type}"
                    
                    if edge_key not in edge_set:
                        edge_set.add(edge_key)
                        rel_label = RELATIONSHIP_LABELS.get(rel.type, rel.type.replace("_", " ").lower())
                        
                        props = dict(rel)
                        if props.get('role'):
                            rel_label = f"{rel_label} ({props['role']})"
                        
                        edges.append(Edge(
                            source=source,
                            target=target,
                            title=f"Rel: {rel_label}",
                            label=rel_label,
                            color="#888888",
                            width=2,
                            smooth={"type": "continuous"},
                            arrows={"to": {"enabled": True, "scaleFactor": 0.5}}
                        ))
    
    return list(nodes.values()), edges


def get_graph_config(width=700, height=450):
    return Config(
        width=width,
        height=height,
        directed=True,
        physics={
            "enabled": True,
            "stabilization": {"enabled": True, "iterations": 100},
            "solver": "forceAtlas2Based",
            "forceAtlas2Based": {
                "gravitationalConstant": -50,
                "centralGravity": 0.01,
                "springLength": 100,
                "springConstant": 0.08
            }
        },
        interaction={"hover": True, "tooltipDelay": 50, "zoomView": True, "dragView": True}
    )

# =============================================================================
# QUERY HELPERS
# =============================================================================

def run_query(query):
    with driver.session() as session:
        result = session.run(query)
        return list(result)


def get_relationships_for_nodes(node_ids):
    if not node_ids:
        return []
    with driver.session() as session:
        result = session.run("""
            MATCH (a)-[r]-(b)
            WHERE elementId(a) IN $ids AND elementId(b) IN $ids
            RETURN a, r, b
        """, ids=list(node_ids))
        return list(result)


def get_database_stats():
    with driver.session() as session:
        stats = {}
        result = session.run("MATCH (n) RETURN count(n) as count").single()
        stats['total_nodes'] = result['count'] if result else 0
        result = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()
        stats['total_relationships'] = result['count'] if result else 0
        result = session.run("MATCH (c:Claim) RETURN count(c) as count").single()
        stats['claims'] = result['count'] if result else 0
        return stats


def get_entity_types():
    with driver.session() as session:
        result = session.run("CALL db.labels()")
        return sorted([r[0] for r in result])


def get_entities_by_type(entity_type):
    with driver.session() as session:
        result = session.run(f"""
            MATCH (n:{entity_type})
            RETURN n.id AS id, n.name AS name, n.number as number, n.street as street, n.vin as vin
            ORDER BY n.name, n.number
            LIMIT 500
        """)
        entities = []
        for r in result:
            display = r['name'] or r['number'] or r['street'] or r['vin'] or r['id']
            entities.append((r['id'], display))
        return entities


def get_neighborhood(entity_type, entity_id, hops):
    with driver.session() as session:
        query = f"""
            MATCH path = (root:{entity_type} {{id: $entity_id}})-[*1..{hops}]-(connected)
            UNWIND relationships(path) as r
            WITH DISTINCT startNode(r) as a, r, endNode(r) as b
            RETURN a, r, b
        """
        result = session.run(query, entity_id=entity_id)
        return list(result)

# =============================================================================
# PAGE: SCENARIO WALKTHROUGH (unchanged)
# =============================================================================

def render_scenario_walkthrough():
    st.title("🎯 Fraud Network Investigation")
    st.caption("Step-by-step demonstration of graph-powered fraud detection")
    
    if 'current_scenario' not in st.session_state:
        st.session_state.current_scenario = 1
    if 'current_hop' not in st.session_state:
        st.session_state.current_hop = 0
    
    # Scenario selector
    scenario_options = {
        1: "🕸️ 1: Provider-Attorney Collusion",
        2: "🎭 2: Staged Accident", 
        3: "🚗 3: Vehicle Recycling",
        4: "🔄 4: Network Migration"
    }
    
    col_select, col_reset = st.columns([5, 1])
    with col_select:
        selected = st.selectbox(
            "Select Investigation",
            options=list(scenario_options.keys()),
            format_func=lambda x: scenario_options[x],
            index=st.session_state.current_scenario - 1,
            label_visibility="collapsed"
        )
    with col_reset:
        if st.button("↩️ Reset"):
            st.session_state.current_hop = 0
            st.rerun()
    
    if selected != st.session_state.current_scenario:
        st.session_state.current_scenario = selected
        st.session_state.current_hop = 0
        st.rerun()
    
    scenario = SCENARIOS[selected]
    max_hop = len(scenario['hops']) - 1
    current_hop = st.session_state.current_hop
    hop = scenario['hops'][current_hop]
    
    # Header with key metrics
    st.markdown(f"### {scenario['icon']} {scenario['title']}")
    
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Total Exposure", scenario['exposure'])
    with col_m2:
        st.metric("Claims Involved", scenario['claims_count'])
    with col_m3:
        st.metric("Investigation Step", f"{current_hop + 1} / {max_hop + 1}")
    
    # Trigger (collapsed after first step)
    with st.expander("📋 Investigation Trigger", expanded=(current_hop == 0)):
        st.markdown(scenario['trigger'])
    
    st.divider()
    
    # Navigation
    st.markdown(f"**Step {current_hop + 1}: {hop['title']}**")
    st.progress((current_hop + 1) / (max_hop + 1))
    
    nav1, nav2, nav3, nav4 = st.columns([1, 1, 2, 1])
    with nav1:
        if st.button("← Previous", disabled=(current_hop == 0), use_container_width=True):
            st.session_state.current_hop -= 1
            st.rerun()
    with nav2:
        if current_hop < max_hop:
            if st.button("Next →", type="primary", use_container_width=True):
                st.session_state.current_hop += 1
                st.rerun()
        else:
            st.button("✓ Complete", disabled=True, use_container_width=True)
    
    st.markdown("")
    
    # Main content: side-by-side comparison (narrower left, wider graph on right)
    col_left, col_right = st.columns([2, 3])
    
    with col_left:
        st.markdown("##### 🔍 Analysis")
        st.info(hop['narrative'])
        
        # Traditional vs Graph - PROMINENT comparison
        st.markdown("##### ⚖️ Traditional vs Graph")
        
        st.markdown(f"""
<div class="traditional-box">
<strong>🐌 Traditional SQL Approach</strong><br>
{hop['traditional']}
</div>
        """, unsafe_allow_html=True)
        
        if hop['graph_insight']:
            st.markdown(f"""
<div class="graph-box">
<strong>⚡ Graph Discovery</strong><br>
{hop['graph_insight']}
</div>
            """, unsafe_allow_html=True)
            
            if hop.get('business_impact'):
                st.caption(f"💡 *{hop['business_impact']}*")
    
    with col_right:
        st.markdown("##### 🕸️ Network Visualization")
        
        timer = PerformanceTimer()
        timer.start()
        
        try:
            records = run_query(hop['query'])
            
            # Get all node IDs and fetch relationships
            node_ids = set()
            for record in records:
                for value in record.values():
                    if value and hasattr(value, 'element_id'):
                        node_ids.add(value.element_id)
            
            rel_records = get_relationships_for_nodes(node_ids) if node_ids else []
            timer.stop()
            
            if records or rel_records:
                nodes, edges = create_graph_visualization(
                    records + rel_records,
                    scenario['starting_entity'][1]
                )
                timer.set_counts(len(nodes), len(edges))
                
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric("Query", f"{timer.duration_ms}ms")
                with m2:
                    st.metric("Entities", len(nodes))
                with m3:
                    st.metric("Links", len(edges))
                
                config = get_graph_config(width=850, height=500)
                agraph(nodes, edges, config)
            else:
                st.warning("No data. Generate demo data in Administration.")
        
        except Exception as e:
            st.error(f"Query error: {str(e)[:100]}")
    
    # Conclusion panel (final step only)
    if current_hop == max_hop:
        st.divider()
        st.markdown("### 📊 Investigation Summary")
        
        conclusion = scenario['conclusion']
        
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            st.metric("💰 Total Exposure", conclusion['exposure'])
        with col_c2:
            st.metric("🐌 Traditional Time", conclusion['traditional_time'])
        with col_c3:
            st.metric("⚡ Graph Time", conclusion['graph_time'])
        
        st.success(f"**Key Finding:** {conclusion['key_finding']}")
        
        with st.expander("📋 Recommended Actions", expanded=True):
            for i, action in enumerate(conclusion['actions'], 1):
                st.markdown(f"{i}. {action}")

# =============================================================================
# PAGE: FREE EXPLORATION (unchanged)
# =============================================================================

def render_free_exploration():
    st.title("🔍 Network Explorer")
    st.caption("Investigate any entity's connections in the fraud network database")
    
    entity_types = get_entity_types()
    if not entity_types:
        st.warning("Database empty. Generate data in Administration.")
        return
    
    # Selection controls
    col1, col2, col3, col4 = st.columns([2, 3, 1, 1])
    
    with col1:
        selected_type = st.selectbox("Entity Type", entity_types)
    
    with col2:
        entities = get_entities_by_type(selected_type)
        if not entities:
            st.warning(f"No {selected_type} entities found")
            return
        selected_entity = st.selectbox("Select Entity", entities, format_func=lambda x: x[1])
    
    with col3:
        hops = st.number_input("Depth", 1, 4, 2)
    
    with col4:
        st.markdown("")
        st.markdown("")
        explore = st.button("🔍 Explore", type="primary", use_container_width=True)
    
    # Entity type filters
    st.markdown("**Filter Visible Entity Types:**")
    
    filter_types = ["Claim", "Person", "Provider", "Attorney", "Address", "Phone", 
                    "Vehicle", "Policy", "Location", "Insurer"]
    available_filters = [ft for ft in filter_types if ft in entity_types]
    
    # Initialize filter state if needed
    if 'explore_filters' not in st.session_state:
        st.session_state.explore_filters = set(available_filters)
    
    # Create checkbox columns
    filter_cols = st.columns(min(len(available_filters), 5))
    
    active_filters = set()
    for i, filter_type in enumerate(available_filters):
        with filter_cols[i % 5]:
            is_selected_type = (filter_type == selected_type)
            
            if is_selected_type:
                st.checkbox(
                    filter_type,
                    value=True,
                    disabled=True,
                    key=f"filter_{filter_type}",
                    help=f"Cannot hide {filter_type} - it's your starting entity"
                )
                active_filters.add(filter_type)
            else:
                if st.checkbox(
                    filter_type,
                    value=filter_type in st.session_state.explore_filters,
                    key=f"filter_{filter_type}"
                ):
                    active_filters.add(filter_type)
    
    # Always include selected type
    active_filters.add(selected_type)
    st.session_state.explore_filters = active_filters
    
    if explore:
        timer = PerformanceTimer()
        timer.start()
        
        with st.spinner("Mapping network..."):
            records = get_neighborhood(selected_type, selected_entity[0], hops)
            timer.stop()
            
            if records:
                nodes, edges = create_graph_visualization(
                    records, 
                    selected_entity[0],
                    entity_filters=active_filters
                )
                timer.set_counts(len(nodes), len(edges))
                
                st.session_state.explore_data = {
                    'nodes': nodes,
                    'edges': edges,
                    'timer': timer,
                    'name': selected_entity[1]
                }
            else:
                st.warning("No connections found.")
                st.session_state.explore_data = None
    
    if st.session_state.get('explore_data'):
        data = st.session_state.explore_data
        
        st.divider()
        st.markdown(f"### Network: {data['name']}")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Query Time", f"{data['timer'].duration_ms}ms")
        with c2:
            st.metric("Entities", len(data['nodes']))
        with c3:
            st.metric("Connections", len(data['edges']))
        
        config = get_graph_config(width="100%", height=550)
        agraph(data['nodes'], data['edges'], config)

# =============================================================================
# PAGE: ADMINISTRATION (unchanged)
# =============================================================================

def render_admin():
    st.title("⚙️ Administration")
    st.caption("Database management and scenario data generation")
    
    # Database Status
    st.markdown("### 📊 Database Status")
    
    try:
        stats = get_database_stats()
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total Nodes", f"{stats['total_nodes']:,}")
        with c2:
            st.metric("Relationships", f"{stats['total_relationships']:,}")
        with c3:
            st.metric("Claims", f"{stats['claims']:,}")
        
        if stats['total_nodes'] == 0:
            st.info("📭 Database empty. Generate scenario data below.")
    except Exception as e:
        st.error(f"Stats error: {e}")
    
    st.divider()
    
    # Data Generation
    st.markdown("### 🚀 Generate Demo Data")
    st.warning("⚠️ This will **clear all existing data** and generate fresh scenarios.")
    
    if st.button("Generate All Scenarios", type="primary", use_container_width=True):
        with st.spinner("Generating data..."):
            try:
                generator = ScenarioDataGenerator()
                result = generator.generate_all_demo_data()
                generator.close()
                
                if result['status'] == 'success':
                    st.success("✅ Data generated successfully!")
                    st.json(result)
                    st.balloons()
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error(f"Generation failed: {result.get('message')}")
            except Exception as e:
                st.error(f"Error: {e}")
    
    st.divider()
    
    # Clear Database
    st.markdown("### 🗑️ Clear Database")
    with st.form("clear_form"):
        confirm = st.checkbox("Confirm: Delete ALL data")
        if st.form_submit_button("Clear Database"):
            if confirm:
                with driver.session() as session:
                    session.run("MATCH (n) DETACH DELETE n")
                st.success("Database cleared.")
                time.sleep(1)
                st.rerun()
            else:
                st.warning("Check confirmation box to proceed.")

# =============================================================================
# INVESTIGATION ASSISTANT - REFACTORED WITH v3 AUDIT FIXES
# =============================================================================

# --- Schema Definitions ---

GRAPH_SCHEMA_DEFINITION = """
=== INSURANCE KNOWLEDGE GRAPH SCHEMA ===

NODE TYPES AND PROPERTIES:
--------------------------
1. Claim - Insurance claim record
   Properties: id, claim_amount, claim_date, incident_type, status, claim_type
   status values: 'Open', 'Closed', 'Paid', 'Denied - Fraud'
   claim_type values: 'Bodily Injury', 'Property Damage Only'

2. Person - Individuals involved in insurance operations
   Properties: id, name, role, license
   role values: 'Claimant', 'Witness', 'Driver', 'Passenger', 'Owner', 'Policyholder', 'Adjuster'
   Note: All individuals use the :Person label. There are no separate :Claimant or :Adjuster labels.

3. Provider - Medical providers, clinics, treatment facilities
   Properties: id, name, type, specialty, status, npi, opened_date, revocation_date
   status values: 'Active', 'License Revoked'
   type values: 'Hospital', 'Clinic', 'Urgent Care', 'Specialist', 'Medical Center', 'Rehab'

4. Attorney - Legal representatives
   Properties: id, name, firm, firm_type, specialty, status, bar_number

5. Vehicle - Insured vehicles
   Properties: id, vin, make, model, year, color, value

6. Policy - Insurance policies
   Properties: id, policy_number, bind_date, premium, coverage_type

7. Address - Physical addresses
   Properties: id, street, city, state, zip, type
   type values: 'Residential', 'Commercial', 'PO Box'

8. Phone - Phone numbers, device identifiers, fax numbers
   Properties: id, number, type
   type values: 'Mobile', 'Office', 'Fax', 'Mobile Device Fingerprint'

9. Location - Accident/incident locations
   Properties: id, name, type, area
   type values: 'Urban Intersection', 'Highway', 'Parking Lot', 'School Zone'

10. Insurer - Insurance carrier
    Properties: id, name

RELATIONSHIPS:
--------------
(Claim)-[:FILED_BY {role}]->(Person)
(Claim)-[:TREATED_AT]->(Provider)
(Claim)-[:REPRESENTED_BY {hours_to_retain}]->(Attorney)
(Claim)-[:HANDLED_BY]->(Person)
(Claim)-[:WITNESSED_BY]->(Person)
(Claim)-[:OCCURRED_AT]->(Location)
(Claim)-[:INVOLVES_VEHICLE]->(Vehicle)
(Claim)-[:INVOLVED {role}]->(Person)
(Claim)-[:UNDER_POLICY]->(Policy)
(Person)-[:HAS_PHONE]->(Phone)
(Person)-[:LIVES_AT]->(Address)
(Person)-[:HAS_POLICY]->(Policy)
(Policy)-[:COVERS]->(Vehicle)
(Policy)-[:INSURED_BY]->(Insurer)
(Attorney)-[:HAS_PHONE]->(Phone)
(Provider)-[:LOCATED_AT]->(Address)
(Attorney)-[:LOCATED_AT]->(Address)
(Provider)-[:OWNED_BY]->(Person)
(Person)-[:FORMER_EMPLOYEE_OF {role, dates, end_reason}]->(Provider)
"""

SCHEMA_INVESTIGATION_GUIDE = """
RELATIONSHIP CHAINS FOR COMMON INVESTIGATIONS:
- Insurance chain: Person -[:HAS_POLICY]-> Policy -[:COVERS]-> Vehicle; Claim -[:UNDER_POLICY]-> Policy
- Treatment chain: Claim -[:TREATED_AT]-> Provider; Claim -[:REPRESENTED_BY]-> Attorney
- Identity chain: Person -[:HAS_PHONE]-> Phone; Person -[:LIVES_AT]-> Address; Attorney -[:HAS_PHONE]-> Phone
- Corporate chain: Provider -[:OWNED_BY]-> Person -[:FORMER_EMPLOYEE_OF]-> Provider
- Incident chain: Claim -[:OCCURRED_AT]-> Location; Claim -[:INVOLVES_VEHICLE]-> Vehicle

DATA VOLUME CONTEXT:
- The graph contains ~300 claims total: ~200 background (legitimate) + ~100 across 4 fraud scenarios
- Background claims span diverse providers, attorneys, and locations — they are the "haystack"
- Fraud patterns emerge from relationship density and structural anomalies, not from any single node property
"""

# GAP-7: Extended SCHEMA_LITE with investigation chain patterns
SCHEMA_LITE = """
GRAPH SCHEMA (Insurance Knowledge Graph):

NODES: Claim (id, claim_amount, claim_date, status, claim_type, incident_type) | Person (id, name, role) | Provider (id, name, specialty, status, npi) | Attorney (id, name, firm, status, bar_number) | Vehicle (id, vin, make, model, year, value) | Policy (id, policy_number, bind_date, premium) | Address (id, street, city, state, zip) | Phone (id, number, type) | Location (id, name, type, area) | Insurer (id, name)

RELATIONSHIPS:
(Claim)-[:FILED_BY {role}]->(Person)
(Claim)-[:TREATED_AT]->(Provider)
(Claim)-[:REPRESENTED_BY {hours_to_retain}]->(Attorney)
(Claim)-[:HANDLED_BY]->(Person)
(Claim)-[:WITNESSED_BY]->(Person)
(Claim)-[:OCCURRED_AT]->(Location)
(Claim)-[:INVOLVES_VEHICLE]->(Vehicle)
(Claim)-[:INVOLVED {role}]->(Person)
(Claim)-[:UNDER_POLICY]->(Policy)
(Person)-[:HAS_PHONE]->(Phone)
(Person)-[:LIVES_AT]->(Address)
(Person)-[:HAS_POLICY]->(Policy)
(Policy)-[:COVERS]->(Vehicle)
(Policy)-[:INSURED_BY]->(Insurer)
(Attorney)-[:HAS_PHONE]->(Phone)
(Provider)-[:OWNED_BY]->(Person)
(Person)-[:FORMER_EMPLOYEE_OF]->(Provider)

COMMON INVESTIGATION CHAINS:
- Provider investigation: (Provider)<-[:TREATED_AT]-(Claim)-[:FILED_BY]->(Person), (Claim)-[:REPRESENTED_BY]->(Attorney)
- Person investigation: (Person)<-[:FILED_BY]-(Claim), (Person)<-[:INVOLVED]-(Claim), (Person)<-[:WITNESSED_BY]-(Claim)
- Vehicle investigation: (Vehicle)<-[:INVOLVES_VEHICLE]-(Claim)-[:FILED_BY]->(Person), (Person)-[:HAS_POLICY]->(Policy)-[:COVERS]->(Vehicle)
- Attorney investigation: (Attorney)<-[:REPRESENTED_BY]-(Claim)-[:TREATED_AT]->(Provider), (Attorney)-[:HAS_PHONE]->(Phone)
"""

# GAP-4: Extended FEW_SHOT_EXAMPLES_LITE with multi-hop example
FEW_SHOT_EXAMPLES_LITE = """
EXAMPLE QUERIES:

Q: Tell me about a specific provider's claims
MATCH (p:Provider)<-[:TREATED_AT]-(c:Claim)
WHERE p.name CONTAINS 'Wellness' OR p.id = $provider_id
OPTIONAL MATCH (c)-[:FILED_BY]->(person:Person)
OPTIONAL MATCH (c)-[:REPRESENTED_BY]->(a:Attorney)
RETURN p, c, person, a
LIMIT 50

Q: Which providers have the most claims?
MATCH (p:Provider)<-[:TREATED_AT]-(c:Claim)
WITH p, count(c) AS claim_count, sum(c.claim_amount) AS total_exposure
RETURN p.name AS provider, p.id AS id, claim_count, total_exposure
ORDER BY claim_count DESC LIMIT 10

Q: Show the network around a specific entity
MATCH path = (root {id: $entity_id})-[*1..2]-(connected)
UNWIND relationships(path) AS r
WITH DISTINCT startNode(r) AS a, r, endNode(r) AS b
RETURN a, r, b

Q: Show a provider's full claim chain — who files, who represents, any shared infrastructure
MATCH (p:Provider {id: $provider_id})<-[:TREATED_AT]-(c:Claim)
OPTIONAL MATCH (c)-[:FILED_BY]->(person:Person)
OPTIONAL MATCH (c)-[:REPRESENTED_BY]->(a:Attorney)
OPTIONAL MATCH (a)-[:HAS_PHONE]->(ph:Phone)
RETURN p, c, person, a, ph
LIMIT 50
"""

# GAP-4: Extended FEW_SHOT_EXAMPLES_FULL with multi-hop example
FEW_SHOT_EXAMPLES_FULL = """
EXAMPLE QUERIES:

Q: Tell me about a provider — their claims, who files them, and who represents them
MATCH (p:Provider)<-[:TREATED_AT]-(c:Claim)
WHERE p.name CONTAINS 'Wellness' OR p.id = $provider_id
OPTIONAL MATCH (c)-[:FILED_BY]->(person:Person)
OPTIONAL MATCH (c)-[:REPRESENTED_BY]->(a:Attorney)
RETURN p, c, person, a
LIMIT 50

Q: Which providers have the most claims, and how many distinct attorneys appear?
MATCH (p:Provider)<-[:TREATED_AT]-(c:Claim)
WITH p, count(c) AS claim_count, sum(c.claim_amount) AS total_exposure
OPTIONAL MATCH (p)<-[:TREATED_AT]-(c2:Claim)-[:REPRESENTED_BY]->(a:Attorney)
WITH p, claim_count, total_exposure, count(DISTINCT a) AS attorney_count
RETURN p.name AS provider, p.id AS id, claim_count, total_exposure, attorney_count
ORDER BY claim_count DESC LIMIT 10

Q: Find two entities of the same type that are both connected to a common node
MATCH (n1)-[r1]->(shared)<-[r2]-(n2)
WHERE n1 <> n2 AND id(n1) < id(n2)
RETURN n1, r1, shared, r2, n2
LIMIT 25

Q: Show the full neighborhood within 2 hops of a specific entity
MATCH path = (root {id: $entity_id})-[*1..2]-(connected)
UNWIND relationships(path) AS r
WITH DISTINCT startNode(r) AS a, r, endNode(r) AS b
RETURN a, r, b

Q: Find claims within a date range and show who filed them
MATCH (c:Claim)-[:FILED_BY]->(p:Person)
WHERE c.claim_date >= '2023-01-01' AND c.claim_date <= '2023-12-31'
OPTIONAL MATCH (c)-[:TREATED_AT]->(prov:Provider)
OPTIONAL MATCH (c)-[:UNDER_POLICY]->(pol:Policy)
RETURN p.name AS claimant, c.id AS claim_id, c.claim_amount AS amount,
       c.claim_date AS date, prov.name AS provider, pol.policy_number AS policy
ORDER BY c.claim_date
LIMIT 50

Q: Explore a provider's claims and trace who represents those claimants, including any shared contact info
MATCH (p:Provider {id: $provider_id})<-[:TREATED_AT]-(c:Claim)
OPTIONAL MATCH (c)-[:FILED_BY]->(person:Person)
OPTIONAL MATCH (c)-[:REPRESENTED_BY]->(a:Attorney)
OPTIONAL MATCH (a)-[:HAS_PHONE]->(ph:Phone)
RETURN p, c, person, a, ph
LIMIT 50
"""

# --- Prompts ---

SYSTEM_PROMPT = """You are a veteran P&C insurance SIU analyst with 20 years of fraud investigation experience. You have access to your organization's claims data through a Neo4j knowledge graph.

Your investigative principles:
- START with the data, not with assumptions. Let the graph reveal patterns.
- THINK in networks — fraud operates through relationships, not isolated transactions.
- QUANTIFY everything — exposure in dollars, patterns in counts, anomalies in standard deviations from peers.
- DISTINGUISH evidence from inference. State what the data shows before interpreting what it means.
- RECOMMEND concrete next steps — who to investigate, what to subpoena, which claims to review.

You communicate findings with the precision and confidence of a seasoned investigator presenting to an SIU review board."""

# GAP-2: Replaced REASONING_PROMPT with investigative depth
REASONING_PROMPT = """You are an insurance SIU analyst planning a graph database investigation.

GRAPH SCHEMA:
{schema}

RECENT CONVERSATION:
{chat_history}

QUESTION: {question}

Plan your investigation approach in 3-6 sentences. Think like a fraud investigator:

1. IDENTIFY the starting entity (provider, person, vehicle, attorney, claim) and what you know about it.
2. DECIDE what to measure or explore:
   - For a PROVIDER: How many claims flow through it? What's the attorney representation rate? Which specific attorneys appear? Do those attorneys share any infrastructure (phones, addresses)?
   - For a PERSON: How many claims are they connected to? In what roles (claimant, witness, driver, passenger)? Who else appears in those same claims?
   - For a VEHICLE: How many claims involve this VIN? How many distinct owners/policyholders? What's the gap between policy bind dates and claim dates?
   - For an ATTORNEY: How many clients? Which providers do those clients use? What's the concentration — do most clients go to one provider?
   - For a CLAIM: Who filed it, who treated, who represented? Are any of those entities connected to other claims?
3. STATE whether you need:
   - Aggregation queries (counts, sums, rates) to quantify patterns
   - Neighborhood exploration (1-3 hops) to map connections
   - Both — an aggregation to identify anomalies, then exploration to trace the network
4. NAME specific entity IDs, names, or properties from the question to filter on.

Write your approach as plain text. Do not write any Cypher queries."""

# GAP-3: Replaced CYPHER_GENERATION_PROMPT with relationship direction guards
CYPHER_GENERATION_PROMPT = """You are an expert Cypher query writer for a Neo4j insurance knowledge graph.

SCHEMA:
{schema}

INVESTIGATION APPROACH:
{reasoning}

QUESTION: {question}

{few_shot_examples}

CRITICAL — RELATIONSHIP DIRECTIONS (all relationships start from the left node):
The Claim node is the HUB — most relationships originate FROM the Claim:
  (Claim)-[:FILED_BY]->(Person)        — NOT (Person)-[:FILED_BY]->(Claim)
  (Claim)-[:TREATED_AT]->(Provider)     — NOT (Provider)-[:TREATED_AT]->(Claim)
  (Claim)-[:REPRESENTED_BY]->(Attorney) — NOT (Attorney)-[:REPRESENTED_BY]->(Claim)
  (Claim)-[:HANDLED_BY]->(Person)       — NOT (Person)-[:HANDLED_BY]->(Claim)
  (Claim)-[:WITNESSED_BY]->(Person)     — NOT (Person)-[:WITNESSED_BY]->(Claim)
  (Claim)-[:OCCURRED_AT]->(Location)
  (Claim)-[:INVOLVES_VEHICLE]->(Vehicle)
  (Claim)-[:INVOLVED]->(Person)
  (Claim)-[:UNDER_POLICY]->(Policy)

Person/Attorney/Policy outbound relationships:
  (Person)-[:HAS_PHONE]->(Phone)
  (Person)-[:LIVES_AT]->(Address)
  (Person)-[:HAS_POLICY]->(Policy)
  (Person)-[:FORMER_EMPLOYEE_OF]->(Provider)
  (Attorney)-[:HAS_PHONE]->(Phone)
  (Policy)-[:COVERS]->(Vehicle)
  (Policy)-[:INSURED_BY]->(Insurer)
  (Provider)-[:OWNED_BY]->(Person)

COMMON DIRECTION ERROR: When finding claims for a provider, write:
  MATCH (p:Provider)<-[:TREATED_AT]-(c:Claim)   CORRECT  (arrow reversed)
  NOT: MATCH (p:Provider)-[:TREATED_AT]->(c:Claim)  WRONG

RULES:
1. Output ONLY Cypher queries. No explanations, no markdown fences, no comments.
2. Return nodes AND relationships for visualization: use RETURN a, r, b patterns.
3. Use OPTIONAL MATCH for secondary data so primary results aren't lost.
4. LIMIT result sets to 50 rows maximum.
5. If two queries are needed, separate them with a line containing only: ---
6. Prefer explicit relationship types over variable-length paths for clarity.
7. For aggregations, include both the aggregate result AND the underlying entities.

QUERY:"""

CYPHER_FIX_PROMPT = """The following Cypher query failed against a Neo4j database.

FAILED QUERY:
{failed_query}

ERROR MESSAGE:
{error_message}

GRAPH SCHEMA (relationship directions):
{schema_relationships_only}

Fix the query. Common issues:
- Wrong relationship direction (check schema above)
- Referencing properties that don't exist on that node type
- Missing parentheses or brackets
- Using labels that don't exist in the schema

Output ONLY the corrected Cypher query. No explanations."""

# GAP-5: Extended SYNTHESIS_PROMPT with analytical framework
SYNTHESIS_PROMPT = """You are a veteran insurance fraud investigator chatting with a colleague about what you found in the claims database.

QUESTION THEY ASKED: {question}

YOUR INVESTIGATION APPROACH: {reasoning}

QUERY RESULTS:
{all_results}

ANALYTICAL FRAMEWORK — What experienced investigators look for in results:
- REPRESENTATION RATES: If >50% of a provider's patients have attorney representation (normal is 10-15%), that's a red flag for provider-attorney collusion.
- CONCENTRATION: If one provider sends most patients to 1-3 attorneys (or one attorney sends most clients to 1-2 providers), that suggests a referral arrangement.
- SHARED INFRASTRUCTURE: Multiple "independent" entities sharing a phone, fax, address, or device fingerprint suggests they're actually the same operation.
- ROLE PATTERNS: Same person appearing across multiple claims in different roles (driver, passenger, witness) suggests staged accidents.
- ASSET HISTORY: A vehicle with multiple total-loss claims under different owners suggests recycling/paper-totaling schemes.
- TEMPORAL PATTERNS: Very short gaps between policy bind date and claim date (< 60 days) suggest the policy was taken out specifically to file a claim.
- NETWORK CONTINUITY: When a sanctioned provider's associated attorney continues operating with a new provider (especially one opened shortly after the old one closed), the fraud network may have migrated rather than disbanded.
- EMPLOYMENT/OWNERSHIP LINKS: Current provider owned by former employee of a sanctioned provider = potential phoenix operation.

If the data matches one of these patterns, name it and quantify the exposure. If it doesn't match any pattern, say the results look routine.

GUIDELINES:
- Start with your headline finding in one plain sentence.
- Walk through the evidence conversationally. "So I pulled up Metro Care and here's what jumped out..." is better than "FINDING: Provider exhibits anomalous patterns."
- If you found something suspicious, say what makes it suspicious and how confident you are. Distinguish what the data shows from what you think it means.
- If the results are unremarkable, say so honestly. "Looks clean to me" is a valid finding.
- If the queries returned empty results or errors, acknowledge it and suggest what might have gone wrong or what to try instead.
- Quantify when you can — dollar exposure, counts, percentages, deviations from averages.
- Keep it concise — 3-6 sentences for simple findings, up to 2-3 short paragraphs for complex network discoveries.
- End with 2-3 suggested follow-up questions that dig deeper into the most interesting aspect of what you found.

FORMAT YOUR FOLLOW-UPS LIKE THIS (after your main analysis):

---FOLLOW_UPS---
First follow-up question here
Second follow-up question here
Third follow-up question here

The follow-up questions should be answerable by querying the graph (not general knowledge) and should build on what was just discovered. Use specific entity names or IDs from the results when relevant."""

QUICK_QUERIES = [
    "Show me the highest-volume providers and their attorney connections",
    "Which claims have the largest dollar exposure?",
    "Find providers with above-average claim amounts",
    "Are there attorneys sharing the same fax phone number?",
    "Show all claims connected to Vehicle VEH_S3_MAIN",
    "What providers have had their licenses revoked?",
    "Find people who appear in multiple claims in different roles",
    "Show the complete network around Provider PROV_S1_MAIN",
    "Which attorneys represent the most claimants?",
    "Find claims where policy bind date is close to claim date",
]

# --- Helper Functions ---

def _serialize_records_for_llm(records, max_rows=15):
    """Serialize Neo4j records into JSON-safe dicts for LLM consumption."""
    serialized = []
    for r in (records or [])[:max_rows]:
        row = {}
        for k, v in r.items():
            if hasattr(v, 'labels'):
                row[k] = dict(v)
            elif hasattr(v, 'type') and hasattr(v, 'start_node'):
                row[k] = f"[:{v.type}]"
            else:
                row[k] = v
        serialized.append(row)
    return serialized


# GAP-6: Trimmed get_graph_schema_context() to remove entity leakage
def get_graph_schema_context():
    """Build schema context enriched with investigation guide and live data stats."""
    schema = GRAPH_SCHEMA_DEFINITION + SCHEMA_INVESTIGATION_GUIDE
    
    try:
        with driver.session() as session:
            # Database summary - label counts only (no entity-specific lists)
            summary = session.run("""
                MATCH (n)
                WITH labels(n)[0] AS label, count(n) AS cnt
                RETURN label, cnt ORDER BY cnt DESC
            """)
            label_counts = {r['label']: r['cnt'] for r in summary}
            
            if label_counts:
                schema += "\nLIVE DATABASE SUMMARY:\n"
                for label, cnt in label_counts.items():
                    schema += f"  - {label}: {cnt} nodes\n"
    
    except Exception:
        pass
    
    return schema


def get_schema_for_query(is_deep):
    """Return appropriate schema context based on query complexity."""
    if is_deep:
        return get_graph_schema_context()
    else:
        return SCHEMA_LITE


# GAP-8: Extended classify_query_complexity() with missing patterns
def classify_query_complexity(question):
    """
    Classify user question as 'simple' or 'deep' using keyword heuristics.
    """
    question_lower = question.lower()
    
    # Deep indicators
    deep_patterns = [
        # Network/relationship analysis
        "connected", "network", "relationship", "linked", "shared",
        "between", "connection", "ring", "pattern", "cluster",
        # Comparison/aggregation
        "compare", "average", "anomal", "unusual", "suspicious",
        "higher than", "lower than", "deviation", "peer",
        # Multi-entity
        "all claims", "all providers", "all attorneys", "every",
        "across", "multiple",
        # Temporal
        "timeline", "before", "after", "tenure", "duration",
        "how long", "when did",
        # Investigation-style
        "investigate", "probe", "dig into", "follow up",
        "what else", "who else", "any other",
        # Explicit complexity
        "complete network", "full history", "everything about",
        # Co-reference / continuation patterns
        "those claims", "those providers", "those attorneys", "that provider",
        "that attorney", "same people", "same person", "same vehicle",
        "same address", "same phone", "same device", "same fax",
        # Quantitative analysis
        "representation rate", "how many", "what percentage", "what fraction",
        "exposure", "total amount", "total value",
        # Infrastructure discovery
        "share", "common", "overlap", "in common",
        "device", "fax", "phone number", "address",
        # Historical / temporal
        "history", "previously", "former", "prior",
        "opened", "closed", "revoked", "sanctioned",
    ]
    
    for pattern in deep_patterns:
        if pattern in question_lower:
            return "deep"
    
    return "simple"


def _extract_relationship_section(schema):
    """Extract just the RELATIONSHIPS section from the full schema string."""
    lines = schema.split("\n")
    in_section = False
    result = []
    for line in lines:
        if "RELATIONSHIPS:" in line:
            in_section = True
        if in_section:
            result.append(line)
            if in_section and line.strip() == "" and len(result) > 5:
                break
    return "\n".join(result) if result else schema[:1000]


def plan_investigation(llm_config, schema, chat_history, question, is_deep):
    """
    Two-call pipeline: Reason about approach, then generate Cypher.
    
    Returns:
        dict with keys:
            - reasoning (str): Plain text investigation approach
            - queries (list[str]): 1-2 Cypher query strings
    """
    # GAP-1: Call 1: Reasoning with system prompt
    reason_prompt = REASONING_PROMPT.format(
        schema=schema,
        chat_history=chat_history or "No prior context.",
        question=question
    )
    reasoning = call_llm(llm_config, reason_prompt, temperature=0.3, max_tokens=300,
                        system_prompt=SYSTEM_PROMPT)
    
    if reasoning.startswith("LLM Error"):
        return {"reasoning": "", "queries": []}
    
    # GAP-1: Call 2: Cypher generation with dedicated system prompt
    few_shots = FEW_SHOT_EXAMPLES_FULL if is_deep else FEW_SHOT_EXAMPLES_LITE
    
    cypher_prompt = CYPHER_GENERATION_PROMPT.format(
        schema=schema,
        reasoning=reasoning,
        question=question,
        few_shot_examples=few_shots
    )
    cypher_raw = call_llm(llm_config, cypher_prompt, temperature=0.1, max_tokens=800,
                         system_prompt="You are an expert Neo4j Cypher query writer. Output ONLY valid Cypher. No explanations.")
    
    if cypher_raw.startswith("LLM Error"):
        return {"reasoning": reasoning, "queries": []}
    
    # Parse: strip markdown fences if present, split on ---
    cypher_clean = cypher_raw.strip()
    if cypher_clean.startswith("```"):
        cypher_clean = cypher_clean.split("\n", 1)[-1]
    if cypher_clean.endswith("```"):
        cypher_clean = cypher_clean.rsplit("```", 1)[0]
    cypher_clean = cypher_clean.strip()
    
    queries = [q.strip() for q in cypher_clean.split("---") if q.strip()]
    
    # Safety cap: max 2 queries
    queries = queries[:2]
    
    return {"reasoning": reasoning, "queries": queries}


def execute_cypher_with_retry(query, llm_config, schema):
    """
    Execute a Cypher query. On failure, attempt one LLM-powered fix.
    
    Returns:
        tuple: (records: list, executed_query: str, had_error: bool)
    """
    # First attempt
    try:
        records = run_query(query)
        return (records, query, False)
    except Exception as e:
        error_msg = str(e)[:300]
    
    # Extract relationships section for fix prompt
    schema_rels = _extract_relationship_section(schema)
    
    fix_prompt = CYPHER_FIX_PROMPT.format(
        failed_query=query,
        error_message=error_msg,
        schema_relationships_only=schema_rels
    )
    
    fixed_cypher = call_llm(llm_config, fix_prompt, temperature=0.0, max_tokens=500)
    
    if fixed_cypher.startswith("LLM Error"):
        return ([], query, True)
    
    # Clean markdown fences
    fixed_clean = fixed_cypher.strip()
    if fixed_clean.startswith("```"):
        fixed_clean = fixed_clean.split("\n", 1)[-1]
    if fixed_clean.endswith("```"):
        fixed_clean = fixed_clean.rsplit("```", 1)[0]
    fixed_clean = fixed_clean.strip()
    
    # Second attempt with fixed query
    try:
        records = run_query(fixed_clean)
        return (records, fixed_clean, False)
    except Exception:
        return ([], query, True)


def enrich_visualization(query_results_records, all_records):
    """
    Extract entity IDs from results and fetch their neighborhoods for visualization.
    """
    # Extract entity IDs from serialized results
    entity_ids = set()
    
    for qr in query_results_records:
        for row in qr.get("data", []):
            for key, value in row.items():
                if isinstance(value, dict):
                    node_id = value.get("id")
                    if node_id:
                        entity_ids.add(node_id)
                elif isinstance(value, str):
                    if any(value.startswith(prefix) for prefix in 
                           ["PROV_", "ATT_", "P_", "CLM_", "VEH_", "POL_", "FAX_", "DEVICE_",
                            "ADDR_", "LOC_", "ADJ_", "INS_"]):
                        entity_ids.add(value)
    
    # Extract existing node IDs
    existing_node_ids = set()
    for record in all_records:
        for value in record.values():
            if value and hasattr(value, 'labels'):
                props = dict(value)
                nid = props.get('id')
                if nid:
                    existing_node_ids.add(nid)
    
    # Find missing IDs
    missing_ids = entity_ids - existing_node_ids
    
    if not missing_ids:
        return []
    
    # Fetch 1-hop neighborhoods for up to 5 missing entities
    ids_to_fetch = list(missing_ids)[:5]
    
    enrichment_records = []
    for eid in ids_to_fetch:
        try:
            with driver.session() as session:
                result = session.run("""
                    MATCH (root {id: $eid})-[r]-(neighbor)
                    RETURN root, r, neighbor
                    LIMIT 30
                """, eid=eid)
                enrichment_records.extend(list(result))
        except Exception:
            continue
    
    return enrichment_records


def parse_synthesis_response(response_text):
    """
    Split synthesis response into main analysis and follow-up questions.
    """
    if "---FOLLOW_UPS---" in response_text:
        parts = response_text.split("---FOLLOW_UPS---", 1)
        analysis = parts[0].strip()
        follow_up_text = parts[1].strip()
        follow_ups = [q.strip() for q in follow_up_text.split("\n") if q.strip()]
        follow_ups = follow_ups[:3]
        return (analysis, follow_ups)
    else:
        return (response_text.strip(), [])


# --- LLM Configuration ---

def configure_llm():
    """Configure available LLM providers."""
    available = {}
    
    if AZURE_OPENAI_AVAILABLE:
        try:
            cfg = st.secrets.get("azure_openai", {})
            endpoint = cfg.get("endpoint")
            apikey = cfg.get("api_key")
            apiversion = cfg.get("api_version", "2024-12-01-preview")
            deployment_4o = cfg.get("deployment_4o", "gpt-4o")
            deployment_4o_mini = cfg.get("deployment_4o_mini", "gpt-4o-mini")
            
            if endpoint and apikey:
                client = AzureOpenAI(
                    azure_endpoint=endpoint,
                    api_key=apikey,
                    api_version=apiversion
                )
                
                available["azure_openai_mini"] = {
                    "client": client,
                    "model": deployment_4o_mini,
                    "name": "Azure OpenAI GPT-4o-mini",
                    "type": "azure_openai"
                }
                
                available["azure_openai_4o"] = {
                    "client": client,
                    "model": deployment_4o,
                    "name": "Azure OpenAI GPT-4o",
                    "type": "azure_openai"
                }
        except Exception:
            pass
    
    if GROQ_AVAILABLE:
        try:
            api_key = st.secrets.get("groq", {}).get("api_key")
            if api_key and len(api_key) > 10:
                client = Groq(api_key=api_key)
                available['groq'] = {
                    'client': client,
                    'model': 'llama-3.3-70b-versatile',
                    'name': 'Groq (Llama 3.3 70B)',
                    'type': 'groq'
                }
        except Exception:
            pass
    
    return available


# GAP-1: Modified call_llm() to accept optional system_prompt
def call_llm(config, prompt, temperature=0.3, max_tokens=2000, system_prompt=None):
    """Call LLM provider with a prompt and optional system message."""
    try:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = config['client'].chat.completions.create(
            model=config['model'],
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        result = response.choices[0].message.content.strip()
        
        # Cost tracking
        if 'llm_call_count' not in st.session_state:
            st.session_state.llm_call_count = 0
            st.session_state.llm_token_estimate = 0
        st.session_state.llm_call_count += 1
        st.session_state.llm_token_estimate += len(prompt) // 4 + len(result) // 4
        
        return result
    except Exception as e:
        return f"LLM Error: {str(e)}"


# --- Main Page Renderer ---

def render_investigation_assistant():
    """Render the AI-powered investigation assistant page."""
    st.title("🤖 Investigation Assistant")
    st.caption("AI-powered natural language querying of the insurance knowledge graph")
    
    # LLM availability check
    available_providers = configure_llm()
    
    if not available_providers:
        st.error("No LLM providers configured.")
        st.info("""
        Configure at least one provider in `.streamlit/secrets.toml`:
        
        **Azure OpenAI (primary):**
        ```toml
        [azure_openai]
        endpoint = "https://your-resource.openai.azure.com/"
        api_key = "your-key"
        api_version = "2024-12-01-preview"
        deployment_4o_mini = "gpt-4o-mini"
        deployment_4o = "gpt-4o"
        ```
        
        **Groq (free tier):**
        ```toml
        [groq]
        api_key = "gsk_your_groq_key"
        ```
        """)
        return
    
    # Sidebar: LLM controls
    with st.sidebar:
        st.markdown("### 🤖 Assistant Settings")
        
        if "selected_provider" not in st.session_state:
            if "azure_openai_mini" in available_providers:
                st.session_state.selected_provider = "azure_openai_mini"
            elif "azure_openai_4o" in available_providers:
                st.session_state.selected_provider = "azure_openai_4o"
            else:
                st.session_state.selected_provider = list(available_providers.keys())[0]
        
        provider_key = st.selectbox(
            "LLM Provider",
            options=list(available_providers.keys()),
            format_func=lambda k: available_providers[k]['name'],
            index=list(available_providers.keys()).index(st.session_state.selected_provider)
                if st.session_state.selected_provider in available_providers else 0
        )
        st.session_state.selected_provider = provider_key
        
        st.markdown("---")
        if st.button("🗑️ Clear Chat"):
            st.session_state.assistant_messages = []
            st.session_state.assistant_chat_history = []
            st.session_state.llm_call_count = 0
            st.session_state.llm_token_estimate = 0
            st.rerun()
        
        if st.session_state.get('llm_call_count'):
            st.caption(
                f"Session: {st.session_state.llm_call_count} LLM calls | "
                f"~{st.session_state.get('llm_token_estimate', 0):,} tokens"
            )
    
    # Initialize chat state
    if "assistant_messages" not in st.session_state:
        st.session_state.assistant_messages = []
    if "assistant_chat_history" not in st.session_state:
        st.session_state.assistant_chat_history = []
    
    # Quick queries
    st.markdown("#### Quick Queries")
    cols = st.columns(3)
    for i, q in enumerate(QUICK_QUERIES[:9]):
        with cols[i % 3]:
            if st.button(q[:50] + "..." if len(q) > 50 else q, key=f"aq_{i}"):
                st.session_state.assistant_pending = q
    
    st.markdown("---")
    
    # Display chat history with follow-ups
    for idx, msg in enumerate(st.session_state.assistant_messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("graph_nodes") and msg.get("graph_edges"):
                config = get_graph_config(width="100%", height=500)
                agraph(msg["graph_nodes"], msg["graph_edges"], config)
            if msg.get("cypher"):
                with st.expander("🔍 Cypher Queries"):
                    st.code(msg["cypher"], language="cypher")
            # Show follow-ups only for the LAST assistant message
            if (msg["role"] == "assistant" 
                and msg.get("follow_ups") 
                and idx == len(st.session_state.assistant_messages) - 1):
                st.markdown("**Continue investigating:**")
                cols = st.columns(min(len(msg["follow_ups"]), 3))
                for i, q in enumerate(msg["follow_ups"]):
                    with cols[i]:
                        if st.button(q[:60] + "..." if len(q) > 60 else q, key=f"hist_fu_{idx}_{i}"):
                            st.session_state.assistant_pending = q
                            st.rerun()
    
    # Handle input
    user_input = st.chat_input("Ask about the insurance graph...")
    
    if hasattr(st.session_state, 'assistant_pending') and st.session_state.assistant_pending:
        user_input = st.session_state.assistant_pending
        st.session_state.assistant_pending = None
    
    if not user_input:
        return
    
    # Display user message
    st.session_state.assistant_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    llm_config = available_providers[st.session_state.selected_provider]
    
    with st.chat_message("assistant"):
        
        # STEP 1: Classify complexity (code, no LLM)
        is_deep = classify_query_complexity(user_input) == "deep"
        schema = get_schema_for_query(is_deep)
        
        # STEP 2: Plan investigation (2 LLM calls)
        chat_history_text = ""
        for h in st.session_state.assistant_chat_history[-5:]:
            chat_history_text += f"Q: {h['question']}\nApproach: {h.get('reasoning', '')}\n\n"
        
        with st.spinner("Thinking..."):
            plan = plan_investigation(llm_config, schema, chat_history_text, user_input, is_deep)
        
        reasoning = plan["reasoning"]
        queries = plan["queries"]
        
        if not queries:
            fallback_msg = ("I wasn't able to translate that into a graph query. "
                          "Could you rephrase? For example, try asking about a specific "
                          "provider, attorney, claim, or vehicle by name or ID.")
            st.markdown(fallback_msg)
            st.session_state.assistant_messages.append({
                "role": "assistant", "content": fallback_msg
            })
            return
        
        # Show plan (collapsed)
        with st.expander("🧠 Investigation approach", expanded=False):
            st.markdown(reasoning)
        
        # STEP 3: Execute queries with retry
        all_records = []
        query_results_text = []
        all_cypher = []
        had_any_error = False
        
        for i, cypher in enumerate(queries):
            with st.spinner(f"Querying graph ({i+1}/{len(queries)})..."):
                records, executed_query, had_error = execute_cypher_with_retry(
                    cypher, llm_config, schema
                )
                all_records.extend(records)
                all_cypher.append(executed_query)
                had_any_error = had_any_error or had_error
                
                serialized = _serialize_records_for_llm(records)
                query_results_text.append({
                    "query_index": i + 1,
                    "cypher": executed_query,
                    "result_count": len(records),
                    "data": serialized,
                    "auto_corrected": had_error and len(records) > 0
                })
        
        # STEP 4: Visualization enrichment (no LLM)
        enrichment_records = enrich_visualization(query_results_text, all_records)
        all_records.extend(enrichment_records)
        
        # STEP 5: Build visualization
        graph_nodes = []
        graph_edges = []
        
        if all_records:
            node_ids = set()
            for record in all_records:
                for value in record.values():
                    if value and hasattr(value, 'element_id'):
                        node_ids.add(value.element_id)
            
            rel_records = get_relationships_for_nodes(node_ids) if node_ids else []
            graph_nodes, graph_edges = create_graph_visualization(all_records + rel_records)
        
        if graph_nodes:
            st.info(
                f"📊 **{len(graph_nodes)} entities** | "
                f"**{len(graph_edges)} connections**"
            )
            config = get_graph_config(width="100%", height=500)
            agraph(graph_nodes, graph_edges, config)
        
        # Show executed queries
        with st.expander(f"🔍 Queries executed ({len(all_cypher)})"):
            for i, c in enumerate(all_cypher):
                st.code(c, language="cypher")
                if query_results_text[i].get("auto_corrected"):
                    st.caption("→ Auto-corrected after initial error")
        
        # GAP-1: STEP 6: Synthesize findings (1 LLM call with system prompt)
        with st.spinner("Analyzing findings..."):
            synthesis_prompt = SYNTHESIS_PROMPT.format(
                question=user_input,
                reasoning=reasoning,
                all_results=json.dumps(query_results_text, indent=2, default=str)
            )
            response_text = call_llm(llm_config, synthesis_prompt, temperature=0.4,
                                    system_prompt=SYSTEM_PROMPT)
        
        # STEP 7: Display analysis + follow-ups
        if response_text and not response_text.startswith("LLM Error"):
            analysis_text, follow_ups = parse_synthesis_response(response_text)
            st.markdown(analysis_text)
            
            # Render follow-up buttons
            if follow_ups:
                st.markdown("**Continue investigating:**")
                cols = st.columns(min(len(follow_ups), 3))
                for i, q in enumerate(follow_ups):
                    with cols[i]:
                        if st.button(
                            q[:60] + "..." if len(q) > 60 else q,
                            key=f"followup_{len(st.session_state.assistant_messages)}_{i}"
                        ):
                            st.session_state.assistant_pending = q
                            st.rerun()
        else:
            analysis_text = ("I ran into an issue generating the analysis. "
                           "The graph results are shown above — try asking "
                           "a more specific question about what you see.")
            follow_ups = []
            st.markdown(analysis_text)
        
        # STEP 8: Store in chat history
        st.session_state.assistant_messages.append({
            "role": "assistant",
            "content": analysis_text,
            "graph_nodes": graph_nodes if graph_nodes else None,
            "graph_edges": graph_edges if graph_edges else None,
            "cypher": "\n---\n".join(all_cypher) if all_cypher else None,
            "follow_ups": follow_ups
        })
        
        st.session_state.assistant_chat_history.append({
            "question": user_input,
            "reasoning": reasoning,
            "cypher": all_cypher[0] if all_cypher else ""
        })

# =============================================================================
# SIDEBAR & ROUTING
# =============================================================================

st.sidebar.title("🔍 Fraud Ring Detection")
st.sidebar.caption("Graph-Powered SIU Platform")

page = st.sidebar.radio(
    "Navigation",
    ["🎯 Scenario Walkthrough", "🤖 Investigation Assistant", "🔍 Network Explorer", "⚙️ Administration"],
    label_visibility="collapsed"
)

st.sidebar.divider()

st.sidebar.markdown("### Legend")
st.sidebar.markdown("""
<div style='line-height: 2.0; font-size: 13px;'>
    <span style='color: #5DADE2;'>●</span> People (Claimants, Witnesses)<br>
    <span style='color: #AF7AC5;'>●</span> Medical Providers<br>
    <span style='color: #F5B041;'>●</span> Attorneys<br>
    <span style='color: #4A90A4;'>●</span> Claims<br>
    <span style='color: #45B7A0;'>●</span> Addresses<br>
    <span style='color: #5499C7;'>●</span> Phones & Devices<br>
    <span style='color: #E74C3C;'>●</span> Vehicles<br>
    <span style='color: #34495E;'>●</span> Policies<br>
    <span style='color: #1A5276;'>●</span> Insurer
</div>
""", unsafe_allow_html=True)

st.sidebar.divider()

# Routing
if page == "🎯 Scenario Walkthrough":
    render_scenario_walkthrough()
elif page == "🤖 Investigation Assistant":
    render_investigation_assistant()
elif page == "🔍 Network Explorer":
    render_free_exploration()
else:
    render_admin()