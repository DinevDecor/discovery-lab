ADR-0003
Title

Specification Before Implementation

Status

Accepted

Context

Early development of KOD alternated between architectural ideas and direct implementation.

This occasionally led to runtime structures being created before the underlying concepts had been fully defined.

Since KOD is intended to protect the integrity of the research process, its own development must follow the same discipline.

Decision

Every KOD component shall exist in two forms.

1. Specification

Defines:

purpose;
responsibilities;
inputs;
outputs;
constitutional constraints;
relationships.

Location:

Foundations/
2. Runtime

Implements the specification.

Location:

Infrastructure/python/

No runtime implementation may exist without an approved specification.

Development Lifecycle
Idea

↓

Research Session

↓

Specification

↓

Architecture Review

↓

Implementation

↓

Tests

↓

Deployment
Consequences

This keeps architecture independent from implementation.

It allows:

multiple implementations;
replacement of technologies;
long-term maintainability;
constitutional consistency.
Architectural Principle

Implementation follows architecture.

Architecture follows methodology.

Methodology follows the Constitution.

The Constitution follows the Mission.