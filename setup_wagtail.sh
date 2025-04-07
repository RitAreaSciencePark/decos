#!/bin/bash

# Set environment variables
DB_CONTAINER="decos_db"
WEBAPP_CONTAINER="decos_webapp"
DJANGO_DIR="/app/django/decos_webapp"
SUPERUSER_NAME="admin"
SUPERUSER_EMAIL="admin@example.com"
SUPERUSER_PASSWORD="admin"
DJANGO_DIR="/app/django/decos_webapp"

# Prompt for hostname input
read -p "Enter the hostname for Wagtail (e.g., easydmp.localhost): " WAGTAIL_HOSTNAME

# Python script to be run directly
PYTHON_SCRIPT="
from django.contrib.auth import get_user_model
from wagtail.models import Page, Site, PageViewRestriction
from home.models import HomePage, SamplePage, EditSamplePage, SampleListPage, ResultsListPage, DMPPage, InstrumentsPage, ResultsPage, PipelinesPage, ExperimentMetadataReportPage

SUPERUSER_NAME = '$SUPERUSER_NAME'
SUPERUSER_EMAIL = '$SUPERUSER_EMAIL'
SUPERUSER_PASSWORD = '$SUPERUSER_PASSWORD'

User = get_user_model()
if not User.objects.filter(username=SUPERUSER_NAME).exists():
    User.objects.create_superuser(SUPERUSER_NAME, SUPERUSER_EMAIL, SUPERUSER_PASSWORD)
    print('✅ Superuser created successfully!')
else:
    print('✅ Superuser already exists!')

# Step 1: Delete the Root Page if it exists
root_nodes = Page.get_root_nodes()
if root_nodes:
    print('⚠️ Root page found! Deleting...')
    root_nodes[0].delete()
    print('✅ Root page deleted!')

# Step 2: Delete the Wagtail Site if it exists
if Site.objects.exists():
    print('⚠️ Wagtail site found! Deleting...')
    Site.objects.all().delete()
    print('✅ Wagtail site deleted!')

# Step 3: Create HomePage as the new Root Page
print('🚀 Creating HomePage as the ROOT page...')
home_page = HomePage(
    title='Home',
    slug='home',
    show_in_menus=True,
    intro='Welcome to EasyDMP!'
)
home_page = HomePage.add_root(instance=home_page)  # ✅ Create as ROOT
home_page.save_revision().publish()
print('✅ HomePage created as the new ROOT page!')

# Step 4: Create a new Wagtail Site with HomePage as Root
site = Site.objects.create(
    hostname='$WAGTAIL_HOSTNAME',
    port=8080,
    site_name='EasyDMP',
    root_page=home_page,
    is_default_site=True
)
print(f'✅ New site created: {site.hostname}:{site.port} with HomePage as root!')

# Step 5: Create Private Pages under HomePage
def add_private_menu_page(page_class, title, slug, parent_page, has_thank_you=False, in_menu=True):
    if not page_class.objects.exists():
        page_data = {
            'title': title,
            'slug': slug,
            'show_in_menus': in_menu
        }
        if has_thank_you:
            page_data['thankyou_page_title'] = 'Thank you!'  # ✅ Only added when needed
        page = page_class(**page_data)
        parent_page.add_child(instance=page)
        page.save_revision().publish()
        PageViewRestriction.objects.create(page=page, restriction_type='login')
        print(f'✅ {title} Page created, set to private, and added under {parent_page.title}!')

# Create private & in-menu pages under HomePage
add_private_menu_page(SampleListPage, 'Samples', 'samples', home_page)
add_private_menu_page(ResultsPage, 'Add Result', 'add-result', home_page, has_thank_you=True)
add_private_menu_page(ResultsListPage, 'Results', 'results', home_page)
add_private_menu_page(DMPPage, 'DMP Information', 'dmp', home_page, has_thank_you=True)
add_private_menu_page(InstrumentsPage, 'Instruments', 'instruments', home_page, has_thank_you=True)
add_private_menu_page(SamplePage, 'Add Sample Page', 'add-sample-page', home_page, has_thank_you=True)
add_private_menu_page(EditSamplePage, 'Edit Sample Page', 'edit-sample-entry', home_page, in_menu=False)
add_private_menu_page(PipelinesPage, 'Pipelines', 'pipelines', home_page, in_menu=False)

# Get ResultsListPage (which is now created) for ExperimentMetadataReportPage
results_list_page = ResultsListPage.objects.first()
if results_list_page:
    add_private_menu_page(ExperimentMetadataReportPage, 'Experiment Metadata', 'dmp', results_list_page)
else:
    print('⚠️ ResultsListPage not found! ExperimentMetadataReportPage cannot be created.')
"

# Write the hostname into dev.py
SETTINGS_FILE="/app/django/decos_webapp/decos_webapp/settings/dev.py"
docker exec -i "$WEBAPP_CONTAINER" /bin/sh -c "echo 'WAGTAILADMIN_BASE_URL = \"http://$WAGTAIL_HOSTNAME:8080\"' >> $SETTINGS_FILE"

# Feed the Python script directly to the container's Python shell
echo "$PYTHON_SCRIPT" | docker exec -w "$DJANGO_DIR" -i "$WEBAPP_CONTAINER" python3 manage.py shell

echo "✅ Wagtail setup completed!"
