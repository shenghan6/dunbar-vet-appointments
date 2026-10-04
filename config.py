# Configuration file for Dunbar Vet Appointment System
import os

class Config:
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///vet.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
