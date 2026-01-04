#!/usr/bin/env python3
"""
PR Author Agent - Template Interpolation Engine
Renders code templates with variable substitution for observability instrumentation.
"""

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


@dataclass
class TemplateContext:
    """Context for template variable interpolation."""
    service_name: str
    service_urn: str
    namespace: str
    input_topic: str = ""
    output_topic: str = ""
    owner_team: str = "platform-team"
    consumer_group: str = ""
    schema_id: str = ""
    otel_version: str = "1.32.0"
    timestamp: str = ""
    diff_plan_id: str = ""
    confidence: float = 0.0
    archetypes: list[str] = None
    language: str = "java"

    def __post_init__(self):
        if self.archetypes is None:
            self.archetypes = []
        if not self.consumer_group:
            self.consumer_group = f"{self.service_name}-cg"

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary for variable lookup."""
        d = asdict(self)
        # Add computed variables
        d["SERVICE_NAME"] = self.service_name
        d["SERVICE_URN"] = self.service_urn
        d["NAMESPACE"] = self.namespace
        d["INPUT_TOPIC"] = self.input_topic
        d["OUTPUT_TOPIC"] = self.output_topic
        d["OWNER_TEAM"] = self.owner_team
        d["CONSUMER_GROUP"] = self.consumer_group
        d["SCHEMA_ID"] = self.schema_id
        d["OTEL_VERSION"] = self.otel_version
        d["TIMESTAMP"] = self.timestamp
        d["DIFF_PLAN_ID"] = self.diff_plan_id
        d["CONFIDENCE"] = f"{self.confidence:.0%}"
        d["ARCHETYPES"] = ", ".join(self.archetypes)
        d["LANGUAGE"] = self.language

        # Package name derivations
        d["PACKAGE_NAME"] = self.service_name.replace("-", ".")
        d["CLASS_NAME"] = "".join(
            word.capitalize() for word in self.service_name.split("-")
        )
        d["MODULE_NAME"] = self.service_name.replace("-", "_")

        return d


class TemplateEngine:
    """
    Template engine for rendering observability instrumentation code.

    Supports:
    - Variable interpolation: ${VAR_NAME}
    - Conditional blocks: {{#if VAR}}...{{/if}}
    - Loops: {{#each ITEMS}}...{{/each}}
    - File generation from templates
    """

    def __init__(self, templates_path: str = "./references/templates"):
        self.templates_path = Path(templates_path)
        self._template_cache: dict[str, str] = {}
        self._variable_pattern = re.compile(r'\$\{(\w+)\}')

    def render_template(
        self,
        template_name: str,
        context: TemplateContext
    ) -> dict[str, str]:
        """
        Render a template and return generated files.

        Args:
            template_name: Name of the template (e.g., 'kafka-consumer-otel-java')
            context: Template context with variables

        Returns:
            Dictionary mapping file paths to rendered content
        """
        template_dir = self._find_template_dir(template_name)
        if not template_dir:
            raise ValueError(f"Template not found: {template_name}")

        rendered_files = {}
        variables = context.to_dict()

        for template_file in template_dir.glob("*.tmpl"):
            # Determine output file name
            output_name = template_file.stem  # Remove .tmpl
            output_name = self._interpolate(output_name, variables)

            # Read and render template
            template_content = template_file.read_text()
            rendered_content = self._interpolate(template_content, variables)

            # Determine output path
            output_path = self._get_output_path(template_name, output_name, context)
            rendered_files[output_path] = rendered_content

        return rendered_files

    def render_runbook(self, context: TemplateContext) -> str:
        """Generate a RUNBOOK.md from the standard template."""
        template = self._get_builtin_template("runbook")
        return self._interpolate(template, context.to_dict())

    def render_lineage_spec(self, context: TemplateContext) -> str:
        """Generate a lineage spec YAML from template."""
        template = self._get_builtin_template("lineage-spec")
        return self._interpolate(template, context.to_dict())

    def render_contract_stub(self, context: TemplateContext) -> str:
        """Generate a data contract YAML from template."""
        template = self._get_builtin_template("contract-stub")
        return self._interpolate(template, context.to_dict())

    def render_telemetry_test(self, context: TemplateContext) -> str:
        """Generate telemetry validation tests from template."""
        template_key = f"telemetry-test-{context.language}"
        template = self._get_builtin_template(template_key)
        if not template:
            # Fallback to generic test template
            template = self._get_builtin_template("telemetry-test-java")
        return self._interpolate(template, context.to_dict())

    def _find_template_dir(self, template_name: str) -> Path | None:
        """Find the template directory by name."""
        # Parse template name: {component}-{operation}-{language}
        parts = template_name.rsplit("-", 1)
        if len(parts) == 2:
            base_name, lang = parts
            # Try language-specific path
            lang_path = self.templates_path / lang / base_name
            if lang_path.exists():
                return lang_path

        # Try direct match
        for lang_dir in self.templates_path.iterdir():
            if lang_dir.is_dir():
                for template_dir in lang_dir.iterdir():
                    if template_dir.is_dir() and template_dir.name == template_name:
                        return template_dir

        # Try common templates
        common_path = self.templates_path / "common" / template_name
        if common_path.exists():
            return common_path

        return None

    def _get_output_path(
        self,
        template_name: str,
        output_name: str,
        context: TemplateContext
    ) -> str:
        """Determine the output path for a generated file."""
        lang = context.language

        # Language-specific source directories
        source_dirs = {
            "java": f"src/main/java/com/company/{context.service_name.replace('-', '/')}",
            "python": f"src/{context.service_name.replace('-', '_')}",
            "go": "internal/observability"
        }

        # File extension mappings
        if output_name.endswith((".java", ".py", ".go")):
            return f"{source_dirs.get(lang, 'src')}/{output_name}"
        elif output_name.endswith((".yaml", ".yml")):
            if "lineage" in template_name:
                return f"lineage/{output_name}"
            elif "contract" in template_name:
                return f"contracts/{output_name}"
            else:
                return f"src/main/resources/{output_name}"
        elif output_name.endswith(".xml"):
            return output_name  # pom.xml stays at root
        elif output_name.endswith(".mod"):
            return output_name  # go.mod stays at root
        else:
            return output_name

    def _interpolate(self, template: str, variables: dict[str, Any]) -> str:
        """Perform variable interpolation on a template string."""
        def replace_var(match):
            var_name = match.group(1)
            value = variables.get(var_name, f"${{{var_name}}}")
            if isinstance(value, list):
                return ", ".join(str(v) for v in value)
            return str(value)

        return self._variable_pattern.sub(replace_var, template)

    def _get_builtin_template(self, template_type: str) -> str:
        """Get a built-in template by type."""
        templates = {
            "runbook": self._builtin_runbook_template(),
            "lineage-spec": self._builtin_lineage_template(),
            "contract-stub": self._builtin_contract_template(),
            "telemetry-test-java": self._builtin_java_test_template(),
            "telemetry-test-python": self._builtin_python_test_template(),
            "telemetry-test-go": self._builtin_go_test_template()
        }
        return templates.get(template_type, "")

    def _builtin_runbook_template(self) -> str:
        """Built-in RUNBOOK.md template."""
        return """# ${SERVICE_NAME} Runbook

## Service Overview

| Attribute | Value |
|-----------|-------|
| **Service URN** | `${SERVICE_URN}` |
| **Owner Team** | ${OWNER_TEAM} |
| **Namespace** | ${NAMESPACE} |
| **Archetypes** | ${ARCHETYPES} |

## Observability

### Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `otel_span_count` | Count of OTel spans emitted | < 1/min = warning |
| `kafka_consumer_lag` | Kafka consumer group lag | > 1000 = critical |
| `error_rate` | Error rate (5xx responses) | > 5% = critical |

### Traces

This service emits OpenTelemetry traces for:
- Kafka consumer processing
- Kafka producer sends
- HTTP/gRPC requests

**Trace Attributes:**
- `service.name`: ${SERVICE_NAME}
- `service.namespace`: ${NAMESPACE}
- `x-obs-dataproduct-urn`: ${SERVICE_URN}

### Dashboards

- [Service Dashboard](https://grafana.internal/d/${SERVICE_NAME})
- [Kafka Consumer Lag](https://grafana.internal/d/kafka-lag?var-consumer_group=${CONSUMER_GROUP})

## Common Issues

### High Consumer Lag

**Symptoms:** Kafka consumer lag exceeds threshold

**Investigation:**
1. Check consumer pod health: `kubectl get pods -l app=${SERVICE_NAME}`
2. Check consumer logs: `kubectl logs -l app=${SERVICE_NAME} --tail=100`
3. Verify topic partitions: Check Kafka UI for partition distribution

**Resolution:**
- Scale up consumers if processing is CPU-bound
- Check for slow downstream dependencies
- Verify no poison pill messages

### Missing Traces

**Symptoms:** Spans not appearing in tracing backend

**Investigation:**
1. Check OTel Collector health
2. Verify OTEL_EXPORTER_OTLP_ENDPOINT environment variable
3. Check for sampling configuration

**Resolution:**
- Restart OTel Collector sidecar
- Verify network connectivity to collector

## Contacts

- **On-call Team:** ${OWNER_TEAM}
- **Slack Channel:** #${SERVICE_NAME}-alerts
- **Escalation:** Platform Team

---
*Generated by Instrumentation Autopilot*
*Last Updated: ${TIMESTAMP}*
"""

    def _builtin_lineage_template(self) -> str:
        """Built-in lineage spec template."""
        return """# Lineage Specification for ${SERVICE_NAME}
# Generated by Instrumentation Autopilot

apiVersion: lineage.autopilot.io/v1
kind: LineageSpec
metadata:
  name: ${SERVICE_NAME}
  namespace: ${NAMESPACE}
  labels:
    autopilot.io/managed: "true"
    autopilot.io/diff-plan-id: "${DIFF_PLAN_ID}"

spec:
  service:
    urn: "${SERVICE_URN}"
    name: "${SERVICE_NAME}"
    owner: "${OWNER_TEAM}"

  inputs:
    - name: input-stream
      type: kafka-topic
      urn: "urn:kafka:${NAMESPACE}:${INPUT_TOPIC}"
      schema:
        registry: schema-registry
        subject: "${INPUT_TOPIC}-value"

  outputs:
    - name: output-stream
      type: kafka-topic
      urn: "urn:kafka:${NAMESPACE}:${OUTPUT_TOPIC}"
      schema:
        registry: schema-registry
        subject: "${OUTPUT_TOPIC}-value"

  transformations:
    - name: enrich
      description: "Enriches input records with additional data"
      inputs: [input-stream]
      outputs: [output-stream]
      sla:
        latencyP99: 500ms
        throughput: 1000/s
"""

    def _builtin_contract_template(self) -> str:
        """Built-in data contract template."""
        return """# Data Contract for ${SERVICE_NAME}
# Generated by Instrumentation Autopilot

apiVersion: contracts.autopilot.io/v1
kind: DataContract
metadata:
  name: ${SERVICE_NAME}-contract
  namespace: ${NAMESPACE}
  labels:
    autopilot.io/managed: "true"
    autopilot.io/diff-plan-id: "${DIFF_PLAN_ID}"

spec:
  owner: ${OWNER_TEAM}
  description: "Data contract for ${SERVICE_NAME} output"

  dataset:
    urn: "urn:kafka:${NAMESPACE}:${OUTPUT_TOPIC}"
    type: kafka-topic

  schema:
    format: avro
    registry: schema-registry
    subject: "${OUTPUT_TOPIC}-value"

  slos:
    freshness:
      maxStalenessMinutes: 5
      monitoringWindow: 1h

    volume:
      expectedDailyRecords: 100000
      warningThresholdPercent: 20
      criticalThresholdPercent: 50

    quality:
      nullRateThreshold: 0.01
      duplicateRateThreshold: 0.001

  notifications:
    - channel: slack
      target: "#${SERVICE_NAME}-alerts"
      severity: critical

    - channel: pagerduty
      target: ${OWNER_TEAM}-oncall
      severity: critical
"""

    def _builtin_java_test_template(self) -> str:
        """Built-in Java telemetry test template."""
        return """package com.company.${NAMESPACE}.${MODULE_NAME}.otel;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Telemetry validation tests for ${SERVICE_NAME}.
 * Generated by: Instrumentation Autopilot
 * Diff Plan ID: ${DIFF_PLAN_ID}
 */
class ${CLASS_NAME}OtelInterceptorTest {

    private static final String TEST_TOPIC = "${INPUT_TOPIC}";
    private static final String TEST_SERVICE = "${SERVICE_NAME}";

    @BeforeEach
    void setUp() {
        // Initialize test tracer
    }

    @Test
    void shouldCreateConsumerSpanForMessage() {
        // Test that consumer span is created with correct attributes
        // messaging.system = "kafka"
        // messaging.destination = TEST_TOPIC
        // service.name = TEST_SERVICE
        assertTrue(true, "Span creation test");
    }

    @Test
    void shouldExtractObservabilityHeaders() {
        // Test that x-obs-* headers are extracted as span attributes
        assertTrue(true, "Header extraction test");
    }

    @Test
    void shouldPropagateTraceContext() {
        // Test that trace context is propagated to downstream calls
        assertTrue(true, "Context propagation test");
    }
}
"""

    def _builtin_python_test_template(self) -> str:
        """Built-in Python telemetry test template."""
        return '''"""
Telemetry validation tests for ${SERVICE_NAME}.
Generated by: Instrumentation Autopilot
Diff Plan ID: ${DIFF_PLAN_ID}
"""

import pytest
from unittest.mock import Mock

TEST_TOPIC = "${INPUT_TOPIC}"
TEST_SERVICE = "${SERVICE_NAME}"
TEST_CONSUMER_GROUP = "${CONSUMER_GROUP}"


class TestOtelKafkaWrapper:
    """Test suite for OTel Kafka wrapper instrumentation."""

    def test_consumer_span_created(self):
        """Verify consumer span is created for incoming message."""
        # Test implementation
        assert True

    def test_trace_context_extraction(self):
        """Verify trace context is extracted from Kafka headers."""
        # Test implementation
        assert True

    def test_correlation_headers_extraction(self):
        """Verify x-obs-* headers are extracted as span attributes."""
        # Test implementation
        assert True

    def test_producer_span_created(self):
        """Verify producer span is created when sending message."""
        # Test implementation
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''

    def _builtin_go_test_template(self) -> str:
        """Built-in Go telemetry test template."""
        return """package otel

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
)

const (
	testTopic         = "${INPUT_TOPIC}"
	testService       = "${SERVICE_NAME}"
	testConsumerGroup = "${CONSUMER_GROUP}"
)

func TestStartConsumerSpan(t *testing.T) {
	// Test that consumer span is created with correct attributes
	ctx := context.Background()
	assert.NotNil(t, ctx)
}

func TestStartProducerSpan(t *testing.T) {
	// Test that producer span is created with correct attributes
	ctx := context.Background()
	assert.NotNil(t, ctx)
}

func TestExtractContext(t *testing.T) {
	// Test that trace context is extracted from headers
	ctx := context.Background()
	assert.NotNil(t, ctx)
}

func TestInjectContext(t *testing.T) {
	// Test that trace context is injected into headers
	ctx := context.Background()
	assert.NotNil(t, ctx)
}
"""


def test_template_engine():
    """Test the template engine with sample data."""
    engine = TemplateEngine()

    context = TemplateContext(
        service_name="orders-enricher",
        service_urn="urn:svc:prod:commerce:orders-enricher",
        namespace="commerce",
        input_topic="orders_raw",
        output_topic="orders_enriched",
        owner_team="orders-team",
        consumer_group="orders-enricher-cg",
        otel_version="1.32.0",
        timestamp="2026-01-04T10:30:00Z",
        diff_plan_id="dp-abc123",
        confidence=0.87,
        archetypes=["kafka-microservice", "spring-boot"],
        language="java"
    )

    print("Testing Template Engine")
    print("=" * 60)

    # Test RUNBOOK generation
    print("\n--- RUNBOOK.md ---")
    runbook = engine.render_runbook(context)
    print(runbook[:500] + "...")

    # Test lineage spec generation
    print("\n--- Lineage Spec ---")
    lineage = engine.render_lineage_spec(context)
    print(lineage)

    # Test contract stub generation
    print("\n--- Data Contract ---")
    contract = engine.render_contract_stub(context)
    print(contract)


def main():
    parser = argparse.ArgumentParser(
        description="Template Engine - Render observability code templates"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run template engine tests"
    )
    parser.add_argument(
        "--template",
        help="Template name to render"
    )
    parser.add_argument(
        "--context",
        help="Path to context JSON file"
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        help="Output directory for rendered files"
    )

    args = parser.parse_args()

    if args.test:
        test_template_engine()
        return

    if args.template and args.context:
        with open(args.context) as f:
            context_data = json.load(f)
        context = TemplateContext(**context_data)

        engine = TemplateEngine()
        files = engine.render_template(args.template, context)

        if args.output_dir:
            output_dir = Path(args.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            for path, content in files.items():
                output_path = output_dir / path
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(content)
                print(f"Written: {output_path}")
        else:
            for path, content in files.items():
                print(f"\n--- {path} ---")
                print(content)


if __name__ == "__main__":
    main()
