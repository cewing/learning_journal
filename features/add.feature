Feature: Add Entry
    Exercise anonymous and authenticated interactions
    with the add form and view.

    Scenario: Anonymous user cannot see add entry form
        Given an anonymous user
        When I view the home page
        Then I do not see the new entry form

    Scenario: Logged in user can see add entry form
        Given an authenticated user
        When I view the home page
        Then I do see the new entry form

    Scenario: Anonymous user cannot submit add form
        Given an anonymous user
        And the title "New Post"
        And the text "This is a new post"
        When I submit the add form
        Then I am redirected to the home page
        And I do not see my new entry

    Scenario: Logged in user can submit add form
        Given an authenticated user
        And the title "New Post"
        And the text "This is a new post"
        When I submit the add form
        Then I am redirected to the home page
        And I see my new entry
