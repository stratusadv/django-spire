---
name: Template
description: Writing templates
---

# Role
The task is properly writing django templates. 

# Important
- Most templates are extended from django-spire.
- Look at other similar files to see the includes and extends needed.
- Pay attention to bootstrap breakpoints. Most breakpoints happen on md (if they are needed).
- Do go rouge and manipulate any files the user did not mention. 

# Workflow when tasked:
### Locate the correct module
- Each module inside of our template directory matches our app directory.
- Find the correct template directory that needs to be modified.

### Analyze Relevant Files
- Look around to see if the file already exists.
- Get an understanding of what is around it.
- Review the related model.py file to understand the data structure.


### Apply changes to html files
- Only apply changes if you know the specific files the user wants. 
- If you are not sure, stop and ask the user for confirmation.
- Apply the changes to the specific html files when ready.
- Do not create JS files or CSS files.
- Do not manipulate the backed python files.

### Review
- Review your html changes. Ensure the implementation is simple and follows patters.
- Mention to the user of other files that might need to be changed or updated that they didn't specify.
 