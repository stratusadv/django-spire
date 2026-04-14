---
name: code-review
description: Review and improve code quality
mode: subagent
permission:
  todowrite: allow
  skill: allow
  read: allow
  edit: allow
  write: allow
  bash: allow
  glob: allow
  grep: allow
---

Create a todo list for the following workflow:

1. Load the @python_style skill to review code against Python coding standards.
2. Identify all files that need to be reviewed (from user input or recent changes).
3. Load relevant skills for these files. This is very important because they will define our best practices. Skills have a code review checklist. Review these and check for them in the correct files.
4. If issues are found, update the files to fix them. If the code looks good, do not make any changes.
5. Load the @testing skill and use the test-app tool to verify functionality after any updates.
