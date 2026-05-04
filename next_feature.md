# Improvement Plan: Replace Search with Filters

## Problem Statement
Currently, when a user attempts to search for a tool using the text search bar (e.g., `/?q=new_tool&submit=Search`), the application does not filter the results and instead returns all active tools.

**Root Cause:** 
The `SearchForm` inherits from `FlaskForm`, which enforces CSRF token validation by default. Because the search form uses a `GET` request to make the results bookmarkable, the CSRF token is not included in the URL parameters. Consequently, `form.validate()` silently fails in `routes/main.py`. This causes the application to fall back to an empty search string, skipping the SQLAlchemy `.ilike()` filter entirely and returning the un-filtered tool directory.

## Proposed Solution
Per the request, we will replace the existing text-based search mechanic with a structured "Filter" mechanic. This will allow users to reliably drill down into the tool directory using specific attributes (e.g., Category, Language).

### 1. Form Updates (`forms.py`)
- **Remove** the existing `SearchForm`.
- **Create** a new `FilterForm` class.
- Explicitly disable CSRF protection for this form so that it can validate `GET` requests successfully:
  ```python
  class Meta:
      csrf = False
  ```
- Add `SelectField` elements for filtering:
  - `category_id` (e.g., Analytics, Reporting)
  - `language_id` (e.g., Python, JavaScript)
- Set validators to `Optional()` and include an empty default choice (e.g., "All Categories").

### 2. Route Updates (`routes/main.py`)
- Update the `index` view to instantiate the new `FilterForm(request.args)`.
- Dynamically populate the choices for `category_id` and `language_id` by querying the `Category` and `Language` tables.
- Modify the `_build_directory_statement` helper function to accept `category_id` and `language_id` instead of a plain text `search_term`.
- Chain SQLAlchemy `.where(Tool.category_id == category_id)` clauses if specific filters are selected.

### 3. UI Updates (`templates/index.html`)
- Replace the current search text box with a responsive layout containing the dropdown filter menus.
- Change the submit button text from "Search" to "Filter".
- Ensure the selected filter values are preserved in the dropdowns after the page reloads.

## Expected Outcome
Users will be able to refine the tool directory via dropdowns. The resulting URLs (e.g., `/?category_id=2&language_id=1&submit=Filter`) will cleanly execute database-level relational filters instead of text matching, providing a more reliable and robust discovery experience.
