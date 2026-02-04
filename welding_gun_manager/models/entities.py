# models/entities.py
import datetime

class User:
    def __init__(self, username, password, role='user', full_name=None, email=None, 
                 created_at=None, updated_at=None, id=None):
        self.id = id
        self.username = username
        self.password = password
        self.role = role
        self.full_name = full_name or username
        self.email = email or ''
        self.created_at = created_at or datetime.datetime.now().isoformat()
        self.updated_at = updated_at

class WeldingGun:
    def __init__(self, name, type=None, model=None, serial_number=None, 
                 status='active', location=None, last_maintenance=None, 
                 notes=None, created_at=None, updated_at=None, created_by=None, id=None):
        self.id = id
        self.name = name
        self.type = type
        self.model = model
        self.serial_number = serial_number
        self.status = status
        self.location = location
        self.last_maintenance = last_maintenance
        self.notes = notes
        self.created_at = created_at or datetime.datetime.now().isoformat()
        self.updated_at = updated_at
        self.created_by = created_by

class Preset:
    def __init__(self, name, gun_type, parameters=None, description=None, 
                 created_at=None, id=None):
        self.id = id
        self.name = name
        self.gun_type = gun_type
        self.parameters = parameters or {}
        self.description = description
        self.created_at = created_at or datetime.datetime.now().isoformat()
