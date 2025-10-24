# ADR 002: Commit After Every Task for Crash Recovery

## Status
Accepted

## Context
The ZeroTrust IAM Analyzer project requires a robust crash recovery mechanism to handle session interruptions without significant progress loss. Traditional batched commit strategies (committing multiple completed tasks at once) create risk windows where work can be lost due to system crashes, power failures, or network issues.

Security analysis and IAM policy review work is inherently complex and time-consuming. Individual tasks may take 30-60 minutes to complete. Losing even one task's worth of progress can be costly, particularly when it involves analysis findings, security assessments, or architectural decisions that are difficult to recreate from memory.

### Requirements
- Minimize work loss during session interruptions
- Enable granular rollback to specific task completions
- Maintain clear correlation between tasks and commits
- Support progress tracking across multiple sessions
- Integrate seamlessly with TODO.md task tracking
- Provide meaningful commit history for auditing

### Constraints
- Must not create excessive commit noise in repository history
- Commit messages must remain informative and professional
- Should integrate with existing GitHub workflow
- Must support automated progress tracking
- Should not significantly slow down development velocity

## Decision
We will implement a **commit-after-every-task** strategy with the following rules:

### Core Rules

1. **Mandatory Task Completion Commits**
   - Every completed task in TODO.md triggers a commit
   - Commit occurs immediately after task verification
   - No batching of multiple completed tasks

2. **Commit Message Format**
   ```
   [Task] Brief task description

   - Detailed change 1
   - Detailed change 2
   - Updated TODO.md to mark task as complete

   Related: TODO.md task #N
   ```

3. **Task-Documentation Coupling**
   - TODO.md updated in same commit as task completion
   - Progress tracking files updated if milestone reached
   - Documentation files included if task involves docs

4. **Atomic Commits**
   - Each commit represents one complete task
   - All files modified for task included in single commit
   - No partial task commits

5. **Progress File Updates**
   - Session log updated at session start/end
   - Session summary created at session completion
   - PROGRESS.md updated when major milestones reached

### Commit Message Examples

**Example 1: Feature Implementation**
```
[Task] Implement AWS IAM policy parser

- Created src/parsers/aws_iam_parser.py with policy parsing logic
- Added unit tests in tests/test_aws_iam_parser.py
- Updated TODO.md to mark task #3 as complete

Related: TODO.md task #3
```

**Example 2: Documentation Update**
```
[Task] Document Zero Trust principles for IAM analysis

- Created claudedocs/analysis/zero-trust-principles.md
- Added references to NIST SP 800-207
- Updated TODO.md to mark task #5 as complete

Related: TODO.md task #5
```

**Example 3: Analysis Work**
```
[Task] Analyze sample IAM policy for overprivileged access

- Created claudedocs/analysis/sample-policy-001-analysis.md
- Identified 3 high-risk permissions
- Documented remediation recommendations
- Updated TODO.md to mark task #8 as complete

Related: TODO.md task #8
```

### Integration with TODO.md
TODO.md uses status markers:
- `[ ]` - Pending
- `[~]` - In Progress
- `[x]` - Completed

**Workflow**:
1. Update task status to `[~]` when starting work
2. Complete task implementation and verification
3. Update task status to `[x]` in TODO.md
4. Commit all changes with "[Task]" prefix
5. Move to next task

### Integration with PROGRESS.md
PROGRESS.md tracks:
- Overall project completion percentage
- Completed vs remaining tasks
- Session summaries

**Update Triggers**:
- Session start: Note session number and goals
- Session end: Update completion metrics and summary
- Milestone completion: Document achievement

## Alternatives Considered

### Alternative 1: Batched Commits (Multiple Tasks)
**Approach**: Commit after completing 3-5 tasks or at end of work session.

**Pros**:
- Cleaner commit history with fewer commits
- Reduced frequency of commit operations
- More substantial changes per commit

**Cons**:
- Higher risk of work loss on crash (could lose 2-4 hours of work)
- Difficult to rollback to specific task completion
- Harder to correlate tasks with commits
- Poor crash recovery characteristics

**Rejection Reason**: Unacceptable risk of significant work loss during interruptions.

### Alternative 2: Autosave Without Commits
**Approach**: Use IDE autosave or file watchers to save changes without committing.

**Pros**:
- No manual commit overhead
- Very frequent saves (every few seconds)
- No commit history noise

**Cons**:
- No version history for intermediate states
- Can't rollback to specific task completions
- Doesn't integrate with Git workflow
- No correlation between tasks and saved states
- Autosaved state may be inconsistent or broken

**Rejection Reason**: Doesn't provide version control benefits or task correlation.

### Alternative 3: Feature Branch Per Task
**Approach**: Create separate feature branch for each task, merge when complete.

**Pros**:
- Clean isolation between tasks
- Easy to abandon failed approaches
- Clear task boundaries in Git history

**Cons**:
- Excessive branch management overhead
- Frequent merge operations
- Branch context switching overhead
- Overkill for small tasks
- Complicates linear progress tracking

**Rejection Reason**: Too much overhead for granular task-based workflow.

### Alternative 4: Stacked Commits with Squash on Merge
**Approach**: Create many small commits, squash them when merging to main.

**Pros**:
- Clean main branch history
- Granular commits during development
- Can preserve or discard intermediate commits

**Cons**:
- Loses granular history after squash
- Doesn't support post-merge rollback to specific tasks
- Extra merge ceremony for solo development
- Complicates progress tracking across sessions

**Rejection Reason**: Loses crash recovery benefit after squash operations.

### Alternative 5: Hourly Time-Based Commits
**Approach**: Commit work-in-progress every hour regardless of task completion.

**Pros**:
- Regular backup intervals
- No need to wait for task completion
- Predictable commit frequency

**Cons**:
- Commits may contain incomplete or broken work
- No correlation with logical task boundaries
- May commit in middle of complex refactoring
- Commit messages less meaningful
- Can't guarantee working state at each commit

**Rejection Reason**: Commits may not represent coherent, working states.

## Consequences

### Positive Consequences
- [+] **Minimal Work Loss**: Maximum 1 task worth of work lost on crash (typically <1 hour)
- [+] **Granular Rollback**: Can rollback to any completed task state
- [+] **Clear History**: Each commit represents one logical unit of work
- [+] **Progress Tracking**: Commits provide automatic progress timeline
- [+] **Audit Trail**: Clear correlation between tasks and implementation
- [+] **Session Resumption**: Easy to identify last completed task and resume
- [+] **Confidence**: Developers can work boldly knowing progress is preserved
- [+] **Documentation Sync**: Forces documentation updates with code changes

### Negative Consequences
- [!] **Commit Frequency**: More commits than typical development workflows
- [!] **Discipline Required**: Must remember to commit after every task
- [!] **Commit Message Overhead**: More commit messages to write
- [!] **Git Log Verbosity**: Git log contains many task-level commits
- [!] **Potential for Tiny Commits**: Very small tasks create small commits

### Mitigation Strategies
- **For Commit Frequency**: Emphasize that commit frequency is intentional for crash recovery
- **For Discipline**: Include commit step in task completion checklist
- **For Commit Messages**: Use standardized template to reduce writing overhead
- **For Git Log Verbosity**: Use `git log --oneline` for concise view, full messages available when needed
- **For Tiny Commits**: Acceptable trade-off for crash recovery benefits

### Risks
- **Risk**: Developers forget to commit after tasks
  - **Mitigation**: TODO.md workflow includes commit step; code review checks for commit-task correlation
  - **Severity**: Low

- **Risk**: Commit messages become less informative over time
  - **Mitigation**: Commit message template and examples provided; enforce in code review
  - **Severity**: Low

- **Risk**: Repository history becomes cluttered
  - **Mitigation**: Use Git tools and filters; emphasize that verbose history is intentional
  - **Severity**: Very Low

- **Risk**: Commits made before proper testing
  - **Mitigation**: Task definition includes verification criteria; only commit after verification
  - **Severity**: Medium

## Workflow Integration

### Task Execution Workflow
1. Select task from TODO.md
2. Update status to `[~]` (In Progress)
3. (Optional) Commit TODO.md update with "[WIP] Starting task #N"
4. Implement task
5. Verify task completion (tests pass, functionality works)
6. Update status to `[x]` (Completed) in TODO.md
7. **Commit all changes with "[Task]" prefix**
8. Move to next task

### Session Workflow
1. **Session Start**:
   - Run `git status` and `git branch` to verify clean state
   - Update claudedocs/progress/session-log.md with session start
   - Review TODO.md for current priorities

2. **During Session**:
   - Work on tasks following task execution workflow
   - Commit after each completed task

3. **Session End**:
   - Commit any in-progress work with "[WIP]" prefix
   - Update claudedocs/progress/session-log.md with session summary
   - Create claudedocs/progress/session-N-summary.md if significant work completed
   - Update PROGRESS.md if milestones reached
   - Final commit with "[Session End]" prefix

### Emergency Interrupt Recovery
1. Check `git log --oneline -10` to see recent commits
2. Review TODO.md to identify last completed task
3. Read session-log.md to understand session context
4. Resume from next pending task

## Notes
- This strategy prioritizes crash recovery over commit history aesthetics
- Commit frequency is intentional and should not be reduced
- Commit messages must remain professional and informative
- Strategy may be adjusted based on team feedback after 2-4 weeks of usage
- Solo development context allows for more aggressive commit frequency

## References
- ADR 001: Documentation Structure (establishes TODO.md and progress tracking)
- GitHub Flow: https://guides.github.com/introduction/flow/
- Conventional Commits: https://www.conventionalcommits.org/ (inspiration for message format)
