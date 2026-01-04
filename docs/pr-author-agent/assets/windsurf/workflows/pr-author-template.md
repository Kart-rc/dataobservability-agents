# PR Author Template Workflow

Create a new archetype template for the PR Author Agent.

## Trigger

Use this workflow when:
- Adding support for a new framework or library
- Creating templates for a new language
- Customizing existing templates for specific needs

## Prerequisites

1. Understanding of the target framework/library
2. Sample code showing desired instrumentation
3. Knowledge of OTel APIs for the language

## Steps

### Step 1: Identify Template Requirements

Determine what files the template needs to generate:

| File Type | Purpose | Example |
|-----------|---------|---------|
| Interceptor/Wrapper | Core instrumentation code | `OtelInterceptor.java` |
| Configuration | Framework config | `application-otel.yaml` |
| Dependencies | Build file additions | `pom-dependency.xml` |
| Tests | Telemetry validation | `OtelInterceptorTest.java` |

### Step 2: Create Template Directory

```bash
mkdir -p references/templates/{language}/{archetype}/
```

Example for Go gRPC:
```bash
mkdir -p references/templates/go/grpc-otel/
```

### Step 3: Create Template Files

Each file should have `.tmpl` extension and use `${VAR}` syntax:

```java
// ${CLASS_NAME}OtelInterceptor.java
package com.company.${NAMESPACE}.${MODULE_NAME}.otel;

public class ${CLASS_NAME}OtelInterceptor {
    private static final String SERVICE_NAME = "${SERVICE_NAME}";
    // ...
}
```

### Step 4: Define Variables

Document required variables in `references/variable-mapping.md`:

| Variable | Source | Example |
|----------|--------|---------|
| `${SERVICE_NAME}` | Diff Plan repo | `orders-enricher` |
| `${CLASS_NAME}` | Derived | `OrdersEnricher` |

### Step 5: Add Output Path Logic

Update `template_engine.py` to handle the new template's output paths:

```python
def _get_output_path(self, template_name, output_name, context):
    if "grpc" in template_name:
        return f"internal/grpc/{output_name}"
    # ...
```

### Step 6: Test Template Rendering

```bash
python scripts/template_engine.py \
  --template grpc-otel-go \
  --context test-context.json \
  --output-dir ./test-output
```

### Step 7: Update Documentation

1. Add template to SKILL.md template library section
2. Add archetype to Scout Agent detection (if new)
3. Update gap-templates.md

## Template Best Practices

### Variable Naming
- Use UPPER_SNAKE_CASE: `${SERVICE_NAME}`
- Be descriptive: `${CONSUMER_GROUP}` not `${CG}`

### Code Quality
- Include proper package/import statements
- Add documentation comments
- Follow language idioms

### Configurability
- Use variables for versions: `${OTEL_VERSION}`
- Don't hardcode environment-specific values

### Testing
- Include test template alongside code template
- Test renders correctly with sample context

## Example: Go Gin OTel Template

```
references/templates/go/gin-otel/
├── otel_gin_middleware.go.tmpl
├── go-mod-dependency.txt.tmpl
└── otel_gin_test.go.tmpl
```

**otel_gin_middleware.go.tmpl:**
```go
package middleware

import (
    "github.com/gin-gonic/gin"
    "go.opentelemetry.io/contrib/instrumentation/github.com/gin-gonic/gin/otelgin"
)

// OtelMiddleware configures OpenTelemetry tracing for ${SERVICE_NAME}
func OtelMiddleware() gin.HandlerFunc {
    return otelgin.Middleware("${SERVICE_NAME}")
}
```

## Output

After completing this workflow:
- New template directory created
- Template files with proper variables
- Documentation updated
- Tests passing
