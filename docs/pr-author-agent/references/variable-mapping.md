# Variable Mapping Reference

This document defines all variables available for template interpolation in the PR Author Agent.

## Variable Syntax

Templates use `${VARIABLE_NAME}` syntax for substitution. Variables are case-sensitive.

```
Hello ${SERVICE_NAME}!  ->  Hello orders-enricher!
```

## Core Variables

### Service Identification

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `${SERVICE_NAME}` | string | Repository/service name | `orders-enricher` |
| `${SERVICE_URN}` | string | Canonical service URN | `urn:svc:prod:commerce:orders-enricher` |
| `${NAMESPACE}` | string | Kubernetes namespace or project | `commerce` |
| `${OWNER_TEAM}` | string | Owning team from CODEOWNERS | `orders-team` |

### Kafka Variables

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `${INPUT_TOPIC}` | string | Kafka input topic name | `orders_raw` |
| `${OUTPUT_TOPIC}` | string | Kafka output topic name | `orders_enriched` |
| `${CONSUMER_GROUP}` | string | Kafka consumer group ID | `orders-enricher-cg` |
| `${BOOTSTRAP_SERVERS}` | string | Kafka bootstrap servers | `kafka:9092` |

### Schema Variables

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `${SCHEMA_ID}` | string | Schema identifier | `orders.v3` |
| `${SCHEMA_REGISTRY_URL}` | string | Schema registry URL | `http://schema-registry:8081` |
| `${INPUT_SCHEMA_SUBJECT}` | string | Input schema subject | `orders_raw-value` |
| `${OUTPUT_SCHEMA_SUBJECT}` | string | Output schema subject | `orders_enriched-value` |

### OTel Variables

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `${OTEL_VERSION}` | string | OpenTelemetry SDK version | `1.32.0` |
| `${OTEL_EXPORTER_ENDPOINT}` | string | OTLP exporter endpoint | `http://otel-collector:4317` |
| `${OTEL_SERVICE_NAME}` | string | OTel service.name attribute | `orders-enricher` |
| `${OTEL_SERVICE_NAMESPACE}` | string | OTel service.namespace | `commerce` |

### Metadata Variables

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `${TIMESTAMP}` | string | Current ISO timestamp | `2026-01-04T10:30:00Z` |
| `${DIFF_PLAN_ID}` | string | Scout Agent Diff Plan ID | `dp-abc123` |
| `${CONFIDENCE}` | string | Confidence score (percentage) | `87%` |
| `${ARCHETYPES}` | string | Comma-separated archetypes | `kafka-microservice, spring-boot` |
| `${LANGUAGE}` | string | Primary programming language | `java` |

## Derived Variables

These variables are computed from core variables:

### Java-specific

| Variable | Derivation | Example |
|----------|------------|---------|
| `${PACKAGE_NAME}` | SERVICE_NAME with `-` -> `.` | `orders.enricher` |
| `${CLASS_NAME}` | SERVICE_NAME in PascalCase | `OrdersEnricher` |
| `${ARTIFACT_ID}` | SERVICE_NAME as-is | `orders-enricher` |
| `${GROUP_ID}` | `com.company.${NAMESPACE}` | `com.company.commerce` |

### Python-specific

| Variable | Derivation | Example |
|----------|------------|---------|
| `${MODULE_NAME}` | SERVICE_NAME with `-` -> `_` | `orders_enricher` |
| `${PACKAGE_DIR}` | MODULE_NAME as path | `orders_enricher/` |

### Go-specific

| Variable | Derivation | Example |
|----------|------------|---------|
| `${GO_MODULE}` | `github.com/company/${SERVICE_NAME}` | `github.com/company/orders-enricher` |
| `${GO_PACKAGE}` | Last segment of module | `ordersenricher` |

## Variable Sources

Variables are populated from multiple sources in this priority order:

1. **Diff Plan** (highest priority)
   - `repo`, `archetypes`, `confidence`, `tech_stack`
   - `gaps[].template`, `patch_plan[]`

2. **Repository Analysis**
   - CODEOWNERS file -> `OWNER_TEAM`
   - Config files -> topic names, consumer groups

3. **Configuration**
   - `autopilot-config.yaml` defaults
   - Environment variables

4. **Computed**
   - Derived variables (PACKAGE_NAME, CLASS_NAME, etc.)
   - Timestamps

## Conditional Blocks

Templates support conditional rendering:

```
{{#if KAFKA_ENABLED}}
kafka:
  bootstrap-servers: ${BOOTSTRAP_SERVERS}
  consumer:
    group-id: ${CONSUMER_GROUP}
{{/if}}
```

### Available Conditions

| Condition | True when |
|-----------|-----------|
| `KAFKA_ENABLED` | Kafka archetype detected |
| `GRPC_ENABLED` | gRPC archetype detected |
| `REST_ENABLED` | REST API archetype detected |
| `SPARK_ENABLED` | Spark job archetype detected |
| `AIRFLOW_ENABLED` | Airflow DAG archetype detected |
| `HAS_LINEAGE_SPEC` | Lineage spec will be generated |
| `HAS_CONTRACT` | Data contract will be generated |

## Loop Blocks

Templates support iteration:

```
{{#each GAPS}}
- {{type}}: {{description}}
{{/each}}
```

### Available Loops

| Collection | Items |
|------------|-------|
| `GAPS` | Gap objects from Diff Plan |
| `ARCHETYPES` | List of archetype strings |
| `INPUT_TOPICS` | List of input topic names |
| `OUTPUT_TOPICS` | List of output topic names |

## Example Template

```java
// ${CLASS_NAME}OtelInterceptor.java
// Generated by PR Author Agent
// Diff Plan: ${DIFF_PLAN_ID}

package com.company.${NAMESPACE}.${MODULE_NAME}.otel;

import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.api.trace.Tracer;

/**
 * OpenTelemetry interceptor for ${SERVICE_NAME}.
 *
 * Service URN: ${SERVICE_URN}
 * Owner: ${OWNER_TEAM}
 *
 * @since ${TIMESTAMP}
 */
public class ${CLASS_NAME}OtelInterceptor {

    private static final String SERVICE_NAME = "${SERVICE_NAME}";
    private static final String SERVICE_NAMESPACE = "${NAMESPACE}";

    private final Tracer tracer;

    public ${CLASS_NAME}OtelInterceptor(OpenTelemetry openTelemetry) {
        this.tracer = openTelemetry.getTracer(SERVICE_NAME, "${OTEL_VERSION}");
    }

    {{#if KAFKA_ENABLED}}
    // Kafka consumer configuration
    private static final String CONSUMER_GROUP = "${CONSUMER_GROUP}";
    private static final String INPUT_TOPIC = "${INPUT_TOPIC}";
    {{/if}}
}
```

## Escaping

To output literal `${...}` without interpolation, use double dollar:

```
$${NOT_REPLACED}  ->  ${NOT_REPLACED}
```

## Missing Variables

When a variable is not defined:
- Warning is logged
- Original `${VAR_NAME}` is preserved in output
- PR creation continues (does not fail)

To require variables, use strict mode in templates:

```
{{#strict}}
${REQUIRED_VAR}
{{/strict}}
```

This will cause template rendering to fail if the variable is missing.
