import tableauserverclient as TSC

# Tableau Cloud details
TABLEAU_SERVER = 'https://us-west-2b.online.tableau.com' # Reeplace with your Tableau Server/Cloud URL
TOKEN_NAME = 'PAT Token Name'
TOKEN_SECRET = 'PAT Token Secret'
SITE_ID = 'Tableau Cloud Site ID'

# Authentication object using PAT
auth = TSC.PersonalAccessTokenAuth(token_name=TOKEN_NAME, personal_access_token=TOKEN_SECRET, site_id=SITE_ID)

# Server object
server = TSC.Server(TABLEAU_SERVER, use_server_version=True)

# Connect to the server
with server.auth.sign_in(auth):
    # Create a new Project
    new_project = TSC.ProjectItem(name="Exercise 1", description="Project for Exercise 1")
    project = server.projects.create(new_project)
    
    # Create the "Emerging Artists" group
    new_group = TSC.GroupItem("Emerging Artists")
    group = server.groups.create(new_group)

    # Add all users to the "Emerging Artists" group
    all_users = list(TSC.Pager(server.users.get))
    for user in all_users:
        server.groups.add_user(group, user.id)

    # Define capabilities for data sources
    ds_capabilities = {
        TSC.Permission.Capability.Read: TSC.Permission.Mode.Allow,
        TSC.Permission.Capability.Write: TSC.Permission.Mode.Allow,
        TSC.Permission.Capability.Connect: TSC.Permission.Mode.Allow,
        TSC.Permission.Capability.ExportXml: TSC.Permission.Mode.Allow,
        TSC.Permission.Capability.SaveAs: TSC.Permission.Mode.Allow
    }

    # Publish two .hyper data sources and set permissions
    datasource_paths = ['Path/to/your/data/source.hyper', 'Path/to/your/second/data/source.hyper']
    for path in datasource_paths:
        new_datasource = TSC.DatasourceItem(project_id=project.id)
        published_datasource = server.datasources.publish(new_datasource, path, TSC.Server.PublishMode.CreateNew)
        
        # Populate and clear existing permissions
        server.datasources.populate_permissions(published_datasource)
        for permission in published_datasource.permissions:
            server.datasources.delete_permission(published_datasource, permission)

        # Set new permissions for the "Emerging Artists" group
        new_permission = TSC.PermissionsRule(grantee=group, capabilities=ds_capabilities)
        server.datasources.update_permission(published_datasource, [new_permission])

    # Set permissions for the project
    print('Setting permissions for Project: Exercise 1')
    server.projects.populate_permissions(project)
    all_permissions = project.permissions
    for permission in all_permissions:
        server.projects.delete_permission(project, permission)

    # Define capabilities for the project
    project_capabilities = {
        TSC.Permission.Capability.Read: TSC.Permission.Mode.Allow,
        TSC.Permission.Capability.Write: TSC.Permission.Mode.Allow,
    }

    # Create PermissionsRule object for the group
    new_permission = TSC.PermissionsRule(grantee=group, capabilities=project_capabilities)
    server.projects.update_permission(project, [new_permission])

    print(f"All users have been added to the 'Emerging Artists' group. Total users added: {len(all_users)}")
    print("Project 'Exercise 1' created and permissions set exclusively for 'Emerging Artists' group.")
    print("Datasources published and permissions set.")
