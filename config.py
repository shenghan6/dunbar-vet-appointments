# Configuration file for Dunbar Vet Appointment System
import os


class BaseConfig:
    """所有环境共用的默认配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False


class DevelopmentConfig(BaseConfig):
    """开发环境"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///vet.db'


class TestingConfig(BaseConfig):
    """测试环境（内存数据库）"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(BaseConfig):
    """生产环境"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///vet.db'


# 根据 APP_ENV 环境变量选择配置
config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}

env_name = os.environ.get('APP_ENV', 'development')
Config = config_map.get(env_name, DevelopmentConfig)
