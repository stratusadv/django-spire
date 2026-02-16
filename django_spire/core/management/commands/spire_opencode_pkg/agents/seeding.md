---
name: seeding
description: Create or update django model seeding.
---

# Role
The task is properly configured seeding. It is very important to have realistic data when developing software applications.

# Skills
Load the @seeding skill.

# Workflow when tasked:

### Locate the correct module
- Each module inside of our app directory has a seeding directory.
- Each seeding directory has a seed.py and a seeder.py

### Analyze Relevant Files
- The class inside of our seeder.py is inherited from Django Model Seeder.
- It needs to link to a django model.
- Analyze the model that it is related to.

### Apply changes to seeder.py
- Apply changes to the seeder.py to have it accurately reflect the model it is related it.
- This is where the skill @seeding is very important to follow.

### Update module seed.py file
- Check the related seed.py file. Ensure we are calling our seeder.

### Update base seed.py file
- At the root of our project we have a seed.py file that is responsible for seeding our entire project.
- Check this file and ensure we are importing the seed.py we just configured.

### Review
- Review the configration changes you made to our seeding.
 