from django.contrib.auth import get_user_model
from wagtail.models import Page, Site, PageViewRestriction
from home.models import HomePage, SamplePage, EditSamplePage, SampleListPage, ResultsListPage, DMPPage, InstrumentsPage, ResultsPage, PipelinesPage
import os
from pathlib import Path
# This is an override of getenv to check if you need to read a file (like for the secrets)



SUPERUSER_NAME = os.getenv("SUPERUSER_NAME","admin")
SUPERUSER_EMAIL = os.getenv("SUPERUSER_EMAIL","")
# Secret read
path = Path("/app/",os.getenv("SUPERUSER_PASSWORD_HOST_FILE"))
with path.open("r", encoding="utf-8") as f:
    SUPERUSER_PASSWORD = f.read().strip()

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
    intro='Welcome to Digital ECOSystem Webapp!'
)
home_page = HomePage.add_root(instance=home_page)  # ✅ Create as ROOT
home_page.save_revision().publish()
print('✅ HomePage created as the new ROOT page!')

# Step 4: Create a new Wagtail Site with HomePage as Root
site = Site.objects.create(
    hostname=os.getenv("WAGTAIL_HOSTNAME",""),
    port=os.getenv("WEB_APP_PORT","8080"),
    site_name='decos-webapp',
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
add_private_menu_page(ExperimentDMPPage, 'Add Experiment DMP', 'add-experiment-dmp', home_page, in_menu=True, has_thank_you=True)
add_private_menu_page(ExperimentDMPListPage, 'Experiment DMP List', 'experiment-dmp-list', home_page, in_menu=True)

# Get ExperimentDMPListPage (which is now created) for ExperimentDMPReportPage
experiment_dmp_list_page = ExperimentDMPListPage.objects.first()
if experiment_dmp_list_page:
    add_private_menu_page(ExperimentDMPReportPage, 'Experiment Data Management Plan', 'experiment-data-management-plan', experiment_dmp_list_page)
else:
    print('⚠️ ExperimentDMPListPage not found! ExperimentDMPReportPage cannot be created.')

# Delete default groups Editors and Moderators, and create Data_Curator and Pipelines roles
from django.contrib.auth.models import Group
# Reset groups: delete 'Editors' and 'Moderators', then create 'Data_Curator' and 'Pipelines'
for name in ["Editors", "Moderators"]:
    deleted, _ = Group.objects.filter(name=name).delete()
    if deleted:
        print(f'🗑️  Deleted group "{name}"')
    else:
        print(f'ℹ️  Group "{name}" did not exist')

for name in ("Data_Curator", "Pipelines"):
    Group.objects.get_or_create(name=name)
    print(f'✅  Ensured group "{name}" exists')
