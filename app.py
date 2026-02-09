"""
Insurance Fraud Ring Detection
Graph-Powered Investigation Platform for SIU Teams

Demonstrates how graph database technology reveals hidden fraud networks
that traditional relational methods consistently miss.

Version: 2.1 - Added Investigation Assistant; synced with refined data model;
               Azure OpenAI primary; standalone OpenAI removed
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
        
        # NOTE: neo4j+ssc hack removed per audit — AuraDB uses valid TLS certs
             
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

# Sync: Generator uses :Phone {type:'Fax'} (not :Entity), :Insurer node, COVERS (not INSURES_VEHICLE)
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

# Sync: SHARES_DEVICE->HAS_PHONE, INSURES_VEHICLE->COVERS, added new rels
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
# SCENARIO DEFINITIONS
# Sync notes:
#   S1 Hop2: SHARES_DEVICE->HAS_PHONE, :Entity->:Phone {type:'Fax'}
#   S1 Hop3: SHARED_FAX_S1->FAX_S1_SHARED, same rel/label changes
#   S3 Hop2: INSURES_VEHICLE->COVERS
#   All other hops unchanged (verified per scenario_schema_audit.md)
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
# PAGE: SCENARIO WALKTHROUGH (original - unchanged)
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
# PAGE: FREE EXPLORATION (original - unchanged)
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
# PAGE: ADMINISTRATION (original - unchanged)
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
# INVESTIGATION ASSISTANT - LLM-Powered Graph Exploration
# =============================================================================

# --- Schema & Prompts (per schema_prompt_refinement.md) ---
# Schema describes ONLY data structure - no fraud interpretations.
# Fraud discovery happens via graph traversal, not prompt hints.

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

SYSTEM_PROMPT = """You are a veteran P&C insurance SIU analyst with 20 years of fraud investigation experience. You have access to your organization's claims data through a Neo4j knowledge graph.

Your investigative principles:
- START with the data, not with assumptions. Let the graph reveal patterns.
- THINK in networks — fraud operates through relationships, not isolated transactions.
- QUANTIFY everything — exposure in dollars, patterns in counts, anomalies in standard deviations from peers.
- DISTINGUISH evidence from inference. State what the data shows before interpreting what it means.
- RECOMMEND concrete next steps — who to investigate, what to subpoena, which claims to review.

You communicate findings with the precision and confidence of a seasoned investigator presenting to an SIU review board."""

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

INVESTIGATION_PLANNER_PROMPT = """You are a veteran P&C insurance fraud analyst with 20 years of SIU experience, planning an investigation using a Neo4j knowledge graph.

GRAPH SCHEMA:
{schema}

INVESTIGATION CONTEXT (recent queries):
{chat_history}

USER QUESTION: {question}

TASK: Think step-by-step about what data you need, then produce an investigation plan.

STEP 1 - UNDERSTAND: What is the user actually asking? Restate in precise investigation terms.

STEP 2 - IDENTIFY: What entities and relationships are central? What graph patterns would answer this?

STEP 3 - PLAN QUERIES: Design 1-3 Cypher queries that progressively build the answer.
- Query 1 should address the core question directly
- Query 2 (if needed) should expand context or corroborate
- Query 3 (only for complex investigations) should find connecting evidence

INVESTIGATION PATTERNS (use as analytical templates, not answers):
- Provider assessment: Check claim volume, attorney concentration ratio, compare to peer benchmarks via aggregation
- Network mapping: Start with 1-hop neighborhood, look for shared connections (e.g., two entities linking to the same node)
- Temporal analysis: Compare dates across connected entities (bind_date vs claim_date, opened_date vs revocation_date)
- Identity linkage: Trace through Phone, Address, Device nodes to find hidden connections between People
- Corporate tracing: Follow OWNED_BY and FORMER_EMPLOYEE_OF chains to find organizational connections

CYPHER GUIDELINES:
- Return nodes AND relationships for visualization: prefer RETURN a, r, b patterns
- Use OPTIONAL MATCH for secondary data to avoid losing primary results
- Include aggregations (COUNT, SUM, AVG) when the question implies comparison
- Use parameterized patterns: {{id: 'VALUE'}} (double braces for format string safety)
- For neighborhood exploration: MATCH path = (root)-[*1..N]-(connected) then UNWIND relationships(path)
- LIMIT large result sets to 50 rows

OUTPUT FORMAT - Respond with ONLY this JSON structure, no other text:
{{
  "reasoning": "Brief explanation of investigation approach (2-3 sentences)",
  "complexity": "simple|moderate|complex",
  "queries": [
    {{
      "purpose": "What this query reveals",
      "cypher": "THE CYPHER QUERY",
      "depends_on": null
    }}
  ]
}}

For sequential queries where Query 2 needs results from Query 1, set depends_on to the index (0-based) and use a placeholder like $PREV_RESULT that you will describe in the purpose field. The system will handle substitution.

IMPORTANT: Output ONLY valid JSON. No markdown fences, no explanation outside the JSON."""

REFLECTION_PROMPT = """You are reviewing investigation results to determine if you have enough evidence to answer the original question.

ORIGINAL QUESTION: {question}

INVESTIGATION PLAN: {reasoning}

QUERIES EXECUTED AND RESULTS:
{query_results}

ASSESSMENT TASK:
1. Did the queries return the data needed to answer the question?
2. Is there a critical gap - a specific piece of information that would significantly strengthen the answer?
3. If yes, what ONE additional query would fill that gap?

OUTPUT FORMAT - Respond with ONLY this JSON, no other text:
{{
  "sufficient": true or false,
  "gap": "Description of missing information (or null if sufficient)",
  "corrective_query": "Cypher query to fill the gap (or null if sufficient)"
}}

Only request a corrective query if results are genuinely insufficient. Empty results on a well-formed query may themselves be informative (absence of evidence). Do not fish for data you merely find interesting — focus on what the user asked."""

ANALYST_SYNTHESIS_PROMPT = """You are a veteran P&C insurance SIU analyst presenting findings to your investigation team.

ORIGINAL QUESTION: {question}

INVESTIGATION SUMMARY:
{investigation_summary}

EVIDENCE (query results):
{all_results}

Synthesize your findings following this structure:

**FINDING**: One-sentence headline of what the data shows.

**EVIDENCE**: Cite specific entities, relationships, and numbers from the results. Name names, reference claim IDs, state dollar amounts. Connect the dots explicitly — show the chain of connections.

**SEVERITY**: Assess as one of:
- ROUTINE — normal patterns, no concern
- NOTABLE — unusual but not conclusive, warrants monitoring
- CONCERNING — multiple indicators suggesting coordinated activity
- CRITICAL — strong evidence of organized fraud requiring immediate action

**EXPOSURE**: Quantify dollar impact where possible. Use claim_amount sums, counts, and averages from the data. If exact figures aren't available, provide a reasoned estimate with stated assumptions.

**NEXT STEPS**: 2-4 specific, actionable recommendations. Reference concrete entities or queries that should be investigated further.

GUIDELINES:
- Write for insurance professionals — use industry terminology naturally
- Be precise: "Dr. Smith's clinic treated 45 claimants, all represented by 3 attorneys sharing one fax" not "there seem to be some connections"
- Distinguish between what the data SHOWS and what it SUGGESTS — evidence vs. inference
- If results are empty or inconclusive, say so directly and explain what the absence might mean
- Keep it concise — findings, not essays"""


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


def configure_llm():
    """Configure available LLM providers. Azure OpenAI (4o-mini and 4o), Groq secondary."""
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
                
                # GPT-4o-mini (default)
                available["azure_openai_mini"] = {
                    "client": client,
                    "model": deployment_4o_mini,
                    "name": "Azure OpenAI GPT-4o-mini",
                    "type": "azure_openai"
                }
                
                # GPT-4o
                available["azure_openai_4o"] = {
                    "client": client,
                    "model": deployment_4o,
                    "name": "Azure OpenAI GPT-4o",
                    "type": "azure_openai"
                }
        except Exception:
            pass  # Azure OpenAI primary...

    
    # Groq (secondary / free tier)
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


def call_llm(config, prompt, temperature=0.3, max_tokens=2000):
    """Call LLM provider with a single prompt. Tracks session cost estimate."""
    try:
        response = config['client'].chat.completions.create(
            model=config['model'],
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        result = response.choices[0].message.content.strip()
        
        # Lightweight cost tracking
        if 'llm_call_count' not in st.session_state:
            st.session_state.llm_call_count = 0
            st.session_state.llm_token_estimate = 0
        st.session_state.llm_call_count += 1
        st.session_state.llm_token_estimate += len(prompt) // 4 + len(result) // 4
        
        return result
    except Exception as e:
        return f"LLM Error: {str(e)}"


def _parse_llm_json(raw_text):
    """Parse JSON from LLM output, stripping markdown fences if present."""
    clean = raw_text.strip()
    if clean.startswith("```"):
        clean = clean.split("\n", 1)[-1]
    if clean.endswith("```"):
        clean = clean.rsplit("```", 1)[0]
    clean = clean.strip()
    return json.loads(clean)


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


def get_graph_schema_context():
    """Build schema context enriched with investigation guide and live data stats.
    
    Layers:
    1. GRAPH_SCHEMA_DEFINITION — node types, properties, relationships
    2. SCHEMA_INVESTIGATION_GUIDE — relationship chains and data volume context
    3. Live data stats — high-volume providers, attorneys, database summary
    """
    schema = GRAPH_SCHEMA_DEFINITION + SCHEMA_INVESTIGATION_GUIDE
    
    try:
        with driver.session() as session:
            # Database summary — gives the LLM a sense of scale
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
            
            # High-volume providers with attorney concentration
            result = session.run("""
                MATCH (p:Provider)<-[:TREATED_AT]-(c:Claim)
                WITH p, count(c) as claim_count
                WHERE claim_count > 3
                OPTIONAL MATCH (p)<-[:TREATED_AT]-(c2:Claim)-[:REPRESENTED_BY]->(a:Attorney)
                WITH p, claim_count, count(DISTINCT a) as attorney_count
                RETURN p.name as provider, p.id as id, p.status as status,
                       claim_count, attorney_count
                ORDER BY claim_count DESC LIMIT 5
            """)
            providers = [dict(r) for r in result]
            
            if providers:
                schema += "\nHIGH-VOLUME PROVIDERS:\n"
                for p in providers:
                    status_tag = f" [{p['status']}]" if p.get('status') and p['status'] != 'Active' else ""
                    schema += (f"  - {p['provider']} (id: {p['id']}){status_tag}: "
                              f"{p['claim_count']} claims, {p['attorney_count']} distinct attorneys\n")
            
            # High-volume attorneys
            att_result = session.run("""
                MATCH (a:Attorney)<-[:REPRESENTED_BY]-(c:Claim)
                WITH a, count(c) as claim_count, sum(c.claim_amount) as total_exposure
                WHERE claim_count > 3
                RETURN a.name as attorney, a.id as id, claim_count,
                       total_exposure
                ORDER BY claim_count DESC LIMIT 5
            """)
            attorneys = [dict(r) for r in att_result]
            
            if attorneys:
                schema += "\nHIGH-VOLUME ATTORNEYS:\n"
                for a in attorneys:
                    exposure = f"${a['total_exposure']:,.0f}" if a.get('total_exposure') else "N/A"
                    schema += (f"  - {a['attorney']} (id: {a['id']}): "
                              f"{a['claim_count']} claims, {exposure} total exposure\n")
    
    except Exception:
        pass
    
    return schema


def render_investigation_assistant():
    """Render the AI-powered investigation assistant page.
    
    Pipeline: Think → Plan → Query (multi-step) → Reflect (complex only) → Synthesize
    Complexity-aware: simple (2 LLM calls), moderate (2), complex (3-4).
    """
    st.title("🤖 Investigation Assistant")
    st.caption("AI-powered natural language querying of the insurance knowledge graph")
    
    # ------------------------------------------------------------------
    # LLM availability check
    # ------------------------------------------------------------------
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
        deployment_name = "gpt-4o-mini"
        ```
        
        **Groq (free tier):**
        ```toml
        [groq]
        api_key = "gsk_your_groq_key"
        ```
        """)
        return
    
    # ------------------------------------------------------------------
    # Sidebar: LLM controls + cost tracker
    # ------------------------------------------------------------------
    with st.sidebar:
        st.markdown("### 🤖 Assistant Settings")
        
        if "selected_provider" not in st.session_state:
            # Default to GPT-4o-mini
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
        
        # Cost tracker display
        if st.session_state.get('llm_call_count'):
            st.caption(
                f"Session: {st.session_state.llm_call_count} LLM calls | "
                f"~{st.session_state.get('llm_token_estimate', 0):,} tokens"
            )
    
    # ------------------------------------------------------------------
    # Initialize chat state
    # ------------------------------------------------------------------
    if "assistant_messages" not in st.session_state:
        st.session_state.assistant_messages = []
    if "assistant_chat_history" not in st.session_state:
        st.session_state.assistant_chat_history = []
    
    # ------------------------------------------------------------------
    # Quick queries
    # ------------------------------------------------------------------
    st.markdown("#### Quick Queries")
    cols = st.columns(3)
    for i, q in enumerate(QUICK_QUERIES[:9]):
        with cols[i % 3]:
            if st.button(q[:50] + "..." if len(q) > 50 else q, key=f"aq_{i}"):
                st.session_state.assistant_pending = q
    
    st.markdown("---")
    
    # ------------------------------------------------------------------
    # Display chat history (with embedded graphs from prior turns)
    # ------------------------------------------------------------------
    for msg in st.session_state.assistant_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("graph_nodes") and msg.get("graph_edges"):
                config = get_graph_config(width="100%", height=500)
                agraph(msg["graph_nodes"], msg["graph_edges"], config)
            if msg.get("cypher"):
                with st.expander("🔍 Cypher Queries"):
                    st.code(msg["cypher"], language="cypher")
    
    # ------------------------------------------------------------------
    # Handle input (typed or quick-query click)
    # ------------------------------------------------------------------
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
        
        # ==============================================================
        # STEP A: Plan Investigation (Think + Generate Cypher)
        # ==============================================================
        with st.spinner("Planning investigation..."):
            schema = get_graph_schema_context()
            
            chat_history_text = ""
            for h in st.session_state.assistant_chat_history[-5:]:
                chat_history_text += f"User: {h['question']}\nApproach: {h.get('reasoning', '')}\n\n"
            
            plan_prompt = INVESTIGATION_PLANNER_PROMPT.format(
                schema=schema,
                chat_history=chat_history_text or "No prior context.",
                question=user_input
            )
            plan_raw = call_llm(llm_config, plan_prompt, temperature=0.2)
        
        # Parse the JSON plan — fallback to treating raw output as single Cypher
        if not plan_raw or plan_raw.startswith("LLM Error"):
            error_msg = f"Failed to plan investigation: {plan_raw}"
            st.error(error_msg)
            st.session_state.assistant_messages.append({"role": "assistant", "content": error_msg})
            return
        
        try:
            plan = _parse_llm_json(plan_raw)
        except (json.JSONDecodeError, ValueError):
            # Fallback: LLM returned raw Cypher instead of JSON
            raw_cypher = plan_raw.strip()
            if raw_cypher.startswith("```"):
                raw_cypher = raw_cypher.split("\n", 1)[-1]
            if raw_cypher.endswith("```"):
                raw_cypher = raw_cypher.rsplit("```", 1)[0]
            plan = {
                "reasoning": "Direct query generation",
                "complexity": "simple",
                "queries": [{"purpose": "Answer the question", "cypher": raw_cypher.strip(), "depends_on": None}]
            }
        
        complexity = plan.get("complexity", "simple")
        reasoning = plan.get("reasoning", "")
        planned_queries = plan.get("queries", [])[:3]  # Cap at 3
        
        # Show the investigation plan
        with st.expander(f"🧠 Investigation Plan ({complexity})", expanded=False):
            st.markdown(f"**Approach:** {reasoning}")
            for i, q in enumerate(planned_queries):
                st.markdown(f"**Query {i+1}:** {q.get('purpose', 'N/A')}")
        
        # ==============================================================
        # STEP B: Execute Planned Queries Sequentially
        # ==============================================================
        all_records = []          # Neo4j record objects for visualization
        query_results_text = []   # Serialized results for LLM prompts
        all_cypher = []           # All executed Cypher strings
        
        for i, q in enumerate(planned_queries):
            cypher = q.get("cypher", "").strip()
            if not cypher:
                continue
            
            all_cypher.append(cypher)
            purpose = q.get("purpose", f"Query {i+1}")
            
            with st.spinner(f"Query {i+1}/{len(planned_queries)}: {purpose[:60]}..."):
                try:
                    records = run_query(cypher)
                    all_records.extend(records if records else [])
                    
                    serialized = _serialize_records_for_llm(records)
                    query_results_text.append({
                        "query_index": i + 1,
                        "purpose": purpose,
                        "cypher": cypher,
                        "result_count": len(records) if records else 0,
                        "data": serialized
                    })
                except Exception as e:
                    query_results_text.append({
                        "query_index": i + 1,
                        "purpose": purpose,
                        "cypher": cypher,
                        "error": str(e)[:200]
                    })
        
        # ==============================================================
        # STEP C: Reflect (complex queries only)
        # ==============================================================
        if complexity == "complex" and any(
            qr.get("result_count", 0) > 0 for qr in query_results_text
        ):
            with st.spinner("Reviewing evidence completeness..."):
                reflect_prompt = REFLECTION_PROMPT.format(
                    question=user_input,
                    reasoning=reasoning,
                    query_results=json.dumps(query_results_text, indent=2, default=str)
                )
                reflect_raw = call_llm(llm_config, reflect_prompt, temperature=0.1)
                
                try:
                    reflection = _parse_llm_json(reflect_raw)
                    
                    if not reflection.get("sufficient") and reflection.get("corrective_query"):
                        corrective = reflection["corrective_query"].strip()
                        all_cypher.append(corrective)
                        gap_desc = reflection.get("gap", "Fill evidence gap")
                        
                        with st.spinner(f"Corrective query: {gap_desc[:60]}..."):
                            try:
                                records = run_query(corrective)
                                all_records.extend(records if records else [])
                                
                                serialized = _serialize_records_for_llm(records)
                                query_results_text.append({
                                    "query_index": len(all_cypher),
                                    "purpose": f"Corrective: {gap_desc}",
                                    "cypher": corrective,
                                    "result_count": len(records) if records else 0,
                                    "data": serialized
                                })
                            except Exception:
                                pass  # Corrective failed — proceed with what we have
                except (json.JSONDecodeError, ValueError):
                    pass  # Reflection parse failed — proceed with what we have
        
        # ==============================================================
        # STEP D: Build Visualization from ALL Collected Records
        # ==============================================================
        graph_nodes = []
        graph_edges = []
        
        if all_records:
            # Gather node IDs across all query results, then fetch interconnecting rels
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
                f"**{len(graph_edges)} connections** | "
                f"**{len(all_cypher)} {'query' if len(all_cypher) == 1 else 'queries'}** executed"
            )
            config = get_graph_config(width="100%", height=500)
            agraph(graph_nodes, graph_edges, config)
        elif all_cypher:
            st.warning("Queries returned no graph-visualizable results.")
        
        # Show all executed Cypher in a single expander
        with st.expander(f"🔍 Executed Queries ({len(all_cypher)})"):
            for i, c in enumerate(all_cypher):
                st.markdown(f"**Query {i+1}:**")
                st.code(c, language="cypher")
        
        # ==============================================================
        # STEP E: Analyst Synthesis
        # ==============================================================
        with st.spinner("Synthesizing findings..."):
            synthesis_prompt = ANALYST_SYNTHESIS_PROMPT.format(
                question=user_input,
                investigation_summary=reasoning,
                all_results=json.dumps(query_results_text, indent=2, default=str)
            )
            response_text = call_llm(llm_config, synthesis_prompt, temperature=0.3)
        
        if response_text:
            st.markdown(response_text)
        
        # ----------------------------------------------------------
        # Store message for chat history replay
        # ----------------------------------------------------------
        st.session_state.assistant_messages.append({
            "role": "assistant",
            "content": response_text or "Analysis unavailable.",
            "graph_nodes": graph_nodes if graph_nodes else None,
            "graph_edges": graph_edges if graph_edges else None,
            "cypher": "\n---\n".join(all_cypher) if all_cypher else None
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

# =============================================================================
# ROUTING
# =============================================================================

if page == "🎯 Scenario Walkthrough":
    render_scenario_walkthrough()
elif page == "🤖 Investigation Assistant":
    render_investigation_assistant()
elif page == "🔍 Network Explorer":
    render_free_exploration()
else:
    render_admin()