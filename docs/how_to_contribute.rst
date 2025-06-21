How to contribute
=================

You can contribute in various ways, if you wish to do so:

Translating the app
-------------------

We want people around the world to use the arbeitszeitapp. To achieve this, it's crucial to translate the app into as many languages as we can. We are happy to help you with the translation process.

Contributing code
------------------

We appreciate contributions to the code! Before you start contributing, you'll need to set up your development environment. We recommend using Linux with Nix for development. The setup process is detailed in our :doc:`development_setup` guide, which covers:

* Setting up PostgreSQL databases
* Installing development dependencies
* Configuring environment variables
* Running the development server

We maintain high code quality standards through:

* Type hints and static type checking with ``mypy``
* Code formatting with ``black`` and ``isort``
* Linting with ``flake8``
* Comprehensive test coverage

You can propose changes by `forking the repository <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo>`_ and creating a pull request on GitHub.
Before submitting changes, run ``./run-checks`` to ensure your code meets our standards.


Working on Milestones
-----------------------

Milestones are our way of organizing larger work packages (>50h of work) that have been identified as important for the project. Unlike regular Issues or Pull Requests, milestones follow a formal approval process that includes an obligatory RFC (Request For Comments). This structured approach helps us plan better and ensures that all developers are aligned with the project's direction.

Milestone Lifecycle
~~~~~~~~~~~~~~~~~~~

1. RFC Candidate
    - An Issue on GitHub that has potential to become a Milestone
    - Marked with the "rfc candidate" label
    - Requires initial conceptual work and discussion
    - View `current candidates <https://github.com/ida-arbeitszeit/arbeitszeitapp/issues?q=state%3Aopen%20label%3A%22rfc%20candidate%22>`_

2. RFC (Request For Comments)
    - A detailed proposal marked with the "RFC" label
    - Must include a motivation for the change and a detailed implementation proposal
    - Sent to the programmers mailing list for visibility
    - Requires approval in an app group meeting
    - View `current RFCs <https://github.com/ida-arbeitszeit/arbeitszeitapp/issues?q=is%3Aissue%20state%3Aopen%20label%3Arfc>`_

3. Active Milestone
    - Published on GitHub after RFC approval
    - Ready for implementation
    - View `all milestones <https://github.com/ida-arbeitszeit/arbeitszeitapp/milestones>`_

Feel free to contribute to any of these stages.