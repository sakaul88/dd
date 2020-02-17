import os
import yaml

from orchutils import vault

offering_settings_files = ['app.yaml', 'infra.yaml', 'secret.yaml']
settings_dir = '/var/orch/settings'
if 'P2PAAS_SETTINGS_DIR' in os.environ:
    settings_dir = os.environ['P2PAAS_SETTINGS_DIR']


def get_settings(
        category=None,
        metro=None,
        offering=None,
        global_settings='global',
        category_settings='category',
        metro_settings='metro'):
    """
    Get a set of parsed settings. These settings can be generic, metro-specific or offering-specific.
    Metro-specific settings will contain the generic settings with the metro-specific values merged in. A metro typically indicates the city hosting the environment.
    Offering-specific settings work the same way but will include generic offering-specific settings as well as metro offering-specific settings.
    Priority for settings of the same name are (from lowest to highest)
    generic -> category -> metro -> offering
    Args:
        category: The category of the environment, for example, production, stage, etc. (Optional, needed to process a metro)
        metro: The name of the metro to pull settings for (Optional, needed to process an offering)
        offering: The name of the offering to pull settings for (Optional)
        global_settings: Prefix for global settings. If value is "global", global.yaml and global-secret.yaml will be parsed (Optional, default: global)
        category_settings: Prefix for category settings. If value is "category", category.yaml and category-secret.yaml will be parsed (Optional, default: category)
        metro_settings: Prefix for metro settings. If value is "metro", metro.yaml and metro-secret.yaml will be parsed (Optional, default: metro)
    Returns: A dictionary of collected settings
    """
    settings = {}
    _merge_settings_type(global_settings, settings_dir, settings, 'settings-global')
    offerings_file = os.path.join(settings_dir, 'offerings.yaml')
    if offering and os.path.exists(offerings_file):
        offerings_settings = read_settings_file(offerings_file)
        offering_settings = offerings_settings[offering]
        offering_settings['offering']['name'] = offering
        settings = merge_settings(settings, offering_settings)
    if category:
        settings_sub_dir = os.path.join(settings_dir, category)
        _merge_settings_type(category_settings, settings_sub_dir, settings, '-'.join(['settings', category]))
        if metro:
            settings_sub_dir = os.path.join(settings_sub_dir, metro)
            _merge_settings_type(metro_settings, settings_sub_dir, settings, '-'.join(['settings', category, metro]))
            if offering:
                encryption_key = '-'.join(['environment', offering, category, metro])
                for setting_file in offering_settings_files:
                    path = os.path.join(settings_sub_dir, offering, setting_file)
                    if os.path.exists(path):
                        new_settings = read_settings_file(path, encryption_key if setting_file == 'secret.yaml' else None)
                        settings = merge_settings(settings, new_settings)
    return settings


def _merge_settings_type(settings_type, settings_dir, master_settings, decryption_key):
    """
    Helper function for reading to standard and encrypted settings for a setting "type". The type is the prefix for the setting files' names.
    New settings are merged into a dictionary that is passed as arguments.
    Args:
        settings_type: The type of settings to parse
        dir: Path to the directory containing the files to parse
        master_settings: Settings dictionary to merge new values into
        decryption_key: Name of decryption key to use for decrypting encrypted settings
    """
    settings_filename = '{type}.yaml'.format(type=settings_type)
    new_settings = read_settings_file(os.path.join(settings_dir, settings_filename))
    merge_settings(master_settings, new_settings)
    secret_filename = '{type}-secret.yaml'.format(type=settings_type)
    path = os.path.join(settings_dir, secret_filename)
    if os.path.exists(path):
        new_settings = read_settings_file(path, decryption_key)
        merge_settings(master_settings, new_settings)


def read_settings_file(settings_file, encryption_key=None):
    """
    Reads a yaml file and returns it's contents as a dictionary. If an encryption key is provided, decrypt the file
    using our Vault library.
    Args:
        settings_file: Path to file containing the settings
        encryption_key: The key to decypher the settings (Optional)
    Returns: A dictionary with the settings values
    """
    if not os.path.isfile(settings_file) or os.path.abspath(settings_file) != settings_file:  # Second check is to prevent traversal attack
        raise IOError('Setting file not found: {settings_file}'.format(settings_file=settings_file))
    with open(settings_file) as fh:
        new_settings = yaml.safe_load(fh)
        if new_settings is None:  # Empty Yaml file
            new_settings = {}
        if encryption_key:
            vault.decrypt_dict(encryption_key, new_settings)
        return new_settings


def merge_settings(master, partial):
    """
    Merges a settings dictionary into another, updating existing values if they exist on both dictionaries.
    Args:
        master: The master dictionary to merge into. This dictionary is mutated
        partial: The values to merge into master
    Returns: A reference to master, the mutated dictionary
    """
    for key in partial:
        if key in master:
            if isinstance(master[key], dict) and isinstance(partial[key], dict):
                merge_settings(master[key], partial[key])
            else:
                master[key] = partial[key]
        else:
            master[key] = partial[key]
    return master


def write_settings(category, metro, offering, new_settings, settings_type, overwrite_conflicts=True):
    """
    Writes offering-specific settings into a settings file. The passed settings data must be a dictionary and valid yaml and will be merged into existing settings.
    If the offering settings file does not exist, it will be created.
    If secrets are being written, they will be automatically encrypted.
    Args:
        category: The category of the environment, for example, production, stage, etc.
        metro: The name of the metro to wirte settings for
        offering: The name of the offering to write settings for
        new_settings: The values to merge into the settings file
        settings_type: The "type" of settings being updated. Must be one of "app", "infra" or "secret"
        overwrite_conflicts: Whether to overwrite any settings in the file if they conflict with new settings (Optional, default: True)
    """
    dir = os.path.join(settings_dir, category, metro, offering)
    if os.path.abspath(dir) != dir:
        raise Exception('Possible directory traversal detected for {dir}'.format(dir=dir))
    settings_file_name = '{type}.yaml'.format(type=settings_type)
    if settings_file_name not in offering_settings_files:
        raise Exception('Invalid settings type selected: {type}'.format(type=settings_type))
    full_path = os.path.join(dir, settings_file_name)
    if os.path.exists(full_path):
        with open(full_path) as fh:
            master_settings = yaml.safe_load(fh) or {}  # Account for the file being blank
    else:
        master_settings = {}
    if settings_type == 'secret':
        encryption_key = '-'.join(['environment', offering, category, metro])
        vault.encrypt_dict(encryption_key, new_settings)
    if not overwrite_conflicts:
        (master_settings, new_settings) = (new_settings, master_settings)  # merge original settings into new settings versus the opposite. Merging overwrites
    merge_settings(master_settings, new_settings)
    if not os.path.exists(dir):
        os.makedirs(dir)
    with open(full_path, 'w') as fh:
        yaml.safe_dump(master_settings, fh, default_flow_style=False, explicit_start=True, width=1000)
