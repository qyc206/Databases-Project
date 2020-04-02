# Databases-Project
Qin Ying Chen, Erica Chou, Moira Duya
March 31, 2020
Databases

Optional Features:

Short Description: This project will have three group members working on five required features and six optional features for an app called “Finstagram”. This app will require us to allow users to share photos with either all of their followers or with a specific group. 
Because our group has three people, we have chosen these six features to add in to our app for Project 4:

Qin Ying Chen:
Manage tags: 
Current user, whom we’ll call x, selects a photo that is visible to her and proposes to tag it with username y (1) If the user is self-tagging (y == x), Finstagram adds a row to the Tag table: (x, photoID, true) (2) else if the photo is visible to y, Finstagram adds a row to the 
Tag table: (y, photoID, false) (3) else if photo is not visible to y, Finstagram doesn’t change the tag table and prints some message saying that she cannot propose this tag. 
Finstagram shows the user relevant data about photos that have proposed tags of this user (i.e. user’s username is Tag.username and acceptedTag is false.) User can choose to accept a tag (change acceptedTag to true), decline a tag (remove the tag from Tag table), or not make a decision (leave the proposed tag in the table with acceptedTag == false.)

Erica Chou:

React to a photo: Users can add comments and/or emojis to photos that are visible to them. 

Unfollow: Think about what should be done when someone is unfollowed, including some reasonable approach to tags that they posted by virtue of being a follower. Write a short summary of how you’re handling this situation. Implement it and test it.

Moira Duya:

Search by tag:Search for photos that are visible to the user and that tag some particular person (the user or someone else ) 

Search by poster:Search for photos that are visible to the user and that were posted by some particular person (the user or someone else )
