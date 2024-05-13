import tableauserverclient as TSC

create_n = 150
# Updated Personal Access Token and secret
tableau_auth = TSC.PersonalAccessTokenAuth('PAT Token Name', 'PAT Token', site_id='Your Tableau Cloud Site ID')
server = TSC.Server('https://us-west-2b.online.tableau.com', use_server_version=True) #might need to replace server ID

with server.auth.sign_in(tableau_auth):
    print('Signed In OK')

    for i in range(1, create_n+1):
        print(f'Iteration: {i}')
        
        # USERS
        # Create new user with SAML authentication
        user_to_add = f'yourusername{i}@youremaildomain.com'
        print(f'Creating User: {user_to_add}')
        tableau_user = TSC.UserItem(user_to_add, 'Viewer', auth_setting='SAML')
        tableau_user = server.users.add(tableau_user)
        user_id = tableau_user.id

        # MAIN PROJECTS (Folders)
        # Create a main project for each user
        project_name = f'yourusername{i}'
        print(f'Creating Project: {project_name}')
        main_project = TSC.ProjectItem(name=project_name)
        main_project = server.projects.create(main_project)
        main_proj_id = main_project.id

        # Set permissions for the main project
        print(f'Setting permissions for Project: {project_name}')
        server.projects.populate_permissions(main_project)
        all_permissions = main_project.permissions

        # Delete all current permissions
        for permission in all_permissions:
            server.projects.delete_permission(main_project, permission)

        # Define capabilities for the main project
        capabilities = {
            TSC.Permission.Capability.Read: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.Write: TSC.Permission.Mode.Allow
        }
        
        # Create PermissionsRule object
        new_permission = TSC.PermissionsRule(grantee=TSC.UserItem.as_reference(user_id), capabilities=capabilities)
        
        # Update main project with new permissions
        server.projects.update_permission(main_project, [new_permission])

        # EXERCISE 3 FOLDER
        # Create a sub-project "Exercise 3" within the main project
        exercise_folder_name = "Exercise 3"
        print(f'Creating Sub-Project: {exercise_folder_name} within {project_name}')
        exercise_project = TSC.ProjectItem(name=exercise_folder_name, parent_id=main_proj_id)
        exercise_project = server.projects.create(exercise_project)

        # DATA SOURCES
        # Publish a .hyper file as a data source for each user
        ds_name = f'Music Production Details_yourusername{i}'
        print(f'Publishing Data Source: {ds_name}')
        new_datasource = TSC.DatasourceItem(name=ds_name, project_id=main_proj_id)
        file_path = '/Users/jzitko/Desktop/TC24 HOT Pulse/HOT Pulse Data/Music Producer/Music Production Details/Music Production Details.hyper'  # Update with the actual path to your .hyper file
        new_datasource = server.datasources.publish(new_datasource, file_path, TSC.Server.PublishMode.Overwrite)

        # Change permissions for the datasource to match the project
        print(f'Setting permissions for Data Source: {ds_name}')
        server.datasources.populate_permissions(new_datasource)
        for permission in new_datasource.permissions:
            server.datasources.delete_permission(new_datasource, permission)

        datasource_capabilities = {
            TSC.Permission.Capability.Read: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.Write: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.Connect: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.ExportXml: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.SaveAs: TSC.Permission.Mode.Allow
        }
        datasource_permission = TSC.PermissionsRule(grantee=TSC.UserItem.as_reference(user_id), capabilities=datasource_capabilities)
        server.datasources.update_permission(new_datasource, [datasource_permission])
