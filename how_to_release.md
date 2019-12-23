## Release instructions

* Follow this instructions to automatically release pergola in the github repository and ``pypi``.

1. Check that tests are passing:

    ```bash
    python pergola/test/test_all.py 
    ```

2. Update ``pergola/_version.py`` with the current version (e.g. 0.2.0)

    ```bash
    __  version__ = "0.2.0"
    ```

3. Tag the version in local

    ```bash
    git tag -a 0.2.0 -m "Version 0.2.0"
    ```

4. Check that the tag is correctly updated in local

    ```bash
    git describe
    ```

5. Push to the GitHub repository:

    ```bash
    git push --follow-tags
    ```

6. Check that the version has been released in (pypi)[https://pypi.org/project/pergola/]