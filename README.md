## Setup
1. Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
2. Run:
   ```bash
   conda env create -f environment.yml
   conda activate st2-uni

## Design Patterns
1. MVC (Model–View–Controller) in Django
   Overview

   Our project follows the Model–View–Controller (MVC) architectural pattern, adapted through Django’s Model–Template–View (MTV) structure.
   This design separates the application logic into clear, modular components — making the system easier to maintain, test, and extend.

   Although Django officially uses the MTV terminology, the underlying principles are the same as MVC:

   Traditional MVC - Django Equivalent
   Model - Model
   View - Template
   Controller - View (in Django)

      How MVC Works in Our Project

      Model (Data Layer)
      Located in: models.py (e.g., movies/models.py, users/models.py)

      The Model defines the structure of the data and handles database interactions.
      It represents entities like:

      Movie, Genre, and List

      CustomUser and FriendRequest

      Each model contains fields, relationships, and methods that define how data behaves and interacts across the system.

      Purpose:
      Encapsulates all business logic related to database data — creation, querying, validation, and relationships.

      Controller (Logic Layer)

      Located in: views.py

      The View in Django acts as the Controller in MVC.
      It processes user requests, interacts with models, and determines what data to send to the template for rendering.

      Purpose:

      Receives and interprets HTTP requests

      Retrieves or updates data through the Models

      Selects the correct Template to render the response

      View (Presentation Layer)

      Located in: templates/

      The Template in Django corresponds to the View in MVC.
      It defines the structure and layout of the HTML pages the user sees — using Django Template Language (DTL) to dynamically display data passed by the controller.

      Purpose:

      Handles presentation and user interface logic

      Displays dynamic data from models

      Keeps business logic separate from design

         Data Flow in the MVC Pattern

         User Action:
         A user sends an HTTP request (e.g., visiting /home or sending a friend request).

         Controller (Django View):
         The view receives the request and communicates with the Model.

         Model:
         Fetches or updates the relevant data in the database.

         Controller:
         Passes the processed data to the Template.

         View (Template):
         Renders and returns a dynamic HTML response to the user.

         User → Controller (View) → Model → Controller → View (Template) → User

2. Observer Pattern (Friend Request Notifications)

   Overview
   The Observer Pattern is a behavioral design pattern that defines a one-to-many relationship between objects — when one object’s state changes, all its dependents are automatically notified.

   In this project, the pattern is applied conceptually to our friend request notification system, allowing the app to “react” when new friend requests are created without tightly coupling the backend and frontend logic.

   Implementation in FilmMate

   When a user sends a friend request, the system automatically “notifies” the recipient with a popup window that appears the next time they visit their home or profile page.

   This implementation follows the Observer pattern structure using Django’s built-in tools — models, views, and templates — without needing real-time websockets or JavaScript events.

   How It Works
      1. Subject (Event Source)

      The FriendRequest
      model acts as the subject.
      When a new record is created (FriendRequest.objects.create(...)), this event signals that the recipient should be notified.

      2. Observer (Listener)

      The home or profile view acts as the observer.
      Every time the user visits their home/profile page, the view checks for any pending friend requests targeted to the current user:

      FriendRequest.objects.filter(to_user=request.user, dismissed=False)

      3. Notification Mechanism

      If such requests exist, the template displays a popup message.
      The popup includes:

      The sender’s username and profile picture

      Buttons for Accept, Decline, and Close

      4. State Management

      Once the user interacts with the popup:

      Accept → Both users become friends (request deleted)

      Decline → Request deleted

      Close → Marks request as dismissed=True (won’t show again)

      This mimics how observers “unsubscribe” after handling an event.

3. Factory Pattern in Movie Creation

We implemented the Factory Pattern via a MovieFactory class to centralize the creation of Movie objects from external API data.

Why:

Keeps object creation logic clean and reusable.

Ensures consistent handling of genres, directors, and posters.

Makes it easy to change how movies are created without touching the seeding command.