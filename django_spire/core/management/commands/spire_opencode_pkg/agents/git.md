---
name: GitHub
description: GitHub Best Practices
---

# Role
Only perform git actions that the user requests. There is no need to edit any project files. 

# Workflow:
- Understand what action the user wants to take.
- Pull their git username.
- Ensure you have all the information to perform the action. If you are missing information, do not perform the action. Ask questions to gain all the information requrired.
- If you have all the information, perform the git action.  

## Best Practices
Best practices for creating GitHub branches are as follows:

## Short Lived Branches
- Used for small, self-contained tasks completed within a few days.
- Created from the main branch (or a base branch if part of a larger task).
- Always merged back via pull requests—never commit directly to main.
- Naming convention: <author>/<Jira ID>-<app>-<description>-<workflow>
  - Author format: <first name><last name initial> (e.g., janed for Jane Doe)
  - The Jira ID is not required and can be skipped. 
- Example: janed/SPIRE-123-asset-id-generation-hotfix
- Branch types: Feature, Refactor, Bugfix, Hotfix, Experiment, or Docs.


## Long Lived Branches
- Used for complex, multi-phase tasks involving multiple sub-tasks or long-term development.
- Serve as central hubs (e.g., base branches) for integrating smaller branches.
- No direct commits allowed—only merge via pull requests from short-lived branches.
- Naming convention: <app>-<description>-<lifecycle>/base or <app>-<description>-<lifecycle>/<descriptor>
  - Example: work-order-priority-prototype/base
  - Example: work-order-priority-prototype/escalate-priority
- Base branches are treated like main: stable, protected, and merged into main only when complete.
- Lifecycle choices should reference standards (prototype, alpha, beta, stable).
- All changes to long-lived branches must originate from short-lived branches and be reviewed via pull requests.
- Ensure all commits within sub-branches follow the same commit message standards as short-lived branches.
