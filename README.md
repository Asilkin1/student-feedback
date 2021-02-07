# Project

## Overview
Allow to post anonymouse feedbacks for college class performance using emojies as a scale from Excited to Mad, in four categories:
- Professor/Instructor
- Teaching style
- Topic
- Other 

Optional text-input field will allow to elaborate student's thoughts.

## Anonymity

It's a huge concern and a challenge since we have to make sure that professor cannot identify anyone who left a feedback. However, we have 
to make sure that the same unique identifier (which we call a student code) is utilized by the same person. For now we allow each student to get their 
own student code. We provide a simple student registration form with one text-input field. We found it easier for students to memorize their unique student code, at the same time makking sure that no one assign this codes to students. Since it will brake the idea of anonimity. Hence, we want each student to use something that they will rememeber easily and at the same time will not compromise their identity.For this purpose we ask them to think about student code as a username for social media account. The only difference that no one should know it. It is basically an idea of creating an anti-social network. 

### Anti-social network

We ask each student to create their own student code which they will easily rememeber. We will make sure that this code is unique for each student. The database will store this unique student code. Even if the database is not encrypted, no one suppose to identify a physical person by student code.

#### Do we need to encrypt student codes in the database?
We attempted to use salting mechnism provided by python module called bcrypt. We found that we can generate a reversable hash for each student code. This might not be necessary, since 


