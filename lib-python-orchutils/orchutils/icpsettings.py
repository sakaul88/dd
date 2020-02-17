import jinja2
import logging
import os
import shutil
import tempfile
import uuid
import yaml

logger = logging.getLogger(__name__)
common_settings_file = 'all.yaml'
offering_settings_file = 'offerings.yaml'
settings_dir = '/var/orch/icpsettings'
if 'P2PAAS_ICP_SETTINGS_DIR' in os.environ:
    settings_dir = os.environ['P2PAAS_ICP_SETTINGS_DIR']
templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icpsettings_templates')


def get_settings(datacenter=None, offering=None, common_settings_only=False):
    """
    Get a set of parsed settings. These settings can be generic, datacenter-specific or offering-specific.
    Datacenter-specific settings will contain the generic settings with the dc-specific values merged in.
    Offering-specific settings work the same way but will include generic offering-specific settings as well as datacenter offering-specific settings.
    Priority for settings of the same name are (from lowest to highest) generic -> offering -> datacenter -> datacenter-offering
    Args:
        datacenter: The name of the datacenter to pull settings for (Optional, at least 1 of datacenter or offering must be provided)
        offering: The name of the offering to pull settings for. Some offering settings may also require a datacenter (Optional)
        common_settings_only: Only load settings from the offering_settings_file files. This is typically done when preping a settings directory for bind-mounting into docker
    Returns: A dictionary of collected settings
    """
    with open(os.path.join(settings_dir, common_settings_file)) as fh:
        settings = yaml.safe_load(fh)
    if offering:  # Generic offering settings. Contains, for example, the letter assigned to the offering
        with open(os.path.join(settings_dir, offering_settings_file)) as fh:
            offering_settings = yaml.safe_load(fh)
        merge_settings(settings, offering_settings.get(offering, {}))
    if datacenter:
        dc_settings_dir = os.path.join(settings_dir, datacenter)
        if not os.path.isdir(dc_settings_dir):
            raise Exception('Datacenter "{dc}" is not valid'.format(dc=datacenter))
        with open(os.path.join(dc_settings_dir, common_settings_file)) as fh:
            merge_settings(settings, yaml.safe_load(fh))
        if offering:
            offering_settings_dir = os.path.join(dc_settings_dir, offering)
            offering_settings_files = [os.path.join(offering_settings_dir, 'group_vars', common_settings_file)]
            if not os.path.isfile(offering_settings_files[0]):
                del offering_settings_files[0]
            var_dir = os.path.join(offering_settings_dir, 'vars')
            if not common_settings_only and os.path.isdir(var_dir):
                for offering_setting_file in os.listdir(var_dir):
                    if offering_setting_file.endswith('.yaml') or offering_setting_file.endswith('.yml'):
                        offering_settings_files.append(os.path.join(var_dir, offering_setting_file))
            for settings_file in offering_settings_files:
                with open(settings_file) as fh:
                    merge_settings(settings, yaml.safe_load(fh))
    return settings


def list_datacenters():
    """
    Retrieves a list of datacenters currently defined in the settings directory.
    Returns: A list of strings of datacenters
    """
    return [dc for dc in os.listdir(settings_dir) if os.path.isdir(os.path.join(settings_dir, dc))]


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


def write_settings(new_settings, relative_path=None, full_path=None, overwrite_conflicts=True):
    """
    Writes settings into a settings file. The passed settings data must be a dictionary and valid yaml and will be merged into existing settings.
    If the target settings file does not exist, it will be created.
    Provide one of relative_path or full_path to update. If both are passed, relative_path is used
    Args:
        new_settings: The values to merge into the settings file
        relative_path: Sub-file of main settings directory to update. Eg. 'wdc04/hub/vars/environment.yaml' (Optional, must provide either relative_path or full_path)
        full_path: Absolute path of a file to update. Will be created if it does not exist. (Optional, must provide either relative_path or full_path)
        overwrite_conflicts: Whether to overwrite any settings in the file if they conflict with new settings (Optional, default: True)
    """
    if relative_path:
        full_path = os.path.join(settings_dir, relative_path)
    if not full_path:
        raise Exception('Either relative_path or full_path must be provided')
    dir_path = os.path.dirname(full_path)
    if os.path.exists(full_path):
        with open(full_path) as fh:
            master_settings = yaml.safe_load(fh) or {}  # Account for the file being blank
    else:
        master_settings = {}
    if not overwrite_conflicts:
        (master_settings, new_settings) = (new_settings, master_settings)  # merge original settings into new settings versus the opposite. Merging overwrites
    merge_settings(master_settings, new_settings)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with open(full_path, 'w') as fh:
        yaml.safe_dump(master_settings, fh, default_flow_style=False, explicit_start=True, width=1000)


def prep_environment_settings(datacenter, offering):
    """
    Prepares and environment's settings for downstream (ansbile) consumption.
    Global, datacenter and offering level settings are merged into an environments settings which are then written to a temporary directory.
    It is the callers responsibility to clean up the temporary directory when they are finished with it.
    Args:
        datacenter: The name of the datacenter to pull settings for
        offering: The name of the offering to pull settings for. Some offering settings may also require a datacenter
    Returns: A string containing the fully qualified path to the prep'ed settings directory
    """
    preped_settings_dir = tempfile.mkdtemp()
    environment_settings_dir = os.path.join(settings_dir, datacenter, offering)
    try:
        os.rmdir(preped_settings_dir)  # Perhaps not the most efficient way to create a path without the directory, but shutil mandates the directory does not exist
        shutil.copytree(environment_settings_dir, preped_settings_dir)
        common_settings = get_settings(datacenter, offering, common_settings_only=True)
        write_settings(common_settings, full_path=os.path.join(preped_settings_dir, 'group_vars', common_settings_file))
    except Exception:
        if os.path.exists(preped_settings_dir):
            shutil.rmtree(preped_settings_dir)  # Purge the temporary settings directory if an exception is raised and re-raise the exception
        raise
    return preped_settings_dir


def seed_environment_settings(datacenter, offering):
    """
    Seeds the settings configuration for a new environment from a template. Any existing settings in the settings directory will not be overwritten.
    If the template process has already executed against an environment, re-calling this function is a no-op. (identified by the presence of the hosts file)
    Args:
        datacenter: The name of the datacenter to contain the new environment
        offering: The name of the offering that the environment is for
    Returns: True if template parsing occured. False is it was identified that this environment already underwent seeding of settings
    """
    environment_settings_dir = os.path.join(settings_dir, datacenter, offering)
    if os.path.exists(os.path.join(environment_settings_dir, 'hosts')):
        logger.info('settings for offering "{offering}" in datacenter "{datacenter}" have already been seeded. Will not reapply'.format(datacenter=datacenter, offering=offering))
        return False
    logger.info('Seeding settings for offering "{offering}" in datacenter "{datacenter}"'.format(datacenter=datacenter, offering=offering))
    base_settings = get_settings(datacenter, offering)
    jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(templates_dir), extensions=['jinja2.ext.do'])
    template_settings = {
        'config': base_settings,
        'datacenter': datacenter,
        'offering': offering,
        'uuid4': uuid.uuid4
    }
    direct_mapping_dirs = ['group_vars', 'vars']  # These directories contain templates that are directly mapped 1:1 into the environment settings directory
    node_dir = 'host_vars'
    logger.info('Creating base settings folders if they do not yet exist')
    for sub_dir in direct_mapping_dirs + [node_dir]:
        sub_dir_path = os.path.join(environment_settings_dir, sub_dir)
        if not os.path.exists(sub_dir_path):
            os.makedirs(sub_dir_path)
    logger.info('Merging common settings into directories {dirs}. Existing settings will not be overwritten'.format(dirs=', '.join(direct_mapping_dirs)))
    for template_subdir in direct_mapping_dirs:
        template_filenames = os.listdir(os.path.join(templates_dir, template_subdir))
        for filename in template_filenames:
            template = jinja_environment.get_template('{template_subdir}/{filename}'.format(template_subdir=template_subdir, filename=filename))
            rendered_template = template.render(**template_settings)
            write_settings(yaml.safe_load(rendered_template), relative_path=os.path.join(datacenter, offering, template_subdir, filename), overwrite_conflicts=False)
    logger.info('Writing node-specific configuration files. Existing settings will not be overwritten')
    nodes = base_settings['icp']['nodes']['vmware']
    for node_type in nodes:
        for node in nodes[node_type]['current']:
            template = jinja_environment.get_template('{node_dir}/{node_type}.yaml'.format(node_dir=node_dir, node_type=node_type))
            rendered_template = template.render(node=node, **template_settings)
            output_file = os.path.join(datacenter, offering, node_dir, '{shortname}.yaml'.format(shortname=node['hostname'].split('.', 2)[0]))
            write_settings(yaml.safe_load(rendered_template), relative_path=output_file, overwrite_conflicts=False)
    zones = base_settings['icp'].get('zones')
    if zones:
        logger.info('Writing zone information. Existing settings will not be overwritten')
        for zone in zones:
            output_file = os.path.join(datacenter, offering, 'group_vars', '{zone_name}.yaml'.format(zone_name=zone['zone_name']))
            write_settings(zone, relative_path=output_file, overwrite_conflicts=False)
    logger.info('Writing hosts file')
    rendered_template = jinja_environment.get_template('hosts').render(**template_settings)
    with open(os.path.join(environment_settings_dir, 'hosts'), 'w') as fh:
        fh.write(rendered_template)
    logger.info('Seeding of settings is complete')
    return True
