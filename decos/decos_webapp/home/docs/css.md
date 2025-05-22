# Static File Structure - DECOS Webapp Home App

This document outlines the structure of the static files directory within the DECOS Webapp Home App module. It primarily contains CSS stylesheets used for styling various forms and pages in the application.

## Root Path
```
django/decos_webapp/home/static/
```

## Directory Structure
```
django/decos_webapp/home/static
|-- css
    |-- forms
    |   |-- labdmp_page.css
    |   |-- lage_form.css
    |   |-- lame_form.css
    |
    |-- home_page.css
    |-- list_page.css
    |-- thank_you_page.css
    |-- user_data.css
```

## File Descriptions

### Forms Stylesheets
- **labdmp_page.css** - Stylesheet for the LabDMP page form.
- **lage_form.css** - Stylesheet for the LAGE form.
- **lame_form.css** - Stylesheet for the LAME form.

### Page Stylesheets
- **home_page.css** - Stylesheet for the Home Page.
- **list_page.css** - Stylesheet for the List Page.
- **thank_you_page.css** - Stylesheet for the Thank You Page.
- **user_data.css** - Stylesheet for User Data display.

## Usage
These stylesheets are intended to be linked in the respective templates within the DECOS Webapp Home App to ensure consistent styling across forms and pages.

