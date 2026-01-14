

**DATA OBSERVABILITY PLATFORM**

High-Level Technical Architecture

**Out-of-Band Enforcement Signal Factory**

*Pattern 1: Pre-Consumption Safety Architecture*

Version 2.0 | January 2026

Enterprise Data Platform Architecture

**Document History**

| Version | Date | Author | Changes |
| :---- | :---- | :---- | :---- |
| 1.0 | Jan 2026 | Architecture Team | Initial HLD with inline gateway |
| 2.0 | Jan 2026 | Architecture Team | Evolved to Out-of-Band Enforcement (Pattern 1\) |

# **Table of Contents**

# **1\. Executive Summary**

This document presents the evolved High-Level Technical Architecture for the Data Observability Platform, implementing the Signal Factory paradigm using Out-of-Band Enforcement (Pattern 1). This architectural evolution addresses a critical constraint: the existing central streaming platform and its producers cannot be modified.

The Out-of-Band Enforcement pattern represents a strategic shift from pre-publish prevention to pre-consumption safety. Instead of blocking data at the ingestion point, we add a powerful observability layer that creates an immutable evidence record for every event, enabling downstream consumers to make trust-based decisions while providing SREs with deterministic root-cause analysis.

## **1.1 Architectural Evolution Summary**

| Dimension | Original HLD (v1.0) | Evolved HLD (v2.0) |
| :---- | :---- | :---- |
| **Core Philosophy** | Pre-publish prevention | Pre-consumption safety |
| **Producer Impact** | Requires SDK adoption, API changes | Zero producer changes required |
| **Platform Constraint** | Assumes control over ingestion | Accepts immutable central platform |
| **Latency Profile** | Adds latency to critical path | Zero latency impact on data flow |
| **Risk Model** | Prevention-first | Detection \+ evidence-first |
| **Failure Blast Radius** | Gateway down \= all ingestion blocked | Enforcer down \= observability gap only |

## **1.2 Strategic Context**

The Signal Factory treats telemetry as a manufactured product rather than an exhaust byproduct of running systems. This paradigm shift enables industrialized observability signal production with rigorous quality controls, standardization, and process engineering. The architecture is designed around a North Star goal: achieving fastest Mean Time to Resolution (MTTR) via an AI-powered RCA Copilot while enabling progressive prevention through contracts and gates.

## **1.3 Target Metrics**

| Metric | Current State | Target State |
| :---- | :---- | :---- |
| RCA Query Latency | 30-60 minutes | \< 2 minutes |
| Mean Time to Detection | 4-6 hours (Tier-1) | \< 15 minutes |
| Mean Time to Resolution | 12+ hours | \< 2 hours |
| False Positive Alert Rate | 60-80% | \< 20% |
| Lineage Coverage | 0% element-level | 100% Tier-1 assets |
| Developer Toil | 20% sprint velocity | \< 5% |

## **1.4 Systems Thinking Analysis**

| Dimension | Analysis |
| :---- | :---- |
| **Inflows** | Raw events from Central Streaming Platform, Schema Registry events, CI/CD pipeline events, Airflow DAG metadata, Spark/Delta commits |
| **Outflows** | Evidence events (per-record truth), Normalized signals, Correlation graphs, Lineage maps, Incident alerts, RCA explanations, Gate decisions |
| **Cost of Action** | 16-week implementation, \~$15K/month AWS infrastructure, 6 engineers initial \+ 2 FTE ongoing, cross-team coordination overhead |
| **Cost of Inaction** | Continued 12+ hour MTTR, 20% developer toil, data trust erosion, repeated incidents without learning, engineer burnout |
| **Hidden Assumptions** | Central platform is immutable; producers cannot be modified; Schema heterogeneity requires canonical registry; adoption requires pull dynamics |

# **2\. Architectural Overview**

The Out-of-Band Enforcement architecture introduces a fundamental separation between the data flow (which remains untouched) and the observability flow (which operates asynchronously). This section describes the evolved five-plane model and the key components that enable pre-consumption safety without modifying producers or the central platform.

## **2.1 Five-Plane Architecture Model (Evolved)**

The Signal Factory architecture remains composed of five distinct planes, but with evolved responsibilities that accommodate the out-of-band enforcement pattern:

| Plane | Function | Key Components |
| :---- | :---- | :---- |
| **Production** | Generates raw data events | Microservices, Central Platform (Kafka/MSK \- unchanged), Spark, Airflow |
| **Enforcement** | Establishes per-record truth | Policy Enforcer (sidecar), Gateway Control Plane, Evidence Bus |
| **Processing** | Transforms evidence into signals | Signal Engines (Freshness, Volume, Contract, DQ, Anomaly, Cost) |
| **Knowledge** | Stores state and relationships | Neptune (Graph), DynamoDB (State), S3 (Archive), OpenSearch (Text) |
| **Consumption** | Interfaces for humans and AI | RCA Copilot, Governance Registry, Alerting, Instrumentation Autopilot |

Note: The Enforcement Plane is a new addition in v2.0, replacing the inline Ingestion Gateway from v1.0. The Ingestion Plane from v1.0 has been absorbed into the Enforcement and Processing planes.

## **2.2 Core Architectural Principle: Record Truth vs System Health**

The Out-of-Band pattern introduces a critical architectural distinction that enables clear ownership boundaries and prevents logic duplication:

| Concern | Owner | Scope | Output |
| :---- | :---- | :---- | :---- |
| **Record Truth** | Policy Enforcer | Atomic (one record at a time) | Evidence (PASS/FAIL) |
| **System Health** | Signal Engines | Aggregated (time windows) | Signals & Incidents |

## **2.3 Decision Matrix: Where Logic Belongs**

| Logic | Policy Enforcer | Signal Engine |
| :---- | :---: | :---: |
| JSON parsing / envelope normalization | ✓ | — |
| Schema validation against registry | ✓ | — |
| Contract validation (required fields, constraints) | ✓ | — |
| PII detection per record | ✓ | — |
| Emit PASS/FAIL evidence for each record | ✓ | — |
| Compute compliance rate over time windows | — | ✓ |
| Static threshold breach detection | — | ✓ |
| Dynamic anomaly detection (ML-based) | — | ✓ |
| Correlate multiple signals into incidents | — | ✓ |
| Provide root cause narrative | — | ✓ (via RCA Copilot) |

# **3\. Core Components**

## **3.1 Policy Enforcer (NEW in v2.0)**

The Policy Enforcer is the cornerstone of the Out-of-Band architecture. It operates as a sidecar observer that consumes events from the Central Streaming Platform after they have been published, running a deterministic pipeline of validation gates to establish per-record truth.

### **3.1.1 Gate Pipeline**

| Gate | Name | Function | Output |
| :---- | :---- | :---- | :---- |
| **G1** | Resolution | Map topic → dataset URN | urn:dp:orders:created |
| **G2** | Identity | Identify producer service | orders-svc (confidence: HIGH) |
| **G3** | Schema | Validate vs Glue Registry | glue:orders.created:17 → PASS |
| **G4** | Contract | Validate vs ODCS contract | dc:orders.created:3 → FAIL |
| **G5** | PII | Scan for PII patterns | PII\_DETECTED / CLEAN |

### **3.1.2 Key Design Principles**

* Non-blocking: The Enforcer NEVER blocks the data flow. Bad data flows through the platform; the Enforcer only creates evidence.  
* Deterministic: Every raw event produces exactly one Evidence event. This is a pure function with no side effects on the data path.  
* Trace-Anchored: All evidence preserves trace\_id from source events (if present) to enable deterministic RCA.  
* Configuration-Driven: All thresholds, SLOs, and policies are managed by the Gateway Control Plane—never hardcoded.

## **3.2 Gateway Control Plane**

The Gateway Control Plane is the authoritative configuration brain of the system. It provides APIs for managing dataset policies, schema bindings, contract definitions, and enforcement rules. Unlike v1.0 where the Gateway was on the critical data path, in v2.0 it is purely a configuration service.

| Capability | Description |
| :---- | :---- |
| **Dataset Registry** | Manages URN mappings, tier classifications, and ownership metadata |
| **Schema Bindings** | Maps topics to Glue Registry schemas with version policies |
| **Contract Definitions** | ODCS contract specifications with required fields and SLOs |
| **Signal SLOs** | Per-dataset freshness, volume, and quality thresholds |
| **Producer Identity Map** | Topic-to-service mappings for attribution when headers unavailable |

## **3.3 Evidence Bus**

The Evidence Bus (signal\_factory.evidence Kafka topic) is the sole, non-negotiable API for all downstream systems. Signal Engines MUST NOT consume raw business topics directly—they operate exclusively on the immutable facts presented in the Evidence stream.

### **3.3.1 Canonical Evidence Schema**

{  
  "evidence\_id": "evd-01J...",  
  "timestamp": "2023-10-27T09:58:02Z",  
  "dataset\_urn": "urn:dp:orders:created",  
  "producer": {  
    "id": "orders-svc",  
    "confidence": "HIGH"  
  },  
  "validation": {  
    "result": "FAIL",  
    "failed\_gates": \["CONTRACT"\],  
    "reason\_codes": \["MISSING\_FIELD:customer\_id"\]  
  },  
  "source": {  
    "topic": "raw.orders.events",  
    "offset": 1882341  
  },  
  "otel": {  
    "trace\_id": "ab91f..."  
  }  
}

## **3.4 Signal Engines (Evolved)**

Signal Engines transform the firehose of per-record Evidence into high-level, actionable signals about system health. In v2.0, they consume ONLY from the Evidence Bus—never from raw topics.

| Engine | Function | Output |
| :---- | :---- | :---- |
| **Freshness** | Monitors time since last valid evidence | FreshnessBreachDetected |
| **Volume** | Detects anomalies in event throughput | VolumeAnomalyDetected |
| **Contract** | Computes compliance rate over windows | ContractBreachDetected |
| **DQ (Data Quality)** | Aggregates Deequ results from evidence | DQBreachDetected |
| **Drift** | Detects schema and distribution changes | DriftDetected |
| **Anomaly** | ML-based pattern detection across metrics | AnomalyDetected |
| **Cost** | Tracks compute and storage costs per asset | CostAnomalyDetected |

# **4\. Data Flow Architecture**

## **4.1 End-to-End Flow: Out-of-Band Pattern**

The following describes the complete data flow from producer to incident, highlighting how the Out-of-Band architecture maintains separation between the data path and the observability path:

| Step | Component | Action |
| :---: | :---- | :---- |
| 1 | **Producer (Orders Service)** | Publishes event to raw.orders.events topic |
| 2 | **Central Platform (Kafka/MSK)** | Accepts and stores event (unchanged, immutable) |
| 3 | **Policy Enforcer (async)** | Consumes event, runs gate pipeline, emits Evidence |
| 4 | **Evidence Bus** | Stores canonical Evidence event |
| 5 | **Signal Engines** | Consume Evidence, compute aggregated signals |
| 6 | **Knowledge Plane** | DynamoDB: state, Neptune: causal graph |
| 7 | **Alerting Engine** | SLO breach triggers SEV-1 incident |
| 8 | **RCA Copilot** | Traverses graph to explain root cause |

## **4.2 Latency Characteristics**

| Path | Target Latency | Notes |
| :---- | :---- | :---- |
| **Data Path (Producer → Kafka)** | Unchanged (0ms added) | Platform remains immutable |
| **Evidence Path (Kafka → Evidence)** | \< 2 seconds | From raw ingest to evidence emit |
| **Signal Path (Evidence → Signal)** | 5-minute windows | Aggregation window for SLO eval |
| **RCA Query Path** | \< 2 minutes | From incident to explanation |

## **4.3 Key Benefits**

| Benefit | Description |
| :---- | :---- |
| **Zero Producer Changes** | The Central Platform remains immutable. Enforcer runs entirely out-of-band as a sidecar consumer. |
| **\< 2s Evidence Latency** | From raw event ingest to Evidence emission and Signal update. |
| **100% Attribution** | Failures are linked to producers via best-effort identity inference and confidence scores. |

# **5\. Knowledge Plane Architecture**

## **5.1 Dual Storage Strategy**

The Knowledge Plane employs a dual storage strategy that separates operational state (fast lookups) from causal relationships (graph traversals):

| Store | Purpose | Use Case |
| :---- | :---- | :---- |
| **DynamoDB** | Operational Truth (State) | Fast dashboards: "What is the current health?" |
| **Neptune** | Causal Graph (Relationships) | Root cause analysis: "Why did this happen?" |

## **5.2 DynamoDB Tables**

| Table | PK | SK | Purpose |
| :---- | :---- | :---- | :---- |
| SignalState | asset\_urn | signal\_type | Current signal state per asset |
| IncidentIndex | incident\_id | timestamp | Active incidents with context |
| DatasetRegistry | dataset\_urn | version | Dataset metadata and policies |
| EvidenceCache | evidence\_id | — | Hot evidence for RCA queries |

## **5.3 Neptune Graph Model**

The Neptune graph enables causal traversal from incidents back to root causes. Key node and edge types:

### **5.3.1 Node Types**

| Node Type | Description |
| :---- | :---- |
| Producer | Service that emits data (orders-svc, payments-svc) |
| Deployment | Specific version deployment (v3.17, v3.18) |
| FailureSignature | Unique failure pattern (MISSING\_FIELD:customer\_id) |
| Signal | Aggregated health signal (Contract Breach, Freshness Breach) |
| Incident | SEV-1/2/3 incident with ticket metadata |

### **5.3.2 Edge Types**

| Edge | From → To | Meaning |
| :---- | :---- | :---- |
| INTRODUCED | Deployment → FailureSignature | This deployment introduced this failure |
| CAUSED | FailureSignature → Signal | This failure pattern caused this signal |
| TRIGGERED | Signal → Incident | This signal breach triggered incident |
| OWNS | Producer → Dataset | Service owns this dataset |

### **5.3.3 Graph Optimization: Failure Signatures**

To prevent graph explosion, we do not store every failed record as a node. Instead, we bucket failures into unique FailureSignatures based on the combination of: failed\_gates \+ reason\_codes \+ dataset\_urn. This provides cardinality control while preserving causal fidelity.

# **6\. Resilience and Failure Modes**

A key advantage of Out-of-Band Enforcement is reduced blast radius. Unlike inline gateway failures that block all ingestion, Enforcer failures only create observability gaps.

## **6.1 Failure Mode Matrix**

| Failure | Impact | Mitigation |
| :---- | :---- | :---- |
| **Enforcer Down** | Evidence Gap | Signal Engines detect "Zero Evidence" vs Raw Lag. Trigger OBSERVABILITY\_PIPELINE\_DOWN alert. |
| **Registry Down** | Cannot validate schema | Enforcer falls back to WARN mode. Emits evidence with failed\_gates=\["REGISTRY\_UNAVAILABLE"\]. Never crashes consumer. |
| **Lag Spikes** | Delayed signals | HPA scales consumers. Signal Engine annotations mark data as "Stale". Dashboard shows staleness indicator. |
| **Neptune Down** | RCA unavailable | DynamoDB serves cached context. RCA Copilot returns "Graph unavailable" with deterministic fallback. |
| **LLM (Bedrock) Down** | Natural language unavailable | Fallback to template-based explanations. Evidence IDs and graph paths still available. |

## **6.2 Observability of Observability**

The platform monitors its own health with dedicated signals:

* enforcer.lag\_seconds: Consumer lag on raw topics (alert if \> 30s)  
* enforcer.evidence\_rate: Evidence events per second (alert if drops \> 50%)  
* engine.signal\_freshness: Age of computed signals (alert if \> 10 minutes)  
* neptune.query\_latency\_p99: Graph query latency (alert if \> 5s)

# **7\. Progressive Gate Strategy**

The progressive gate strategy enables gradual adoption without disruption. Gates are enforcement levels that increase strictness over time as confidence grows.

## **7.1 Gate Definitions**

| Gate | Name | Action | Timeline |
| :---- | :---- | :---- | :---- |
| **G0** | Visibility | Telemetry collected, dashboarding only | Weeks 1-4 |
| **G1** | Warn | CI warnings for missing contracts/URNs | Weeks 5-8 |
| **G2** | Soft-Fail | Reject in staging; alert in prod | Weeks 9-12 (Tier-1) |
| **G3** | Hard-Fail | Reject in prod; block deploys | Week 13+ (Tier-1) |

## **7.2 Tier-Based Enforcement**

Not all assets are equal. Tier classification determines enforcement strictness:

| Tier | Criteria | Enforcement |
| :---- | :---- | :---- |
| **Tier-1** | Revenue-critical, customer-facing, regulatory | Full G3 enforcement; 15-min freshness SLO |
| **Tier-2** | Internal analytics, operational dashboards | G2 enforcement; 1-hour freshness SLO |
| **Tier-3** | Experimental, development, low-impact | G0-G1 only; best-effort monitoring |

# **8\. Implementation Roadmap**

## **8.1 Phase Overview**

| Phase | Duration | Deliverables |
| :---- | :---- | :---- |
| **1** | Weeks 1-4 | Gateway Control Plane, Policy Enforcer (G1 gates), Evidence Bus, basic Signal Engine |
| **2** | Weeks 5-8 | Neptune graph model, all Signal Engines, DynamoDB state tables, alerting integration |
| **3** | Weeks 9-12 | RCA Copilot (Bedrock), Instrumentation Autopilot agents, G2 enforcement for Tier-1 |
| **4** | Weeks 13-16 | G3 enforcement, production hardening, documentation, training |

## **8.2 Success Criteria**

| Metric | Target |
| :---- | :---- |
| Evidence coverage for Tier-1 topics | \> 95% |
| Evidence latency (raw → evidence) | \< 2 seconds P99 |
| Signal freshness | \< 5 minutes |
| RCA query latency | \< 2 minutes |
| False positive alert rate | \< 20% |
| Platform availability | \> 99.5% |

## **8.3 Infrastructure Cost Estimate**

| Component | Monthly Cost |
| :---- | :---- |
| EKS (Enforcer \+ Control Plane) | \~$3,000 |
| Amazon Neptune | \~$4,000 |
| DynamoDB | \~$2,000 |
| Kinesis / MSK (Evidence Bus) | \~$3,000 |
| Bedrock (LLM for RCA) | \~$2,000 |
| S3, CloudWatch, Misc | \~$1,000 |
| **Total Estimated Monthly** | **\~$15,000** |

# **9\. Security Architecture**

| Domain | Approach | Implementation |
| :---- | :---- | :---- |
| **Authentication** | Service-to-service: IAM roles | IRSA (IAM Roles for Service Accounts) |
| **Authorization** | Least-privilege per component | Scoped IAM policies; Neptune IAM auth |
| **Encryption (Transit)** | TLS 1.3 everywhere | Internal ALBs with ACM certs; mTLS option |
| **Encryption (Rest)** | KMS for all data stores | Neptune KMS; DynamoDB AWS-managed keys |
| **Secrets Management** | No credentials in code | AWS Secrets Manager; no env vars for secrets |
| **PII Protection** | Field-level detection | Enforcer PII gate; evidence flags PII presence |

# **Appendix A: Glossary**

| Term | Definition |
| :---- | :---- |
| **Signal Factory** | Architectural paradigm treating telemetry as a manufactured product with quality controls |
| **Out-of-Band Enforcement** | Pattern where validation occurs after data publication, not inline |
| **Policy Enforcer** | Sidecar service that consumes raw events and produces evidence |
| **Evidence** | Immutable record of per-event validation result (PASS/FAIL with reason codes) |
| **Record Truth** | Per-record validation state established by Policy Enforcer |
| **System Health** | Aggregated signal state computed by Signal Engines over time windows |
| **RCA Copilot** | AI-powered assistant that explains incidents using evidence from the Knowledge Graph |
| **FailureSignature** | Unique pattern of failure (gate \+ reason) used for graph deduplication |
| **Progressive Gates** | Three-stage enforcement (Warn → Soft-Fail → Hard-Fail) for gradual adoption |
| **MTTR** | Mean Time to Resolution: average time from incident detection to resolution |
| **MTTD** | Mean Time to Detection: average time from issue occurrence to detection |

# **Appendix B: URN Conventions**

| Asset Type | URN Pattern | Example |
| :---- | :---- | :---- |
| Service | urn:svc:\<env\>:\<name\> | urn:svc:prod:order-service |
| Kafka Topic | urn:kafka:\<env\>:\<cluster\>:\<topic\> | urn:kafka:prod:main:orders-created |
| Dataset | urn:dp:\<domain\>:\<name\> | urn:dp:orders:created |
| Delta Table | urn:delta:\<env\>:\<catalog\>:\<schema\>:\<table\> | urn:delta:prod:unity:sales:orders\_silver |
| Column | urn:col:\<parent\_urn\>:\<column\> | urn:col:...:orders:customer\_id |
| Schema | urn:schema:\<registry\>:\<subject\>:\<ver\> | urn:schema:glue:orders-created:42 |
| Evidence | evd-\<ulid\> | evd-01HQXYZ... |

# **Appendix C: Architecture Decision Record**

## **ADR-001: Out-of-Band Enforcement over Inline Gateway**

**Status: ACCEPTED**

Date: January 2026

### **Context**

The original HLD (v1.0) proposed a Central Managed Ingestion Gateway that would sit inline on the data path, validating and enriching events before they reach Kafka. However, a critical constraint emerged: the existing central streaming platform and its producers cannot be modified.

### **Decision**

Adopt Out-of-Band Enforcement (Pattern 1\) where validation occurs asynchronously after data publication rather than inline before publication.

### **Comparison**

| Factor | Inline Gateway | Out-of-Band |
| :---- | :---- | :---- |
| Producer changes | Required | None |
| Platform modification | Required | None |
| Latency impact | Adds P99 latency | Zero |
| Failure blast radius | Blocks all ingestion | Observability gap only |
| Bad data handling | Blocked at entry | Evidenced, consumer decides |
| Adoption friction | High | Low (transparent) |

### **Consequences**

* Positive: Zero producer changes required; reduced blast radius; faster adoption  
* Positive: Platform stability preserved; no latency impact on critical path  
* Negative: Bad data enters the platform before being flagged (detection vs prevention)  
* Negative: Consumers must make trust-based decisions using evidence  
* Mitigated: Progressive gates allow gradual enforcement; RCA Copilot provides immediate value

*— End of Document —*