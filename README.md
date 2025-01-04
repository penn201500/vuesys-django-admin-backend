# VueSys - Admin Dashboard Backend

## Overview
This project is for VueSys admin dashboard, built with Django and Django REST Framework. It provides API for user management, authentication, role-based access control, and comprehensive audit logging. Featuring secure token handling, HTTPS support, and activity tracking.

Frontend: [VueSys - Admin Dashboard Frontend](https://github.com/penn201500/vuesys-vue3-admin-frontend)

## Features
- 🔐 Authentication System
  - JWT-based token authentication via HttpOnly cookies
  - Secure token refresh mechanism
  - Access and refresh token rotation
  - Session management
  - CSRF protection
  - HTTPS/SSL support
  - Rate limiting
  - Security headers configuration
- 👥 User Management
  - User CRUD operations
  - Profile management
  - Avatar handling
  - Password management
- 🔑 Role-Based Access Control
  - Role management
  - Permission system
  - Menu access control
- 📝 Comprehensive Audit Logging
  - Detailed action tracking with timestamps
  - User activity monitoring
  - [ ] System changes logging
  - IP address tracking
  - Request/response details
  - Success/failure status
  - Searchable audit history
  - [ ] Exportable audit reports
- 📊 Data Handling
  - Server-side pagination
  - Dynamic sorting
  - Filtered searches
  - Customizable page sizes
- 🌐 Internationalization
  - Multi-language support (locales files not finished yet)
  - URL-based language switching
- 🔒 Security Features
  - Rate limiting
  - Token blacklisting
  - Secure cookie handling

## Tech Stack
- **Django** - Web framework
- **Django REST Framework** - API framework
- **MySQL** - Database
- [ ] **Redis** - Caching (not finished yet)
- **Simple JWT** - JWT authentication
- **PyMySQL** - MySQL database adapter

## Prerequisites
- Python 3.12+
- MySQL 8.0+
- Django 5.1
- pip
- anaconda

## Installation

1. Clone the repository
```bash
git clone https://github.com/penn201500/vuesys-django-admin-backend.git
cd vuesys-django-admin-backend
```

2. Create and activate virtual environment
```bash
conda create -n vuesys python=3.12.2
conda activate vuesys
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment variables
Create a `.env` file in the root directory:
```env
DEBUG=True
DJANGO_SECRET_KEY=your-secret-key
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306
ALLOWED_HOSTS=localhost,127.0.0.1

CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

RATE_LIMIT_LOGIN=10/m
RATE_LIMIT_REFRESH=3/m
RATE_LIMIT_CSRF=2/m
```

5. Run migrations
```bash
python manage.py migrate
```

6. Create superuser
```bash
python manage.py createsuperuser
```

7. Insert records for testing
```bash
# sys_menu.sql
INSERT INTO vuesys.sys_menu (id, name, icon, parent_id, order_num, path, component, perms, create_time, update_time, remark, deleted_at, status) VALUES (1, 'System Management', 'system', 0, 0, '/settings', '', '', '2024-07-04 00:00:00.000000', '2024-12-30 17:30:55.882450', 'System Management Directory test', null, 1);
INSERT INTO vuesys.sys_menu (id, name, icon, parent_id, order_num, path, component, perms, create_time, update_time, remark, deleted_at, status) VALUES (2, 'Business Management', 'monitor', 0, 1, '/bizm', '', '', '2024-07-04 00:00:00.000000', '2024-12-30 17:30:42.555547', 'Business Management Directory', null, 1);
INSERT INTO vuesys.sys_menu (id, name, icon, parent_id, order_num, path, component, perms, create_time, update_time, remark, deleted_at, status) VALUES (3, 'User Management', 'user', 1, 1, '/settings/user', 'settings/user/UserManagement', '', '2024-07-04 00:00:00.000000', '2024-07-04 00:00:00.000000', 'User Management Menu', null, 1);
INSERT INTO vuesys.sys_menu (id, name, icon, parent_id, order_num, path, component, perms, create_time, update_time, remark, deleted_at, status) VALUES (4, 'Role Management', 'grid', 1, 3, '/settings/role', 'settings/role/RoleManagement', '', '2024-07-04 00:00:00.000000', '2024-07-04 00:00:00.000000', 'Role Management Menu', null, 1);
INSERT INTO vuesys.sys_menu (id, name, icon, parent_id, order_num, path, component, perms, create_time, update_time, remark, deleted_at, status) VALUES (5, 'Menu Management', 'menus', 1, 2, '/settings/menu', 'settings/menu/MenuManagement', '', '2024-07-04 00:00:00.000000', '2024-12-30 17:31:46.652890', 'Menu Management Menu', null, 1);
INSERT INTO vuesys.sys_menu (id, name, icon, parent_id, order_num, path, component, perms, create_time, update_time, remark, deleted_at, status) VALUES (6, 'Department Management', 'tree', 2, 2, '/bizm/department', 'bizm/DepartmentView', '', '2024-07-04 00:00:00.000000', '2024-07-04 00:00:00.000000', 'Department Management Menu', null, 1);
INSERT INTO vuesys.sys_menu (id, name, icon, parent_id, order_num, path, component, perms, create_time, update_time, remark, deleted_at, status) VALUES (7, 'Position Management', 'post', 2, 0, '/bizm/post', 'bizm/PostView', '', '2024-07-04 00:00:00.000000', '2024-12-30 22:58:38.640239', 'Position Management Menu', null, 0);
INSERT INTO vuesys.sys_menu (id, name, icon, parent_id, order_num, path, component, perms, create_time, update_time, remark, deleted_at, status) VALUES (16, 'Audit Log', 'clock', 1, 4, '/audit/logs', 'settings/audit/AuditLog', null, '2025-01-02 02:29:39.000000', '2025-01-01 18:30:06.215937', 'Audit Log Menu', null, 1);


# sys_user.sql
INSERT INTO vuesys.sys_user (id, username, password, avatar, email, phone, status, create_time, update_time, comment, date_joined, first_name, is_staff, is_superuser, last_login, last_name, deleted_at) VALUES (1, 'admin', 'pbkdf2_sha256$870000$wRvkFBpQn0Z9d4ayqJTC54$Zf9u93zq0Z8Yi29Vla6a6cDH3LrGQI4/4T409q3GnRs=', '/media/avatars/avatar_1_1735296305.jpeg', '123@123.com', '11111111111', 1, '2024-08-08 00:00:00.000000', '2024-08-08 00:00:00.000000', 'test a very long sentence with many words so that it can not displayed in only one line', '2024-11-06 13:35:39.311139', '', 0, 0, '2025-01-03 12:26:55.353504', '', null);
INSERT INTO vuesys.sys_user (id, username, password, avatar, email, phone, status, create_time, update_time, comment, date_joined, first_name, is_staff, is_superuser, last_login, last_name, deleted_at) VALUES (3, 'test3', 'pbkdf2_sha256$870000$Y4JfGYDJNlDvtcQgHIcjU9$lsNrp+5iB3+8AOQOVDpaN2wG1lQSPj2l7qWSzn2L7xo=', '', '123@123.com', '11111111111', 1, '2024-08-08 00:00:00.000000', '2024-08-14 00:00:00.000000', 'test', '2024-11-06 13:35:39.311139', '', 0, 0, null, '', null);
INSERT INTO vuesys.sys_user (id, username, password, avatar, email, phone, status, create_time, update_time, comment, date_joined, first_name, is_staff, is_superuser, last_login, last_name, deleted_at) VALUES (8, 'test8', 'pbkdf2_sha256$870000$Y4JfGYDJNlDvtcQgHIcjU9$lsNrp+5iB3+8AOQOVDpaN2wG1lQSPj2l7qWSzn2L7xo=', '', null, null, 1, null, null, null, '2024-11-06 13:35:39.311139', '', 0, 0, '2024-12-29 14:11:55.670619', '', null);
INSERT INTO vuesys.sys_user (id, username, password, avatar, email, phone, status, create_time, update_time, comment, date_joined, first_name, is_staff, is_superuser, last_login, last_name, deleted_at) VALUES (11, 'test11', 'pbkdf2_sha256$870000$Y4JfGYDJNlDvtcQgHIcjU9$lsNrp+5iB3+8AOQOVDpaN2wG1lQSPj2l7qWSzn2L7xo=', '', null, null, 0, null, null, null, '2024-11-06 13:35:39.311139', '', 0, 0, null, '', '2024-12-29 14:07:21.215912');
INSERT INTO vuesys.sys_user (id, username, password, avatar, email, phone, status, create_time, update_time, comment, date_joined, first_name, is_staff, is_superuser, last_login, last_name, deleted_at) VALUES (17, 'test12', 'pbkdf2_sha256$870000$Y4JfGYDJNlDvtcQgHIcjU9$lsNrp+5iB3+8AOQOVDpaN2wG1lQSPj2l7qWSzn2L7xo=', '/media/avatars/avatar_1_1735295916.jpeg', '111@qq.com', '15586521012', 1, '2024-09-05 00:00:00.000000', '2024-12-26 22:33:39.211151', '555678', '2024-11-06 13:35:39.311139', '', 0, 0, null, '', null);
INSERT INTO vuesys.sys_user (id, username, password, avatar, email, phone, status, create_time, update_time, comment, date_joined, first_name, is_staff, is_superuser, last_login, last_name, deleted_at) VALUES (19, 'test14', 'pbkdf2_sha256$870000$Y4JfGYDJNlDvtcQgHIcjU9$lsNrp+5iB3+8AOQOVDpaN2wG1lQSPj2l7qWSzn2L7xo=', '', 'test@t.com', '11111111111', 1, '2024-09-05 00:00:00.000000', '2024-12-17 05:10:47.180588', 'udpate2', '2024-11-06 13:36:05.096741', '', 0, 0, '2025-01-01 13:16:28.010826', '', null);
INSERT INTO vuesys.sys_user (id, username, password, avatar, email, phone, status, create_time, update_time, comment, date_joined, first_name, is_staff, is_superuser, last_login, last_name, deleted_at) VALUES (21, 'test21', 'pbkdf2_sha256$870000$Y4JfGYDJNlDvtcQgHIcjU9$lsNrp+5iB3+8AOQOVDpaN2wG1lQSPj2l7qWSzn2L7xo=', '/media/avatars/avatar_1_1735295902.jpg', 'test2@t.com', null, 1, '2024-12-13 11:01:46.378012', null, null, '2024-12-13 11:01:46.378086', '', 0, 0, '2024-12-13 11:04:25.913908', '', null);
INSERT INTO vuesys.sys_user (id, username, password, avatar, email, phone, status, create_time, update_time, comment, date_joined, first_name, is_staff, is_superuser, last_login, last_name, deleted_at) VALUES (27, 'test10', 'pbkdf2_sha256$870000$DyexIbo627yVX5szWHFjfb$UiMsjVg7AEBW5GbQliwTA16ZCaUF51x5XCAvGsMy4Yk=', null, 'test10@test.com', null, 1, '2025-01-01 16:27:01.216307', null, null, '2025-01-01 16:27:01.216384', '', 0, 0, null, '', null);


# sys_role.sql
INSERT INTO vuesys.sys_role (id, name, code, create_time, update_time, remark, deleted_at, is_system, status) VALUES (1, 'Super Admin', 'admin', '2024-12-20 00:00:00.000000', '2024-12-20 00:00:00.000000', 'Has the highest privileges in the system', null, 1, 1);
INSERT INTO vuesys.sys_role (id, name, code, create_time, update_time, remark, deleted_at, is_system, status) VALUES (2, 'Common Role', 'common', '2024-12-20 00:00:00.000000', '2024-12-28 14:10:09.495252', 'This is a Common role 002', null, 0, 1);
INSERT INTO vuesys.sys_role (id, name, code, create_time, update_time, remark, deleted_at, is_system, status) VALUES (3, 'role1', 'test', '2024-12-28 21:31:55.000000', '2024-12-30 08:41:07.576029', 'Test role', null, 0, 1);


# sys_role_menu.sql
INSERT INTO vuesys.sys_role_menu (id, menu_id, role_id) VALUES (1, 1, 1);
INSERT INTO vuesys.sys_role_menu (id, menu_id, role_id) VALUES (2, 2, 1);
INSERT INTO vuesys.sys_role_menu (id, menu_id, role_id) VALUES (3, 3, 1);
INSERT INTO vuesys.sys_role_menu (id, menu_id, role_id) VALUES (4, 4, 1);
INSERT INTO vuesys.sys_role_menu (id, menu_id, role_id) VALUES (5, 5, 1);
INSERT INTO vuesys.sys_role_menu (id, menu_id, role_id) VALUES (6, 6, 1);
INSERT INTO vuesys.sys_role_menu (id, menu_id, role_id) VALUES (7, 7, 1);
INSERT INTO vuesys.sys_role_menu (id, menu_id, role_id) VALUES (8, 8, 1);
INSERT INTO vuesys.sys_role_menu (id, menu_id, role_id) VALUES (9, 2, 2);
INSERT INTO vuesys.sys_role_menu (id, menu_id, role_id) VALUES (10, 5, 2);
INSERT INTO vuesys.sys_role_menu (id, menu_id, role_id) VALUES (11, 6, 2);


# sys_user_role.sql
INSERT INTO vuesys.sys_user_role (id, role_id, user_id) VALUES (1, 1, 1);
INSERT INTO vuesys.sys_user_role (id, role_id, user_id) VALUES (2, 2, 1);
INSERT INTO vuesys.sys_user_role (id, role_id, user_id) VALUES (3, 3, 1);


# core_auditlog.sql
INSERT INTO vuesys.core_auditlog (id, username, user_email, action, module, resource_id, resource_type, detail, ip_address, timestamp, status, message, user_id) VALUES (1, 'system', null, 'CREATE', 'USER', 'None', 'USER', '{"params": {}, "request_data": {"email": "test10@test.com", "password": "Test@1234", "username": "test10"}, "response_data": {"code": 400, "message": "Username already exists"}}', '127.0.0.1', '2025-01-01 16:37:59.467095', 1, 'Successfully created USER', null);
INSERT INTO vuesys.core_auditlog (id, username, user_email, action, module, resource_id, resource_type, detail, ip_address, timestamp, status, message, user_id) VALUES (2, '', null, 'CREATE', 'USER', 'None', 'USER', '{"params": {}, "status_code": 400, "request_data": {"email": "test10@test.com", "password": "Test@1234", "username": "test10"}, "response_data": {"code": 400, "message": "Username already exists"}}', '127.0.0.1', '2025-01-01 16:55:37.669844', 1, 'Failed to create USER: Username already exists', null);
INSERT INTO vuesys.core_auditlog (id, username, user_email, action, module, resource_id, resource_type, detail, ip_address, timestamp, status, message, user_id) VALUES (3, '', null, 'CREATE', 'USER', 'None', 'USER', '{"params": {}, "status_code": 400, "request_data": {"email": "test10@t.com", "password": "Test@1234", "username": "test10"}, "response_data": {"code": 400, "message": "Username already exists"}}', '127.0.0.1', '2025-01-01 20:21:10.310516', 1, 'Failed to create USER: Username already exists', null);
INSERT INTO vuesys.core_auditlog (id, username, user_email, action, module, resource_id, resource_type, detail, ip_address, timestamp, status, message, user_id) VALUES (4, '', null, 'CREATE', 'USER', 'None', 'USER', '{"params": {}, "status_code": 400, "request_data": {"email": "test10@t.com", "password": "Test@1234", "username": "test10"}, "response_data": {"code": 400, "message": "Username already exists"}}', '127.0.0.1', '2025-01-01 20:21:11.138378', 1, 'Failed to create USER: Username already exists', null);
INSERT INTO vuesys.core_auditlog (id, username, user_email, action, module, resource_id, resource_type, detail, ip_address, timestamp, status, message, user_id) VALUES (5, '', null, 'CREATE', 'USER', 'None', 'USER', '{"params": {}, "status_code": 400, "request_data": {"email": "test10@t.com", "password": "Test@1234", "username": "test10"}, "response_data": {"code": 400, "message": "Username already exists"}}', '127.0.0.1', '2025-01-01 20:21:11.331333', 1, 'Failed to create USER: Username already exists', null);
INSERT INTO vuesys.core_auditlog (id, username, user_email, action, module, resource_id, resource_type, detail, ip_address, timestamp, status, message, user_id) VALUES (6, '', null, 'CREATE', 'USER', 'None', 'USER', '{"params": {}, "status_code": 400, "request_data": {"email": "test10@t.com", "password": "Test@1234", "username": "test10"}, "response_data": {"code": 400, "message": "Username already exists"}}', '127.0.0.1', '2025-01-01 20:21:11.467821', 1, 'Failed to create USER: Username already exists', null);
INSERT INTO vuesys.core_auditlog (id, username, user_email, action, module, resource_id, resource_type, detail, ip_address, timestamp, status, message, user_id) VALUES (7, '', null, 'CREATE', 'USER', 'None', 'USER', '{"params": {}, "status_code": 400, "request_data": {"email": "test10@t.com", "password": "Test@1234", "username": "test10"}, "response_data": {"code": 400, "message": "Username already exists"}}', '127.0.0.1', '2025-01-01 20:21:11.794294', 1, 'Failed to create USER: Username already exists', null);
INSERT INTO vuesys.core_auditlog (id, username, user_email, action, module, resource_id, resource_type, detail, ip_address, timestamp, status, message, user_id) VALUES (8, '', null, 'CREATE', 'USER', 'None', 'USER', '{"params": {}, "status_code": 400, "request_data": {"email": "test10@t.com", "password": "Test@1234", "username": "test10"}, "response_data": {"code": 400, "message": "Username already exists"}}', '127.0.0.1', '2025-01-01 20:21:11.970864', 1, 'Failed to create USER: Username already exists', null);
INSERT INTO vuesys.core_auditlog (id, username, user_email, action, module, resource_id, resource_type, detail, ip_address, timestamp, status, message, user_id) VALUES (9, '', null, 'CREATE', 'USER', 'None', 'USER', '{"params": {}, "status_code": 400, "request_data": {"email": "test10@t.com", "password": "Test@1234", "username": "test10"}, "response_data": {"code": 400, "message": "Username already exists"}}', '127.0.0.1', '2025-01-01 20:21:12.240538', 1, 'Failed to create USER: Username already exists', null);
INSERT INTO vuesys.core_auditlog (id, username, user_email, action, module, resource_id, resource_type, detail, ip_address, timestamp, status, message, user_id) VALUES (10, '', null, 'CREATE', 'USER', 'None', 'USER', '{"params": {}, "status_code": 400, "request_data": {"email": "test10@t.com", "password": "Test@1234", "username": "test10"}, "response_data": {"code": 400, "message": "Username already exists"}}', '127.0.0.1', '2025-01-01 20:21:12.392809', 1, 'Failed to create USER: Username already exists', null);
INSERT INTO vuesys.core_auditlog (id, username, user_email, action, module, resource_id, resource_type, detail, ip_address, timestamp, status, message, user_id) VALUES (11, '', null, 'CREATE', 'USER', 'None', 'USER', '{"params": {}, "status_code": 400, "request_data": {"email": "test10@t.com", "password": "Test@1234", "username": "test10"}, "response_data": {"code": 400, "message": "Username already exists"}}', '127.0.0.1', '2025-01-01 20:21:12.542894', 1, 'Failed to create USER: Username already exists', null);
INSERT INTO vuesys.core_auditlog (id, username, user_email, action, module, resource_id, resource_type, detail, ip_address, timestamp, status, message, user_id) VALUES (12, '', null, 'CREATE', 'USER', 'None', 'USER', '{"params": {}, "status_code": 400, "request_data": {"email": "test10@t.com", "password": "Test@1234", "username": "test10"}, "response_data": {"code": 400, "message": "Username already exists"}}', '127.0.0.1', '2025-01-01 20:21:12.688729', 1, 'Failed to create USER: Username already exists', null);
INSERT INTO vuesys.core_auditlog (id, username, user_email, action, module, resource_id, resource_type, detail, ip_address, timestamp, status, message, user_id) VALUES (13, '', null, 'CREATE', 'USER', 'None', 'USER', '{"params": {}, "status_code": 429, "request_data": {"email": "test10@t.com", "password": "Test@1234", "username": "test10"}, "response_data": {"code": 429, "message": "Too many requests, please try again later."}}', '127.0.0.1', '2025-01-01 20:21:12.850088', 1, 'Failed to create USER: Too many requests, please try again later.', null);
INSERT INTO vuesys.core_auditlog (id, username, user_email, action, module, resource_id, resource_type, detail, ip_address, timestamp, status, message, user_id) VALUES (14, '', null, 'CREATE', 'USER', 'None', 'USER', '{"params": {}, "status_code": 429, "request_data": {"email": "test10@t.com", "password": "Test@1234", "username": "test10"}, "response_data": {"code": 429, "message": "Too many requests, please try again later."}}', '127.0.0.1', '2025-01-01 20:21:13.066208', 1, 'Failed to create USER: Too many requests, please try again later.', null);
INSERT INTO vuesys.core_auditlog (id, username, user_email, action, module, resource_id, resource_type, detail, ip_address, timestamp, status, message, user_id) VALUES (15, '', null, 'CREATE', 'USER', 'None', 'USER', '{"params": {}, "status_code": 429, "request_data": {"email": "test10@t.com", "password": "Test@1234", "username": "test10"}, "response_data": {"code": 429, "message": "Too many requests, please try again later."}}', '127.0.0.1', '2025-01-01 20:21:14.307508', 1, 'Failed to create USER: Too many requests, please try again later.', null);
INSERT INTO vuesys.core_auditlog (id, username, user_email, action, module, resource_id, resource_type, detail, ip_address, timestamp, status, message, user_id) VALUES (16, '', null, 'CREATE', 'USER', 'None', 'USER', '{"params": {}, "status_code": 429, "request_data": {"email": "test10@t.com", "password": "Test@1234", "username": "test10"}, "response_data": {"code": 429, "message": "Too many requests, please try again later."}}', '127.0.0.1', '2025-01-01 20:21:14.460564', 1, 'Failed to create USER: Too many requests, please try again later.', null);
INSERT INTO vuesys.core_auditlog (id, username, user_email, action, module, resource_id, resource_type, detail, ip_address, timestamp, status, message, user_id) VALUES (17, '', null, 'CREATE', 'USER', 'None', 'USER', '{"params": {}, "status_code": 429, "request_data": {"email": "test10@t.com", "password": "Test@1234", "username": "test10"}, "response_data": {"code": 429, "message": "Too many requests, please try again later."}}', '127.0.0.1', '2025-01-01 20:21:14.606622', 1, 'Failed to create USER: Too many requests, please try again later.', null);
INSERT INTO vuesys.core_auditlog (id, username, user_email, action, module, resource_id, resource_type, detail, ip_address, timestamp, status, message, user_id) VALUES (18, '', null, 'CREATE', 'USER', 'None', 'USER', '{"params": {}, "status_code": 429, "request_data": {"email": "test10@t.com", "password": "Test@1234", "username": "test10"}, "response_data": {"code": 429, "message": "Too many requests, please try again later."}}', '127.0.0.1', '2025-01-01 20:21:14.750308', 1, 'Failed to create USER: Too many requests, please try again later.', null);
INSERT INTO vuesys.core_auditlog (id, username, user_email, action, module, resource_id, resource_type, detail, ip_address, timestamp, status, message, user_id) VALUES (19, '', null, 'CREATE', 'USER', 'None', 'USER', '{"params": {}, "status_code": 429, "request_data": {"email": "test10@t.com", "password": "Test@1234", "username": "test10"}, "response_data": {"code": 429, "message": "Too many requests, please try again later."}}', '127.0.0.1', '2025-01-01 20:21:14.887806', 1, 'Failed to create USER: Too many requests, please try again later.', null);
INSERT INTO vuesys.core_auditlog (id, username, user_email, action, module, resource_id, resource_type, detail, ip_address, timestamp, status, message, user_id) VALUES (20, '', null, 'CREATE', 'USER', 'None', 'USER', '{"params": {}, "status_code": 429, "request_data": {"email": "test10@t.com", "password": "Test@1234", "username": "test10"}, "response_data": {"code": 429, "message": "Too many requests, please try again later."}}', '127.0.0.1', '2025-01-01 20:21:15.024686', 1, 'Failed to create USER: Too many requests, please try again later.', null);


```

8. Start development server
```bash
python manage.py runserver
```
```text
If you want to run HTTPS in your development env. Install mkcert or certbot to generate SSL files. Then run:
```
```bash
python manage.py runserver_plus --cert-file ~/tmp/localhost+2.pem --key-file ~/tmp/localhost+2-key.pem
```

## Development

### Project Structure
```
djangoProjectAdmin/
├── user/           # User management app
├── role/           # Role management app
├── menu/           # Menu management app
├── core/           # Audit logging app and logging handlers
├── settings/       # Project settings
│   ├── base.py
│   ├── development.py
│   └── production.py
└── urls.py         # Main URL configuration
```

### Creating New Apps
1. Create new Django app
```bash
python manage.py startapp new_app
```

2. Add to INSTALLED_APPS in settings
3. Create models, views, and URLs
4. Register URLs in app urls.py and main urls.py

### Database Migrations
If models are updated.

```bash
python manage.py makemigrations
python manage.py migrate
```

### Running Tests
- [ ] TODO: Add test cases.
```bash
python manage.py test
```

## API 

Key endpoints:
- `/api/user/login/` - User authentication
- `/api/user/users/` - User management
- `/api/role/roles/` - Role management
- `/api/menu/menus/` - Menu management
- `/api/audit/logs/` - Audit log


## Contributing
1. Fork the repository or open a Pull Request

## License
This project is licensed under the MIT License - see the [LICENSE](./LICENSE.md) file for details
