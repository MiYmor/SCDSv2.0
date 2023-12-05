from werkzeug.security import generate_password_hash

admin_data = [
        {
            'SysAdminNumber': '2020-00001-AD-0',
            'Name': 'Admin 1',
            'Email': 'admin1@example.com',
            'Password': generate_password_hash('password1'),
            'Gender': 2,
            'DateOfBirth': '1995-03-10',
            'PlaceOfBirth': 'City 3',
            'ResidentialAddress': 'City 3',
            'MobileNumber': '09123123222',
            'IsActive': True
            # Add more attributes here
            
        },
        {
            'SysAdminNumber': '2020-00002-AD-0',
            'Name': 'Admin 2',
            'Email': 'admin2@example.com',
            'Password': generate_password_hash('password2'),
            'Gender': 1,
            'DateOfBirth': '1980-09-18',
            'PlaceOfBirth': 'City 4',
            'ResidentialAddress': 'City 4',
            'MobileNumber': '09123123223',
            'IsActive': True
            # Add more attributes here
        },
        # Add more admin data as needed
    ]