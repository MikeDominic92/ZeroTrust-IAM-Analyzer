# ADR 001: Documentation Structure for Crash Recovery

## Status
Accepted

## Context
The ZeroTrust IAM Analyzer project requires a robust documentation structure to support crash recovery, knowledge preservation, and project continuity. When development sessions are interrupted (system crashes, power loss, network issues), the ability to quickly resume work without losing context is critical.

Traditional project documentation often lacks the granularity needed for effective crash recovery. Generic README files and scattered notes don't provide sufficient detail for resuming complex analysis and implementation work. This is particularly important for security-focused projects like IAM analysis where maintaining continuity of thought and decision-making is essential.

### Requirements
- Enable rapid session recovery after interruptions
- Preserve architectural decisions with full context
- Track granular progress across multiple sessions
- Maintain analysis artifacts and findings
- Support both human and AI agent consumption
- Minimize knowledge loss between sessions

### Constraints
- Must integrate with existing GitHub workflow
- Should not create excessive maintenance overhead
- Must remain accessible to all team members
- Documentation must be searchable and navigable

## Decision
We will implement a `claudedocs/` directory structure with four primary subdirectories:

```
claudedocs/
├── analysis/          # Security analysis findings, IAM policy reviews
├── tasks/             # TODO.md and granular task tracking
├── decisions/         # Architecture Decision Records (ADRs)
└── progress/          # Session logs, summaries, and progress tracking
```

### Directory Purposes

**analysis/**
- Security findings and vulnerability assessments
- IAM policy analysis results
- Threat model documentation
- Risk assessments and mitigation strategies
- Zero Trust architecture evaluations

**tasks/**
- TODO.md: Master task list with status tracking
- Task breakdowns and dependencies
- Work-in-progress task details
- Task completion criteria

**decisions/**
- Architecture Decision Records (ADR format)
- Technical choices and trade-offs
- Tool selection rationale
- Methodology decisions

**progress/**
- Session logs (chronological work tracking)
- Session summaries (comprehensive session reviews)
- Milestone tracking
- Progress metrics

### File Naming Conventions
- ADRs: `###-kebab-case-title.md` (e.g., `001-documentation-structure.md`)
- Session logs: `session-log.md` (append chronologically)
- Session summaries: `session-N-summary.md` (e.g., `session-1-summary.md`)
- Analysis artifacts: Descriptive names reflecting content

## Alternatives Considered

### Alternative 1: Flat Documentation Directory
**Approach**: Single `docs/` directory with all documentation files at the root level.

**Pros**:
- Simpler initial structure
- Easier to browse in file explorers
- No need to decide on categorization

**Cons**:
- Becomes cluttered with >10 files
- Difficult to locate specific document types
- No clear organization for different concerns
- Scales poorly as project grows

**Rejection Reason**: Doesn't support rapid crash recovery due to poor organization.

### Alternative 2: Wiki-Based Documentation
**Approach**: Use GitHub Wiki or external wiki platform for all documentation.

**Pros**:
- Rich formatting options
- Built-in search and navigation
- Separate from code repository

**Cons**:
- Not version-controlled with code
- Additional tool/platform dependency
- Harder to maintain locally
- Requires internet access for full functionality
- Complicates offline work

**Rejection Reason**: Lacks tight integration with development workflow and offline accessibility.

### Alternative 3: External Documentation Platform
**Approach**: Use Notion, Confluence, or similar tool for project documentation.

**Pros**:
- Advanced formatting and collaboration features
- Better UI for non-technical stakeholders
- Built-in templates and workflows

**Cons**:
- External dependency and potential cost
- Data not co-located with code
- Export/backup complexity
- Requires separate access management
- Complicates CI/CD integration

**Rejection Reason**: Introduces unnecessary external dependencies and separates documentation from codebase.

### Alternative 4: Code Comments Only
**Approach**: Document decisions and progress solely through code comments and commit messages.

**Pros**:
- Documentation co-located with code
- No separate files to maintain
- Natural fit for implementation details

**Cons**:
- Poor discoverability
- Difficult to get high-level overview
- Doesn't support non-code artifacts
- Hard to track cross-cutting concerns
- Inadequate for architectural decisions

**Rejection Reason**: Insufficient for crash recovery and architectural decision tracking.

## Consequences

### Positive Consequences
- [+] **Rapid Session Recovery**: Clear structure enables quick location of relevant context after interruptions
- [+] **Knowledge Preservation**: Explicit documentation of decisions, findings, and progress prevents knowledge loss
- [+] **Project Continuity**: New team members or AI agents can onboard quickly using structured documentation
- [+] **Searchability**: Organized structure improves discoverability of specific information
- [+] **Version Control**: All documentation tracked in Git alongside code changes
- [+] **Offline Access**: Full documentation available without external dependencies
- [+] **Low Overhead**: Markdown-based documentation requires minimal tooling
- [+] **Scalability**: Structure supports project growth without reorganization

### Negative Consequences
- [!] **Initial Setup Time**: Requires upfront effort to create directory structure and initial documents
- [!] **Discipline Required**: Team must maintain documentation consistently for benefits to materialize
- [!] **Potential Duplication**: Risk of information duplication between README.md and claudedocs/ files
- [!] **Context Switching**: Developers must switch between code and documentation files
- [!] **Maintenance Burden**: Documentation can become stale if not actively maintained

### Mitigation Strategies
- **For Maintenance Burden**: Implement commit strategy requiring documentation updates with code changes (see ADR 002)
- **For Duplication Risk**: Establish clear boundaries (README.md for overview, claudedocs/ for details)
- **For Discipline**: Make documentation updates part of definition of done for all tasks
- **For Context Switching**: Use IDE plugins and shortcuts to navigate between code and docs efficiently

### Risks
- **Risk**: Documentation becomes outdated as project evolves
  - **Mitigation**: Link documentation updates to commit strategy (ADR 002)
  - **Severity**: Medium

- **Risk**: Structure too rigid for unforeseen documentation needs
  - **Mitigation**: Allow new subdirectories as needed, document in future ADRs
  - **Severity**: Low

- **Risk**: Team members bypass documentation structure
  - **Mitigation**: Code review process includes documentation verification
  - **Severity**: Medium

## Notes
- This ADR establishes the foundation for crash recovery strategy
- Commit strategy (ADR 002) builds on this structure
- Directory structure may be extended in future ADRs if new needs emerge
- All documentation uses Markdown format for consistency and tooling compatibility

## References
- Architecture Decision Records (ADR) format: https://adr.github.io/
- Zero Trust Architecture (NIST SP 800-207)
- Project README.md for high-level overview
