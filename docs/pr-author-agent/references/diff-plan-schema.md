# Observability Diff Plan Schema

The Observability Diff Plan is the contract between Scout Agent (producer) and PR Author Agent (consumer).

## JSON Schema Definition

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ObservabilityDiffPlan",
  "description": "Scout Agent output consumed by PR Author Agent",
  "type": "object",
  "required": ["repo", "scan_timestamp", "archetypes", "confidence", "tech_stack", "current_observability", "gaps"],
  "properties": {
    "repo": {
      "type": "string",
      "description": "Repository name or identifier"
    },
    "repo_url": {
      "type": "string",
      "format": "uri",
      "description": "Full repository URL"
    },
    "diff_plan_id": {
      "type": "string",
      "description": "Unique identifier for this Diff Plan",
      "pattern": "^dp-[a-z0-9]+$"
    },
    "scan_timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of scan"
    },
    "archetypes": {
      "type": "array",
      "items": { "type": "string" },
      "minItems": 1,
      "description": "Detected repository archetypes"
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Confidence score for automated instrumentation"
    },
    "tech_stack": {
      "$ref": "#/definitions/TechStack"
    },
    "current_observability": {
      "$ref": "#/definitions/ObservabilityState"
    },
    "gaps": {
      "type": "array",
      "items": { "$ref": "#/definitions/Gap" }
    },
    "patch_plan": {
      "type": "array",
      "items": { "$ref": "#/definitions/Patch" }
    },
    "risk_notes": {
      "type": "array",
      "items": { "type": "string" }
    }
  },
  "definitions": {
    "TechStack": {
      "type": "object",
      "properties": {
        "language": {
          "type": "string",
          "enum": ["java", "python", "go", "typescript", "scala"]
        },
        "build_system": {
          "type": "string",
          "enum": ["maven", "gradle", "pip", "poetry", "go", "npm", "sbt"]
        },
        "framework": {
          "type": "string",
          "description": "Primary framework with version"
        },
        "kafka_client": {
          "type": "string",
          "description": "Kafka client library and version"
        },
        "spark_version": {
          "type": "string"
        },
        "airflow_version": {
          "type": "string"
        },
        "go_version": {
          "type": "string"
        },
        "http_framework": {
          "type": "string",
          "description": "HTTP framework (gin, echo, fiber, chi, fastapi, etc.)"
        }
      }
    },
    "ObservabilityState": {
      "type": "object",
      "description": "Current observability instrumentation state",
      "properties": {
        "otel_sdk": {
          "type": "boolean",
          "description": "OTel SDK present in dependencies"
        },
        "correlation_propagation": {
          "type": "boolean",
          "description": "Correlation headers being propagated"
        },
        "lineage_spec": {
          "type": "boolean",
          "description": "Lineage specification file exists"
        },
        "contract_stub": {
          "type": "boolean",
          "description": "Data contract definition exists"
        },
        "runbook": {
          "type": "boolean",
          "description": "RUNBOOK.md file exists"
        }
      }
    },
    "Gap": {
      "type": "object",
      "required": ["type", "location", "description", "priority", "template"],
      "properties": {
        "type": {
          "type": "string",
          "enum": [
            "missing_otel",
            "missing_correlation",
            "missing_lineage_spec",
            "missing_contract",
            "missing_runbook",
            "outdated_otel",
            "incomplete_headers"
          ]
        },
        "location": {
          "type": "string",
          "description": "File path where change is needed"
        },
        "description": {
          "type": "string",
          "description": "Human-readable gap description"
        },
        "priority": {
          "type": "string",
          "enum": ["P0", "P1", "P2"],
          "description": "Priority (P0=critical, P1=high, P2=medium)"
        },
        "template": {
          "type": "string",
          "description": "Template name for remediation"
        }
      }
    },
    "Patch": {
      "type": "object",
      "required": ["file", "action"],
      "properties": {
        "file": {
          "type": "string",
          "description": "Target file path"
        },
        "action": {
          "type": "string",
          "enum": ["add_dependency", "merge_config", "create_file", "modify_file"]
        },
        "content": {
          "type": "string",
          "description": "Content to add/merge/create"
        },
        "position": {
          "type": "string",
          "description": "Where to insert (for add_dependency)"
        }
      }
    }
  }
}
```

## Example Diff Plan

```json
{
  "repo": "orders-enricher",
  "repo_url": "https://github.com/company/orders-enricher",
  "diff_plan_id": "dp-abc123",
  "scan_timestamp": "2026-01-04T10:30:00Z",
  "archetypes": ["kafka-microservice", "spring-boot"],
  "confidence": 0.87,
  "tech_stack": {
    "language": "java",
    "build_system": "maven",
    "framework": "spring-boot-3.2",
    "kafka_client": "spring-kafka-3.1"
  },
  "current_observability": {
    "otel_sdk": false,
    "correlation_propagation": false,
    "lineage_spec": false,
    "contract_stub": false,
    "runbook": false
  },
  "gaps": [
    {
      "type": "missing_otel",
      "location": "src/main/java/com/company/OrderConsumer.java",
      "description": "Kafka consumer lacks OTel interceptor",
      "priority": "P0",
      "template": "kafka-consumer-otel-java"
    },
    {
      "type": "missing_correlation",
      "location": "src/main/java/com/company/OrderProducer.java",
      "description": "Producer not injecting x-obs-* headers",
      "priority": "P0",
      "template": "kafka-producer-headers-java"
    },
    {
      "type": "missing_lineage_spec",
      "location": "lineage/",
      "description": "No lineage spec file defining input/output mappings",
      "priority": "P1",
      "template": "lineage-spec-kafka"
    },
    {
      "type": "missing_contract",
      "location": "contracts/",
      "description": "No data contract with SLO definitions",
      "priority": "P1",
      "template": "contract-stub"
    },
    {
      "type": "missing_runbook",
      "location": "./",
      "description": "No operational runbook",
      "priority": "P2",
      "template": "runbook"
    }
  ],
  "patch_plan": [
    {
      "file": "pom.xml",
      "action": "add_dependency",
      "content": "<dependency>\n  <groupId>io.opentelemetry</groupId>\n  <artifactId>opentelemetry-api</artifactId>\n  <version>1.32.0</version>\n</dependency>",
      "position": "dependencies"
    },
    {
      "file": "src/main/resources/application.yaml",
      "action": "merge_config",
      "content": "otel:\n  instrumentation:\n    kafka:\n      enabled: true"
    }
  ],
  "risk_notes": [
    "Custom Kafka serializer detected - may need manual OTel wrapper review",
    "No existing tests for Kafka consumer - recommend adding telemetry tests"
  ]
}
```

## Gap Types Reference

| Type | Description | Default Priority | Templates |
|------|-------------|------------------|-----------|
| `missing_otel` | No OTel SDK in dependencies | P0 | `*-otel-*` |
| `missing_correlation` | No correlation header propagation | P0 | `*-headers-*` |
| `missing_lineage_spec` | No lineage spec file | P1 | `lineage-spec-*` |
| `missing_contract` | No data contract definition | P1 | `contract-stub` |
| `missing_runbook` | No RUNBOOK.md | P2 | `runbook` |
| `outdated_otel` | OTel SDK version too old | P1 | `otel-upgrade-*` |
| `incomplete_headers` | Some headers missing | P1 | `*-headers-*` |

## Template Naming Convention

Templates follow the pattern: `{component}-{operation}-{language}`

Examples:
- `kafka-consumer-otel-java`
- `kafka-producer-headers-python`
- `spark-lineage-listener-scala`
- `airflow-openlineage-config`
- `gin-otel-go`
- `grpc-otel-go`

## Validation

PR Author Agent validates Diff Plans before processing:

1. **Schema Validation**: JSON must match schema
2. **Required Fields**: All required fields present
3. **Archetypes**: At least one archetype detected
4. **Confidence**: Must meet threshold (default 0.7)
5. **Gaps**: At least one gap identified

Invalid Diff Plans are rejected with appropriate error messages.
